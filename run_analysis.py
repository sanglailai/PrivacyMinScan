from extract_schema import extract_mysql_schema
from identify import identify_sensitive_fields
from report import generate_excel_report

# 请根据你自己的数据库配置进行修改
host = "localhost"
port = 3306
user = "root"
password = "200492"
database = "privacy_demo"

# 1. 提取数据库结构
schema = extract_mysql_schema(host, port, user, password, database)

# 2. 识别敏感字段
sensitive_fields = identify_sensitive_fields(schema)

# 3. 生成带法规映射的合规审计报告
generate_excel_report(sensitive_fields, output_path="minimization_report_with_regulations.xlsx")
