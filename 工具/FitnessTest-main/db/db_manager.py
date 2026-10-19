"""
体测数据查询数据库管理模块
专门用于体测标准数据的查询操作
"""

import mysql.connector
from mysql.connector import Error
from typing import List, Dict
import logging

from config.db_config import DB_CONFIG

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.connection = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """
        建立数据库连接
        Returns:
            bool: 连接是否成功
        """
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                self.logger.info("数据库连接成功")
                return True
        except Error as e:
            self.logger.error(f"数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("数据库连接已关闭")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """
        执行查询语句
        Args:
            query: SQL查询语句
            params: 查询参数
        Returns:
            List[Dict]: 查询结果
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            self.logger.error(f"查询执行失败: {e}")
            return []
    
    # 仅保留核心查询功能，删除所有插入、更新、复杂查询方法
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()

# 该模块专用于体测数据查询，不包含测试代码