#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
Test what global objects are available when running from Resolve Scripts menu
"""

import sys

print("=" * 60)
print(" Testing Available Globals in Resolve")
print("=" * 60)
print()

# Check what's in globals
print("Checking globals():")
for key in sorted(globals().keys()):
    if not key.startswith('_'):
        print(f"  - {key}: {type(globals()[key])}")

print()
print("Checking builtins:")
import builtins
for key in dir(builtins):
    if key.lower() in ['resolve', 'fusion', 'bmd', 'app', 'scriptapp']:
        print(f"  - {key}: {getattr(builtins, key, 'not found')}")

print()
print("Checking sys.modules:")
for key in sys.modules.keys():
    if 'resolve' in key.lower() or 'fusion' in key.lower() or 'blackmagic' in key.lower():
        print(f"  - {key}")

print()
print("=" * 60)
input("Press Enter to close...")

