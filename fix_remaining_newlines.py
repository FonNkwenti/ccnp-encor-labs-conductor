#!/usr/bin/env python3
"""
Replace remaining b"\\n" with b"\\r\\n" and b'\\n' with b'\\r\\n' in Python files.
Skip those that already have \\r\\n.
"""
import os
import re

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace b"
" with b"\r\n" (double quotes)
    # Use negative lookbehind to avoid replacing b"\r\n"
    pattern1 = r'b"\\n"'
    # Actually we want to match b"
" but not b"\r\n"
    # Simpler: replace all b"
" with b"\r\n", but ensure we don't double
    # We'll do a simple replace: b"
" -> b"\r\n"
    # If there is already \r before \n, skip.
    # Use regex with negative lookbehind: (?<!\r)
    # However, the string contains backslash-n, not newline character.
    # In source code, it's b"\\n". So we need to match b"\\n"
    # We'll replace with b"\\r\\n"
    new_content = re.sub(r'b"\\n"', r'b"\r\n"', content)
    # Replace b'
' with b'\r\n'
    new_content = re.sub(r"b'\\n'", r"b'\r\n'", new_content)
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f'Updated {filepath}')
        return True
    return False

def main():
    root = os.getcwd()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                try:
                    fix_file(filepath)
                except Exception as e:
                    print(f'Error processing {filepath}: {e}')

if __name__ == '__main__':
    main()