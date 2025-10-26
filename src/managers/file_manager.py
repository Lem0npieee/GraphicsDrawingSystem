"""
文件管理器 - 负责文件的保存和加载
"""
import json
import os
from typing import Dict, Any, List


class FileManager:
    """文件管理器类"""
    
    def __init__(self):
        self.current_file = None
        self.file_filters = [
            ("项目文件", "*.json"),
            ("所有文件", "*.*")
        ]
        self.image_filters = [
            ("PNG文件", "*.png"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("BMP文件", "*.bmp"),
            ("所有图片", "*.png *.jpg *.jpeg *.bmp"),
            ("所有文件", "*.*")
        ]
        
    def save_project(self, shapes: List[Dict[str, Any]], filename: str) -> bool:
        """保存项目文件"""
        try:
            data = {
                'version': '1.0',
                'metadata': {
                    'created_by': '2D图形绘制系统',
                    'shape_count': len(shapes)
                },
                'shapes': shapes
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.current_file = filename
            return True
            
        except Exception as e:
            print(f"保存文件失败: {e}")
            return False
            
    def load_project(self, filename: str) -> List[Dict[str, Any]]:
        """加载项目文件"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.current_file = filename
            return data.get('shapes', [])
            
        except Exception as e:
            print(f"加载文件失败: {e}")
            return []
            
    def get_current_file(self) -> str:
        """获取当前文件路径"""
        return self.current_file
        
    def set_current_file(self, filename: str):
        """设置当前文件路径"""
        self.current_file = filename
        
    def is_file_modified(self) -> bool:
        """检查文件是否被修改"""
        # 这里可以添加文件修改检测逻辑
        return False
        
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """获取文件信息"""
        if not os.path.exists(filename):
            return {}
            
        stat = os.stat(filename)
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'created': stat.st_ctime
        }