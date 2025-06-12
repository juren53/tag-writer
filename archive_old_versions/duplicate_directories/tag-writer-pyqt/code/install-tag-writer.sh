#!/bin/bash

# Check if tag-writer.py exists in the current directory
if [ ! -f "tag-writer.py" ]; then
    echo "Error: tag-writer.py not found in the current directory."
    exit 1
fi

# Create ~/.local/bin directory if it doesn't exist
if [ ! -d "$HOME/.local/bin" ]; then
    echo "Creating directory $HOME/.local/bin"
    mkdir -p "$HOME/.local/bin"
fi

# Copy the file to ~/.local/bin/tag-writer
echo "Copying tag-writer.py to $HOME/.local/bin/tag-writer"
cp "tag-writer.py" "$HOME/.local/bin/tag-writer"

# Make it executable
echo "Making $HOME/.local/bin/tag-writer executable"
chmod +x "$HOME/.local/bin/tag-writer"

echo "Installation complete!"
echo "Make sure $HOME/.local/bin is in your PATH to use tag-writer from any directory."

