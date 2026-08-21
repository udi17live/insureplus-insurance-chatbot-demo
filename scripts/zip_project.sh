#!/bin/bash

# Go to the project root directory
cd "$(dirname "$0")/.." || exit

# Create the output directory if it doesn't exist
mkdir -p scripts/output

# Name of the zip file, including a human-readable timestamp
TIMESTAMP=$(date +"%b_%d_%Y_at_%I_%M_%p")
OUTPUT_FILE="scripts/output/project_archive_${TIMESTAMP}.zip"

echo "Creating archive at $OUTPUT_FILE ..."

# Remove the existing zip if it exists to avoid appending to it
rm -f "$OUTPUT_FILE"

# Zip the files, respecting .gitignore
# git ls-files -c (tracked) -o (untracked) --exclude-standard (respect .gitignore)
git ls-files -c -o --exclude-standard | zip -@ "$OUTPUT_FILE"

echo "Done!"
