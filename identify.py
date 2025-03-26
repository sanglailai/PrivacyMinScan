SENSITIVE_KEYWORDS = [
    "name", "email", "phone", "mobile", "birthday", "birth", "gender",
    "card", "ip", "id", "location", "address"
]


def identify_sensitive_fields(schema):
    """
    输入数据库 schema，识别字段名中含有敏感关键词的字段。
    :param schema: dict 形式的 {table_name: [字段列表]}
    :return: list，包含每个敏感字段的表名、字段名、类型、识别理由
    """
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


def generate_minimization_report(sensitive_fields):
    """
    针对识别出的敏感字段，生成合规整改建议。
    :param sensitive_fields: 上一步识别出的敏感字段列表
    :return: list，包含表名、字段、类型、识别理由、建议
    """
    report = []
    for item in sensitive_fields:
        field_name = item['field']

        if "ip" in field_name:
            advice = "建议避免长期存储用户IP，除非业务需要日志追踪"
        elif "credit_card" in field_name:
            advice = "建议使用加密或 token 替代明文存储"
        elif "birthday" in field_name or "gender" in field_name:
            advice = "建议仅在统计需要时保存，默认应省略"
        else:
            advice = "建议评估该字段是否属于业务必要字段"

        report.append({
            "表名": item['table'],
            "字段": item['field'],
            "数据类型": item['type'],
            "识别理由": item['reason'],
            "建议": advice
        })
    return report


import pandas as pd

def save_report(report):
    """
    将最终报告保存为 Excel 文件
    :param report: 包含敏感字段信息和建议的列表
    """
    df = pd.DataFrame(report)
    df.to_excel("minimization_report.xlsx", index=False)
    print("✅ 审计报告已导出为 minimization_report.xlsx")
