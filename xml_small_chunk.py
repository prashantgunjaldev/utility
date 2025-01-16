import xml.etree.ElementTree as ET
import os

def split_large_xml(file_path, output_dir, parent_tag, chunk_size=100):
    """
    Splits a large XML file into smaller files.

    :param file_path: Path to the large XML file.
    :param output_dir: Directory where smaller chunks will be saved.
    :param parent_tag: The parent tag used to group chunks.
    :param chunk_size: Number of child elements per chunk.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Parse the XML file
    context = ET.iterparse(file_path, events=("start", "end"))
    _, root = next(context)  # Grab the root element

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

    print(f"XML split completed. {chunk_count} files created in '{output_dir}'.")

def write_chunk(output_dir, root_tag, elements, chunk_count):
    """
    Writes a chunk of XML elements to a file.

    :param output_dir: Directory where the file will be saved.
    :param root_tag: Root tag for the XML file.
    :param elements: List of XML elements to include in the file.
    :param chunk_count: The chunk number for naming the file.
    """
    chunk_file = os.path.join(output_dir, f"chunk_{chunk_count}.xml")
    with open(chunk_file, "wb") as f:
        f.write(f"<{root_tag}>\n".encode("utf-8"))
        for element in elements:
            f.write(ET.tostring(element, encoding="utf-8"))
        f.write(f"</{root_tag}>\n".encode("utf-8"))

# Example Usage
if __name__ == "__main__":
    file_path = "large_file.xml"  # Replace with your large XML file path
    output_dir = "output_chunks"  # Directory to save chunks
    parent_tag = "record"  # Replace with the tag you want to split on
    chunk_size = 100  # Number of elements per chunk

    split_large_xml(file_path, output_dir, parent_tag, chunk_size)
