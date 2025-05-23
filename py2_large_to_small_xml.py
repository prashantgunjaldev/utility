import xml.etree.ElementTree as ET
import os
import sys

def detect_parent_tag(file_path):
    """
    Detects the child tag in the XML file under the root (i.e., <book>).

    :param file_path: Path to the XML file.
    :return: Detected child tag (like <book>).
    """
    try:
        with open(file_path, "r") as f:  # Default encoding in Python 2.7
            for line in f:
                # Look for the first non-root element (which will be <book>)
                if "<book" in line:
                    return "book"  # Return the child tag (<book>) directly
    except Exception, e:
        raise ValueError("Error detecting parent tag: %s" % e)
    raise ValueError("Could not detect a parent tag in the XML file.")

def split_large_xml(file_path, output_dir, chunk_size=1):
    """
    Splits a large XML file into smaller files.

    :param file_path: Path to the large XML file.
    :param output_dir: Directory where smaller chunks will be saved.
    :param chunk_size: Number of child elements per chunk.
    """
    # Validate chunk_size
    if chunk_size <= 0:
        print("Error: Chunk size must be a positive integer.")
        sys.exit(1)

    # Ensure output directory exists
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    except Exception, e:
        print("Error: Failed to create or access output directory '%s'. %s" % (output_dir, e))
        sys.exit(1)

    # Detect the child tag (like <book>)
    try:
        parent_tag = detect_parent_tag(file_path)
        print("Detected child tag: <%s>" % parent_tag)
    except ValueError, e:
        print("Error: %s" % e)
        sys.exit(1)

    # Parse the XML file
    try:
        context = ET.iterparse(file_path, events=("start", "end"))
        _, root = next(context)  # Grab the root element
    except Exception, e:
        print("Error: Failed to parse the XML file '%s'. %s" % (file_path, e))
        sys.exit(1)

    chunk_count = 0
    current_chunk = []

    for event, elem in context:
        if event == "end" and elem.tag == parent_tag:
            current_chunk.append(elem)

            # Once we reach the chunk size, write to a new file
            if len(current_chunk) == chunk_size:
                chunk_count += 1
                write_chunk(output_dir, root.tag, current_chunk, chunk_count)
                current_chunk = []
                root.clear()  # Free memory by clearing the root

    # Write any remaining elements
    if current_chunk:
        chunk_count += 1
        write_chunk(output_dir, root.tag, current_chunk, chunk_count)

    print("XML split completed. %d files created in '%s'." % (chunk_count, output_dir))

def write_chunk(output_dir, root_tag, elements, chunk_count):
    """
    Writes a chunk of XML elements to a file.

    :param output_dir: Directory where the file will be saved.
    :param root_tag: Root tag for the XML file.
    :param elements: List of XML elements to include in the file.
    :param chunk_count: The chunk number for naming the file.
    """
    chunk_file = os.path.join(output_dir, "chunk_%d.xml" % chunk_count)
    try:
        with open(chunk_file, "wb") as f:
            f.write("<%s>\n" % root_tag)
            for element in elements:
                f.write(ET.tostring(element, encoding="utf-8"))
            f.write("</%s>\n" % root_tag)
    except Exception, e:
        print("Error: Failed to write chunk file '%s'. %s" % (chunk_file, e))
        sys.exit(1)

if __name__ == "__main__":
    # Validate the number of arguments
    if len(sys.argv) != 2:
        print("Usage: python split_large_xml.py <XML_FILE_PATH>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Check if the file exists and is a valid file
    if not os.path.isfile(file_path):
        print("Error: File '%s' not found." % file_path)
        sys.exit(1)

    output_dir = "./xml_chunk_output"  # Fixed output directory
    chunk_size = 1  # Number of elements per chunk

    # Start the XML splitting process
    split_large_xml(file_path, output_dir, chunk_size)
