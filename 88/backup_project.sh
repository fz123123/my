#!/bin/bash

# 涨停先知项目备份脚本
# Backup ZTB Seer Project

BACKUP_DIR="c:/Users/Administrator/Documents/trae_projects/88"
BACKUP_NAME="ZTB_Seer_backup_$(date +'%Y%m%d_%H%M%S')"

echo "========================================"
echo "  涨停先知 - 项目备份工具"
echo "========================================"
echo ""

echo "备份源目录: $BACKUP_DIR"
echo "备份目标: $BACKUP_NAME"
echo ""

# 创建备份目录
mkdir -p "$BACKUP_NAME"

# 复制项目文件
echo "正在复制项目文件..."
cp -r "$BACKUP_DIR"/* "$BACKUP_NAME"/

# 创建备份说明
cat > "$BACKUP_NAME/BACKUP_INFO.txt" << EOF
========================================
涨停先知项目备份信息
========================================

备份时间: $(date +'%Y-%m-%d %H:%M:%S')
备份版本: v1.0.0
技术栈: Vue 3 + Vite + ECharts

项目特点:
- 实时股票行情分析
- 技术指标分析系统
- 智能选股评分
- 专业K线图表

启动命令:
cd $BACKUP_NAME
npm install
npm run dev

========================================
EOF

echo "✅ 备份完成！"
echo ""
echo "备份位置: $BACKUP_NAME"
echo ""
ls -lh "$BACKUP_NAME"
