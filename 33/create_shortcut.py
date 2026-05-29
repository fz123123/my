#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建桌面快捷方式
"""

import os
import sys
from pathlib import Path
import pythoncom
from win32com.shell import shell, shellcon
import win32api
import win32con
import win32gui
import win32print


def create_shortcut():
    """创建桌面快捷方式"""

    # 目标文件路径
    target_path = r"C:\Users\Administrator\Documents\trae_projects\33\恐慌盘扫描.bat"

    # 桌面路径
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    # 快捷方式路径
    shortcut_path = os.path.join(desktop, "恐慌盘扫描.lnk")

    # 检查目标文件是否存在
    if not os.path.exists(target_path):
        print(f"错误: 找不到文件 {target_path}")
        return False

    try:
        # 使用WScript创建快捷方式
        import pythoncom
        from win32com.shell import shell, shellcon

        pythoncom.CoInitialize()

        # 创建快捷方式对象
        shortcut = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink,
            None,
            pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IShellLink
        )

        # 设置目标路径
        shortcut.SetPath(target_path)

        # 设置工作目录
        shortcut.SetWorkingDirectory(r"C:\Users\Administrator\Documents\trae_projects\33")

        # 设置描述
        shortcut.SetDescription("恐慌盘自动扫描工具")

        # 保存快捷方式
        persister = shortcut.QueryInterface(shell.IID_IPersistFile)
        persister.Save(shortcut_path, 0)

        pythoncom.CoUninitialize()

        print(f"成功创建桌面快捷方式!")
        print(f"位置: {shortcut_path}")
        return True

    except Exception as e:
        print(f"错误: {e}")
        return False


def create_shortcut_simple():
    """使用简单方法创建快捷方式"""

    target_path = r"C:\Users\Administrator\Documents\trae_projects\33\恐慌盘扫描.bat"
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop, "恐慌盘扫描.lnk")

    if not os.path.exists(target_path):
        print(f"错误: 找不到文件")
        return False

    try:
        import win32com.client
        import pythoncom

        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = r"C:\Users\Administrator\Documents\trae_projects\33"
        shortcut.Description = "恐慌盘自动扫描"
        shortcut.Save()

        pythoncom.CoUninitialize()

        print("成功创建桌面快捷方式!")
        print(f"位置: {shortcut_path}")
        return True

    except Exception as e:
        print(f"错误: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("创建桌面快捷方式")
    print("=" * 60)
    print()
    create_shortcut_simple()
    print()
    print("=" * 60)
