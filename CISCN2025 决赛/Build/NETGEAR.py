import json
import csv
import re
import sys
from datetime import datetime

def extract_affected_versions(cpe_configurations, description):
    """提取受影响版本信息"""
    if cpe_configurations:
        try:
            cpe_data = json.loads(cpe_configurations)
            versions = set()
            
            # 从CPE配置中提取版本
            for node in cpe_data.get('nodes', []):
                for cpe_match in node.get('cpe_match', []):
                    if cpe_match.get('vulnerable', False):
                        uri = cpe_match.get('cpe23Uri', '')
                        # 从URI中提取版本
                        version_match = re.search(r':([\d\.]+)[:*]', uri)
                        if version_match:
                            versions.add(version_match.group(1))
                
                for child in node.get('children', []):
                    for cpe_match in child.get('cpe_match', []):
                        if cpe_match.get('vulnerable', False):
                            uri = cpe_match.get('cpe23Uri', '')
                            # 从URI中提取版本
                            version_match = re.search(r':([\d\.]+)[:*]', uri)
                            if version_match:
                                versions.add(version_match.group(1))
            
            return ", ".join(versions) if versions else ""
        except:
            pass
    
    # 如果CPE配置为空，尝试从描述中提取版本
    version_patterns = [
        r'(\d+\.\d+\.\d+[\w\.]*)',  # 标准版本号 (1.0.1.26)
        r'before (\d+\.\d+\.\d+[\w\.]*)',  # "before X.X.X"格式
        r'up to (\d+\.\d+\.\d+[\w\.]*)'   # "up to X.X.X"格式
    ]
    
    for pattern in version_patterns:
        match = re.search(pattern, description)
        if match:
            return match.group(1)
    
    return "unknown versions"

def extract_patch_links(references):
    """提取厂商补丁链接"""
    if not references:
        return "Not provided"
    
    try:
        ref_data = json.loads(references)
        patch_links = set()
        
        for ref in ref_data.get('reference_data', []):
            url = ref.get('url', '')
            name = ref.get('name', '')
            
            # 优先选择NETGEAR官网链接
            if "netgear.com" in url.lower():
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

def extract_product_models(description):
    """从描述中提取NETGEAR产品型号"""
    models = set()
    
    # 匹配NETGEAR产品型号 (如R6900, DGN1000等)
    netgear_model_pattern = r'\b(?:NETGEAR\s+)?([A-Z]{1,5}[\d\-]{2,10}[A-Z]?)\b'
    matches = re.findall(netgear_model_pattern, description, re.IGNORECASE)
    
    for match in matches:
        # 清理型号中的额外字符
        model = re.sub(r'[^a-zA-Z0-9\-]', '', match)
        if model:
            models.add(model.upper())
    
    # 如果没有找到型号，尝试其他方法
    if not models:
        # 尝试从描述中提取特定短语
        if "router" in description.lower():
            models.add("Router")
        elif "switch" in description.lower():
            models.add("Switch")
        elif "access point" in description.lower():
            models.add("Access Point")
        elif "modem" in description.lower():
            models.add("Modem")
    
    return ", ".join(models) if models else "Unknown"

def determine_device_type(description, product_models):
    """根据描述和产品型号确定设备类型"""
    description_lower = description.lower()
    
    # 根据关键词判断设备类型
    if "router" in description_lower:
        return "Router"
    elif "switch" in description_lower:
        return "Switch"
    elif "access point" in description_lower or "ap" in description_lower:
        return "Access Point"
    elif "modem" in description_lower:
        return "Modem"
    elif "extender" in description_lower:
        return "Wi-Fi Extender"
    elif "storage" in description_lower or "nas" in description_lower:
        return "Network Storage"
    elif "camera" in description_lower:
        return "Security Camera"
    # 根据产品型号前缀判断
    elif any(model.startswith('R') for model in product_models.split(",")):
        return "Router"
    elif any(model.startswith('GS') for model in product_models.split(",")):
        return "Switch"
    elif any(model.startswith('WAX') for model in product_models.split(",")):
        return "Access Point"
    else:
        return "Networking Device"

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
                # 设备品牌默认为NETGEAR
                vendor = "NETGEAR"
                
                # 提取产品型号
                description = record.get('description_main', '')
                product_models = extract_product_models(description)
                
                # 确定设备类型
                device_type = determine_device_type(description, product_models)
                
                # 其他字段
                cve = record.get('cve', '')
                attack_vector = record.get('access_vector', '').replace('_', ' ').title()
                if not attack_vector and "remote" in description.lower():
                    attack_vector = "Network"
                patch_links = extract_patch_links(record.get('references', ''))
                affected_versions = extract_affected_versions(
                    record.get('cpe_configurations', ''), 
                    description
                )
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
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    
    input_json = "C:\\Users\\Asus\\Desktop\\build\\3.json"
    output_csv = "C:\\Users\\Asus\\Desktop\\build\\3.csv"
    
    if not main(input_json, output_csv):
        sys.exit(1)