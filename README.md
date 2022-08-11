# workoutdb

## An Easy Way to Track Your Workout Routine

This simple program uses sqlite and python to create and manage a database of different user specified categories.

# Installation

```
git clone https://github.com/Potato-git13/workoutdb.git
make build install
```

## For Users

The above commands will build and install the program that can now be used with the ```workoutdb``` command.

## For Developers 

The source files can be found in the ```src/``` directory

# Usage

## Creating a Database

To create and initialize a new database enter the command: 

```workoutdb FILENAME --init CATEGORY CATEGORY ...```

 - ```FILENAME``` is the path to the database file. The file does not have to exist to be chosen.
 - ```CATEGORY``` is a a name of a category that will be included in the database.

This command creates a database file/uses an existing one and initializes it with the given categories.

A ```--verbose``` flag can be added to any of the commands for more information on what the program is doing.

## Using a Database

After a database is initialized you can start to interact with it. For more information about using workoutdb call the help command ```workoutdb --help```