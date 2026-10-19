"""
Fitness data query cache manager.
Handles cache initialization, access, and reload.
"""

import logging
from typing import Dict, Optional, Any
from db.db_manager import DatabaseManager
from config.const import PROJECT_MAPPING

logger = logging.getLogger(__name__)


class CacheManager:
    """Cache manager for fitness standard tables."""

    def __init__(self) -> None:
        self._cache_data: Dict[str, Dict[int, Dict[str, Any]]] = {}
        self._initialized = False

    def is_initialized(self) -> bool:
        return self._initialized

    def get_all_cached_data(self) -> Dict[str, Any]:
        return self._cache_data.copy()

    def get_table_cache(self, table_name: str) -> Optional[Dict]:
        return self._cache_data.get(table_name)

    def clear_cache(self) -> None:
        self._cache_data.clear()
        self._initialized = False
        logger.info("Cache cleared")

    def _load_table_to_cache(self, db_manager: DatabaseManager, table_name: str) -> None:
        try:
            check_table_query = f"SHOW TABLES LIKE '{table_name}'"
            table_exists = db_manager.execute_query(check_table_query)
            if not table_exists:
                logger.warning(f"Table {table_name} not found, skipping")
                return

            desc_query = f"DESCRIBE {table_name}"
            columns_result = db_manager.execute_query(desc_query)
            grade_fields = [row['Field'] for row in columns_result if row['Field'].startswith('grade_')]

            select_query = f"SELECT * FROM {table_name}"
            all_data = db_manager.execute_query(select_query)

            table_cache: Dict[int, Dict[str, Any]] = {}
            for row in all_data:
                source_value = int(row['source']) if isinstance(row['source'], str) else row['source']
                table_cache[source_value] = {}
                for field in grade_fields:
                    if field in row:
                        table_cache[source_value][field] = row[field]

            self._cache_data[table_name] = table_cache
            logger.info(f"Cached table {table_name} with {len(all_data)} rows")

        except Exception as e:
            logger.error(f"Failed to load table {table_name} into cache: {e}")

    def initialize_cache(self) -> bool:
        if self._initialized:
            logger.info("Cache already initialized")
            return True

        logger.info("Initializing cache...")
        db_manager = DatabaseManager()

        try:
            if not db_manager.connect():
                raise Exception("Database connection failed")

            all_tables = set()
            for gender_tables in PROJECT_MAPPING.values():
                all_tables.update(gender_tables.values())

            for table_name in all_tables:
                self._load_table_to_cache(db_manager, table_name)

            self._initialized = True
            db_manager.disconnect()
            logger.info(f"Cache initialized, {len(self._cache_data)} tables loaded")
            return True

        except Exception as e:
            logger.error(f"Cache initialization failed: {e}")
            return False

    def get_cached_value(self, table_name: str, grade_field: str, score: int) -> Optional[str]:
        try:
            if not self._initialized:
                logger.warning("Cache not initialized, call initialize_cache() first")
                return None

            if table_name not in self._cache_data:
                logger.warning(f"Table {table_name} not found in cache")
                return None

            table_cache = self._cache_data[table_name]
            if score not in table_cache:
                return None

            grade_data = table_cache[score]
            if grade_field not in grade_data:
                return None

            return grade_data[grade_field]

        except Exception as e:
            logger.error(f"Error reading cache for {table_name}: {e}")
            return None

    def get_cache_statistics(self) -> Dict[str, Any]:
        table_counts = {table_name: len(table_data) for table_name, table_data in self._cache_data.items()}
        return {
            'is_initialized': self._initialized,
            'total_tables': len(self._cache_data),
            'table_details': table_counts,
            'total_records': sum(len(data) for data in self._cache_data.values())
        }

    def reload_cache(self) -> bool:
        self.clear_cache()
        return self.initialize_cache()


CACHE = CacheManager()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Initialize Cache ===")
    success = CACHE.initialize_cache()
    print(f"Result: {'OK' if success else 'FAILED'}")

    print("\n=== Cache Stats ===")
    stats = CACHE.get_cache_statistics()
    print(f"Initialized: {stats['is_initialized']}")
    print(f"Tables: {stats['total_tables']}")
    print(f"Records: {stats['total_records']}")
    print("\nTable details:")
    for table, count in stats['table_details'].items():
        print(f"  {table}: {count} rows")

    print("\n=== Sample Query ===")
    value = CACHE.get_cached_value('man_fei', 'grade_1', 80)
    print(f"man_fei grade_1 score 80: {value}")
