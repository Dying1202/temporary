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
    
    suffixes = ['-forge', '-neoforge', '-neo']
    for suffix in suffixes:
        if result.lower().endswith(suffix.lower()):
            result = result[:-len(suffix)]
            break
    
    return result.replace('-', '')

def parse_program1_result(filepath):
    """
    读取程序一生成的结果文件，提取所有 mod 名（去掉标注）
    返回列表，保持原始顺序，去重
    """
    mods = []
    seen = set()
    if not os.path.exists(filepath):
        return mods
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('【') or line.startswith('MC') or line.startswith('='):
                continue
            bracket_pos = line.find('（')
            if bracket_pos != -1:
                mod_name = line[:bracket_pos].strip()
            else:
                mod_name = line.strip()
            if mod_name and mod_name not in seen:
                mods.append(mod_name)
                seen.add(mod_name)
    return mods

def main():
    print("=" * 50)
    print("MC Mod 清理工具 - 删除已在文件夹中的 mod")
    print("=" * 50)
    
    # 1. 读取程序一的结果文件
    desktop = Path.home() / "Desktop"
    file_program1 = desktop / "mods_with_1.21.1.txt"
    
    if not os.path.exists(file_program1):
        print(f"\n❌ 未找到程序一的结果文件: {file_program1}")
        print("请确保桌面上有 mods_with_1.21.1.txt")
        input("\n按回车退出...")
        return
    
    program1_mods = parse_program1_result(file_program1)
    print(f"📋 程序一结果中共有 {len(program1_mods)} 个 mod 名称")
    
    if not program1_mods:
        print("⚠️ 程序一结果文件中没有找到任何 mod 名称")
        input("\n按回车退出...")
        return
    
    # 2. 输入 mod 文件夹路径
    mod_path = input("\n请输入 mod 文件夹路径: ").strip().strip('"')
    if not os.path.isdir(mod_path):
        print("❌ 路径无效，请检查后重试。")
        input("\n按回车退出...")
        return
    
    # 3. 提取文件夹中所有 mod 名
    folder_mods = set()
    file_count = 0
    for file in os.listdir(mod_path):
        if file.lower().endswith('.jar'):
            file_count += 1
            mod_name = extract_mod_name(file)
            if mod_name:
                folder_mods.add(mod_name)
    
    print(f"📁 文件夹中找到 {file_count} 个 .jar 文件")
    print(f"📝 提取到 {len(folder_mods)} 个 mod 名称")
    
    # 4. 对比：程序一中有但文件夹中没有的
    remaining = [mod for mod in program1_mods if mod not in folder_mods]
    
    # 5. 输出结果
    file_output = desktop / "mod_not_in_folder.txt"
    
    try:
        with open(file_output, 'w', encoding='utf-8') as f:
            if remaining:
                f.write("以下 mod 在程序一结果中，但不在当前 mod 文件夹中：\n")
                f.write("=" * 40 + "\n\n")
                for mod in remaining:
                    f.write(mod + '\n')
            else:
                f.write("程序一结果中的所有 mod 都在当前文件夹中找到了对应文件。\n")
        
        print(f"\n✅ 结果已保存到桌面: mod_not_in_folder.txt")
    except Exception as e:
        print(f"❌ 保存文件出错: {e}")
        input("\n按回车退出...")
        return
    
    # 6. 汇总
    print(f"\n📊 统计:")
    print(f"   程序一结果中 mod 总数: {len(program1_mods)}")
    print(f"   文件夹中 mod 数: {len(folder_mods)}")
    print(f"   文件夹中已存在的: {len(program1_mods) - len(remaining)}")
    print(f"   剩余（不在文件夹中）: {len(remaining)}")
    
    if remaining:
        print(f"\n不在文件夹中的 mod：")
        for mod in remaining:
            print(f"   • {mod}")
    else:
        print(f"\n✅ 所有 mod 都已在文件夹中，无需清理。")

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
