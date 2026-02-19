# ADB SQLite MCP 服务器

这是一个基于MCP（Model Context Protocol）协议的服务器，专门用于通过ADB连接Android设备并查询SQLite数据库。此服务器提供了一系列工具来方便地查询和操作Android设备上的数据库。

## 环境设置

### 虚拟环境设置

建议使用虚拟环境来管理项目依赖：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 依赖管理

项目依赖已导出到 `requirements.txt` 文件中，可以通过以下命令安装：

```bash
pip install -r requirements.txt
```

## MCP 配置

### 配置文件设置

为了使用MCP协议，您需要创建适当的配置文件。典型的 `.env` 配置文件应包含：

```env
MCP_SERVER_NAME=ADB_SQLite_Server
DEFAULT_DB_PATH=/data/data/com.wzh.ai/databases/hook_logs.db
```

### MCP 客户端配置

如果您使用虚拟环境，请使用虚拟环境中的Python解释器路径：

```json
{
  "mcpServers": {
    "hook-logs-db": {
      "command": "D:\\workspace\\ahook_mcp\\venv\\Scripts\\python.exe",
      "args": [
        "D:\\workspace\\ahook_mcp\\adb_sqlite_mcp.py"
      ]
    }
  }
}
```

我们已为您创建了使用虚拟环境的配置文件：`mcp_config.json`

### 服务器启动

要启动MCP服务器，请运行：

```bash
python adb_sqlite_mcp.py
```

或者使用虚拟环境：

```bash
.\venv\Scripts\Activate.ps1
python adb_sqlite_mcp.py
```

## 功能概述

### 1. execute_sql(sql_query: str, db_path: str = DEFAULT_DB_PATH) -> str
执行任意SQL查询语句并返回JSON结果。

### 2. get_tables(db_path: str = DEFAULT_DB_PATH) -> str
获取数据库中的所有表名。

### 3. get_table_schema(table_name: str, db_path: str = DEFAULT_DB_PATH) -> str
获取指定表的结构（包含字段名和数据类型）。

### 4. search_hook_logs(keyword: str, limit: int = 10, db_path: str = DEFAULT_DB_PATH) -> str
快捷工具：在日志表的关键字段中模糊搜索关键字。

## 技术实现细节

- 使用Base64编码来传输SQL语句，避免Shell引号转义问题
- 通过ADB连接Android设备
- 支持JSON格式的结果返回
- 默认数据库路径：`/data/data/com.wzh.ai/databases/hook_logs.db`

## 使用示例

```python
# 获取所有表
tables = await client.tools.get_tables()

# 获取特定表的结构
schema = await client.tools.get_table_schema("logs")

# 执行自定义SQL查询
result = await client.tools.execute_sql("SELECT * FROM logs LIMIT 5")

# 搜索关键字
search_results = await client.tools.search_hook_logs("password", limit=20)
```

## 实际使用结果

我们已成功调用服务并获得以下结果：

- 发现数据库包含3个表：`android_metadata`, `logs`, `sqlite_sequence`
- `logs` 表是核心日志表，可用于查询hook日志数据
- 服务功能正常，可以进行数据查询操作

### logs表结构详情

通过`get_table_schema`工具获取的详细表结构：

- `_id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `timestamp`: TEXT NOT NULL (时间戳)
- `log_name`: TEXT NOT NULL (日志名称)
- `package_name`: TEXT (包名)
- `app_name`: TEXT (应用名称)
- `key_type`: TEXT (密钥类型)
- `key_string`, `key_hex`, `key_base64`: 各种格式的密钥
- `input_string`, `input_hex`, `input_base64`: 输入数据的各种格式
- `output_string`, `output_hex`, `output_base64`: 输出数据的各种格式
- `stack_trace`: TEXT (堆栈跟踪)
- `iv_string`, `iv_hex`, `iv_base64`: IV向量的各种格式

### 服务验证

- 所有MCP工具功能正常工作
- 数据库连接正常
- 可以成功执行SQL查询
- 返回正确的JSON格式结果

## 注意事项

1. 需要确保Android设备已启用USB调试模式
2. 设备需要有root权限以访问应用数据库
3. 数据库路径可能因应用而异，需要相应调整
4. ADB工具需要正确安装并添加到系统PATH中
5. 建议使用虚拟环境以避免依赖冲突
6. 确保MCP客户端正确配置以连接服务器