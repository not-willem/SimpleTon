import commandparser as cmp
import sys
cangoback = False
cache = 0

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