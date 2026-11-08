#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/keysym.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include "display.h"
#include "commandparser.h"
#include "input.h"

#define VIRTUAL_W 1920.0
#define VIRTUAL_H 1080.0

static Display *dpy     = NULL;
static Window   win     = 0;
static GC       gc      = NULL;
static int      screen  = 0;
static int      win_w   = 0;
static int      win_h   = 0;
static int      running = 0;

static char tri_stash[6][256];
static int  tri_active = 0;

static unsigned long parse_color(const char *s) {
    int r = 0, g = 0, b = 0;
    if (sscanf(s, "(%d,%d,%d)", &r, &g, &b) != 3)
        if (sscanf(s, "%d,%d,%d", &r, &g, &b) != 3)
            r = g = b = 0;
    if (r < 0) r = 0; if (r > 255) r = 255;
    if (g < 0) g = 0; if (g > 255) g = 255;
    if (b < 0) b = 0; if (b > 255) b = 255;

    XColor c;
    c.red   = (unsigned short)(r * 257);
    c.green = (unsigned short)(g * 257);
    c.blue  = (unsigned short)(b * 257);
    c.flags = DoRed | DoGreen | DoBlue;
    if (XAllocColor(dpy, DefaultColormap(dpy, screen), &c)) return c.pixel;
    return BlackPixel(dpy, screen);
}

static double sx(double v) { return v * ((double)win_w / VIRTUAL_W); }
static double sy(double v) { return v * ((double)win_h / VIRTUAL_H); }

static void draw_one(const char *s1, const char *s2, const char *s3,
                     const char *s4, const char *s5, const char *s6) {
    unsigned long color = parse_color(s5);

    if (!strcmp(s6, "circle") || !strcmp(s6, "filledcircle")) {
        double x = sx(atof(s1)), y = sy(atof(s2));
        double w = sx(atof(s3) - atof(s1));
        double h = sy(atof(s4) - atof(s2));
        XSetForeground(dpy, gc, color);
        if (!strcmp(s6, "filledcircle"))
            XFillArc(dpy, win, gc, (int)x, (int)y, (int)w, (int)h, 0, 360*64);
        else {
            XSetLineAttributes(dpy, gc, 1, LineSolid, CapButt, JoinMiter);
            XDrawArc(dpy, win, gc, (int)x, (int)y, (int)w, (int)h, 0, 360*64);
        }
    } else if (!strcmp(s6, "square") || !strcmp(s6, "filledsquare")) {
        double x = sx(atof(s1)), y = sy(atof(s2));
        double w = sx(atof(s3) - atof(s1));
        double h = sy(atof(s4) - atof(s2));
        if (w < 0) { x += w; w = -w; }
        if (h < 0) { y += h; h = -h; }
        XSetForeground(dpy, gc, color);
        if (!strcmp(s6, "filledsquare"))
            XFillRectangle(dpy, win, gc, (int)x, (int)y, (int)w, (int)h);
        else {
            XSetLineAttributes(dpy, gc, 1, LineSolid, CapButt, JoinMiter);
            XDrawRectangle(dpy, win, gc, (int)x, (int)y, (int)w, (int)h);
        }
    } else if (!strcmp(s6, "text")) {
        XFontStruct *font = XLoadQueryFont(dpy, "fixed");
        if (font) XSetFont(dpy, gc, font->fid);
        XSetForeground(dpy, gc, color);
        XDrawString(dpy, win, gc, (int)sx(atof(s1)), (int)sy(atof(s2)),
                    s4, (int)strlen(s4));
        if (font) XFreeFont(dpy, font);
    } else if (!strcmp(s6, "triangle") || !strcmp(s6, "filledtriangle")) {
        if (strcmp(s4, "none") != 0 && !tri_active) {
            snprintf(tri_stash[0], sizeof tri_stash[0], "%s", s1);
            snprintf(tri_stash[1], sizeof tri_stash[1], "%s", s2);
            snprintf(tri_stash[2], sizeof tri_stash[2], "%s", s3);
            snprintf(tri_stash[3], sizeof tri_stash[3], "%s", s4);
            snprintf(tri_stash[4], sizeof tri_stash[4], "%s", s5);
            snprintf(tri_stash[5], sizeof tri_stash[5], "%s", s6);
            tri_active = 1;
        } else if (!strcmp(s4, "none") && tri_active) {
            double x1 = sx(atof(tri_stash[0])), y1 = sy(atof(tri_stash[1]));
            double x2 = sx(atof(tri_stash[2])), y2 = sy(atof(tri_stash[3]));
            unsigned long tc = parse_color(tri_stash[4]);
            int  filled = !strcmp(tri_stash[5], "filledtriangle");
            double x3 = sx(atof(s1)), y3 = sy(atof(s2));
            int outline = (int)atof(s3);
            XPoint pts[3] = {{(short)x1,(short)y1},{(short)x2,(short)y2},{(short)x3,(short)y3}};
            XSetForeground(dpy, gc, tc);
            if (filled) {
                if (outline == 0) XFillPolygon(dpy, win, gc, pts, 3, Complex, CoordModeOrigin);
                else {
                    XSetLineAttributes(dpy, gc, outline, LineSolid, CapButt, JoinMiter);
                    XDrawLines(dpy, win, gc, pts, 3, CoordModeOrigin);
                    XDrawLine(dpy, win, gc, pts[2].x, pts[2].y, pts[0].x, pts[0].y);
                }
            } else {
                XSetLineAttributes(dpy, gc, outline == 0 ? 1 : outline, LineSolid, CapButt, JoinMiter);
                XDrawLines(dpy, win, gc, pts, 3, CoordModeOrigin);
                XDrawLine(dpy, win, gc, pts[2].x, pts[2].y, pts[0].x, pts[0].y);
            }
            tri_active = 0;
        }
    }
                     }

                     void display_render(void) {
                         if (!running || !dpy || !win) return;
                         char slots[6][256];
                         if (!display_take_frame(slots)) return;
                         for (int i = 0; i < 6; i++) slots[i][strcspn(slots[i], "\r\n")] = '\0';
                         draw_one(slots[0], slots[1], slots[2], slots[3], slots[4], slots[5]);
                     }

                     static void *display_thread(void *arg) {
                         (void)arg;
                         dpy = XOpenDisplay(NULL);
                         if (!dpy) { fprintf(stderr, "display: cannot open X display\n"); return NULL; }
                         screen = DefaultScreen(dpy);
                         win_w = DisplayWidth(dpy, screen);
                         win_h = DisplayHeight(dpy, screen);

                         XSetWindowAttributes attrs;
                         attrs.background_pixel = BlackPixel(dpy, screen);
                         attrs.event_mask = ExposureMask | KeyPressMask | StructureNotifyMask;
                         win = XCreateWindow(dpy, RootWindow(dpy, screen), 0, 0, win_w, win_h, 0,
                                             CopyFromParent, InputOutput, CopyFromParent,
                                             CWBackPixel | CWEventMask, &attrs);
                         XStoreName(dpy, win, "SimpleTon");
                         XMapWindow(dpy, win);
                         XFlush(dpy);

                         gc = XCreateGC(dpy, win, 0, NULL);
                         XSetForeground(dpy, gc, WhitePixel(dpy, screen));
                         running = 1;

                         XEvent ev;
                         while (!input_should_exit()) {
                             while (XPending(dpy)) {
                                 XNextEvent(dpy, &ev);
                                 if (ev.type == ConfigureNotify) {
                                     win_w = ev.xconfigure.width;
                                     win_h = ev.xconfigure.height;
                                 } else if (ev.type == KeyPress) {
                                     KeySym ks = XLookupKeysym(&ev.xkey, 0);
                                     if (ks == XK_Escape) {
                                         running = 0;
                                         XFreeGC(dpy, gc);
                                         XDestroyWindow(dpy, win);
                                         XCloseDisplay(dpy);
                                         win = 0; dpy = NULL;
                                         return NULL;
                                     }
                                 }
                             }
                             display_render();
                             XFlush(dpy);
                             usleep(16000);
                         }

                         XFreeGC(dpy, gc);
                         XDestroyWindow(dpy, win);
                         XCloseDisplay(dpy);
                         win = 0; dpy = NULL;
                         running = 0;
                         return NULL;
                     }

                     static pthread_t disp_tid;

                     void display_start(void) {
                         if (running) return;
                         pthread_create(&disp_tid, NULL, display_thread, NULL);
                         pthread_detach(disp_tid);
                     }
                     void display_stop(void) { usleep(60000); }
