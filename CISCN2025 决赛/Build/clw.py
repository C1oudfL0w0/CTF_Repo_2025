import json
import csv
import re
from bs4 import BeautifulSoup

def extract_affected_versions(affected_component):
    """从affectedComponent字段中提取受影响版本"""
    if not affected_component:
        return ""
    
    # 尝试按逗号分割，取第二部分作为版本信息
    parts = affected_component.split(',', 1)
    if len(parts) > 1:
        return parts[1].strip()
    
    # 如果没有逗号，直接返回整个字符串
    return affected_component

def extract_cve(ref_link_content):
    """从refLinkContent中提取CVE编号"""
    if not ref_link_content:
        return ""
    
    cve_pattern = r'CVE-\d{4}-\d{4,}'
    matches = re.findall(cve_pattern, ref_link_content)
    return matches[0] if matches else ""

def extract_first_link(html_content):
    """从HTML内容中提取第一个链接"""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    link = soup.find('a')
    return link.get('href') if link else ""

def clean_html(html_content):
    """去除HTML标签并清理文本"""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    # 移除多余的空格和换行
    return ' '.join(text.split())

def determine_brand_type_model(vul_name, affected_component):
    """根据漏洞名称和受影响组件确定品牌、类型和型号"""
    # 默认值
    brand = "未知"
    device_type = "未知"
    model = "未知"
    
    # 尝试从受影响组件中提取主要组件
    primary_component = ""
    if affected_component:
        # 获取第一个组件名称
        if ',' in affected_component:
            primary_component = affected_component.split(',')[0].strip()
        else:
            primary_component = affected_component
    
    # 智能推断设备信息
    # 1. 处理车型相关漏洞
    if "车型" in vul_name or "IVI" in vul_name or "TBOX" in vul_name or "网关" in vul_name:
        brand = "某车型"
        device_type = "车载系统"
        
        if "IVI" in vul_name:
            model = "车载信息娱乐系统(IVI)"
        elif "TBOX" in vul_name:
            model = "远程信息处理单元(TBOX)"
        elif "网关" in vul_name:
            model = "车载网关"
        else:
            model = "车载系统"
    
    # 2. 处理组件相关漏洞
    elif primary_component:
        # 品牌使用组件名称（首字母大写）
        brand = primary_component.capitalize() if primary_component.islower() else primary_component
        
        # 设备类型根据常见组件类型推断
        if "kernel" in primary_component.lower():
            device_type = "操作系统内核"
        elif "adbd" in primary_component.lower():
            device_type = "调试服务"
        elif "sshd" in primary_component.lower():
            device_type = "安全服务"
        elif "vim" in primary_component.lower():
            device_type = "文本编辑器"
        else:
            device_type = "软件组件"
        
        # 产品型号使用组件名称
        model = primary_component
    
    # 3. 尝试从漏洞名称中提取信息
    else:
        # 尝试识别常见设备类型
        if "组件" in vul_name:
            device_type = "软件组件"
        
        # 尝试提取品牌信息
        brand_match = re.search(r'(\w+)\s*(组件|系统|服务|漏洞)', vul_name)
        if brand_match:
            brand = brand_match.group(1)
        
        # 产品型号使用漏洞名称中的关键词
        key_phrases = ["内核", "服务", "系统", "组件"]
        for phrase in key_phrases:
            if phrase in vul_name:
                model = phrase
                break
    
    return brand, device_type, model

# 主处理函数
def json_to_csv(input_file, output_file):
    # 读取JSON数据
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 检查数据是否有效
    if not data.get('success') or 'data' not in data:
        print("无效的JSON格式")
        return
    
    records = data['data'].get('records', [])
    
    # 准备CSV文件和表头
    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = [
            "设备品牌", "设备类型", "产品型号", "CVE编号",
            "漏洞描述", "攻击向量", "厂商补丁链接", "受影响版本", "公开日期"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # 处理每条记录
        for record in records:
            vul_name = record.get('vulName', '')
            affected_component = record.get('affectedComponent', '')
            
            # 确定品牌、类型和型号
            brand, device_type, model = determine_brand_type_model(
                vul_name, affected_component
            )
            
            # 提取关键数据
            row = {
                "设备品牌": brand,
                "设备类型": device_type,
                "产品型号": model,
                "CVE编号": extract_cve(record.get('refLinkContent', '')),
                "漏洞描述": clean_html(record.get('vulDescContent', '')),
                "攻击向量": "待补充",  # JSON中无直接对应字段
                "厂商补丁链接": extract_first_link(record.get('vulPatchContent', '')),
                "受影响版本": extract_affected_versions(affected_component),
                "公开日期": record.get('publishDateStr', '')
            }
            writer.writerow(row)

# 使用示例
if __name__ == "__main__":
    json_to_csv('C:\\Users\\Asus\\Desktop\\build\\clw.json', 'C:\\Users\\Asus\\Desktop\\build\\output.csv')
    print("转换完成！输出文件: output.csv")