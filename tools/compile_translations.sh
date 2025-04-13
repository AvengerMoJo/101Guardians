#!/bin/bash

# This script compiles all translation files

# Change to the project root directory if not already there
cd "$(dirname "../$0")"

echo "Compiling translation files..."
pybabel compile -d translations

if [ $? -eq 0 ]; then
    echo "Translations compiled successfully!"
    echo "Your app now supports the following languages:"
    for d in translations/*/LC_MESSAGES; do
        LANG=$(echo $d | cut -d'/' -f2)
        echo "- $LANG"
    done
else
    echo "Error: Failed to compile translations"
    exit 1
fi

echo "Done!"
