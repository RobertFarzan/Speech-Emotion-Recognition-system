# Installation guide

This installation guide will help you to set up and get all the necessary tools to run the client program. However, this installation guide does not include instructions to run the notebook code to reproduce the experiments to develop the SER model, just the client app.

## Prerequisites

- **Ubuntu 18.04** (probably compatible with other Linux distributions)
- **Python 3.8-dev** (comes with the installation script)

## 1. Clone or download the project
First of all, you'll have to **clone or download the repository** from GitHub manually or by typing:

```
$ git clone https://github.com/RobertFarzan/Speech-Emotion-Recognition-system.git
```
## 2. Setting up the execution environment
Once you have all the project files on your local machine, there are two ways of building the execution environment:

### a. Using the `setup.sh` script

The script `setup.sh` contains all the necessary commands and dependencies to run the program, including a `python3.8-dev` installation, `python3-pip` and more. To run the script, open a shell, enter the project's root folder with `$ cd` command and just type:

```
$ source setup.sh
```

This will require `sudo` permissions. If the installation was successful, your current shell should be inside a Python virtual environment (venv) and you should see something like this:

```
(venv) yourusername@yourmachine:~/projectfolder
```

Otherwise, if the installation script failed, check the file to see if some package or library may conflict with your current set up. In this case, it might be more convenient to proceed with the manual installation shown in the next step.

### b. Manual installation

In some cases, some dependencies or previous installations of the same software (e.g. another Python version) may conflict with the current installation, causing unexpected behaviour. 

In such a case, it is best to install every dependency one by one.

1. Firstly, update your packages with
    ```
    $ sudo apt-get update
    ```

2. Secondly, install the following Python 3.8 **developer version**. It is important that it is the dev version instead of the usual installation because it includes some *header files* necessary for the project. If already have a Python 3.8 installation, it might be convenient to uninstall it to avoid conflicts.

    ```
    $ sudo apt-get install python3.8-dev
    $ sudo apt install libpython3.8-dev
    ```

3. Install the Python **venv** library to create the virtual environment necessary to run the program.

    ```
    $ sudo apt-get install python3.8-venv
    ```

4. Install the `pip` version for Python 3. If already installed, skip this step.

    ```
    $ sudo apt-get install python3-pip
    ```

5. Install the audio controllers necessary to record audio from the main script. If not installed, it will cause problems and errors when running the program.

    ```
    $ sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
    ```

6. Create a virtual environment with the same Python installation we did already.

    ```
    $ python3.8 -m venv venv
    ```

    > **IMPORTANT NOTE**: if run with `python3` or `python` commands instead of `python3.8`, it might create the virtual env with another version you may have installed, causing conflicts later on.

7. Activate the virtual environment with

    ```
    $ source venv/bin/activate
    ```

8. Install the dependencies with `pip` inside the virtual environment.

    ```
    $ pip install --upgrade pip
    $ pip install -r requirements.txt
    ```

## Running the program

Now we have all the necessary tools and dependencies installed, there are a couple of things to take into account before running the app.

1. **Always** activate the virtual environment before running. If you don't see `(venv)` in your command prompt, it is most likely it is not activated. In such case, remember to do:

    ```
    $ source venv/bin/activate
    ```

2. Set the $PYTHONPATH environment variable to the `src` folder of the project. This will allow the script `app.py` to find the packages inside the `src` directory. Otherwise it will fail.

    You can do this in two ways:

    * Temporarily. This would require to execute the following command each time you would like to run the program:

        ```
        $ cd /path/to/project_root (not literal)
        $ export PYTHONPATH="$PWD/src"
        ```
    * Permanently. This would only need to be done once. Take the full path of the src folder inside the project's root folder (e.g `/home/user/project/src`). Then open the `.bashrc` file located in your home directory with your favorite text editor and do as follows:

        ```
        $ nano $HOME/.bashrc (or vi, vim etc.)
        > write "export PYTHONPATH=/home/path/to/project/src" at the end (not literal). Save the file and exit.
        $ source $HOME/.bashrc
        ```

3. Check the PYTHONPATH variable is set correctly by running `$ echo $PYTHONPATH`. If the output is empty, something went wrong.

Now everything is set to go. You just have to run the program to see the magic with:

```
$ python3.8 app.py
```