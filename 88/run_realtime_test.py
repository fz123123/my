#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from test_realtime_data import main

if __name__ == "__main__":
    main()
