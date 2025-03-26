# PrivacyMinScan：自动化数据最小化合规审计器（含GDPR/ISO映射）

## 一、项目背景与意义

在隐私保护日益重要的今天，**如何确保数据库中的敏感字段“必要、合规、最小化”存储**，成为企业和开发者必须面对的挑战。

《GDPR》第5条第1(c)款明确提出了**数据最小化（Data Minimization）原则**：

> 个人数据应是适当、相关且仅限于为处理目的所必需的。
> 

与此同时，国际标准如 **ISO/IEC 27701** 也对 PII（可识别个人信息）的治理提出具体要求。

为此，我开发了 **PrivacyMinScan** ——一个轻量级工具，可自动识别数据库或 API 中的敏感字段，生成合规建议，输出审计报告，**可落实数据最小化要求**。

---

## 二、项目架构与功能设计

### 架构图（本地离线版）

```
+---------------------+          +--------------------------+
|   MySQL 数据库      |  -->     |   Schema 分析模块        |
+---------------------+          +--------------------------+
                                      |
                                      v
                             +----------------------+
                             | 敏感字段识别引擎     |
                             | (正则 + 词库匹配)     |
                             +----------------------+
                                      |
                                      v
                         +---------------------------+
                         | 合规风险评估模块（打分）  |
                         +---------------------------+
                                      |
                                      v
                         +---------------------------+
                         | 最小化建议报告生成模块    |
                         +---------------------------+

```

---

## 三、环境搭建与依赖配置

### 3.1 安装 Python 依赖

```bash
pip install pymysql pandas openpyxl

```


---

### 3.2 配置数据库（MySQL）

### 示例建库 SQL：

```sql
CREATE DATABASE privacy_demo;
USE privacy_demo;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    gender VARCHAR(10),
    birthday DATE,
    credit_card_number VARCHAR(20),
    login_ip VARCHAR(30)
);

```

### 示例插入数据：

```sql
INSERT INTO users (name, email, phone, gender, birthday, credit_card_number, login_ip)
VALUES
('Alice', 'alice@example.com', '1234567890', 'female', '1995-05-10', '4111111111111111', '192.168.1.100'),
('Bob', 'bob@example.com', '0987654321', 'male', '1990-09-20', '5555555555554444', '10.0.0.2');

```

---

## 四、开发步骤详解

### 4.1 数据库 Schema 抽取

```python
# extract_schema.py
import pymysql

def extract_mysql_schema(host, port, user, password, database):
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
    cursor = conn.cursor()

    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]
    schema = {}

    for table in tables:
        cursor.execute(f"DESCRIBE {table}")
        fields = cursor.fetchall()
        schema[table] = [{"Field": f[0], "Type": f[1]} for f in fields]

    conn.close()
    return schema

```

---

### 4.2 敏感字段识别 + 风险建议生成

```python
# identify.py
SENSITIVE_KEYWORDS = [
    "name", "email", "phone", "mobile", "birthday", "birth", "gender",
    "card", "ip", "id", "location", "address"
]

def identify_sensitive_fields(schema):
    results = []
    for table, fields in schema.items():
        for field in fields:
            for keyword in SENSITIVE_KEYWORDS:
                if keyword in field['Field'].lower():
                    results.append({
                        "table": table,
                        "field": field['Field'],
                        "type": field['Type'],
                        "reason": f"字段名包含关键词 `{keyword}`"
                    })
    return results

```

---

### 4.3 合规建议与法规映射

```python
# report.py
import pandas as pd

REGULATION_MAP = {
    "email": "GDPR 5.1(c), ISO 27701 §7.2.1",
    "phone": "GDPR 5.1(c), ISO 27701 §7.2.1",
    "credit_card": "PCI-DSS, ISO 27701 §7.2.1",
    "ip": "GDPR Recital 30, ISO 27701 §7.2.6",
    "birthday": "GDPR 5.1(c), ISO 27701 §7.4.6",
    "gender": "GDPR 5.1(c), ISO 27701 §7.2.1",
    "id": "GDPR 5.1(c), ISO 27701 §7.2.1"
}

def generate_excel_report(sensitive_fields, output_path="minimization_report.xlsx"):
    report_data = []

    for field in sensitive_fields:
        fname = field['field']
        advice = ""
        regulation = ""

        if "ip" in fname:
            advice = "避免长期存储用户 IP，默认应脱敏"
        elif "credit_card" in fname:
            advice = "必须加密或使用 token 替代"
        elif "birthday" in fname or "gender" in fname:
            advice = "仅限于统计分析，默认不应收集"
        else:
            advice = "建议评估字段用途，是否必要采集"

        matched = [v for k, v in REGULATION_MAP.items() if k in fname.lower()]
        regulation = ", ".join(matched) if matched else "可选监管要求"

        report_data.append({
            "表名": field['table'],
            "字段名": field['field'],
            "字段类型": field['type'],
            "识别理由": field['reason'],
            "整改建议": advice,
            "适用法规条款": regulation
        })

    df = pd.DataFrame(report_data)
    df.to_excel(output_path, index=False)
    print(f"✅ 报告生成成功：{output_path}")

```

---

### 4.4 主程序入口：一键执行全流程

```python
# run_analysis.py
from extract_schema import extract_mysql_schema
from identify import identify_sensitive_fields
from report import generate_excel_report

def main():
    print("🔍 PrivacyMinScan - 数据最小化合规审计器 启动中...\n")

    try:
        print("🚀 正在连接数据库并提取结构...")
        schema = extract_mysql_schema(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="your_password",  # 请修改为自己的密码
            database="privacy_demo"
        )

        print("🔎 正在识别敏感字段...")
        sensitive_fields = identify_sensitive_fields(schema)

        if not sensitive_fields:
            print("✅ 未发现明显敏感字段，符合数据最小化要求。")
        else:
            print(f"⚠️ 发现 {len(sensitive_fields)} 个潜在敏感字段，正在生成整改建议...")
            generate_excel_report(sensitive_fields)

    except Exception as e:
        print("❌ 运行失败，错误信息如下：")
        print(str(e))

if __name__ == "__main__":
    main()

```

---

## 五、输出示例（审计报告）

最终生成的 Excel 文件包含如下结构（minimization_report.xlsx）：

| 表名 | 字段名 | 字段类型 | 识别理由 | 整改建议 | 适用法规条款 |
| --- | --- | --- | --- | --- | --- |
| users | email | VARCHAR | 字段名包含关键词 `email` | 建议评估字段用途，是否必要采集 | GDPR 5.1(c), ISO 27701 §7.2.1 |
| users | credit_card_number | VARCHAR | 字段名包含关键词 `card` | 必须加密或使用 token 替代 | PCI-DSS, ISO 27701 §7.2.1 |
| users | login_ip | VARCHAR | 字段名包含关键词 `ip` | 避免长期存储用户 IP，默认应脱敏 | GDPR Recital 30, ISO 27701 §7.2.6 |

---

## 六、合规优势总结

| 合规维度 | 项目支持情况 |
| --- | --- |
| 数据最小化原则（GDPR 5.1(c)） | ✅ 自动识别并评估非必要字段 |
| PII 识别与管理（ISO/IEC 27701） | ✅ 支持 §7.2 和 §7.4 条款映射 |
| 可审计性 | ✅ 输出可归档的审计报告（Excel） |
| 本地执行 | ✅ 不依赖云平台，适合内部审计 |

---
