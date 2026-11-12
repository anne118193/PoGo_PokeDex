I just want to be able to look at my Pokedex on my laptop while I evolve various Pokemon to fill out the rest of my Pokedex. (bec how am I supposed to know which XXL Pokemon I have) PoGo doesn't have an API for this so I need to scrape all of my own data somehow. 

Utilizes Mac's "Iphone Mirroring" App which allows you to use your iPhone with your Mac

Obviously claude wrote a bunch of this code. 

## Version 1
works, kinda clunky, not aesthetically pleasing, but it works and it does what I need it to do (and honestly I could just stop here because I have solved my problem) <br>

### 1. Clone the Repository

``` bash
git clone https://github.com/anne118193/PoGo_PokeDex.git
```

or you can just download the files 

### 2. Environment Setup

I usually just read the errors and fix them one at a time ... 

Check to see if Homebrew is installed
```bash
brew --version
```

Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

This is what you need for your computer to control your mouse and automatically scroll for you.
```bash
brew install cliclick
brew install imagemagick
```


### 3. How to Run

#### Screen Record Pokedex
There are privacy and security things that you need to allow so that this will work.
<br>
Allow Terminal to control the mouse: go to System Settings → Privacy & Security → Accessibility and turn on Terminal


make the file executable (only need to do this once)
```bash
chmod +x autoscroll.sh
```

mirror your iPhone to your MacBook with the iPhone mirroring app <br>
1. open PokemonGo
2. go to PokeDex
3. click on the 1st pokemon you want to start recording from (only 1 pokemon should be shown on the screen)
4. start screen recording (drag box so that it only covers the iPhone screen)<br>
&emsp;&emsp; cmd + shift + 5 <br>

5. run the file
```bash
./autoscroll.sh
```
6. move mouse to the center of your mirrored iPhone, you have 5 sec to do this (putting it over the word "info" works well enough for me) <br>

to stop the script, forcibly move your mouse and click into the terminal <br>
&emsp; ctrl + c <br>

I really do need to make a better way to stop the script but I'm lazy so for now this is how it is

#### Process Screen Recording (Video)
you may want to crop the videos a bit manually before you start this process but it is up to you
<br>
There are privacy and security things that you need to allow so that this will work.
<br>
Allow terminal to take screenshots of different parts of different frames in the video (terminal needs screen recording access): go to System Settings → Privacy & Security → Screen & System Audio Recording.

**file name = region name** <br>
The region name comes from the file name, so the name each recording after its region

for 1 video 
```bash
python3 process_pokedex.py <filepath/filename>
```

```bash
python3 process_pokedex.py ~/Desktop/Kanto.mov
```

for multiple videos
``` bash
python3 process_pokedex.py ~/Desktop/Kanto.mov ~/Desktop/Johto.mov ~/Desktop/Hoenn.mov
```
**custom region name** <br>
To keep the original file names, put the region name in front with =. Use quotes when the name has spaces.

```bash
python3 process_pokedex.py "Kanto=<path>/Screen Recording 1.mov" "Johto=<path>Screen Recording 2.mov"
```

you should be able to open up index.html in the poxedex_viewer folder and use your pokedex :)

### 4. File + Folder Descriptions
- pokedex_viewer: folder where images are saved + where the populated pokedex html is saved
- pokedex_viewer/index.html: populated pokedex
- autoscroll.sh: shell script for automatically scrolling through pokedex
- process_pokedex.py: python script for processing a video of someone scrolling through the PoGo pokedex, saves every entry as seperate images that can be used to populate index.html
- rebuild_viewer.py: rebuild the html for viewing pokedex without reprocessing a video
- viewer.html: empty html template for pokedex

## Version 2
Is there a more efficient way to do this that doesn't involve parsing long videos?


haven't stated v2 ... 

