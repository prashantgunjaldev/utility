import xml.etree.ElementTree as ET
import os
import sys

def detect_repeating_tag(file_path):
    """
    Detects the first repeating tag in the XML file and its immediate parent.

    :param file_path: Path to the XML file.
    :return: Tuple of (parent tag, repeating tag).
    """
    try:
        with open(file_path, "r") as f:
            context = ET.iterparse(f, events=("start", "end"))
            tag_hierarchy = []
            tag_counts = {}

            for event, elem in context:
                if event == "start":
                    tag_hierarchy.append(elem.tag)

                    # Track occurrences of parent-child tag combinations
                    if len(tag_hierarchy) > 1:
                        parent = tag_hierarchy[-2]
                        child = tag_hierarchy[-1]
                        key = (parent, child)

                        if key in tag_counts:
                            tag_counts[key] += 1
                            if tag_counts[key] > 1:
                                return key  # Return the first repeating parent-child tag pair
                        else:
                            tag_counts[key] = 1

                elif event == "end":
                    tag_hierarchy.pop()

        raise ValueError("No repeating tag found in the XML file.")

    except Exception as e:
        raise ValueError("Error detecting repeating tag: %s" % e)

def split_large_xml(file_path, output_dir, chunk_size):
    """
    Splits a large XML file into smaller files based on repeating tags.

    :param file_path: Path to the large XML file.
    :param output_dir: Directory where smaller chunks will be saved.
    :param chunk_size: Number of child elements per chunk.
    """
    if chunk_size <= 0:
        print("Error: Chunk size must be a positive integer.")
        sys.exit(1)

    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    except Exception as e:
        print("Error: Failed to create or access output directory '%s'. %s" % (output_dir, e))
        sys.exit(1)

    try:
        parent_tag, repeating_tag = detect_repeating_tag(file_path)
        print("Detected repeating tag: <%s> under parent <%s>" % (repeating_tag, parent_tag))
    except ValueError as e:
        print("Error: %s" % e)
        sys.exit(1)

    try:
        context = ET.iterparse(file_path, events=("start", "end"))
        _, root = next(context)  # Grab the root element
    except Exception as e:
        print("Error: Failed to parse the XML file '%s'. %s" % (file_path, e))
        sys.exit(1)

    chunk_count = 0
    current_chunk = []

    for event, elem in context:
        if event == "end" and elem.tag == repeating_tag:
            current_chunk.append(elem)

            if len(current_chunk) == chunk_size:
                chunk_count += 1
                write_chunk(output_dir, root.tag, parent_tag, current_chunk, chunk_count)
                current_chunk = []
                root.clear()  # Free memory by clearing the root

    if current_chunk:
        chunk_count += 1
        write_chunk(output_dir, root.tag, parent_tag, current_chunk, chunk_count)

    print("XML split completed. %d files created in '%s'." % (chunk_count, output_dir))

def write_chunk(output_dir, root_tag, parent_tag, elements, chunk_count):
    """
    Writes a chunk of XML elements to a file, wrapping them with their parent and root tags.

    :param output_dir: Directory where the file will be saved.
    :param root_tag: Root tag for the XML file.
    :param parent_tag: Parent tag wrapping the repeating elements.
    :param elements: List of XML elements to include in the file.
    :param chunk_count: The chunk number for naming the file.
    """
    chunk_file = os.path.join(output_dir, "chunk_%d.xml" % chunk_count)
    try:
        with open(chunk_file, "wb") as f:
            f.write("<?xml version=\"1.0\"?>\n")
            f.write("<%s>\n" % root_tag)
            f.write("<%s>\n" % parent_tag)
            for element in elements:
                f.write(ET.tostring(element, encoding="utf-8"))
            f.write("</%s>\n" % parent_tag)
            f.write("</%s>\n" % root_tag)
    except Exception as e:
        print("Error: Failed to write chunk file '%s'. %s" % (chunk_file, e))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python split_large_xml.py <XML_FILE_PATH> <NO_OF_XML_TAGS> <OUTPUT_DIR>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.isfile(file_path):
        print("Error: File '%s' not found." % file_path)
        sys.exit(1)

    try:
        chunk_size = int(sys.argv[2])
    except ValueError:
        print("Error: <NO_OF_XML_TAGS> must be an integer.")
        sys.exit(1)

    output_dir = sys.argv[3]

    split_large_xml(file_path, output_dir, chunk_size)
