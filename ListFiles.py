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

def list_tree(path, follow_symlinks=False, excluded=None, nestedLevel=1):
    """
    Recursively print directory tree in Obsidian using collapsible code blocks.
    Each folder is a foldable block; files are indented inside.
    """
    excluded = excluded or set()
    indent = "  " * nestedLevel  # 2 spaces per level

    try:
        entries = sorted(
            os.listdir(path),
            key=lambda n: (not os.path.isdir(os.path.join(path, n)), n.lower())
        )
    except (OSError, PermissionError):
        print(f"{indent}[ ] !! {os.path.basename(path)} <inaccessible>")
        return

    for name in entries:
        if name in excluded:
            continue

        full = os.path.join(path, name)
        is_dir = os.path.isdir(full)

        try:
            size_bytes = dir_size(full, follow_symlinks) if is_dir else os.path.getsize(full)
            size_str = human_size(size_bytes)
        except (OSError, PermissionError):
            size_str = "<inaccessible>"

        icon = "FO" if is_dir else "FI"

        if is_dir:
            print(f"{indent}[ ] {icon} {name}  {size_str}")
            # recursive call for contents
            list_tree(full, follow_symlinks, excluded=excluded, nestedLevel=nestedLevel + 1)
        else:
            print(f"{indent}- [ ] {icon} {name}  {size_str}")

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
    print("```")
    print(f"[ ] FO {base_name:<30} {human_size(size_bytes)}")
    list_tree(root, follow_symlinks=True, excluded=excluded)
    print("```")
    input("Please entry any key to exit....")
    sys.exit()

if __name__ == "__main__":
    main()

