# database.py - 支持PostgreSQL版本
import os
import psycopg2
from psycopg2 import pool
import json
from datetime import datetime
import time

class Database:
    def __init__(self):
        # 从环境变量获取数据库连接字符串
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            # 本地测试用
            database_url = "postgresql://localhost/ai_song"
            print("⚠️ 使用本地数据库连接")
        
        self.database_url = database_url
        self.connection_pool = None
        
    def get_connection(self):
        """获取数据库连接"""
        if not self.connection_pool:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20, self.database_url
            )
        
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        """归还数据库连接"""
        if self.connection_pool:
            self.connection_pool.putconn(conn)
    
    def init_database(self):
        """初始化数据库表（第一次运行）"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. 创建用户表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        hardware_id VARCHAR(100),
                        verification_key VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # 创建索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
                
                # 2. 创建VIP卡密表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vip_keys (
                        id SERIAL PRIMARY KEY,
                        card_key VARCHAR(100) UNIQUE NOT NULL,
                        vip_level INT NOT NULL,
                        days INT NOT NULL,
                        lyrics_limit INT NOT NULL,
                        music_limit INT NOT NULL,
                        status VARCHAR(20) DEFAULT '未激活',
                        activated_by VARCHAR(100),
                        activated_hwid VARCHAR(100),
                        activated_time TIMESTAMP,
                        expire_time TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT
                    )
                """)
                
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_vip_keys_card_key ON vip_keys(card_key)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_vip_keys_status ON vip_keys(status)")
                
                # 3. 创建会员表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS members (
                        id SERIAL PRIMARY KEY,
                        user_id INT NOT NULL,
                        email VARCHAR(100) NOT NULL,
                        vip_level INT NOT NULL,
                        total_lyrics_limit INT DEFAULT 0,
                        total_music_limit INT DEFAULT 0,
                        lyrics_used INT DEFAULT 0,
                        music_used INT DEFAULT 0,
                        activate_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expire_time TIMESTAMP NOT NULL,
                        last_check TIMESTAMP,
                        last_used TIMESTAMP,
                        last_activated_key VARCHAR(100)
                    )
                """)
                
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_members_user_id ON members(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_members_email ON members(email)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_members_expire ON members(expire_time)")
                
                # 4. 创建使用记录表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usage_logs (
                        id SERIAL PRIMARY KEY,
                        user_id INT NOT NULL,
                        email VARCHAR(100) NOT NULL,
                        action_type VARCHAR(20) NOT NULL,
                        action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        details TEXT
                    )
                """)
                
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_user_action ON usage_logs(user_id, action_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_time ON usage_logs(action_time)")
                
                conn.commit()
                print("✅ 数据库表创建成功！")
                
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            conn.rollback()
        finally:
            self.return_connection(conn)