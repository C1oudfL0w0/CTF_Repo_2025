import json
import csv
import re
import sys
from datetime import datetime

def extract_affected_versions(cpe_configurations):
    if not cpe_configurations:
        return "unknown versions"
    
    try:
        cpe_data = json.loads(cpe_configurations)
        versions = set()
        
        # 提取所有受影响版本
        for node in cpe_data.get('nodes', []):
            # 处理直接匹配项
            for cpe_match in node.get('cpe_match', []):
                if cpe_match.get('vulnerable', False):
                    version_info = extract_version_info(cpe_match)
                    if version_info:
                        versions.add(version_info)
            
            # 处理子节点
            for child in node.get('children', []):
                for cpe_match in child.get('cpe_match', []):
                    if cpe_match.get('vulnerable', False):
                        version_info = extract_version_info(cpe_match)
                        if version_info:
                            versions.add(version_info)
        
        return ", ".join(versions) if versions else "unknown versions"
    except:
        return "unknown versions"

def extract_version_info(cpe_match):
    # 提取版本信息
    uri = cpe_match.get('cpe23Uri', '')
    version = re.search(r':([\d\.]+)[:*]', uri)
    version = version.group(1) if version else ""
    
    # 添加版本范围信息
    if cpe_match.get('versionEndExcluding'):
        return f"{version} (before {cpe_match['versionEndExcluding']})"
    elif cpe_match.get('versionEndIncluding'):
        return f"{version} (up to {cpe_match['versionEndIncluding']})"
    elif cpe_match.get('versionStartIncluding'):
        return f"{version} (from {cpe_match['versionStartIncluding']})"
    elif version:
        return version
    
    return ""

def extract_patch_links(references):
    if not references:
        return "Not provided"
    
    try:
        ref_data = json.loads(references)
        patch_links = set()
        
        for ref in ref_data.get('reference_data', []):
            url = ref.get('url', '')
            name = ref.get('name', '')
            tags = ref.get('tags', [])
            
            # 优先选择ASUS安全公告
            if "asus.com" in url.lower() and "security" in url.lower():
                patch_links.add(url)
            # 其次选择ASUS官网链接
            elif "asus.com" in url.lower():
                patch_links.add(url)
            # 选择包含"advisory"或"patch"的链接
            elif "advisory" in name.lower() or "patch" in name.lower():
                patch_links.add(url)
            # 选择包含"security"的链接
            elif "security" in name.lower():
                patch_links.add(url)
        
        return ' | '.join(patch_links) if patch_links else "Not provided"
    except:
        return "Not provided"

def extract_product_models(record):
    """从描述中提取ASUS产品型号"""
    description = record.get('description_main', '')
    product_field = record.get('product', '')
    
    # 如果product字段有值，优先使用
    if product_field:
        return product_field
    
    # 尝试从描述中提取型号
    models = set()
    
    # 匹配ASUS产品型号 (如RT-AX55, RT-AX58U等)
    asus_model_pattern = r'\b(?:ASUS|ExpertWiFi|ROG|TUF|ZenWiFi|RT|RT-AC|RT-AX|RT-BE)[\w\-]+\b'
    matches = re.findall(asus_model_pattern, description, re.IGNORECASE)
    
    for match in matches:
        # 清理型号中的额外字符
        model = re.sub(r'[^a-zA-Z0-9\-]', '', match)
        if model:
            models.add(model)
    
    # 如果没有找到型号，尝试其他方法
    if not models:
        # 尝试从描述中提取特定短语
        if "router" in description.lower():
            models.add("Router")
        elif "laptop" in description.lower():
            models.add("Laptop")
        elif "motherboard" in description.lower():
            models.add("Motherboard")
        elif "graphics card" in description.lower():
            models.add("Graphics Card")
    
    return ", ".join(models) if models else "Unknown"

def determine_device_type(description, product_models):
    """根据描述和产品型号确定设备类型"""
    description_lower = description.lower()
    
    # 根据关键词判断设备类型
    if "router" in description_lower or any("RT" in model for model in product_models.split(",")):
        return "Router"
    elif "laptop" in description_lower or "notebook" in description_lower:
        return "Laptop"
    elif "motherboard" in description_lower:
        return "Motherboard"
    elif "graphics" in description_lower or "gpu" in description_lower:
        return "Graphics Card"
    elif "monitor" in description_lower:
        return "Monitor"
    elif "phone" in description_lower or "zenfone" in description_lower:
        return "Smartphone"
    elif "tablet" in description_lower or "zenpad" in description_lower:
        return "Tablet"
    elif "bios" in description_lower:
        return "BIOS/Firmware"
    elif "vivo" in description_lower:
        return "Mini PC"
    else:
        return "Unknown"

def format_date(date_str):
    if not date_str:
        return ""
    try:
        # 尝试解析不同格式的日期
        for fmt in ("%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d %H:%M:%S.%f%z", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        # 如果都不匹配，返回原始字符串的日期部分
        return date_str.split(' ')[0]
    except:
        return date_str.split(' ')[0] if date_str else ""

def main(json_file_path, output_csv_path):
    try:
        # 加载JSON数据
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 准备CSV输出
        headers = [
            "设备品牌", "设备类型", "产品型号", "CVE编号", "漏洞描述", 
            "攻击向量", "厂商补丁链接", "受影响版本", "公开日期"
        ]

        with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)
            
            # 处理每条记录
            for record in data.get('RECORDS', []):
                # 设备品牌默认为ASUS
                vendor = "ASUS"
                
                # 提取产品型号
                product_models = extract_product_models(record)
                
                # 确定设备类型
                description = record.get('description_main', '')
                device_type = determine_device_type(description, product_models)
                
                # 其他字段
                cve = record.get('cve', '')
                attack_vector = record.get('access_vector', '').replace('_', ' ').title()
                patch_links = extract_patch_links(record.get('references', ''))
                affected_versions = extract_affected_versions(record.get('cpe_configurations', ''))
                published_date = format_date(record.get('published_date', ''))
                
                # 写入行
                writer.writerow([
                    vendor,
                    device_type,
                    product_models,
                    cve,
                    description,
                    attack_vector,
                    patch_links,
                    affected_versions,
                    published_date
                ])

        print(f"成功创建CSV文件: {output_csv_path}")
        return True
    
    except FileNotFoundError:
        print(f"错误: 找不到JSON文件 {json_file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {str(e)}")
        return False
    except Exception as e:
        print(f"意外错误: {str(e)}")
        return False

if __name__ == "__main__":
    input_json = "C:\\Users\\Asus\\Desktop\\build\\2.json"
    output_csv = "C:\\Users\\Asus\\Desktop\\build\\2.csv"
    
    if not main(input_json, output_csv):
        sys.exit(1)