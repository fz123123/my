#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from 鹰眼压金_回测版 import EagleEyeSystem

if __name__ == "__main__":
    system = EagleEyeSystem()
    system.print_banner()
    print("\n🚀 正在运行策略对比分析...")
    results, best = system.run_all_strategies()
