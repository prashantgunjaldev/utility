#!/bin/bash

# Configuration
OUTPUT_DIR="./xml_chunk_output"  # Directory to save the chunks
CHUNK_SIZE=100                   # Number of elements per chunk

# Ensure the XML file is provided as a command-line argument
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <XML_FILE_PATH>"
    exit 1
fi

FILE_PATH="$1"

# Check if the file exists
if [[ ! -f "$FILE_PATH" ]]; then
    echo "Error: File '$FILE_PATH' not found."
    exit 1
fi

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Detect the parent tag
PARENT_TAG=$(awk '/<\/[^>]+>/ { match($0, /<\/([^>]+)>/, arr); if (arr[1] != "root") { print arr[1]; exit } }' "$FILE_PATH")

if [[ -z "$PARENT_TAG" ]]; then
    echo "Error: Could not detect the parent tag in the XML file."
    exit 1
fi

echo "Detected parent tag: <$PARENT_TAG>"

# Initialize variables
chunk_count=0
record_count=0
chunk_file=""

# Read the XML file line by line
while IFS= read -r line; do
    # Check if the line contains the start of the parent tag
    if [[ $line == *"<$PARENT_TAG>"* ]]; then
        ((record_count++))
    fi

    # If a new chunk is starting, create a new file
    if ((record_count % CHUNK_SIZE == 1)); then
        ((chunk_count++))
        chunk_file="$OUTPUT_DIR/chunk_$chunk_count.xml"
        echo "Creating $chunk_file"
        # Add the root start tag to the new chunk file
        echo "<root>" > "$chunk_file"
    fi

    # Append the current line to the current chunk file
    echo "$line" >> "$chunk_file"

    # Check if the line contains the end of the parent tag
    if [[ $line == *"</$PARENT_TAG>"* ]] && ((record_count % CHUNK_SIZE == 0)); then
        # Add the root end tag to close the chunk file
        echo "</root>" >> "$chunk_file"
    fi
done < "$FILE_PATH"

# Close the final chunk if it hasn't been closed
if ((record_count % CHUNK_SIZE != 0)); then
    echo "</root>" >> "$chunk_file"
fi

echo "XML split completed. $chunk_count files created in '$OUTPUT_DIR'."
