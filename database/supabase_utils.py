from supabase import create_client

class SupabaseUtils:
    def __init__(self, url: str, key: str):
        self.db = create_client(url, key)
        
    def count_records(self, table: str, filters=None) -> int:
        """统计记录数"""
        query = self.db.table(table).select("id", count="exact")
        
        if filters:
            for field, value in filters.items():
                query = query.eq(field, value)
                
        response = query.execute()
        return response.count
        
    def check_exists(self, table: str, field: str, value: any) -> bool:
        """检查记录是否存在"""
        try:
            response = self.db.table(table)\
                .select("id")\
                .eq(field, value)\
                .execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Check exists error: {str(e)}")
            
    def get_distinct_values(self, table: str, column: str) -> list:
        """获取唯一值列表"""
        try:
            response = self.db.table(table)\
                .select(column)\
                .execute()
            return list(set(item[column] for item in response.data))
        except Exception as e:
            raise Exception(f"Get distinct error: {str(e)}")