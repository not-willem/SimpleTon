import linecache
import re

# creating a new storage, you probably shouldnt do this every time but it works for little tests

with open("STORAGE.SV", "w") as file:
    for i in range(1000):
        file.write(""+"\n")

#command parser
def parse(command, line, verbose):
    #split
    commandlist = re.findall(r'"[^"]*"|\S+', command)
    parsecommmand = commandlist[0]
    if parsecommmand == "m":
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

    elif parsecommmand == "p":
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
    elif parsecommmand == "a":
        if findtype(commandlist[1]) == "number":
            if findtype(commandlist[2]) == "sector":
                numbrero = int(getline(int(commandlist[2].replace("x", ""))))
                fixed = commandlist[1].replace("(", "")
                numbrero = numbrero + int(fixed.replace(")", ""))
                mov(str(numbrero), int(commandlist[2].replace("x", ""))-1)
        else:
            if line == 0:
                print("Please enter a number!")
            else:
                print(f"Please enter a number on line {line}")
    elif parsecommmand == "s":
        if findtype(commandlist[1]) == "number":
            if findtype(commandlist[2]) == "sector":
                numbrero = int(getline(int(commandlist[2].replace("x", ""))))
                fixed = commandlist[1].replace("(", "")
                numbrero = numbrero - int(fixed.replace(")", ""))
                mov(str(numbrero), int(commandlist[2].replace("x", ""))-1)
        else:
            if line == 0:
                print("Please enter a number!")
            else:
                print(f"Please enter a number on line {line}")
    elif parsecommmand == "c":
        print("call")
    elif parsecommmand == "j":
        print("jump")
    elif parsecommmand == "i":
        print("if")
    elif parsecommmand == "f":
        if line == 0:
            print("You cannot create functions in shell mode!")
        else:
            print("i should implement functions..")
    elif parsecommmand == "#":
        pass
    else:
        if not line == 0:
            print(f'Failed to parse command "{parsecommmand}" on line {line}.. Maybe check your spelling?')
        else:
            print(f'Failed to parse command "{parsecommmand}".. Maybe check your spelling?')

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
    if "x" in argument:
        return "sector"
    if '"' in argument:
        return "string"
    if "(" in argument:
        return "number"
    else:
        return "error"