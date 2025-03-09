from supabase import create_client
from database.table_manager import TableManager
from database.supabase_utils import SupabaseUtils
from typing import Dict, List
from loguru import logger

'''
ltd_infos:
{
    'ltd_name': 'so',
    'last_check_domain': 'yhc',
    'update_at': ''
}

so:
{
    'name': 'yhc.so'
}
'''
class SupabaseCRUD:
    def __init__(self, url: str, key: str):
        self.db = create_client(url, key)
        self.table_manager = TableManager(url, key)
        self.util = SupabaseUtils(url, key)

    def upsert_one(self, table: str, record: Dict, conflict_col: str) -> Dict:
        """插入或更新单条记录"""
        try:
            response = self.db.table(table).upsert(record, on_conflict=conflict_col).execute()
            return {"status": "success", "data": response.data[0] if response.data else None}
        except Exception as e:
            logger.info(f"error: {str(e)}")
            return {"status": "error", "message": str(e)}

    def bulk_upsert(self, table: str, records: List[Dict], conflict_col: str) -> Dict:
        """批量插入记录，忽略冲突"""
        try:
            response = self.db.table(table).upsert(records, on_conflict=conflict_col).execute()
            return {"status": "success", "data": response.data}
        except Exception as e:
            logger.info(f"bulk_upsert error: {str(e)}")
            return {"status": "error", "message": str(e)}

