import pymysql

def extract_mysql_schema(host, port, user, password, database):
    # 连接数据库
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
    cursor = conn.cursor()

    # 获取所有表名
    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]

    schema = {}

    # 遍历每个表，提取字段结构
    for table in tables:
        cursor.execute(f"DESCRIBE {table}")
        fields = cursor.fetchall()
        schema[table] = [{"Field": f[0], "Type": f[1]} for f in fields]

    # 关闭连接
    conn.close()
    return schema

# 示例调用（可在main.py中调用）
if __name__ == "__main__":
    schema = extract_mysql_schema(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="200492",  # 替换为你的MySQL密码
        database="privacy_demo"  # 示例数据库
    )

    print("数据库结构如下：")
    for table, fields in schema.items():
        print(f"表：{table}")
        for field in fields:
            print(f"  - 字段: {field['Field']}  类型: {field['Type']}")
