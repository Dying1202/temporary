import os
import re
from pathlib import Path
import sys

def extract_mod_name(filename):
    """
    提取 mod 名称：
    1. 去掉 .jar 扩展名
    2. 找到第一个数字的位置
    3. 往前找离它最近的 '-'
    4. 取 '-' 之前的内容
    5. 去掉末尾的 '-forge'、'-neoforge'、'-neo'（不区分大小写）
    6. 删除内容中所有的 '-'
    """
    name = filename
    if name.lower().endswith('.jar'):
        name = name[:-4]
    
    # 找到第一个数字的位置
    first_digit_match = re.search(r'\d', name)
    if not first_digit_match:
        dash_pos = name.find('-')
        if dash_pos == -1:
            result = name
        else:
            result = name[:dash_pos]
    else:
        first_digit_pos = first_digit_match.start()
        dash_pos = name.rfind('-', 0, first_digit_pos)
        if dash_pos == -1:
            result = name[:first_digit_pos]
        else:
            result = name[:dash_pos]
    
    # 去掉末尾的 -forge、-neoforge、-neo（不区分大小写）
    suffixes = ['-forge', '-neoforge', '-neo']
    for suffix in suffixes:
        if result.lower().endswith(suffix.lower()):
            result = result[:-len(suffix)]
            break
    
    # 删除所有 '-'
    return result.replace('-', '')

def parse_program1_result(filepath):
    """
    读取程序一生成的结果文件，提取所有 mod 名（去掉标注）
    """
    mods = set()
    if not os.path.exists(filepath):
        return mods
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过空行和标题行
            if not line or line.startswith('【') or line.startswith('MC') or line.startswith('='):
                continue
            # 去掉末尾的标注，如 "（无1.21.1版本）"、"（未搜索到）"
            # 找到 "（" 的位置，去掉后面的部分
            bracket_pos = line.find('（')
            if bracket_pos != -1:
                mod_name = line[:bracket_pos].strip()
            else:
                mod_name = line.strip()
            if mod_name:
                mods.add(mod_name)
    return mods

def main():
    print("=" * 50)
    print("MC Mod 名称对比工具 v1.0")
    print("=" * 50)
    
    # 1. 输入路径
    mod_path = input("\n请输入 mod 文件夹路径: ").strip().strip('"')
    if not os.path.isdir(mod_path):
        print("❌ 路径无效，请检查后重试。")
        input("\n按回车退出...")
        return

    # 2. 提取所有 mod 名
    mod_names = []
    file_count = 0
    for file in os.listdir(mod_path):
        if file.lower().endswith('.jar'):
            file_count += 1
            mod_name = extract_mod_name(file)
            if mod_name:
                mod_names.append(mod_name)

    print(f"\n📁 找到 {file_count} 个 .jar 文件")
    print(f"📝 提取到 {len(mod_names)} 个 mod 名称")

    if not mod_names:
        print("⚠️ 未找到符合格式的 mod 文件。")
        input("\n按回车退出...")
        return

    # 3. 生成文件A：mod_names_list.txt
    desktop = Path.home() / "Desktop"
    file_a = desktop / "mod_names_list.txt"
    
    try:
        with open(file_a, 'w', encoding='utf-8') as f:
            for name in mod_names:
                f.write(name + '\n')
        print(f"✅ 已生成 mod 名称列表: {file_a}")
    except Exception as e:
        print(f"❌ 保存文件A出错: {e}")
        input("\n按回车退出...")
        return

    # 4. 读取程序一的结果文件
    file_program1 = desktop / "mods_with_1.21.1.txt"
    
    if not os.path.exists(file_program1):
        print(f"\n⚠️ 未找到程序一的结果文件: {file_program1}")
        print("请确保桌面上有 mods_with_1.21.1.txt")
        print("将跳过对比，仅生成 mod 名称列表。")
        input("\n按回车退出...")
        return

    program1_mods = parse_program1_result(file_program1)
    print(f"📋 程序一结果中有 {len(program1_mods)} 个 mod 名称")

    # 5. 对比：文件A中有但程序一结果中没有的
    set_a = set(mod_names)
    diff = set_a - program1_mods

    # 6. 生成文件B：mod_diff.txt
    file_b = desktop / "mod_diff.txt"
    
    try:
        with open(file_b, 'w', encoding='utf-8') as f:
            if diff:
                f.write("以下 mod 在文件夹中存在，但未出现在程序一的结果中：\n")
                f.write("=" * 40 + "\n\n")
                for name in sorted(diff):
                    f.write(name + '\n')
            else:
                f.write("所有 mod 均已出现在程序一的结果中，无差异。\n")
        
        print(f"✅ 差异结果已保存: {file_b}")
    except Exception as e:
        print(f"❌ 保存文件B出错: {e}")
        input("\n按回车退出...")
        return

    # 7. 汇总
    print(f"\n📊 统计:")
    print(f"   文件夹中 mod 总数: {len(set_a)}")
    print(f"   程序一结果中 mod 数: {len(program1_mods)}")
    print(f"   差异数量（文件夹有但结果中没有）: {len(diff)}")
    
    if diff:
        print(f"\n差异 mod 列表：")
        for name in sorted(diff):
            print(f"   • {name}")

    input("\n按回车退出...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        input("按回车退出...")
