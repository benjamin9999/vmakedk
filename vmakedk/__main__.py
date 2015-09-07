#!/usr/bin/env python
"""
vmakedk module/executable bootstrap

inspired ;) by youtube-dl's layout and __main__

Execute with
# python vmakedk/__main__.py (2.6)
# python -m vmakedk          (2.7)

"""
import sys

if __package__ is None and not hasattr(sys, 'frozen'):
    # this is a direct call to __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(path)))

import vmakedk

if __name__ == '__main__':
    vmakedk.main()
