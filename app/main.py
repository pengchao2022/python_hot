import os
from pathlib import Path


# 定义文件读取类
class ReadMyFile:

    # 定义方法
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding

    def read_entire_file(self, file_path):
        """读取整个文件内容"""
        try:
            with open(file_path, 'r', encoding=self.encoding) as file:
                return file.read()
            
        except FileNotFoundError:
            return f"错误！文件'{file_path}' 未找到！"
        except PermissionError:
            return f"错误！没有权限读取该文件 '{file_path}'"
        except UnicodeDecodeError:
            return f"错误！文件编码问题，尝试使用其他编码"
        except Exception as e:
            return f"读取文件出错！{e}"
        
    def read_lines(self, file_path):
        """读取文件所有行，返回列表"""
        try:
            with open(file_path, 'r', encoding=self.encoding) as file:
                return [line.strip() for line in file]
        except FileNotFoundError:
            print(f"文件'{file_path} 未找到！")
            return []
        
    def read_large_file(self, file_path, chunk_size=8192):
        """读取大文件，分块处理"""
        try:
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    # 处理每个块
                    yield chunk
        except FileNotFoundError:
            print(f"文件 '{file_path}' 未找到！")

    def read_with_validation(self, file_path):
        """带验证的文件读取"""
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"错误！文件'{file_path}'不存在！"
        
        # 检查是否是文件
        if not os.path.isfile(file_path):
            return f"错误！'{file_path}' 不是文件"
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return "文件为空"
        
        print(f"文件太小：{file_size} 字节")

        # 读取文件
        return self.read_entire_file(file_path)
    

# 使用该类
if __name__ == "__main__":
    reader = ReadMyFile()

    # 读取整个文件
    content = reader.read_entire_file('海阔天空.txt')
    print("文件内容：")
    print(content)

    # 读取不同路径的文件
    content = reader.read_entire_file('../requirements.txt')
    print("文件内容：")
    print(content)

    # 读取所有行
    lines = reader.read_lines('海阔天空.txt')
    print("\n文件行数：", len(lines))

    # 读取大文件
    print("\n大文件分块读取：")
    for i, chunk in enumerate(reader.read_large_file('../100Mb.dat'), 1):
        print(f"块{i}: {len(chunk)}字符")


