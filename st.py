import commandparser as cmp
import sys
if len(sys.argv) < 2:
    while True:
        userinput = input("> ")
        cmp.parse(userinput, 0, False)
else:
    with open(sys.argv[1], "r") as file:
        lines = [line.rstrip() for line in file]
    for item in lines:
        cmp.parse(item, 0, False)