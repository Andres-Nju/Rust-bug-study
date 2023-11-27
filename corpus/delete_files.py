import os
import shutil

# 替换为您的顶级年份目录的路径
top_dir = "."

# 遍历顶级目录
for year in os.listdir(top_dir):
    year_path = os.path.join(top_dir, year)
    
    # 确保是目录
    if os.path.isdir(year_path):
        for project in os.listdir(year_path):
            project_path = os.path.join(year_path, project)

            # 检查项目目录
            if os.path.isdir(project_path):
                for report in os.listdir(project_path):
                    report_path = os.path.join(project_path, report)

                    # 检查报告目录
                    if os.path.isdir(report_path):
                        for item in os.listdir(report_path):
                            item_path = os.path.join(report_path, item)

                            # 如果是不需要的目录，则删除
                            if os.path.isdir(item_path) and not item.endswith('class.txt'):
                                shutil.rmtree(item_path)
