# -*- coding: utf-8 -*-
"""
@author: sota_masuda
python 3.6
"""
import os
import sys
import re

# ========================================
# refer to shapefile.py
# ========================================
PYTHON3 = sys.version_info[0] == 3
def b_sjis(v):
    if PYTHON3:
        if isinstance(v, str):
            # For python 3 encode str to bytes.
            return v.encode('cp932')
        elif isinstance(v, bytes):
            # Already bytes.
            return v
        else:
            # Error.
            raise Exception('Unknown input type')
    else:
        # For python 2 assume str passed in and return str.
        return v

def u_sjis(v):
    if PYTHON3:
        # try/catch added 2014/05/07
        # returned error on dbf of shapefile
        # from www.naturalearthdata.com named
        # "ne_110m_admin_0_countries".
        # Just returning v as is seemed to fix
        # the problem.  This function could
        # be condensed further.
        try:
          if isinstance(v, bytes):
              # For python 3 decode bytes to str.
              return v.decode('cp932')
          elif isinstance(v, str):
              # Already str.
              return v
          else:
              # Error.
              raise Exception('Unknown input type')
        except: return v
    else:
        # For python 2 assume str passed in and return str.
        return v