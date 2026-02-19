import subprocess
import base64
import json
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP("ADB_SQLite_Server")

# 默认的数据库路径，你可以根据需要修改
DEFAULT_DB_PATH = "/data/data/com.wzh.ai/databases/hook_logs.db"

def execute_adb_sql(sql: str, db_path: str = DEFAULT_DB_PATH) -> str:
    """
    核心执行器：使用 Base64 编码 SQL，彻底避开 Shell 引号转义地狱
    """
    try:
        # 将 SQL 语句转为 Base64
        sql_b64 = base64.b64encode(sql.encode('utf-8')).decode('utf-8')
        
        # 构建 ADB 命令：echo Base64 -> 解码 -> 传给 su -> 传给 sqlite3
        adb_cmd = (
            f'adb shell "echo {sql_b64} | base64 -d | '
            f'su -c \'sqlite3 -json {db_path}\'"'
        )
        
        # 执行命令
        result = subprocess.run(
            adb_cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            return f"Error executing ADB command: {result.stderr}"
            
        # 如果返回为空，说明执行成功但无数据（如 INSERT/UPDATE）
        if not result.stdout.strip():
            return "[]"
            
        return result.stdout.strip()
    except Exception as e:
        return f"Python Exception: {str(e)}"

@mcp.tool()
def execute_sql(sql_query: str, db_path: str = DEFAULT_DB_PATH) -> str:
    """
    执行任意 SQL 查询语句并返回 JSON 结果。
    """
    return execute_adb_sql(sql_query, db_path)

@mcp.tool()
def get_tables(db_path: str = DEFAULT_DB_PATH) -> str:
    """
    获取数据库中的所有表名。
    """
    sql = "SELECT name FROM sqlite_master WHERE type='table';"
    return execute_adb_sql(sql, db_path)

@mcp.tool()
def get_table_schema(table_name: str, db_path: str = DEFAULT_DB_PATH) -> str:
    """
    获取指定表的结构（包含字段名和数据类型）。
    """
    sql = f"PRAGMA table_info('{table_name}');"
    return execute_adb_sql(sql, db_path)

@mcp.tool()
def search_hook_logs(keyword: str, limit: int = 10, db_path: str = DEFAULT_DB_PATH) -> str:
    """
    快捷工具：在日志表的关键字段中模糊搜索关键字。
    """
    # 过滤掉不需要的堆栈信息，保留核心的明文/Hex/Base64
    sql = f"""
    SELECT timestamp, log_name, package_name, 
           key_string, key_hex, key_base64, 
           iv_string, iv_hex, iv_base64, 
           input_string, input_hex, input_base64, 
           output_string, output_hex, output_base64
    FROM logs 
    WHERE (
        key_string LIKE '%{keyword}%' OR key_hex LIKE '%{keyword}%' OR key_base64 LIKE '%{keyword}%' 
        OR iv_string LIKE '%{keyword}%' OR iv_hex LIKE '%{keyword}%' OR iv_base64 LIKE '%{keyword}%' 
        OR input_string LIKE '%{keyword}%' OR input_hex LIKE '%{keyword}%' OR input_base64 LIKE '%{keyword}%' 
        OR output_string LIKE '%{keyword}%' OR output_hex LIKE '%{keyword}%' OR output_base64 LIKE '%{keyword}%'
    )
    ORDER BY timestamp DESC
    LIMIT {limit};
    """
    return execute_adb_sql(sql, db_path)

if __name__ == "__main__":
    # 启动 MCP 服务器
    mcp.run()