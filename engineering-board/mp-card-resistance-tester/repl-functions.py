import os

# To use these functions from the REPL:
# exec(open("repl-functions.py").read())


def rm(file_path):
    try:
        os.remove(file_path)
        print(f"Removed file: {file_path}")
    except OSError as e:
        print(f"Error removing file: {e}")


def rmr(dir_path):
    try:
        os.rmdir(dir_path)
        print(f"Removed directory: {dir_path}")
    except OSError as e:
        print(f"Error removing directory: {e}")


def cat(file_path):
    try:
        with open(file_path, "r") as f:
            content = f.read()
            print(content)
    except OSError as e:
        print(f"Error reading file: {e}")


def lsr(dir_path="/"):
    # List all files and folders in the current directory
    print(f"{'Size':<7} {'Path'}")
    for entry in os.ilistdir(dir_path):
        name = entry[0]
        status = entry[1]

        size = -1 if len(entry) < 4 else entry[3]

        # Create full path
        full_path = dir_path + "/" + name if dir_path != "/" else "/" + name

        try:
            # Check if entry is a directory (status 0x4000)
            if status & 0x4000:
                lsr(full_path)
            else:
                print(f"{size:<7} {full_path}")
        except OSError:
            # Handle cases where os.stat might fail (e.g., hidden system files)
            continue


# # Usage: list starting from root
# list_files_recursive()

print("REPL Functions Loaded. You can call:")
print("   lsr(path = '/')")
print("   rm(file_path)")
print("   rmr(dir_path)")
print("   cat(file_path)")
