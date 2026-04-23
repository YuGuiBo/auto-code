"""
数据库初始化脚本
运行此脚本创建所有数据库表
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine, Base
from app.models import Project, Process, Artifact

def init_database():
    """初始化数据库，创建所有表"""
    print("开始创建数据库表...")
    
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✓ 数据库表创建成功！")
        
        # 打印创建的表
        print("\n已创建的表:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")
            
    except Exception as e:
        print(f"✗ 创建数据库表失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()

# Made with Bob
