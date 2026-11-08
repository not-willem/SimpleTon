#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>
#include <pthread.h>
#include "commandparser.h"

#define MAX_TOKENS 32
#define MAX_TOKEN  256

char  *STORAGE[STORAGE_SIZE];
char **functions_name;
int   *functions_line;
int    functions_count = 0;
int    functions_cap   = 0;

int skip         = 0;
int runfunction  = 0;
int jumpback     = 0;
int functionitem = 0;

static pthread_mutex_t storage_lock = PTHREAD_MUTEX_INITIALIZER;

static char accum[6][256];
static char disp_frame[6][256];
static int  disp_has_frame = 0;
static int  disp_exit = 0;

void cmp_init(void) {
    for (int i = 0; i < STORAGE_SIZE; i++)
        STORAGE[i] = strdup("");
    for (int i = 0; i < 6; i++) {
        accum[i][0] = '\0';
        disp_frame[i][0] = '\0';
    }
    disp_has_frame = 0;
    disp_exit = 0;
}

void cmp_shutdown(void) {
    for (int i = 0; i < STORAGE_SIZE; i++) { free(STORAGE[i]); STORAGE[i] = NULL; }
    for (int i = 0; i < functions_count; i++) free(functions_name[i]);
    free(functions_name);
    free(functions_line);
    functions_name = NULL;
    functions_line = NULL;
    functions_count = functions_cap = 0;
}

void mov(const char *text, int line) {
    if (line < 0 || line >= STORAGE_SIZE) return;
    char *copy = strdup(text);
    pthread_mutex_lock(&storage_lock);
    free(STORAGE[line]);
    STORAGE[line] = copy;
    pthread_mutex_unlock(&storage_lock);
}

const char *getline_(int line) {
    if (line <= 0 || line > STORAGE_SIZE) return "";
    return STORAGE[line - 1];
}

const char *getsector(const char *sector) {
    return getline_(atoi(sector + 1));
}

int getline_copy(int line, char *out, size_t outsz) {
    if (line <= 0 || line > STORAGE_SIZE) { if (outsz) out[0] = '\0'; return 0; }
    pthread_mutex_lock(&storage_lock);
    snprintf(out, outsz, "%s", STORAGE[line - 1]);
    pthread_mutex_unlock(&storage_lock);
    return 1;
}

void clear_slot(int line) {
    if (line < 0 || line >= STORAGE_SIZE) return;
    pthread_mutex_lock(&storage_lock);
    free(STORAGE[line]);
    STORAGE[line] = strdup("");
    pthread_mutex_unlock(&storage_lock);
}

int frame_accumulate(void) {
    int completed = 0;
    pthread_mutex_lock(&storage_lock);

    for (int i = 0; i < 6; i++) {
        if (*STORAGE[i])
            snprintf(accum[i], sizeof accum[i], "%s", STORAGE[i]);
        free(STORAGE[i]);
        STORAGE[i] = strdup("");
    }

    int all = 1;
    for (int i = 0; i < 6; i++)
        if (!*accum[i]) { all = 0; break; }

        if (all) {
            for (int i = 0; i < 6; i++)
                snprintf(disp_frame[i], sizeof disp_frame[i], "%s", accum[i]);
            for (int i = 0; i < 6; i++)
                accum[i][0] = '\0';
            disp_has_frame = 1;
            completed = 1;
        }

        pthread_mutex_unlock(&storage_lock);
        return completed;
}

int display_take_frame(char out[6][256]) {
    int got = 0;
    pthread_mutex_lock(&storage_lock);
    if (disp_has_frame) {
        for (int i = 0; i < 6; i++)
            snprintf(out[i], 256, "%s", disp_frame[i]);
        disp_has_frame = 0;
        got = 1;
    }
    pthread_mutex_unlock(&storage_lock);
    return got;
}

void display_signal_exit(void) {
    pthread_mutex_lock(&storage_lock);
    disp_exit = 1;
    pthread_mutex_unlock(&storage_lock);
}

static int tokenize(const char *s, char tokens[][MAX_TOKEN], int max_tokens) {
    int n = 0;
    while (*s && n < max_tokens) {
        while (*s && isspace((unsigned char)*s)) s++;
        if (!*s) break;
        if (*s == '"') {
            int i = 0;
            tokens[n][i++] = *s++;
            while (*s && *s != '"' && i < MAX_TOKEN - 1) tokens[n][i++] = *s++;
            if (*s == '"') tokens[n][i++] = *s++;
            tokens[n][i] = '\0';
        } else {
            int i = 0;
            while (*s && !isspace((unsigned char)*s) && i < MAX_TOKEN - 1)
                tokens[n][i++] = *s++;
            tokens[n][i] = '\0';
        }
        n++;
    }
    return n;
}

typedef enum { T_SECTOR, T_STRING, T_NUMBER, T_IFFUNC, T_ERROR } ArgType;

static ArgType findtype(const char *arg) {
    if (!arg || !*arg) return T_ERROR;
    if (arg[0] == 'x') return T_SECTOR;
    if (strchr(arg, '"')) return T_STRING;
    if (strchr(arg, '(')) return T_NUMBER;
    if (strchr(arg, ':')) return T_IFFUNC;
    return T_ERROR;
}

static const char *strip(const char *src, const char *chars) {
    static char buf[MAX_TOKEN];
    int i = 0;
    for (const char *p = src; *p && i < MAX_TOKEN - 1; p++) {
        if (strchr(chars, *p)) continue;
        buf[i++] = *p;
    }
    buf[i] = '\0';
    return buf;
}

void functionfind(const char *filename) {
    FILE *f = fopen(filename, "r");
    if (!f) return;
    char line[1024];
    int index = 0;
    while (fgets(line, sizeof line, f)) {
        index++;
        line[strcspn(line, "\r\n")] = '\0';
        char toks[MAX_TOKENS][MAX_TOKEN];
        int n = tokenize(line, toks, MAX_TOKENS);
        if (n >= 2 && strcmp(toks[0], "f") == 0) {
            if (functions_count == functions_cap) {
                functions_cap = functions_cap ? functions_cap * 2 : 16;
                functions_name = realloc(functions_name, functions_cap * sizeof(char *));
                functions_line = realloc(functions_line, functions_cap * sizeof(int));
            }
            functions_name[functions_count] = strdup(strip(toks[1], "\""));
            functions_line[functions_count] = index;
            functions_count++;
        }
    }
    fclose(f);
}

static void runfunc(const char *name, int jb) {
    for (int i = 0; i < functions_count; i++) {
        if (strcmp(functions_name[i], name) == 0) {
            runfunction  = 1;
            functionitem = functions_line[i];
            jumpback     = jb;
            return;
        }
    }
}

static void read_sector(const char *tok, char *out, size_t outsz) {
    getline_copy(atoi(tok + 1), out, outsz);
}

void parse(const char *command, int line, int verbose) {
    (void)verbose;
    char toks[MAX_TOKENS][MAX_TOKEN];
    int n = tokenize(command, toks, MAX_TOKENS);

    const char *parsecommand = (n > 0) ? toks[0] : "#";

    #define ERR_SPELLING() do { \
    if (line == 0) printf("Please check your spelling!\n"); \
        else           printf("Please check your spelling on line %d\n", line); \
            return; } while (0)

            #define NEED(k) do { if (n <= (k)) { ERR_SPELLING(); } } while (0)

            if (strcmp(parsecommand, "m") == 0) {
                NEED(2);
                if (findtype(toks[1]) == T_SECTOR) {
                    char src[MAX_TOKEN * 4];
                    read_sector(toks[1], src, sizeof src);
                    if (findtype(toks[2]) == T_SECTOR)
                        mov(src, atoi(toks[2] + 1) - 1);
                } else if (findtype(toks[1]) == T_STRING) {
                    if (findtype(toks[2]) == T_SECTOR) {
                        char buf[MAX_TOKEN + 2];
                        snprintf(buf, sizeof buf, "%s\n", strip(toks[1], "\""));
                        mov(buf, atoi(toks[2] + 1) - 1);
                    }
                } else if (findtype(toks[1]) == T_NUMBER) {
                    if (findtype(toks[2]) == T_SECTOR) {
                        char buf[MAX_TOKEN + 2];
                        snprintf(buf, sizeof buf, "%s\n", strip(toks[1], "()"));
                        mov(buf, atoi(toks[2] + 1) - 1);
                    }
                }

            } else if (strcmp(parsecommand, "p") == 0) {
                NEED(1);
                ArgType t = findtype(toks[1]);
                if (t == T_STRING)      printf("%s\n", strip(toks[1], "\""));
                else if (t == T_NUMBER) printf("%s\n", strip(toks[1], "()"));
                else if (t == T_SECTOR) {
                    char buf[MAX_TOKEN * 4];
                    read_sector(toks[1], buf, sizeof buf);
                    buf[strcspn(buf, "\r\n")] = '\0';
                    printf("%s\n", buf);
                }

            } else if (strcmp(parsecommand, "a") == 0) {
                NEED(2);
                if (strcmp(toks[1], "t") == 0) {
                    NEED(3);
                    if (findtype(toks[3]) == T_SECTOR) {
                        char lb[MAX_TOKEN * 4], rb[MAX_TOKEN * 4];
                        read_sector(toks[3], lb, sizeof lb);
                        double lhs = atof(lb), rhs;
                        if (findtype(toks[2]) == T_SECTOR) { read_sector(toks[2], rb, sizeof rb); rhs = atof(rb); }
                        else rhs = atof(strip(toks[2], "()"));
                        char buf[64];
                        snprintf(buf, sizeof buf, "%.10g\n", lhs * rhs);
                        mov(buf, atoi(toks[3] + 1) - 1);
                    }
                } else {
                    if (findtype(toks[2]) == T_SECTOR) {
                        char lb[MAX_TOKEN * 4], rb[MAX_TOKEN * 4];
                        read_sector(toks[2], lb, sizeof lb);
                        double lhs = atof(lb), rhs;
                        if (findtype(toks[1]) == T_SECTOR) { read_sector(toks[1], rb, sizeof rb); rhs = atof(rb); }
                        else rhs = atof(strip(toks[1], "()"));
                        char buf[64];
                        snprintf(buf, sizeof buf, "%.10g\n", lhs + rhs);
                        mov(buf, atoi(toks[2] + 1) - 1);
                    }
                }

            } else if (strcmp(parsecommand, "s") == 0) {
                NEED(2);
                if (strcmp(toks[1], "d") == 0) {
                    NEED(3);
                    if (findtype(toks[3]) == T_SECTOR) {
                        char lb[MAX_TOKEN * 4], rb[MAX_TOKEN * 4];
                        read_sector(toks[3], lb, sizeof lb);
                        double lhs = atof(lb), rhs;
                        if (findtype(toks[2]) == T_SECTOR) { read_sector(toks[2], rb, sizeof rb); rhs = atof(rb); }
                        else rhs = atof(strip(toks[2], "()"));
                        char buf[64];
                        snprintf(buf, sizeof buf, "%.10g\n", lhs / rhs);
                        mov(buf, atoi(toks[3] + 1) - 1);
                    }
                } else {
                    if (findtype(toks[2]) == T_SECTOR) {
                        char lb[MAX_TOKEN * 4], rb[MAX_TOKEN * 4];
                        read_sector(toks[2], lb, sizeof lb);
                        double lhs = atof(lb), rhs;
                        if (findtype(toks[1]) == T_SECTOR) { read_sector(toks[1], rb, sizeof rb); rhs = atof(rb); }
                        else rhs = atof(strip(toks[1], "()"));
                        char buf[64];
                        snprintf(buf, sizeof buf, "%.10g\n", lhs - rhs);
                        mov(buf, atoi(toks[2] + 1) - 1);
                    }
                }

            } else if (strcmp(parsecommand, "c") == 0) {
                NEED(1);
                runfunc(strip(toks[1], "\""), 1);

            } else if (strcmp(parsecommand, "j") == 0) {
                NEED(1);
                runfunc(strip(toks[1], "\""), 0);

            } else if (strcmp(parsecommand, "i") == 0) {
                NEED(4);
                char first[MAX_TOKEN * 4] = "", second[MAX_TOKEN * 4] = "";

                ArgType t1 = findtype(toks[1]);
                if      (t1 == T_SECTOR) read_sector(toks[1], first, sizeof first);
                else if (t1 == T_NUMBER) snprintf(first, sizeof first, "%s", strip(toks[1], "()"));
                else if (t1 == T_STRING) snprintf(first, sizeof first, "%s", strip(toks[1], "\""));
                else                     snprintf(first, sizeof first, "%s", toks[1]);

                ArgType t3 = findtype(toks[3]);
                if      (t3 == T_SECTOR) read_sector(toks[3], second, sizeof second);
                else if (t3 == T_NUMBER) snprintf(second, sizeof second, "%s", strip(toks[3], "()"));
                else if (t3 == T_STRING) snprintf(second, sizeof second, "%s", strip(toks[3], "\""));
                else                     snprintf(second, sizeof second, "%s", toks[3]);

                first[strcspn(first, "\r\n")] = '\0';
                second[strcspn(second, "\r\n")] = '\0';

                const char *op = toks[2];

                if (findtype(toks[4]) != T_IFFUNC) {
                    int truth = 0;
                    int cmp = strcmp(first, second);
                    double a = atof(first), b = atof(second);
                    if      (!strcmp(op, "="))  truth = (cmp == 0);
                    else if (!strcmp(op, ">"))  truth = (a > b);
                    else if (!strcmp(op, "<"))  truth = (a < b);
                    else if (!strcmp(op, "!=") || !strcmp(op, "=!")) truth = (cmp != 0);
                    mov(truth ? "1" : "0", atoi(toks[4] + 1));
                } else {
                    const char *func = strip(toks[4], ":");
                    int truth = 0;
                    int cmp = strcmp(first, second);
                    double a = atof(first), b = atof(second);
                    if      (!strcmp(op, "="))  truth = (cmp == 0);
                    else if (!strcmp(op, ">"))  truth = (a > b);
                    else if (!strcmp(op, "<"))  truth = (a < b);
                    else if (!strcmp(op, "!=") || !strcmp(op, "=!")) truth = (cmp != 0);
                    if (truth) runfunc(func, 1);
                }

            } else if (strcmp(parsecommand, "l") == 0) {
                NEED(3);
                if (strcmp(toks[1], "j") == 0) {
                    NEED(4);
                    char buf[MAX_TOKEN * 2 + 2];
                    snprintf(buf, sizeof buf, "%s%s\n", strip(toks[2], "\""), strip(toks[3], "\""));
                    mov(buf, atoi(toks[4] + 1) - 1);
                } else {
                    char text[MAX_TOKEN * 4] = "";
                    if (findtype(toks[1]) == T_STRING)
                        snprintf(text, sizeof text, "%s", strip(toks[1], "\""));
                    else if (findtype(toks[1]) == T_SECTOR)
                        read_sector(toks[1], text, sizeof text);

                    int idx  = atoi(strip(toks[2], "()")) - 1;
                    int dest = atoi(toks[3] + 1) - 1;

                    char out[3] = {0};
                    if (idx >= 0 && (size_t)idx < strlen(text)) out[0] = text[idx];

                    if (findtype(toks[1]) == T_SECTOR) {
                        char w[4]; snprintf(w, sizeof w, "%s\n", out); mov(w, dest);
                    } else {
                        mov(out, dest);
                    }
                }

            } else if (strcmp(parsecommand, "f") == 0) {
                if (line == 0) printf("You cannot create functions in shell mode!\n");
                else           skip = 1;

            } else if (strcmp(parsecommand, "t") == 0) {
                NEED(3);
                if (strcmp(toks[1], "w") == 0) {
                    double secs = atof(strip(toks[2], "()"));
                    const char *func = strip(toks[3], ":");
                    struct timespec ts;
                    ts.tv_sec  = (time_t)secs;
                    ts.tv_nsec = (long)((secs - (double)ts.tv_sec) * 1e9);
                    nanosleep(&ts, NULL);
                    runfunc(func, 1);
                }

            } else if (strcmp(parsecommand, "d") == 0 ||
                strcmp(parsecommand, "#") == 0 ||
                strcmp(parsecommand, "e") == 0) {
                /* no-op */

                } else {
                    if (line != 0)
                        printf("Failed to parse command \"%s\" on line %d.. Maybe check your spelling?\n", parsecommand, line);
                    else
                        printf("Failed to parse command \"%s\".. Maybe check your spelling?\n", parsecommand);
                }

                #undef NEED
                #undef ERR_SPELLING
}
