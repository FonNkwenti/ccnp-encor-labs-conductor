#!/usr/bin/env python3
"""
Replace \\n with \\r\\n inside byte string literals in Python files.
"""
import os
import re

def fix_string(content):
    """Replace \\n with \\r\\n inside byte string literals."""
    # State machine
    i = 0
    result = []
    in_string = False
    quote_char = None
    backslash = False
    while i < len(content):
        ch = content[i]
        if not in_string:
            # Not inside string
            if ch == 'b' and i + 1 < len(content) and content[i+1] in ('"', "'"):
                # Start of byte string
                result.append(ch)
                i += 1
                quote_char = content[i]
                result.append(quote_char)
                in_string = True
                backslash = False
                i += 1
                continue
            result.append(ch)
            i += 1
        else:
            # Inside byte string
            if backslash:
                # Previous char was backslash
                if ch == 'n':
                    # Found \n escape sequence
                    # Check if preceded by \r already
                    if result[-2] == '\\' and result[-1] == 'r':
                        # Already \r\n, keep
                        result.append(ch)
                    else:
                        # Replace \n with \r\n
                        # Need to insert \r before \n
                        # result currently ends with backslash
                        # Remove the backslash and 'n' we haven't added yet
                        # Actually we have already added backslash? Let's think.
                        # We have added previous char (maybe backslash) already.
                        # Since backslash flag was True, we haven't added ch yet.
                        # result currently ends with the backslash (added when we saw it).
                        # We'll replace the backslash and 'n' with \r\n
                        # Remove the backslash from result
                        result.pop()  # remove backslash
                        result.append('\\\\')
                        result.append('r')
                        result.append('\\\\')
                        result.append('n')
                else:
                    # Other escape, keep
                    result.append(ch)
                backslash = False
                i += 1
                continue
            if ch == '\\\\':
                # Backslash
                backslash = True
                result.append(ch)
                i += 1
                continue
            if ch == quote_char and not backslash:
                # Closing quote
                in_string = False
                result.append(ch)
                i += 1
                continue
            # Normal character inside string
            result.append(ch)
            i += 1
    return ''.join(result)

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    new_content = fix_string(content)
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f'Fixed {filepath}')
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