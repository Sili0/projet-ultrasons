# projet-ultrasons

## Description
_Repository containing the data and code (**AnimPlot**) regarding the Projet Tuteuré about ultrasound propagation._

## Repository Contents
This repository includes:  
- **Python source code** of AnimPlot
- **Compiled versions** of AnimPlot for macOS and Windows  
- **Folders with .csv files** to be opened with AnimPlot  
- **Raw and processed data** 
- A **link to the YouTube channel** with the videos of the acquisitions


## AnimPlot
It's an simple python program similar to a video player that let you plot the animated waveform acquired by the **Record** function of [OpenWave-1KB](https://github.com/other-username/https://github.com/OpenWave-GW/OpenWave-1KB). The animated plot acts like a video player, you can pause and go frame per frame. The horizontals and verticals axis are respected, and reproduce the range of data seen on the oscilloscope during the acquisition. As it uses MatplotLib, you can point using the cursor to find the precise value of a point in the waveform, and a more precise cursor is currently in development. As the acquisition speed is not constant, you can use a current ramp in the second channel of the oscilloscope to let the program recover the real elasped time between frames.
### Installation
You need Python 3 installed, and the dependencies: **MatplotLib**, **Numpy**

### Usage
Simply run the script using :

```
python3 AnimPlot.py
```

Or use the pre-compiled version for your system, then follow the instructions.

## Data
Each acquisition is named by the experimental parameters used, and contains the list of the .CSV containing the raw data acquired by [OpenWave-1KB](https://github.com/other-username/https://github.com/OpenWave-GW/OpenWave-1KB)

## Resources
Youtube channel with the video used to identify bubble sizes and their time-code in the acquisition:

[![YouTube](https://img.shields.io/badge/YouTube-Channel-red?logo=youtube&logoColor=white)](https://www.youtube.com/@Projet_tut)  


## Technologies Used
![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)  


## Author
[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?logo=github)](https://github.com/Sili0)  

## License
[![License](https://img.shields.io/badge/License-MIT-green)](https://mit-license.org/) 
