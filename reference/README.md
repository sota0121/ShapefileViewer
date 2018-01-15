# About Ratel

This repository includes App for viewing shapefiles visually.

- **[Features](#features)**
- **[Requirements](#requirements)**
- **[Getting started](#getting-started)**

### Features

- View Shapefile
- Load Shapefile for GSI(..later)
- Load SQLite DB(..later)
- Output Shapefile(..later)
- Output SQLite DB(..later)
- Create and Update SQLite DB from Shapefile(..later)

`GSI` means Geospatial Information Authority of Japan

### Requirements

- Recommend
  - Anaconda3(ver 4.2.9)

> Check Anaconda Version
```
conda -V
```


### Getting started

1. Clone the repository using Git:
  `git clone https://github.com/sota0121/Ratel.git`

2. Get Shapefile from [GSI Page][1]

3. Edit `config.ini`
    - Section `App` Key `InputDir` :Shapefile directory
    - Section `App` Key `OutputDir` :directory that save sqlite db

4. Run `Ratel.py` with Python 3.6 or more

[1]: http://nlftp.mlit.go.jp/ksj/
