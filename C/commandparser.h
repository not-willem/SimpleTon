#ifndef COMMANDPARSER_H
#define COMMANDPARSER_H

#include <stddef.h>

#ifdef MICRO
#define STORAGE_SIZE 100
#else
#define STORAGE_SIZE 1000
#endif

void  cmp_init(void);
void  cmp_shutdown(void);
void  mov(const char *text, int line);
const char *getline_(int line);
const char *getsector(const char *sector);
int   getline_copy(int line, char *out, size_t outsz);
void  clear_slot(int line);
int   frame_accumulate(void);
int   display_take_frame(char out[6][256]);
void  display_signal_exit(void);
void  functionfind(const char *filename);
void  parse(const char *command, int line, int verbose);

extern int skip;
extern int runfunction;
extern int jumpback;
extern int functionitem;

#endif
