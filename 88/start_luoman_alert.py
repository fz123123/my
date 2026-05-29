#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONLEGACYWINDOWSSTDIO'] = 'utf-8'

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.append('C:\\Users\\Administrator\\Documents\\trae_projects\\88')

from luoman_alert import LuomanAlertSystem

if __name__ == "__main__":
    alert_system = LuomanAlertSystem()
    print("\n" + "="*120)
    print("启动罗曼股份价格预警系统...")
    print("="*120 + "\n")
    price = alert_system.run_alert_system()
