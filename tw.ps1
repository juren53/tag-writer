#!/usr/bin/env pwsh

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Run the Python script from its directory
& python "$ScriptDir\tag-writer.py" @args
