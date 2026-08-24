import commandparser as cmp
import sys
import keyboard
import threading

cangoback = False
cache = 0

key = ""

def onkeypressed(event):
    global key
    special = {
        'shift': 'shift',
        'right shift': 'shift',
        'ctrl': 'ctrl',
        'alt': 'alt',
        'windows': 'logo',
        'cmd': 'logo',
        'space': 'space',
        'caps lock': 'caps',
        'tab': 'tab',
        'up': 'up',
        'down': 'down',
        'left': 'left',
        'right': 'right',
        'enter': 'enter',
    }
    keyname = event.name

    if keyname in special:
        key = special[keyname]
    elif len(keyname) == 1:
        key = keyname.lower()
    else:
        key = keyname.lower()

    cmp.mov(key + "\n", 6)

def startlistener():
    keyboard.on_press(onkeypressed)
    keyboard.wait()

threadman = threading.Thread(target=startlistener, daemon=True)
threadman.start()

if len(sys.argv) < 2:
    while True:
        userinput = input("> ")
        cmp.parse(userinput, 0, False)
else:
    with open(sys.argv[1], "r") as file:
        lines = [line.rstrip() for line in file]
    cmp.functionfind(sys.argv[1])
    global fileindex
    fileindex = 0
    while fileindex < len(lines):
        cmp.parse(lines[fileindex], fileindex + 1, False)
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