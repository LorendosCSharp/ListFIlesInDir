'''
This script list all file in a given directory
The output looks like this 
[x]Foldername 1GB 
    [x]Filename 1 20KB 
    [x]Filename 2 3MB
where [x] stands for ready status
'''
import os

def get_size(path):
    """Return size of a file or directory in human-readable form."""
    total_size = 0
    if os.path.isfile(path):
        total_size = os.path.getsize(path)
    else:
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
    return convert_size(total_size)

def convert_size(size_bytes):
    """Convert bytes to a readable size (KB, MB, GB)."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int((len(str(size_bytes)) - 1) / 3)
    p = 1024 ** i
    s = round(size_bytes / p, 2)
    return f"{s}{size_name[i]}"

def list_directory(path):
    for entry in os.scandir(path):
        if entry.is_dir():
            folder_size = get_size(entry.path)
            print(f"[ ]{entry.name} {folder_size}")
            for file in os.scandir(entry.path):
                if file.is_file():
                    file_size = convert_size(os.path.getsize(file.path))
                    print(f"    [ ]{file.name} {file_size}")
        elif entry.is_file():
            file_size = convert_size(os.path.getsize(entry.path))
            print(f"[ ]{entry.name} {file_size}")

# Example usage:
if __name__ == "__main__":
    directory = input("Enter absolute directory path: ").strip()
    if os.path.exists(directory):
        list_directory(directory)
    else:
        print("Invalid path.")
