import os
import sys

'''
This script list all file in a given directory
It allows you to exclude certain folders interactively.

The output looks like this 
[ ] FolderName          1.2GB
│   [ ] file1.txt        20KB
│   [ ] file2.log         3MB

Where:
  [ ] = status marker
  FO  = Folder
  FI  = File
'''

# ---- Utility Functions ----

def human_size(nbytes):
    """Return human-readable size using binary units (KB = 1024)."""
    if nbytes < 1024:
        return f"{nbytes}B"
    for unit in ("KB", "MB", "GB", "TB", "PB"):
        nbytes /= 1024.0
        if nbytes < 1024.0:
            s = f"{nbytes:.2f}".rstrip("0").rstrip(".")
            return f"{s}{unit}"
    return f"{nbytes:.2f}PB"

def dir_size(path, follow_symlinks=False):
    """Compute total size of a directory."""
    total = 0
    for root, _, files in os.walk(path, followlinks=follow_symlinks):
        for f in files:
            fp = os.path.join(root, f)
            try:
                if not os.path.exists(fp):
                    continue
                total += os.path.getsize(fp)
            except (OSError, PermissionError):
                continue
    return total

# ---- Printing Tree ----

def list_tree(path, prefix="", follow_symlinks=False, excluded=None, is_last=True):
    """Recursively print directory tree with improved formatting."""
    excluded = excluded or set()

    try:
        entries = sorted(os.listdir(path), key=lambda n: (not os.path.isdir(os.path.join(path, n)), n.lower()))
    except (OSError, PermissionError):
        print(prefix + f"[ ] !! {os.path.basename(path)} <inaccessible>")
        return

    for i, name in enumerate(entries):
        if name in excluded:
            continue  # skip excluded folders

        full = os.path.join(path, name)
        is_dir = os.path.isdir(full)
        last_entry = (i == len(entries) - 1)
        connector = "└── " if last_entry else "├── "

        try:
            size_bytes = dir_size(full, follow_symlinks) if is_dir else os.path.getsize(full)
            size_str = human_size(size_bytes)
        except (OSError, PermissionError):
            size_str = "<inaccessible>"

        icon = "FO " if is_dir else "FI "
        color_start = "\033[94m" if is_dir else "\033[0m"
        color_end = "\033[0m"

        print(f"{prefix}{connector}[ ]{color_start}{icon}{name:<30}{color_end} {size_str}")

        if is_dir:
            new_prefix = prefix + ("    " if last_entry else "│   ")
            list_tree(full, new_prefix, follow_symlinks, excluded=excluded, is_last=last_entry)

# ---- Folder Selection ----

def choose_excluded_folders(root):
    """Show top-level folders and allow user to uncheck (exclude) them."""
    try:
        entries = [e for e in os.listdir(root) if os.path.isdir(os.path.join(root, e))]
    except (OSError, PermissionError):
        print("Cannot read directory contents.")
        return set()

    if not entries:
        return set()

    print("\nTop-level folders found:\n")
    for i, name in enumerate(entries, 1):
        print(f"  {i}. [x] {name}")

    print("\nEnter numbers of folders you want to EXCLUDE (comma-separated).")
    print("Example: 1,3,5 or leave blank to include all.\n")

    to_exclude = input("Exclude: ").strip()
    excluded = set()

    if to_exclude:
        try:
            indices = [int(x) for x in to_exclude.split(",") if x.strip().isdigit()]
            for i in indices:
                if 1 <= i <= len(entries):
                    excluded.add(entries[i - 1])
        except ValueError:
            print("Invalid input — no folders excluded.")

    print("\nExcluded folders:", ", ".join(excluded) if excluded else "None")
    print("-" * 60)
    return excluded

# ---- Main ----

def main():
    root = input("Enter absolute directory path: ").strip()
    if not os.path.exists(root):
        print("Path does not exist:", root)
        sys.exit(1)

    excluded = choose_excluded_folders(root)

    base_name = os.path.basename(root) or root
    size_bytes = dir_size(root, follow_symlinks=True)
    print(f"\n[ ] FO {base_name:<30} {human_size(size_bytes)}")
    list_tree(root, prefix="", follow_symlinks=True, excluded=excluded)

if __name__ == "__main__":
    main()
