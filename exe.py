import os
import subprocess
import shutil

def build_exe():
    # 项目配置
    main_script = "main.py"  # 入口文件
    output_dir = "dist"      # 输出目录
    icon_path = None         # 可选：图标路径，如"icon.ico"
    
    # 构建PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",         # 生成单个EXE文件
        "--name", "GraphicsDrawingSystem",  # 生成的EXE文件名
        "--distpath", output_dir,
        "--paths", "src",    # 添加src目录到Python路径
        "--hidden-import", "src.ui.main_window",
        "--hidden-import", "src.ui.tool_bar", 
        "--hidden-import", "src.ui.property_panel",
        "--hidden-import", "src.managers.drawing_manager",
        "--hidden-import", "src.managers.file_manager",
        "--hidden-import", "src.shapes.base_shape",
        "--hidden-import", "src.shapes.point",
        "--hidden-import", "src.shapes.line",
        "--hidden-import", "src.shapes.rectangle",
        "--hidden-import", "src.shapes.circle",
        "--hidden-import", "src.shapes.polygon",
        "--hidden-import", "src.shapes.bezier_curve",
        "--hidden-import", "src.shapes.brush_stroke",
        "--add-data", "src;src",  # 将src目录包含到exe中
        "--windowed"         # 隐藏控制台窗口
    ]
    
    # 添加图标（如果有）
    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
    
    # 添加入口文件
    cmd.append(main_script)
    
    # 清理之前的构建文件
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    if os.path.exists("GraphicsDrawingSystem.spec"):
        os.remove("GraphicsDrawingSystem.spec")
    
    print("开始构建EXE文件...")
    print("PyInstaller命令:")
    print(" ".join(cmd))
    print()
    
    # 执行构建命令
    try:
        subprocess.run(cmd, check=True)
        print(f"构建成功！EXE文件在 {os.path.join(output_dir, 'GraphicsDrawingSystem.exe')}")
        
        # 复制示例文件
        if os.path.exists("examples"):
            dest_examples = os.path.join(output_dir, "examples")
            if os.path.exists(dest_examples):
                shutil.rmtree(dest_examples)
            shutil.copytree("examples", dest_examples)
            print("示例文件已复制到输出目录")
            
        # 复制文档
        if os.path.exists("docs"):
            dest_docs = os.path.join(output_dir, "docs")
            if os.path.exists(dest_docs):
                shutil.rmtree(dest_docs)
            shutil.copytree("docs", dest_docs)
            print("文档已复制到输出目录")
            
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")

if __name__ == "__main__":
    build_exe()
