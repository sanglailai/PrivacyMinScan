# privacyminscan/report.py

import pandas as pd

# 法规映射表（可按需拓展）
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

        # 映射法规
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
