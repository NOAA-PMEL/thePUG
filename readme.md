# The PopUp GUI

This is a graphical interface for loading configurations onto PopUps
It contains both the executable file for running on desktops and the source files.

Unfortunately is this was written while I was still learning git and so branches are bit of a mess.
However, main should contain the working GUI with its files, using wxPython as it's GUI
package. Operation of this is described in the PUG User Guide contained here. The program is
segmented, with main.py starting the program, the GUI and it's functions contained in GUI.py.
Backend contains useful fucntions and the serial i/o code. cft.py contains useful data
structures including config templates, human readable names and dummy configs.

A new version using dearpygui was under development, but I was unable to complete it. It is
contained in the "migrating_to_dearpygui" branch. It also has important developments that 
should have been integrated into the wxPython version. In particular, it uses threading
to improve serial i/o reliability. It also has an active serial monitor, so the user can see
when the program has gotten stuck in a communication loop, unfortunately a common event.
Also, given the nature of dearpygui, much of the backend code has been integrated directly
into the GUI code. This makes the file more convoluted a long, but the improvements from 
dearpygui make it worthwhile.