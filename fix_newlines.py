#!/usr/bin/env python3
"""
Replace b"\\n" with b"\\r\\n" and b'\\n' with b'\\r\\n' in Python files.
"""
import os
import re
import sys

def replace_in_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace b"\r\n" with b"\r\n" (double quotes)
    # Use regex to avoid replacing b"\r\n" again
    pattern1 = r'b"\\n"'
    replacement1 = r'b"\r\n"'
    new_content = re.sub(pattern1, replacement1, content)
    
    # Replace b'\r\n' with b'\r\n' (single quotes)
    pattern2 = r"b'\\n'"
    replacement2 = r"b'\r\n'"
    new_content = re.sub(pattern2, replacement2, new_content)
    
    # Replace line.encode('ascii') + b"\r\n" pattern
    # This is more specific; we can just replace all b"\r\n" occurrences already covered
    # But ensure we don't miss those with spaces: + b"\r\n"
    # Actually the regex above already catches them
    
    # Also replace b"\\n" in triple quotes? The regex should catch them
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f'Updated {filepath}')
        return True
    return False

def main():
    root = os.getcwd()
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                try:
                    replace_in_file(filepath)
                except Exception as e:
                    print(f'Error processing {filepath}: {e}')

if __name__ == '__main__':
    main()