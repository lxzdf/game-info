# 1. 使用文本编辑器创建
nano run.sh

# 2. 复制我提供的脚本内容，粘贴后保存
# 3. 按 Ctrl+X，然后按 Y，再按 Enter 保存

# 或者使用 echo 命令直接创建
echo '#!binbash

# 玩家配置评分系统 - 运行脚本

echo 🎮 玩家配置评分系统
echo ==================

# 检查Python版本
python_version=$(python3 --version 2&1  awk '''{print $2}''')
echo Python版本 $python_version

# 安装依赖
echo 安装依赖...
pip install -r requirements.txt

# 检查输入文件
if [ ! -f dataplayer_pc_configs.csv ]; then
    echo 错误 找不到输入文件 dataplayer_pc_configs.csv
    echo 请将玩家配置数据放在 data 目录下
    exit 1
fi

# 检查配置文件
required_configs=(CPU理论性能.xlsx 显卡理论性能.xlsx 内存理论性能.xlsx 硬盘理论性能.xlsx)
for config in ${required_configs[@]}; do
    if [ ! -f configs$config ]; then
        echo 警告 找不到配置文件 configs$config
    fi
done

# 运行主程序
echo 开始处理...
python3 main.py

# 检查输出
if [ -f output玩家配置评分数据.csv ]; then
    echo ✅ 处理完成!
    echo 输出文件
    echo   - output玩家配置评分数据.csv
    echo   - output玩家配置评分数据.xlsx
    echo   - logsmatching_statistics.csv
else
    echo ❌ 处理失败，请检查日志
fi'  run.sh

# 4. 给文件添加执行权限
chmod +x run.sh