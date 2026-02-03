"""
数据库连接测试脚本

用于测试后端服务与 MySQL 数据库的连接
"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import sys

# 数据库配置
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "123456"
DB_NAME = "gongchibigwork"

def test_database_connection():
    """
    测试数据库连接
    
    @output 测试结果
    """
    print("=" * 60)
    print("数据库连接测试")
    print("=" * 60)
    
    # 构建数据库连接 URL
    database_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(f"\n数据库地址: {DB_HOST}:{DB_PORT}")
    print(f"数据库名称: {DB_NAME}")
    print(f"用户名: {DB_USER}")
    print("-" * 60)
    
    try:
        # 创建数据库引擎
        print("\n正在连接数据库...")
        engine = create_engine(database_url, echo=False)
        
        # 测试连接
        with engine.connect() as conn:
            # 查询数据库版本
            result = conn.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            print(f"✓ 数据库连接成功!")
            print(f"  MySQL 版本: {version}")
            
            # 查询数据库名称
            result = conn.execute(text("SELECT DATABASE()"))
            current_db = result.fetchone()[0]
            print(f"  当前数据库: {current_db}")
            
            # 检查表是否存在
            print("\n检查数据表...")
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            print(f"  现有表: {', '.join(tables) if tables else '无'}")
            
            # 检查 users 表
            if 'users' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.fetchone()[0]
                print(f"  ✓ users 表存在，记录数: {count}")
            else:
                print("  ✗ users 表不存在")
            
            # 检查 documents 表
            if 'documents' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM documents"))
                count = result.fetchone()[0]
                print(f"  ✓ documents 表存在，记录数: {count}")
            else:
                print("  ✗ documents 表不存在")
        
        print("\n" + "=" * 60)
        print("测试通过! 数据库连接正常。")
        print("=" * 60)
        return True
        
    except SQLAlchemyError as e:
        print(f"\n✗ 数据库连接失败!")
        print(f"错误信息: {str(e)}")
        print("\n请检查:")
        print("  1. MySQL 服务是否已启动")
        print("  2. 数据库名称 'gongchibigwork' 是否已创建")
        print("  3. 用户名和密码是否正确")
        print("  4. 是否有权限访问该数据库")
        print("=" * 60)
        return False
    
    except Exception as e:
        print(f"\n✗ 发生未知错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
