#!/bin/bash
cd /home/WebSearchAIO

# 检查环境变量是否存在
if [ -z "$AILawyerEnv" ]; then
  echo "环境变量AILawyerEnv未设置或为空。请设置AILawyerEnv环境变量并重新运行脚本。"
  exit 1
fi

# 输出环境变量a的值
echo "环境变量a的值为: $AILawyerEnv"

# 构建文件名
config_filename="gunicorn_config_${AILawyerEnv}.py"

echo "config_filename: $config_filename"

# 启动服务
gunicorn -c ${config_filename} web_search:app
