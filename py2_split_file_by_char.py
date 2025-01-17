import sys
import os

def split_file(file_name, chunk_size):
    try:
        chunk_size = int(chunk_size)
        with open(file_name, 'r') as f:
            content = f.read()
        
        base_name, ext = os.path.splitext(file_name)
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            chunk_file_name = "{}_part_{}{}".format(base_name, i // chunk_size + 1, ext)
            with open(chunk_file_name, 'w') as chunk_file:
                chunk_file.write(chunk)
            print("Created:", chunk_file_name)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python split_file.py <file_name> <chunk_size>")
    else:
        split_file(sys.argv[1], sys.argv[2])
