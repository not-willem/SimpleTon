import linecache
import re
import time

global functions
global skip
global runfunction
global jumpback
global functionitem
global mousex
global mousey
functions = []
skip = False
functionitem = 0
runfunction = False
jumpback = False

# creating a new storage..
with open("STORAGE.SV", "w") as file:
    for i in range(1000):
        file.write(""+"\n")

def functionfind(filename):
    with open(filename, "r") as file:
        lines = [line.rstrip() for line in file]
    index = 0
    for item in lines:
        comlist = re.findall(r'"[^"]*"|\S+', item)
        index = index + 1
        try:
            if comlist[0] == "f":
                functions.append([comlist[1].replace('"', ""), index])
        except:
            pass
        


#command parser
def parse(command, line, verbose):
    
    #split
    commandlist = re.findall(r'"[^"]*"|\S+', command)
    try:
        parsecommand = commandlist[0]
    except:
        parsecommand = "#"
    if parsecommand == "m":
            try:
                if findtype(commandlist[1]) == "sector":
                    # checks if the param is a sector, gets rid of the x and 1-indexes it
                    number = commandlist[1].replace("x", "")
                    number = int(number)
                    #gets it from the storage file
                    storagesector = linecache.getline("STORAGE.SV", number)
                    if verbose:
                        print(storagesector)
                    if findtype(commandlist[2]) == "sector":
                        #moving time
                        number = commandlist[2].replace("x", "")
                        number = int(number)
                        #gets it from the storage file
                        storagesector2 = linecache.getline("STORAGE.SV", number)
                        if verbose:
                            print(storagesector2)
                        #moves the things around
                        mov(storagesector, number-1)
                elif findtype(commandlist[1]) == "string":
                    #if type 1 is string
                    string = commandlist[1].replace('"', "")
                    if findtype(commandlist[2]) == "sector":
                        #if type 2 is sector
                        number = commandlist[2].replace("x", "")
                        if verbose:
                            print(string)
                        number = int(number)
                        #put the string in the sector
                        mov(string + "\n", number-1)
                elif findtype(commandlist[1]) == "number":
                    #if type 1 is a numbrero
                    numbrero = commandlist[1].replace("(", "")
                    numbrero = numbrero.replace(")", "")
                    if findtype(commandlist[2]) == "sector":
                        # oh no he's onto me i think he knows im a sector oh no
                        number = commandlist[2].replace("x", "")
                        if verbose:
                            print(numbrero)
                        number = int(number)
                        # put
                        mov(str(numbrero) + "\n", number-1)
            except:
                if line == 0:
                    print("Please check your spelling!")
                else:
                    print(f"Please check your spelling on line {line}")

    elif parsecommand == "p":
        if findtype(commandlist[1]) == "string":
            print(commandlist[1].replace('"',""))
        elif findtype(commandlist[1]) == "number":
            fixed = commandlist[1].replace(')',"")
            fixed = fixed.replace('(',"")
            print(fixed)
        elif findtype(commandlist[1]) == "sector":
            if verbose:
                print(commandlist[1].replace('x',""))
            print(getline(int(commandlist[1].replace('x',""))).strip())
    elif parsecommand == "a":
        if findtype(commandlist[1]) == "number":
            if findtype(commandlist[2]) == "sector":
                numbrero = float(getline(int(commandlist[2].replace("x", ""))))
                fixed = commandlist[1].replace("(", "")
                numbrero = round(numbrero + float(fixed.replace(")", "")), 10)
                mov(str(numbrero)+"\n", int(commandlist[2].replace("x", ""))-1)
        elif findtype(commandlist[1]) == "sector":
            if findtype(commandlist[2]) == "sector":
                numbrero = float(getline(int(commandlist[2].replace("x", ""))))
                fixed = float(getline(int(commandlist[1].replace("x",""))))
                numbrero = round(numbrero + float(fixed), 10)
                mov(str(numbrero)+"\n", int(commandlist[2].replace("x", ""))-1)
        else:
            if line == 0:
                print("Please enter a number!")
            else:
                print(f"Please enter a number on line {line}")
    elif parsecommand == "s":
        if findtype(commandlist[1]) == "number":
            if findtype(commandlist[2]) == "sector":
                numbrero = float(getline(int(commandlist[2].replace("x", ""))))
                fixed = commandlist[1].replace("(", "")
                numbrero = round(numbrero - float(fixed.replace(")", "")), 10)
                mov(str(numbrero)+"\n", int(commandlist[2].replace("x", ""))-1)
        elif findtype(commandlist[1]) == "sector":
            if findtype(commandlist[2]) == "sector":
                numbrero = float(getline(int(commandlist[2].replace("x", ""))))
                fixed = float(getline(int(commandlist[1].replace("x",""))))
                numbrero = round(numbrero - float(fixed), 10)
                mov(str(numbrero)+"\n", int(commandlist[2].replace("x", ""))-1)
        else:
            if line == 0:
                print("Please enter a number!")
            else:
                print(f"Please enter a number on line {line}")
    elif parsecommand == "c":
        global runfunction
        global jumpback
        global functionitem
        for item in functions:
            for item2 in item:
                if item2 == commandlist[1].replace('"',""):
                    runfunction = True
                    functionitem = int(item[1])
                    jumpback = True
    elif parsecommand == "j":
        for item in functions:
            for item2 in item:
                if item2 == commandlist[1].replace('"',""):
                    runfunction = True
                    functionitem = int(item[1])
                    jumpback = False
    elif parsecommand == "i":
        if findtype(commandlist[1]) == "sector":
            first = getsector(commandlist[1])
        elif findtype(commandlist[1]) == "number":
            first = commandlist[1].replace("(","")
            first = first.replace(")", "")
        elif findtype(commandlist[1]) == "string":
            first = commandlist[1].replace('"', "")

        if findtype(commandlist[3]) == "sector":
            second = getsector(commandlist[3])
        elif findtype(commandlist[3]) == "number":
            second = commandlist[3].replace("(","")
            second = second.replace(")", "")
        elif findtype(commandlist[3]) == "string":
            second = commandlist[3].replace('"', "")
        first = first.split()
        second = second.split()

        if verbose:
            print(first)
            print(second)
            if first == second:
                print("ok")
            else:
                print("no")
        
        
        try:
            if not findtype(commandlist[4]) == "iffunc":
                if commandlist[2] == "=":
                    if str(first) == str(second):
                        mov("1", int(commandlist[4].replace("x", "")))
                    else:
                        mov("0", int(commandlist[4].replace("x", "")))
                if commandlist[2] == ">":
                    if int(first) > int(second):
                        mov("1", int(commandlist[4].replace("x", "")))
                    else:
                        mov("0", int(commandlist[4].replace("x", "")))
                if commandlist[2] == "<":
                    if int(first) < int(second):
                        mov("1", int(commandlist[4].replace("x", "")))
                    else:
                        mov("0", int(commandlist[4].replace("x", "")))
                if commandlist[2] == "!=":
                    if not str(first) == str(second):
                        mov("1", int(commandlist[4].replace("x", "")))
                    else:
                        mov("0", int(commandlist[4].replace("x", "")))
                if commandlist[2] == "=!":
                    if not str(first) == str(second):
                        mov("1", int(commandlist[4].replace("x", "")))
                    else:
                        mov("0", int(commandlist[4].replace("x", "")))
            else:

                # faaahh

                if commandlist[2] == "=":
                    if str(first) == str(second):
                        runfunc(commandlist[4].replace(":",""), True)
                if commandlist[2] == ">":
                    if str(first) > str(second):
                        runfunc(commandlist[4].replace(":",""), True)
                if commandlist[2] == "<":
                    if str(first) < str(second):
                        runfunc(commandlist[4].replace(":",""), True)
                if commandlist[2] == "!=":
                    if not str(first) == str(second):
                        runfunc(commandlist[4].replace(":",""), True)
                if commandlist[2] == "=!":
                    if not str(first) == str(second):
                        runfunc(commandlist[4].replace(":",""), True)

        except:
            if line == 0:
                print("Please enter the i command like: i x12 = x12 x13")
            else:
                print(f"Please enter the i command on line {line} like: i x12 = x12 x13")


    elif parsecommand == "l":
        try:
            if commandlist[1] == "j":
                if verbose:
                    print("Detected join flag")
                string1 = commandlist[2]
                string2 = commandlist[3]
                sector = commandlist[4]
                string1 = string1.replace('"',"")
                string2 = string2.replace('"',"")
                sector = sector.replace("x", "")
                string1 = string1+string2
                mov(string1+"\n", int(sector)-1)


            else:
                if findtype(commandlist[1]) == "text":
                    text = commandlist[1]
                    text = text.replace('"', "")
                    letter = commandlist[2].replace("(", "")
                    letter = letter.replace(")","")
                    letter = int(letter)
                    sector = commandlist[3].replace("x", "")
                    
                    mov(text[letter-1], int(sector))
                elif findtype(commandlist[1]) == "sector":
                    text = commandlist[1]
                    text = text.replace('x', "")
                    text = getline(int(text))
                    letter = commandlist[2].replace("(", "")
                    letter = letter.replace(")","")
                    letter = int(letter)
                    sector = commandlist[3].replace("x", "")
                    mov(text[letter-1]+"\n", int(sector)-1)
        except:
            if line == 0:
                print('Please format "l" like "l "sausage" (4) x9"')
            else:
                print(f'Please format "l" on line {line} like "l "sausage" (4) x9"')

    elif parsecommand == "f":
        global skip
        if line == 0:
            print("You cannot create functions in shell mode!")
        else:
            skip = True
    elif parsecommand == "t":
        try:
            if commandlist[1] == "w":
                timeman = commandlist[2].replace("(","")
                timeman = timeman.replace(")","")
                timeman = float(timeman)
                functionman = commandlist[3].replace(":","")
                
                time.sleep(timeman)
                runfunc(functionman, True)
        except:
            if line == 0:
                print('Please format "t" like "t w (1) :function:"')
            else:
                print(f'Please format "t" like "t w (1) :function:" on line {line}')
            
    elif parsecommand == "#":
        pass
    elif parsecommand == "e":
        pass
    elif parsecommand == "d":
        pass
    else:
        if not line == 0:
            print(f'Failed to parse command "{parsecommand}" on line {line}.. Maybe check your spelling?')
        else:
            print(f'Failed to parse command "{parsecommand}".. Maybe check your spelling?')

def mov(text, line):
    with open("STORAGE.SV", "r") as file:
        lines = file.readlines()
    if 0 <= line < len(lines):
        lines[line] = text
    with open("STORAGE.SV", "w") as file:
        file.writelines(lines)

def getline(line):
    linecache.clearcache()
    return linecache.getline("STORAGE.SV", line)

def findtype(argument):
    if "x" in argument[0]:
        return "sector"
    if '"' in argument:
        return "string"
    if "(" in argument:
        return "number"
    if ":" in argument:
        return "iffunc"
    else:
        return "error"

def getsector(sector):
    return getline(int(sector.replace("x", "")))

def runfunc(functionname, jb):
    global runfunction
    global functionitem
    global jumpback
    for item in functions:
        for item2 in item:
            if item2 == functionname:
                runfunction = True
                functionitem = int(item[1])
                jumpback = jb