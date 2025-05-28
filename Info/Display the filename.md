tag-writer.py has been modified to display the filename of the loaded file clearly in the GUI. Here's what the changes do:

1. Added a new label (filename_label) near the top of the interface that shows the currently loaded filename
2. Modified the select_file() function to update this label whenever a file is selected
3. The label shows the basename of the file (just the filename without the path) for cleaner display.
   The full path/filename is show at the bottom of the window.
4. Added "No file selected" text as the default state when no file is loaded
5. Made the label text bold for better visibility

Now, when you run the application:

•  The label will show "No file selected" initially

•  After selecting a file (either through the GUI or command line argument), it will display "File: [filename]"

•  The label is positioned directly beneath the "Select File" and "Write Metadata" buttons

These changes make it easy to see which file is currently loaded without having to check elsewhere in the interface.


