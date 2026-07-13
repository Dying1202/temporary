import os
import re
import webbrowser
from pathlib import Path
import sys

def extract_mod_name(filename):
    """从文件名中提取 mod 名称（第一个 '-' 之前的部分）"""
    name = filename.replace('.jar', '')
    dash_pos = name.find('-')
    if dash_pos == -1:
        return None
    return name[:dash_pos]

def main():
    print("=" * 50)
    print("MC Mod 版本检查工具 v1.0")
    print("=" * 50)
    
    # 1. 手动输入路径
    mod_path = input("\n请输入 mod 文件夹路径: ").strip().strip('"')
    if not os.path.isdir(mod_path):
        print("❌ 路径无效，请检查后重试。")
        input("\n按回车退出...")
        return

    # 2. 获取所有 .jar 文件并提取 mod 名
    mod_names = set()
    file_count = 0
    for file in os.listdir(mod_path):
        if file.lower().endswith('.jar'):
            file_count += 1
            mod_name = extract_mod_name(file)
            if mod_name:
                mod_names.add(mod_name)

    print(f"\n📁 找到 {file_count} 个 .jar 文件")
    print(f"📝 提取到 {len(mod_names)} 个 mod 名称")

    if not mod_names:
        print("⚠️ 未找到符合格式的 mod 文件。")
        input("\n按回车退出...")
        return

    # 3. 查找已有 1.21.1 版本的 mod
    found_mods = []
    total = len(mod_names)
    
    print("\n" + "=" * 50)
    print("正在逐个检查 mod（需要你人工确认）...")
    print("浏览器会自动打开 CurseForge 和 Modrinth 的搜索页面")
    print("请查看是否有 1.21.1 版本，然后回到这里回答 y/n")
    print("=" * 50)

    for i, mod_name in enumerate(sorted(mod_names), 1):
        print(f"\n[{i}/{total}] Mod: {mod_name}")
        
        # 打开浏览器搜索
        curseforge_url = f"https://www.curseforge.com/minecraft/search?search={mod_name}"
        modrinth_url = f"https://modrinth.com/mods?q={mod_name}"
        
        try:
            webbrowser.open(curseforge_url)
            webbrowser.open(modrinth_url)
        except:
            print("  ⚠️ 无法自动打开浏览器，请手动复制以下链接：")
            print(f"  CurseForge: {curseforge_url}")
            print(f"  Modrinth: {modrinth_url}")

        answer = input("  是否有 1.21.1 版本? (y/n，默认 n): ").strip().lower()
        if answer == 'y':
            found_mods.append(mod_name)
            print(f"  ✓ 已记录")
        else:
            print(f"  ✗ 跳过")

    # 4. 输出结果到桌面
    desktop = Path.home() / "Desktop"
    output_file = desktop / "mods_with_1.21.1.txt"

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for mod in found_mods:
                f.write(mod + '\n')
        print(f"\n✅ 结果已保存到桌面: mods_with_1.21.1.txt")
    except:
        # 如果桌面路径有问题，保存到当前目录
        output_file = Path.cwd() / "mods_with_1.21.1.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            for mod in found_mods:
                f.write(mod + '\n')
        print(f"\n✅ 结果已保存到: {output_file}")

    print(f"📊 共有 {len(found_mods)} 个 mod 有 1.21.1 版本")
    
    # 显示找到的 mod
    if found_mods:
        print("\n找到的 mod：")
        for mod in found_mods:
            print(f"  • {mod}")

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
