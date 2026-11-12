I just want to be able to look at my Pokedex on my laptop while I evolve various Pokemon to fill out the rest of my Pokedex. (bec how am I supposed to know which XXL Pokemon I have) PoGo doesn't have an API for this so I need to scrape all of my own data somehow. 

Obviously claude wrote a bunch of this code. 

## Version 1
works, kinda clunky, not aesthetically pleasing, but it works and it does what I need it to do (and honestly I could just stop here because I have solved my problem)

### 1. Clone the Repository

``` bash
git clone https://github.com/anne118193/PoGo_PokeDex.git
```

or you can just download the files 

### 3. Environment Setup

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


### 2. How to Run

#### Screen Record Pokedex
There are privacy and security things that you need to allow so that this will work.

Allow Terminal to control the mouse: go to System Settings → Privacy & Security → Accessibility and turn on Terminal

make the file executable and then run the file
```bash
chmod +x autoscroll.sh
./autoscroll.sh
```

#### Process Screen Recording (Video)
There are privacy and security things that you need to allow so that this will work.

Allow terminal to take screenshots of different parts of different frames in the video (terminal needs screen recording access): go to System Settings → Privacy & Security → Screen & System Audio Recording.

**file name = region name**
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
**custom region name**
To keep the original file names, put the region name in front with =. Use quotes when the name has spaces.

```bash
python3 process_pokedex.py "Kanto=<path>/Screen Recording 1.mov" "Johto=<path>Screen Recording 2.mov"
```

## Version 2
Is there a more efficient way to do this that doesn't involve parsing long videos?

