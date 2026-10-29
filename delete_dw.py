import os

def force_delete_tree(path):
    """Delete directory tree using \\?\ prefix for long paths."""
    if path.startswith("\\\\?\\"):
        long = path
    else:
        long = "\\\\?\\" + os.path.abspath(path)

    for root, dirs, files in os.walk(long, topdown=False):
        # Ensure root also uses long path prefix
        if not root.startswith("\\\\?\\"):
            root = "\\\\?\\" + root
        for f in files:
            fpath = os.path.join(root, f)
            try:
                os.remove(fpath)
            except Exception as e:
                print(f"  Cannot remove file {fpath}: {e}")
        try:
            os.rmdir(root)
        except Exception as e:
            print(f"  Cannot remove dir {root}: {e}")

base = r"D:\git\mulesoft\projects\api-cert-level-2\src\test\resources"

for name in os.listdir(base):
    if name.startswith("embedded-dw_"):
        path = os.path.join(base, name)
        print(f"Deleting: {name}")
        force_delete_tree(path)
        if not os.path.exists(path):
            print(f"  -> Deleted successfully")
        else:
            print(f"  -> Still exists!")
