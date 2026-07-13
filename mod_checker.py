import os
import re
import urllib.request
import urllib.error
import json
import time
from pathlib import Path
import sys

def extract_mod_name(filename):
    """
    提取 mod 名称：
    1. 去掉 .jar 扩展名
    2. 找到第一个数字的位置
    3. 往前找离它最近的 '-'
    4. 取 '-' 之前的内容
    5. 删除内容中所有的 '-'
    """
    name = filename
    if name.lower().endswith('.jar'):
        name = name[:-4]
    
    # 找到第一个数字的位置
    first_digit_match = re.search(r'\d', name)
    if not first_digit_match:
        # 没有数字，尝试取第一个 '-' 之前的部分
        dash_pos = name.find('-')
        if dash_pos == -1:
            return name.replace('-', '')  # 整个文件名（无扩展名）去掉 '-'
        return name[:dash_pos].replace('-', '')
    
    first_digit_pos = first_digit_match.start()
    
    # 从第一个数字往前找最近的 '-'
    dash_pos = name.rfind('-', 0, first_digit_pos)
    if dash_pos == -1:
        # 数字前没有 '-'，取数字前的全部
        result = name[:first_digit_pos]
    else:
        result = name[:dash_pos]
    
    # 删除所有 '-'
    return result.replace('-', '')

def search_modrinth(mod_name):
    """
    用 Modrinth API 搜索 mod，返回是否有 1.21.1 版本
    返回: (found, has_1211)
        - found=False: 完全没搜到
        - found=True, has_1211=False: 搜到了但没有 1.21.1
        - found=True, has_1211=True: 有 1.21.1 版本
    """
    base_url = "https://api.modrinth.com/v2"
    
    try:
        # 搜索 mod
        search_url = f"{base_url}/search?query={urllib.parse.quote(mod_name)}&limit=3"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'MCModChecker/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            search_data = json.loads(response.read().decode())
        
        hits = search_data.get('hits', [])
        if not hits:
            return (False, False)  # 没搜到
        
        # 取第一个结果的 slug
        slug = hits[0].get('slug')
        if not slug:
            return (False, False)
        
        # 查询该 mod 的版本列表
        versions_url = f"{base_url}/project/{slug}/version"
        req2 = urllib.request.Request(versions_url, headers={'User-Agent': 'MCModChecker/1.0'})
        with urllib.request.urlopen(req2, timeout=10) as response2:
            versions_data = json.loads(response2.read().decode())
        
        # 检查是否有支持 1.21.1 的版本
        for version in versions_data:
            game_versions = version.get('game_versions', [])
            if '1.21.1' in game_versions:
                return (True, True)
        
        return (True, False)  # 搜到了但没有 1.21.1
        
    except urllib.error.HTTPError as e:
        # HTTP 错误（如 404）
        return (False, False)
    except Exception as e:
        # 网络错误等
        print(f"    ⚠️ 搜索出错: {e}")
        return (False, False)

def main():
    print("=" * 50)
    print("MC Mod 版本检查工具 v2.0 (Modrinth 自动检测)")
    print("=" * 50)
    
    # 1. 输入路径
    mod_path = input("\n请输入 mod 文件夹路径: ").strip().strip('"')
    if not os.path.isdir(mod_path):
        print("❌ 路径无效，请检查后重试。")
        input("\n按回车退出...")
        return

    # 2. 提取 mod 名
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

    # 3. 逐个查询 Modrinth
    has_1211 = []
    no_1211 = []
    not_found = []
    
    total = len(mod_names)
    print(f"\n正在通过 Modrinth API 自动检测 {total} 个 mod...")
    print("（每次搜索间隔 0.3 秒，避免请求过快）\n")
    
    for i, mod_name in enumerate(mod_names, 1):
        print(f"[{i}/{total}] 检查: {mod_name} ... ", end='', flush=True)
        
        found, has_version = search_modrinth(mod_name)
        
        if not found:
            print("❓ 未搜索到")
            not_found.append(mod_name)
        elif has_version:
            print("✅ 有 1.21.1 版本")
            has_1211.append(mod_name)
        else:
            print("❌ 无 1.21.1 版本")
            no_1211.append(mod_name)
        
        # 避免请求过快
        if i < total:
            time.sleep(0.3)

    # 4. 生成结果文件到桌面
    desktop = Path.home() / "Desktop"
    output_file = desktop / "mods_with_1.21.1.txt"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入说明
            f.write("MC Mod 1.21.1 版本检查结果\n")
            f.write("=" * 40 + "\n\n")
            
            if has_1211:
                f.write("【已有 1.21.1 版本】\n")
                for mod in has_1211:
                    f.write(f"{mod}\n")
                f.write("\n")
            
            if no_1211:
                f.write("【无 1.21.1 版本】\n")
                for mod in no_1211:
                    f.write(f"{mod}（无1.21.1版本）\n")
                f.write("\n")
            
            if not_found:
                f.write("【未搜索到】\n")
                for mod in not_found:
                    f.write(f"{mod}（未搜索到）\n")
        
        print(f"\n✅ 结果已保存到桌面: mods_with_1.21.1.txt")
    except Exception as e:
        print(f"\n❌ 保存文件出错: {e}")
        # 备用：保存到当前目录
        output_file = Path.cwd() / "mods_with_1.21.1.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            for mod in has_1211:
                f.write(f"{mod}\n")
            for mod in no_1211:
                f.write(f"{mod}（无1.21.1版本）\n")
            for mod in not_found:
                f.write(f"{mod}（未搜索到）\n")
        print(f"✅ 已保存到备用位置: {output_file}")

    # 5. 汇总
    print(f"\n📊 统计:")
    print(f"   ✅ 有 1.21.1 版本: {len(has_1211)} 个")
    print(f"   ❌ 无 1.21.1 版本: {len(no_1211)} 个")
    print(f"   ❓ 未搜索到: {len(not_found)} 个")

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
