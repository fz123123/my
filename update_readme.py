#!/usr/bin/env python3
"""
README 自动更新脚本
自动生成或更新项目文档
"""

import os
import json
from datetime import datetime


def get_project_info(project_dir):
    """获取项目信息"""
    info = {
        'name': project_dir,
        'has_package_json': False,
        'has_requirements_txt': False,
        'has_tests': False,
        'has_src': False,
        'has_dist': False,
        'test_count': 0,
        'description': ''
    }
    
    # 检查 package.json
    package_json = os.path.join(project_dir, 'package.json')
    if os.path.exists(package_json):
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                info['has_package_json'] = True
                info['description'] = data.get('description', '')
        except:
            pass
    
    # 检查 requirements.txt
    if os.path.exists(os.path.join(project_dir, 'requirements.txt')):
        info['has_requirements_txt'] = True
    
    # 检查 tests 目录
    tests_dir = os.path.join(project_dir, 'tests')
    if os.path.exists(tests_dir) and os.path.isdir(tests_dir):
        info['has_tests'] = True
        test_files = [f for f in os.listdir(tests_dir) if f.startswith('test_') or f.endswith('.test.ts')]
        info['test_count'] = len(test_files)
    
    # 检查 src 和 dist 目录
    if os.path.exists(os.path.join(project_dir, 'src')):
        info['has_src'] = True
    if os.path.exists(os.path.join(project_dir, 'dist')):
        info['has_dist'] = True
    
    return info


def generate_readme_section():
    """生成 README 更新部分"""
    projects = ['0', '17', '33', '88']
    project_info_list = []
    
    for proj in projects:
        if os.path.exists(proj):
            project_info_list.append(get_project_info(proj))
    
    # 生成项目状态表格
    table = "## 📊 项目状态 (自动生成)\n\n"
    table += "| 项目 | 配置文件 | 源码 | 编译输出 | 测试 | 测试数 | 最后更新 |\n"
    table += "|------|---------|------|---------|------|--------|---------|\n"
    
    for info in project_info_list:
        package_json = "✅" if info['has_package_json'] else "❌"
        requirements_txt = "✅" if info['has_requirements_txt'] else "❌"
        src = "✅" if info['has_src'] else "❌"
        dist = "✅" if info['has_dist'] else "❌"
        tests = "✅" if info['has_tests'] else "❌"
        test_count = info['test_count']
        last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        table += f"| **项目{info['name']}** | {package_json}/{requirements_txt} | {src} | {dist} | {tests} | {test_count} | {last_update} |\n"
    
    return table


def update_readme():
    """更新 README.md"""
    readme_path = 'README.md'
    
    if not os.path.exists(readme_path):
        print("README.md 不存在，跳过更新")
        return
    
    # 读取现有 README
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有自动生成部分
    auto_section = generate_readme_section()
    
    # 替换或添加自动生成部分
    marker_start = "<!-- AUTO-START -->"
    marker_end = "<!-- AUTO-END -->"
    
    if marker_start in content and marker_end in content:
        # 替换现有部分
        start_idx = content.index(marker_start)
        end_idx = content.index(marker_end) + len(marker_end)
        new_content = content[:start_idx] + marker_start + "\n" + auto_section + "\n" + marker_end + content[end_idx:]
    else:
        # 在末尾添加新部分
        new_content = content + "\n\n" + marker_start + "\n" + auto_section + "\n" + marker_end
    
    # 写入更新后的 README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ README.md 已更新")
    return True


if __name__ == "__main__":
    update_readme()
