import linecache


# creating a new storage, you probably shouldnt do this every time but it works for little tests

with open("STORAGE.SV", "w") as file:
    for i in range(1000):
        file.write(""+"\n")

#command parser
def parse(command, line, verbose):
    commandlist = command.split()
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
            except:
                if line == 0:
                    print("Please check your spelling!")
                else:
                    print(f"Please check your spelling on line {line}")

    elif parsecommmand == "p":
        print('print')
    elif parsecommmand == "a":
        print('add')
    elif parsecommmand == "s":
        print('subtract')
    elif parsecommmand == "c":
        print("call")
    elif parsecommmand == "j":
        print("jump")
    elif parsecommmand == "i":
        print("if")
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

def findtype(argument):
    if "x" in argument:
        return "sector"
    if '"' in argument:
        return "string"
    if "(" in argument:
        return "number"
    