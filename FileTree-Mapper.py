import os
import argparse
from pathlib import Path
import matplotlib.pyplot as plt


def build_tree_and_count(root_dir, report_file):
    """遍历目录结构，写入文本报告，并统计每个文件夹的文件数"""
    root_path = Path(root_dir).resolve()

    if not root_path.exists() or not root_path.is_dir():
        print(f"❌ 错误: 路径 '{root_dir}' 不存在或不是文件夹。")
        return None

    dir_stats = {}  # 用于存储 文件夹路径: 文件数量
    total_files = 0
    total_dirs = 0

    print(f"🔍 正在扫描目录: {root_path} ...")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"📁 核心扫描目录: {root_path}\n")
        f.write("=" * 70 + "\n")

        for dirpath, dirnames, filenames in os.walk(root_path):
            current_path = Path(dirpath)

            # 计算当前深度，用于缩进排版
            if current_path == root_path:
                depth = 0
            else:
                depth = len(current_path.relative_to(root_path).parts)

            indent = "│   " * depth
            folder_name = current_path.name if depth > 0 else root_path.name
            file_count = len(filenames)

            total_dirs += 1
            total_files += file_count

            # 记录用于可视化的数据 (去掉根路径的冗长前缀，保留相对路径)
            rel_name = str(current_path.relative_to(root_path))
            display_name = folder_name if rel_name == "." else rel_name
            dir_stats[display_name] = file_count

            # 写入文件夹信息
            f.write(f"{indent}├── 📂 {folder_name}/  [{file_count} 个文件]\n")

            # 写入文件信息
            sub_indent = "│   " * (depth + 1)
            for file in filenames:
                f.write(f"{sub_indent}├── 📄 {file}\n")

        f.write("=" * 70 + "\n")
        f.write(f"✅ 统计总结: 共计 {total_dirs} 个文件夹, {total_files} 个文件。\n")

    print(f"📄 文本目录树报告已生成: {Path(report_file).resolve()}")
    return dir_stats


def plot_folder_stats(dir_stats, output_img, top_n=15):
    """生成可视化图表：文件数量最多的 Top N 文件夹"""
    if not dir_stats:
        return

    # 过滤掉空文件夹，并按文件数量降序排序
    sorted_dirs = sorted(
        [(k, v) for k, v in dir_stats.items() if v > 0],
        key=lambda item: item[1],
        reverse=True
    )

    # 提取前 N 个
    top_dirs = sorted_dirs[:top_n]
    if not top_dirs:
        print("⚠️ 没有包含文件的文件夹，跳过生成可视化图表。")
        return

    # 为了让柱状图自上而下按降序排列，画图前需要反转列表
    folders = [item[0] for item in top_dirs][::-1]
    counts = [item[1] for item in top_dirs][::-1]

    # 设置 matplotlib 画布
    plt.figure(figsize=(10, 8))
    # 使用系统默认无衬线字体，并解决负号显示问题
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']  # 兼容 Windows 和 Mac 中文
    plt.rcParams['axes.unicode_minus'] = False

    bars = plt.barh(folders, counts, color='#4C72B0', edgecolor='none')

    # 在柱子旁边添加具体数字标签
    for bar in bars:
        plt.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                 f'{int(bar.get_width())}',
                 va='center', ha='left', fontsize=10)

    plt.title(f"📊 文件夹内文件数量分布 (Top {len(folders)})", fontsize=14, pad=20)
    plt.xlabel("文件数量 (个)", fontsize=12)
    plt.ylabel("相对文件夹路径", fontsize=12)

    # 自适应布局并保存
    plt.tight_layout()
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    print(f"📊 数据可视化图表已生成: {Path(output_img).resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="深度扫描目录结构，输出树状文本报告及可视化分布图。")
    parser.add_argument("-d", "--dir", type=str, default=".", help="需要扫描的目标文件夹路径 (默认为当前目录)")
    parser.add_argument("-o", "--out_text", type=str, default="Directory_Tree_Report.txt", help="生成的文本报告文件名")
    parser.add_argument("-p", "--out_plot", type=str, default="Folder_Distribution.png", help="生成的可视化图表文件名")

    args = parser.parse_args()

    # 1. 扫描并写入报告
    stats = build_tree_and_count(args.dir, args.out_text)

    # 2. 生成图表
    if stats:
        plot_folder_stats(stats, args.out_plot)