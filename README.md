# projet-ultrasons
![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)  [![GitHub](https://img.shields.io/badge/GitHub-Profile-black?logo=github)](https://github.com/Sili0)  [![License](https://img.shields.io/badge/License-MIT-green)](https://mit-license.org/) 
## Description
_Repository containing the data and code (**AnimPlot**) regarding the Projet Tutoré about ultrasound propagation._

## Repository Contents
This repository includes:  
- **Python source code** of AnimPlot
- **Compiled versions** of AnimPlot for macOS and Windows  
- **Folders with .csv raw data files** to be opened with AnimPlot  
- A **link to the YouTube channel** with the videos of the acquisitions
- **QtiPlot** processed data included in the report


## AnimPlot
It's an simple python program similar to a video player that let you plot the animated waveform acquired by the **Record** function of [OpenWave-1KB](https://github.com/other-username/https://github.com/OpenWave-GW/OpenWave-1KB). The animated plot acts like a video player, you can pause and go frame per frame. The horizontals and verticals axis are respected, and reproduce the range of data seen on the oscilloscope during the acquisition. You can also navigate through the values with a precise cursor, and providing the velocity of ultrasound inside the liquid used during acquisition, it calculates the spatial position of the cursor. As the acquisition speed is not constant, you can use a current ramp in the second channel of the oscilloscope to let the program recover the real elasped time between frames.
### Installation
You need Python 3 installed, and the dependencies: **MatplotLib**, **Numpy**

### Usage
Simply run the script using :

```
python3 AnimPlot.py
```

Or use the pre-compiled version for your system, then follow the instructions. If you want to test it with our data, you can download the source code, then use one of the acquisitions folders in the raw_data section.

## Data
Each acquisition is named by the experimental parameters used, and contains the list of the .CSV containing the raw data acquired with [OpenWave-1KB](https://github.com/OpenWave-GW/OpenWave-1KB). As the version isn't written for Python 3, we used this [fork](https://github.com/mamin27/OpenWave-1KB) to be able to run it on macOS, with some tweaking on the libraries used.

## Videos
Youtube channel with the video used to identify bubble sizes and their time-code in the acquisition:

[![YouTube](https://img.shields.io/badge/YouTube-projetultrasons-red?logo=youtube&logoColor=white)](https://www.youtube.com/@projet-ultrasons)  
> **_NOTE:_**  The video playback speed is not constant due to YouTube encoding issue as the original file is in high frame rate (240 frame per second), so it appears that the ramp speed is not constant. It is of course not the case in the original video.
