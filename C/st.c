#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "commandparser.h"
#include "input.h"
#include "display.h"

static char **lines = NULL;
static int    line_count = 0;

static void load_file(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); exit(1); }
    char tmp[4096];
    int cap = 0;
    while (fgets(tmp, sizeof tmp, f)) {
        tmp[strcspn(tmp, "\r\n")] = '\0';
        if (line_count == cap) {
            cap = cap ? cap * 2 : 64;
            lines = realloc(lines, cap * sizeof(char *));
        }
        lines[line_count++] = strdup(tmp);
    }
    fclose(f);
}

int main(int argc, char **argv) {
    cmp_init();
    input_start();

    if (argc < 2) {
        char buf[4096];
        while (!input_should_exit()) {
            fputs("> ", stdout); fflush(stdout);
            if (!fgets(buf, sizeof buf, stdin)) break;
            buf[strcspn(buf, "\r\n")] = '\0';
            parse(buf, 0, 0);
        }
        input_stop(); cmp_shutdown();
        return 0;
    }

    load_file(argv[1]);
    int wants_display = line_count > 0 && strcmp(lines[0], "d") == 0;
    if (wants_display) display_start();
    functionfind(argv[1]);

    int fileindex = 0, cache = 0;

    while (fileindex < line_count && !input_should_exit()) {
        parse(lines[fileindex], fileindex + 1, 0);
        if (wants_display) frame_accumulate();

        if (skip) {
            while (fileindex < line_count && strcmp(lines[fileindex], "e") != 0)
                fileindex++;
            if (fileindex >= line_count)
                printf("Please add a \"e\" command to your code to end the function!\n");
            skip = 0;
        }

        if (runfunction) { cache = fileindex; fileindex = functionitem - 1; runfunction = 0; }
        if (fileindex < line_count && strcmp(lines[fileindex], "e") == 0)
            if (jumpback) { fileindex = cache; jumpback = 0; }

            fileindex++;
    }

    input_stop();
    if (wants_display) { display_signal_exit(); display_stop(); }
    for (int i = 0; i < line_count; i++) free(lines[i]);
    free(lines);
    cmp_shutdown();
    return 0;
}
