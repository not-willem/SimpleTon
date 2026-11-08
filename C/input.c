#include <X11/Xlib.h>
#include <X11/keysym.h>
#include <X11/XKBlib.h>
#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <unistd.h>
#include <signal.h>
#include "input.h"
#include "commandparser.h"

static volatile sig_atomic_t want_exit = 0;
static void on_sigint(int sig) { (void)sig; want_exit = 1; }

#define MAX_HELD 32
static char held[MAX_HELD][32];
static int  held_n = 0;

static const char *keysym_name(KeySym ks, char *buf, size_t bufsz) {
    switch (ks) {
        case XK_Shift_L: case XK_Shift_R:     return "shift";
        case XK_Control_L: case XK_Control_R: return "ctrl";
        case XK_Alt_L: case XK_Alt_R:         return "alt";
        case XK_Super_L: case XK_Super_R:     return "logo";
        case XK_space:                        return "space";
        case XK_Caps_Lock:                    return "caps";
        case XK_Tab:                          return "tab";
        case XK_Up:                           return "up";
        case XK_Down:                         return "down";
        case XK_Left:                         return "left";
        case XK_Right:                        return "right";
        case XK_Return:                       return "enter";
        case XK_Escape:                       return "escape";
        case XK_BackSpace:                    return "backspace";
        case XK_Delete:                       return "delete";
        case XK_Home:                         return "home";
        case XK_End:                          return "end";
        case XK_Page_Up:                      return "pageup";
        case XK_Page_Down:                    return "pagedown";
        default: break;
    }
    if (ks >= XK_F1 && ks <= XK_F12) {
        snprintf(buf, bufsz, "F%ld", (long)(ks - XK_F1 + 1));
        return buf;
    }
    if (ks >= 0x20 && ks < 0x7f) {
        buf[0] = (char)ks; buf[1] = '\0';
        for (int i = 0; buf[i]; i++)
            buf[i] = (char)tolower((unsigned char)buf[i]);
        return buf;
    }
    return NULL;
}

static void held_add(const char *name) {
    for (int i = 0; i < held_n; i++) if (!strcmp(held[i], name)) return;
    if (held_n >= MAX_HELD) return;
    snprintf(held[held_n++], 32, "%s", name);
}

static void publish_keys(void) {
    char out[1024] = "";
    if (held_n == 0) {
        snprintf(out, sizeof out, "none\n");
    } else {
        for (int i = 0; i < held_n; i++) {
            if (i) strncat(out, " ", sizeof out - strlen(out) - 1);
            strncat(out, held[i], sizeof out - strlen(out) - 1);
        }
        strncat(out, "\n", sizeof out - strlen(out) - 1);
    }
    mov(out, 6);
}

static void *listener_thread(void *arg) {
    (void)arg;
    Display *dpy = XOpenDisplay(NULL);
    if (!dpy) { fprintf(stderr, "input: cannot open X display\n"); return NULL; }
    Window root = DefaultRootWindow(dpy);

    char keymap[32];
    int last_mx = -1, last_my = -1;

    while (!want_exit) {
        XQueryKeymap(dpy, keymap);
        held_n = 0;
        for (int code = 8; code < 256; code++) {
            if (!(keymap[code / 8] & (1 << (code % 8)))) continue;
            KeySym ks = XkbKeycodeToKeysym(dpy, (KeyCode)code, 0, 0);
            char buf[16];
            const char *nm = keysym_name(ks, buf, sizeof buf);
            if (nm && *nm) held_add(nm);
        }
        publish_keys();

        Window r, c; int rx, ry, wx, wy; unsigned mask;
        if (XQueryPointer(dpy, root, &r, &c, &rx, &ry, &wx, &wy, &mask)) {
            if (rx != last_mx || ry != last_my) {
                char b[32];
                snprintf(b, sizeof b, "%d\n", rx); mov(b, 7);
                snprintf(b, sizeof b, "%d\n", ry); mov(b, 8);
                last_mx = rx; last_my = ry;
            }
        }
        usleep(10000);
    }

    XCloseDisplay(dpy);
    return NULL;
}

static pthread_t tid;
static int started = 0;

void input_start(void) {
    if (started) return;
    signal(SIGINT,  on_sigint);
    signal(SIGTERM, on_sigint);
    pthread_create(&tid, NULL, listener_thread, NULL);
    pthread_detach(tid);
    started = 1;
}

void input_stop(void) { want_exit = 1; usleep(50000); started = 0; }
int  input_should_exit(void) { return want_exit; }
