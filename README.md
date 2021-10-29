# `legends`

This repository contains the `legends` Python package, which offers tools for managing *Star Trek: Legends* player data using Python. The subpackage, `legends.ui`, contains a complete GUI coded with `tkinter`. From this, a standalone Mac app, *STL Planner*, has been built and is available for download.

* [The *STL Planner* app](#the-stl-planner-app)
* [The `legends` package](#the-legends-package)

## The *STL Planner* app

![STL Planner screenshot 1](https://github.com/probabilist/legends/blob/main/screenshot.png)
![STL Planner screenshot 2](https://github.com/probabilist/legends/blob/main/screenshot2.png)
![STL Planner screenshot 3](https://github.com/probabilist/legends/blob/main/screenshot3.png)

The *STL Planner* app is a tool to manage and optimize all of your *Star Trek: Legends* data.

### Requirements

The *STL Planner* app must be run on a Mac. If your Mac has *Star Trek: Legends* installed, you can import your game data with the click of a button. If not, you will have to import your game data using a support email. A detailed explanation of how to do this is provided by the app itself.

> NOTE: On Windows, you can still use the STL Planner, but you must launch it from Python using the `legends` package. Read below for how to do that.

### Download

Version 0.22.0: [STL Planner.app.zip on Google Drive](https://drive.google.com/file/d/1bqo2Df8ZatPk-rfg7ytinrmaVeSYeRdc/view?usp=sharing)

### Install

There is no install required, but you will need to follow these steps:

1. Open the dmg file downloaded above and drag the app to your Applications folder.
2. Find the app in your Applications folder, right click on it, and select "Open" from the contextual menu.
3. A dialog will pop up, warning you of the security risk. You can then agree to run the app anyway.

If you skip Step 2 and try to open the app directly, a security dialog will prevent you from running the app.

<!--### Developer version

If you'd like to try the latest developer version, it's here: [v0.10.1-dev](https://drive.google.com/file/d/1cC8wh6WpsdCjdXFE43TPNpQ_vRyhuQ3J/view?usp=sharing)

The developer version is a Unix Executable. When you run it in macOS, you will see two windows. One is the app, as usual. The other is a Terminal console.

The developer version may sometimes write to the console, not just for error messages, but for intended functionality. If the app is not functioning the way you expect, be sure to check the console.-->

## The legends package

This package uses text assets from Star Trek: Legends. For extracting/updating these text assets, see https://github.com/probabilist/legends-assets.

* [Installing the package](#installing-the-package)
* [Documentation](#documentation)
* [Running *STL Planner* from a command line](#running-stl-planner-from-a-command-line)
* [Building the *STL Planner* app](#building-the-stl-planner-app)
* [Examples using the package](#examples-using-the-package)
* [Comparison to the `legendscli` package](#comparison-to-the-legendscli-package)

### Installing the package

You will need to have Python installed to use the `legends` package. This package is built and tested with Python 3.7.11.

To use the `legends` package, simply copy the "legends" folder from this repository to your current working directory.

The `legends` package uses other packages that you might not have installed. To ensure that you have the required packages installed, also copy the file, 'requirements.txt' to your current working directory. Then, at the command prompt, enter
```
% pip install -r requirements.txt
```

### Documentation

Complete documentation can be found at https://probabilist.github.io/legends/legends/.

### Running *STL Planner* from a command line

With the `legends` package installed, you can run *STL Planner* directly, without downloading the app. There are two ways to do this: from inside a Python interactive session, or from a command prompt in Terminal.

To run *STL Planner* from inside a Python interactive session, first enter
```
% python
```
at the command prompt. This will open the `Python` interpreter in interactive mode. Your command prompt should to change to the Python prompt `>>>`. Now enter
```
>>> from legends.ui import STLPlanner
>>> STLPlanner()
```

To run *STL Planner* from a command prompt in Terminal, first copy the script, "stlplannerapp.py" to your current working directory (the same location where the "legends" folder is). Then, at the command prompt, enter
```
% python stlplannerapp.py
```

### Building the *STL Planner* app

If you do not already have `pyinstaller` installed, then at the command prompt, enter
```
% pip install pyinstaller
```
Now, copy the files, "stlplannerapp.py" and "stlplannerapp.spec" to your current working directory (the same location where the "legends" folder is). Then, at the command prompt, enter
```
% pyinstaller stlplannerapp.spec
```
When the process is finished, you will find the app inside the newly created "dist" folder.

### Examples using the package

For an example that uses the package, see "skillstomd.py", which creates a markdown-formatted file listing all skills in the game, for both current and upcoming characters. You can see the output of this script, after conversion to HTML, at https://probabilist.github.io/legends/skills.html.

Another example is "missionstomd.py". This script outputs (in markdown format) detailed information about all the missions in the game. You can see its output, after conversion to HTML, at https://probabilist.github.io/legends/missions.html.

Yet another example is "bridgeskills.py". This script outputs a csv-formatted spreadsheet of all bridge abilities, for both enabled and upcoming characters. This simple spreadsheet has been used as the basis for a worksheet you can use to select your bridge stations. Here is a link to [the bridge skills worksheet](https://docs.google.com/spreadsheets/d/1bdKFLJ48N37STNxIX1DTIKrymVTiLZsREI6XDuoJ14g/edit?usp=sharing).

### Comparison to the legendscli package

There is another Python package, `legendscli`, that is also designed to manage and optimize data in Star Trek: Legends. Unlike the `legends` package, `legendscli` is designed to be used from a command line. It has no GUI component.

The `legends` package is intended to have the same core tools and functionality as `legendscli`, but accessible through a GUI. It is a work in progress, with features being ported slowly over time.

The `legends` package is not an extension of `legendscli`. It is being rebuilt from the ground up. The `legendscli` package has many features whose sole purpose is to facilitate easy command-line operation. Most of those are stripped away in `legends`. That means `legends` is more streamlined and efficient, but it also requires more Python experience to use.

The `legendscli` package can be found at https://github.com/probabilist/legendscli. It may be worth noting, in case you want to dig into the historical revisions of the `legendscli` package, that it used to be called "legends", and it used to reside here, in this repository.
