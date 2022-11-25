# UnixLikeFileExplorer - aka 'THE_FILE_GLOBBER'
A console application that functions as a file explorer, but entirely cross-platform.<br/>
It's main objective is to allow the use of Unix-like patterns on Windows.

## Installation
### Using Git
*This method requires the use of the Git software ([http://git-scm.com](http://git-scm.com)).*

Open a command prompt/terminal on your system, and `cd` your way into the directory you want to extract the project into.

Type `git clone https://github.com/megat69/UnixLikeFileExplorer.git`.

Wait until the download is complete.

You are good to move on to the [setup](#Setup).

### Downloading from ZIP
Click on the green `Code` button. It will open a dropdown menu containing a `Download ZIP` option. Click this option.

Wait until the download is complete and extract the file wherever you want.

You are good to move on to the [setup](#setup).

## Setup
You now need to run the `setup.py` file.

To do so, open a command prompt/terminal and run the `python setup.py` command. **WARNING: If your Python is installed in a system directory, I recommend opening the command prompt/terminal as administrator so the dependencies can be installed.**

Once the setup is complete, you can just [launch the explorer](#launching).

## Launching
To launch the explorer, simply open a terminal/command prompt inside the software's folder, then run the `python main.py` command.

## How to Use
Use you arrow keys to select folders/files.

You can type as you go to move across folders.

Using the Enter key will :
- Move into the selected folder if the selected item is a directory ;
- Open the selected file in its default program if the selected item is a file.

You can type `:` followed by a pattern inside any valid directory to search for specific files.

You can leave the app by pressing the '$' key.
