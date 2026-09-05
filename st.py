import commandparser as cmp
import pygame
import sys
import threading
from pynput import keyboard
import ast
from screeninfo import get_monitors
import linecache
import time

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
tricommands = None

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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        mousex, mousey = pygame.mouse.get_pos()
        pygame.display.flip()
        clock.tick(60)
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
        time.sleep(0.01)

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
    global tricommands
    displaycommands = ["","","","","",""]
    tricommands = None
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
            
            for i in range(6):
                line_data = cmp.getline(int(i)+1)
                if line_data and line_data != "\n" and line_data != "":
                    displaycommands[int(i)] = line_data.replace("\n", "")
                cmp.mov(""+"\n",int(i))
            
            if screen is not None and all(x != "" for x in displaycommands):
                try:
                    if displaycommands[5] == "circle":
                        pygame.draw.ellipse(screen, ast.literal_eval(displaycommands[4]), [int(displaycommands[0]), int(displaycommands[1]), int(displaycommands[2]), int(displaycommands[3])], 1)
                        displaycommands = ["","","","","",""]
                    elif displaycommands[5] == "square":
                        pygame.draw.rect(screen, ast.literal_eval(displaycommands[4]), [int(displaycommands[0]), int(displaycommands[1]), int(displaycommands[2]), int(displaycommands[3])], 1)
                        displaycommands = ["","","","","",""]
                    elif displaycommands[5] == "filledcircle":
                        pygame.draw.ellipse(screen, ast.literal_eval(displaycommands[4]), [int(displaycommands[0]), int(displaycommands[1]), int(displaycommands[2]), int(displaycommands[3])])
                        displaycommands = ["","","","","",""]
                    elif displaycommands[5] == "filledsquare":
                        pygame.draw.rect(screen, ast.literal_eval(displaycommands[4]), [int(displaycommands[0]), int(displaycommands[1]), int(displaycommands[2]), int(displaycommands[3])])
                        displaycommands = ["","","","","",""]                            
                    elif displaycommands[5] == "text":
                        fonter = pygame.font.Font(None, int(displaycommands[2]))
                        textperson = fonter.render(str(displaycommands[3]), True, ast.literal_eval(displaycommands[4]))
                        screen.blit(textperson, (int(displaycommands[0]), int(displaycommands[1])))
                        displaycommands = ["","","","","",""] 
                    elif displaycommands[5] in ["triangle", "filledtriangle"]:
                        if displaycommands[3] != "none" and tricommands is None:
                            tricommands = displaycommands.copy()
                            displaycommands = ["","","","","",""]
                        elif displaycommands[3] == "none" and tricommands is not None:
                            x1 = int(tricommands[0])
                            y1 = int(tricommands[1])
                            x2 = int(tricommands[2])
                            y2 = int(tricommands[3])
                            color = ast.literal_eval(tricommands[4])
                            
                            x3 = int(displaycommands[0])
                            y3 = int(displaycommands[1])
                            outline_width = int(displaycommands[2])
                            
                            if tricommands[5] == "filledtriangle":
                                if outline_width == 0:
                                    pygame.draw.polygon(screen, color, [(x1, y1), (x2, y2), (x3, y3)])
                                else:
                                    pygame.draw.polygon(screen, color, [(x1, y1), (x2, y2), (x3, y3)], outline_width)
                            else:
                                if outline_width == 0:
                                    pygame.draw.polygon(screen, color, [(x1, y1), (x2, y2), (x3, y3)], 1)
                                else:
                                    pygame.draw.polygon(screen, color, [(x1, y1), (x2, y2), (x3, y3)], outline_width)
                            
                            tricommands = None
                            displaycommands = ["","","","","",""]
                except Exception as e:
                    pass

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