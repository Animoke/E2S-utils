# Features

E2S-utils lets you convert your .wav for them to be ready to put on your SD card!\
This tool was made for the Korg Electribe Sampler 2, but can be used on any machines that supports mono/44100Hz\
You can also speed up - *or down* - your samples (they are also pitched), so you can gain space on your machine.\
This script will find files recursively, so it's easier to manage your library. It will make a backup, and proceed. Backups are NOT automatically deleted.

NOTE: This script only supports windows operating systems.

# Usage

Install required modules:
```
pip install -r requirements.txt
```

Put the path of the root directory of your library in line 8 (this will be added in arguments):\
`user_path = "C:\\Users\\Path\\To\\E2S_SD\\Sample"`\
NOTE: Sanitizing is not yet added so double all `\`.

Execute the script with desired arguments:

e.g: 
```
python.exe .\e2s-utils.py --convert-mono
```
\
**Arguments list:**


```
usage: main.py [-h] [-m] [-s SPEED] [-a]

Convert all files recursively in directories to mono, with adjustable speed. Made for Korg machines

options:
  -h, --help            show this help message and exit
  -m, --convert-mono    Convert to mono
  -s SPEED, --speed SPEED
                        Speed selection (0.5-2.0)
  -a, --all             Do everything (default speed: 2) [DEFAULT]
```
\
This software may not be 100% reliable. I am not responsible for any data losses, take your precautions!