import os
import hashlib

def has_file(filename):
    h=hashlib.md5()
    with open(filename,'rb') as file:
        while chunk:=file.read(8192):
            h.update(chunk)
    return h.hexdigest()

def find_dup(folder):
    hashes = {}
    duplicates = []
    for dirpath, _, filenames in os.walk(folder):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            file_hash = has_file(full_path)
            if file_hash in hashes:
                duplicates.append((full_path, hashes[file_hash]))
            else:
                hashes[file_hash] = full_path
    return duplicates

def delete_file(filepath):
    try:
        os.remove(filepath)
        return True
    except Exception as e:
        return False
