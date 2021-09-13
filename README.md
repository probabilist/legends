# legends

This repository features two key items:

* The STL Planner app
* The `legends` Python package

The STL Planner app is a very rudimentary incarnation (version 0.0.1) of what will eventually become a full-featured app that can help manage and optimize all of your Star Trek: Legends data. It must be run on a Mac that also has Star Trek: Legends installed.

The `legends` Python package is an all-new, streamlined version of the old `legends` Python package. The old package has been renamed to `legendscli` and can be found at https://github.com/probabilist/legendscli. The differences between this new package and the old one are discussed at the end of this document.

## Running the app

There are four ways you can run the STL Planner app:

1. Simply download the app to your Mac and run it.
2. Install the `legends` package and start the app from a Terminal command prompt.
3. Install the `legends` package and start the app from inside a Python interactive session.
4. Install the `legends` package and build the app yourself.

Option 1 should not require you to even have Python installed. The app itself contains a copy of everything it needs, including Python.

The other options require you to have Python installed. This repository is built and tested with Python 3.7.11.

## 1. Downloading the app

You can download 'STL PLanner.app.zip' from my Google Drive with this link: https://drive.google.com/file/d/1co-I9lxzeiUUGcwZTFNaq76km2AyHcC9/view?usp=sharing.

Once downloaded you will need to extract 'STL Planner.app' from the zip file.

Finally, you will need to right click on the app and select 'Open'. A dialog will pop up, warning you of the security risk. You can then agree to run the app anyway.

If you try to double-click the app after extracting it, the security warning will appear, but you will not have the option to run it anyway. You will simply be blocked from using the app.

## Installing the `legends` package

Note: Depending on how you installed Python, you may need to replace `pip` and `python` with `pip3` and `python3` in everything below.

1. Create a new folder somewhere. For the sake of the example, let's say your new folder is 'Documents/StarTrek'.

2. Copy the 'legends' folder and the 'requirements.txt' text file from this repository into your new folder, 'Documents/StarTrek'.

3. Open a command prompt at 'Documents/StarTrek'. There are many ways to do this. On a Mac, you can open Finder, navigate to 'Documents', right click on 'StarTrek', and select 'Services > New Terminal at Folder'.

4. At the command prompt, enter
```
% pip install -r requirements.txt
```
This will install the packages needed to run the `legends` package.

5. (optional) At the command prompt, enter
```
% python -m pydoc -b
```
This will open a browser page with Python documentation. Find the "**legends** (package)" link and click it. You can now explore all the package documentation.

### 2. Starting the app from Terminal

Copy the file, `stlplannerapp.py`, to 'Documents/StarTrek'. At the command prompt, enter
```
% python stlplannerapp.py
```
That's it.

### 3. Starting the app interactively

At the command prompt, enter
```
% python
```
This will open the `Python` interpreter in interactive mode. Your command prompt ought to change to the Python prompt `>>>`. Now enter
```
>>> from legends.ui import STLPlanner
>>> STLPlanner()
```

### 4. Building the app yourself

If you do not already have `pyinstaller` installed, then at the command prompt, enter
```
% pip install pyinstaller
```
Then enter
```
% pyinstaller stlplannerapp.spec
```
When the process is finished, you will find the app inside the newly created 'dist' folder.

## About the new `legends` package

The `legends` package in this repository is completely different from the old `legends` package, which has been renamed to `legendscli` and moved to https://github.com/probabilist/legendscli.

The `legendscli` package contains many features designed solely for making it easy to use at a Python interactive prompt. Most of those have been stripped away in the new `legends` package. That means the new package is more streamlined and efficient, but it also requires more Python experience to use.

Since the new `legends` package is being rebuilt from the ground up, it does not yet have all the features that `legendscli` has. Those will all be added eventually (except possibly the Sela Stat Calculator).
