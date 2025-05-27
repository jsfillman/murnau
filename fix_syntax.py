#!/usr/bin/env python3
"""Fix syntax errors in main_window.py"""

import re

# Read the file
with open('src/murnau/ui/main_window.py', 'r') as f:
    content = f.read()

# Fix the duplicate 'if (' issue
content = re.sub(r'if \(\s*if \(', 'if (', content)

# Fix missing commas in hasattr calls
content = re.sub(r'hasattr\(self "([^"]+)"\)', r'hasattr(self, "\1")', content)

# Fix missing commas in exception tuples
content = re.sub(r'\(RuntimeError AttributeError\)', '(RuntimeError, AttributeError)', content)

# Write the fixed content back
with open('src/murnau/ui/main_window.py', 'w') as f:
    f.write(content)

print("Fixed syntax errors in main_window.py")