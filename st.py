import commandparser as cmp
import pygame
import sys
import threading
from pynput import keyboard
import ast
from screeninfo import get_monitors
import linecache

global mtsx
global mtsy
for monitor in get_monitors():
    mtsx = monitor.width
    mtsy = monitor.height

global verbose
verbose = False
cangoback = False
cache = 0
current_key = "none"
displaycommands = []
screen = None

def setupdisplay():
    global screen
    global mtsx
    global mtsy
    global mousex
    global mousey
    pygame.init()
    screen = pygame.display.set_mode((mtsx, mtsy), pygame.FULLSCREEN)
    pygame.display.set_caption("SimpleTon Display Output")
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        mousex, mousey = pygame.mouse.get_pos()
        pygame.display.flip()
        clock.tick(10000)
    pygame.quit()
    sys.exit()

def on_press(key):
    global current_key
    try:
        if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            current_key = "shift"
        elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_r:
            current_key = "ctrl"
        elif key == keyboard.Key.alt or key == keyboard.Key.alt_r:
            current_key = "alt"
        elif key == keyboard.Key.cmd:
            current_key = "logo"
        elif key == keyboard.Key.space:
            current_key = "space"
        elif key == keyboard.Key.caps_lock:
            current_key = "caps"
        elif key == keyboard.Key.tab:
            current_key = "tab"
        elif key == keyboard.Key.up:
            current_key = "up"
        elif key == keyboard.Key.down:
            current_key = "down"
        elif key == keyboard.Key.left:
            current_key = "left"
        elif key == keyboard.Key.right:
            current_key = "right"
        elif key == keyboard.Key.enter:
            current_key = "enter"
        else:
            current_key = key.char.lower()
    except:
        current_key = str(key).replace("Key.", "").lower()
    
    cmp.mov(current_key + "\n", 6)

def sendmouse():
    global mousex
    global mousey
    mousex = None
    mousey = None
    while True:
        if mousex is not None:
            cmp.mov(str(mousex) + "\n", 7)
            cmp.mov(str(mousey) + "\n", 8)

def on_release(key):
    global current_key
    current_key = "none"
    cmp.mov("none\n", 6)

def startlistener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def runterminalinbackground():
    global displaycommands
    global screen
    displaycommands = ["","","","","",""]

    if len(sys.argv) < 2:
        while True:
            userinput = input("> ")
            cmp.parse(userinput, 0, verbose)
    else:
        with open(sys.argv[1], "r",encoding='utf-8') as file:
            lines = [line.rstrip() for line in file]
        cmp.functionfind(sys.argv[1])
        fileindex = 0
        while fileindex < len(lines):
            cmp.parse(lines[fileindex], fileindex + 1, verbose)
            if screen is not None:
                if "" not in displaycommands:
                    try:
                        if displaycommands[5] == "circle":
                            pygame.draw.ellipse(screen, ast.literal_eval(displaycommands[4]), [int(displaycommands[0]), int(displaycommands[1]), int(displaycommands[2]), int(displaycommands[3])], 1)
                            displaycommands = ["","","","","",""]
                        if displaycommands[5] == "square":
                            pygame.draw.rect(screen, ast.literal_eval(displaycommands[4]), [int(displaycommands[0]), int(displaycommands[1]), int(displaycommands[2]), int(displaycommands[3])], 1)
                            displaycommands = ["","","","","",""]
                        if displaycommands[5] == "filledcircle":
                            pygame.draw.ellipse(screen, ast.literal_eval(displaycommands[4]), [int(displaycommands[0]), int(displaycommands[1]), int(displaycommands[2]), int(displaycommands[3])])
                            displaycommands = ["","","","","",""]
                        if displaycommands[5] == "filledsquare":
                            pygame.draw.rect(screen, ast.literal_eval(displaycommands[4]), [int(displaycommands[0]), int(displaycommands[1]), int(displaycommands[2]), int(displaycommands[3])])
                            displaycommands = ["","","","","",""]                            
                        if displaycommands[5] == "text":
                            fonter = pygame.font.Font("Ac437_IBM_VGA_8x16.ttf", int(displaycommands[2]))
                            textperson = fonter.render(str(displaycommands[3]), True, ast.literal_eval(displaycommands[4]))
                            screen.blit(textperson, (int(displaycommands[0]), int(displaycommands[1])))
                            displaycommands = ["","","","","",""] 
                    except:
                        pass

            for i in range(6):
                if not cmp.getline(int(i)+1) == "\n":
                    displaycommands[int(i)] = cmp.getline(int(i)+1).replace("\n", "")
                cmp.mov(""+"\n",int(i))
                
            if cmp.skip:
                try:
                    while not lines[fileindex] == "e":
                        fileindex = fileindex + 1
                        
                        if fileindex > len(lines) - 1:
                            print('Please add a "e" command to your code to end the function!')
                except:
                    pass
            
            if cmp.runfunction == True:
                cache = fileindex
                fileindex = cmp.functionitem - 1
                cmp.runfunction = False
            if lines[fileindex] == "e":
                if cmp.jumpback == True:
                    fileindex = cache
                    cmp.jumpback = False

            fileindex = fileindex + 1

threadman = threading.Thread(target=startlistener, daemon=True)
threadman.start()


if len(sys.argv) > 1:
    with open(sys.argv[1], "r") as file:
        if linecache.getline(sys.argv[1], 1).strip() == "d":
            if verbose:
                print("Display detected!! Starting it now..")
            program_thread = threading.Thread(target=runterminalinbackground, daemon=True)
            program_thread.start()
            setupdisplay()
            mouseman = threading.Thread(target=sendmouse, daemon=True)
            mouseman.start()
            
        else:
            if verbose:
                print("Display not found..")
            runterminalinbackground()
else:
    runterminalinbackground()