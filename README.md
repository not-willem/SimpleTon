# SimpleTon
a universal coding language

i've began working on writing a coding language and it's going great so far!!

Also, i came back to this project a few months later to touch things up and i realized just how useful this programming language is.
You could probably run this on the Commodore 64 if you tried hard enough!

Anyway probably gonna use this for some like calculation stuff

# Installation

## Windows (from pre-built release)

1. Go to the releases tab on this github and download `st-windows_x86-64-bit_x.x.x.zip` or whichever one fits your version of windows best.
2. Extract the .exe and icon into a folder
3. Create a new file called `test.st` and put this inside:

```
m (0) x99
j "poop"
f "poop"

p x99
a (1) x99

j "poop"
e
```

4. Open up a terminal and run the .exe file inside using the format `st.exe test.st`
5. Close it using `CTRL+C`


## Windows (from source)
1. Download the source code by going to "Code" then "Download as zip"

2. Unzip the file into any directory

3. Use cd to get into the directory you unzipped the file to, then run ``` pip install -r requirements.txt ```

4. Now, run ```py st.py``` or ```python st.py``` and put the name of the .st file you want to run.

5. It should bring you to a terminal that you can quit easily by pressing ctrl+c

6. now, you can run "py st.py hello.st" to run my graphics test. the z-layering may flicker but that's because i really haven't implemented it that well.

## Linux (from pre-built release, easiest)

1. Download the latest linux release from the releases page
2. Rename the file to `st` (no file extension) for easier use
3. Create a file called `test.st` in the same place as `st` and paste this into it:

```
d
j "screen"
f "screen"
m (0) x1
m (0) x2
m (1920) x3
m (1080) x4
m x11 x5
m "filledsquare" x6
i x7 = "shift" :shift:
i x7 = "none" :none:
j "screen"
e
f "shift"
m "(255,0,0)" x11
e
f "none"
m "(0,255,0)" x11
e
```

4. Open up a terminal and cd into the folder "st" is in
5. Run the command `./st test.st` and press "shift" to make your screen red

## Linux (build from C)

1. Download the code from the github page using Code -> Download as Zip
2. Extract the zip and CD into the `C` folder using a console
3. Run `bash build.sh`, it will give a few warnings but it should compile fine.
4. Run `./simpleton test.st`. It should spit out a bunch of numbers but it's just changing it up by one every time.
5. You can move the `simpleton` file to any folder you like now and have it run your programs.
   
also if i haven't already, i might package it and port it to windows, linux, etc so if i have, then just download the executable from releases and run it like:



also keep the ttf file with the exe file! for some reason, it doesnt want to pack it into the exe so ive just zipped it up

# Documentation and porting help

Basically i have just a big google doc of the commands that made sense to me at the time but i dont know if they still do. anyway look for things like "l docs" or "m docs" etc

alright [here it is](https://docs.google.com/document/d/1G4AS6eHCkXI7fpvRMn4jlNm_3g9bSfDH1YFZpNRLRWc/edit?usp=sharing)
