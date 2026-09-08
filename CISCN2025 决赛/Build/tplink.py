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
        versions = []
        
        for node in cpe_data.get('nodes', []):
            for child in node.get('children', []):
                for cpe_match in child.get('cpe_match', []):
                    if cpe_match.get('vulnerable', False):
                        uri = cpe_match.get('cpe23Uri', '')
                        version = extract_version_from_uri(uri)
                        
                        # 处理版本范围
                        if version:
                            versions.append(version)
                        
                        # 添加版本排除/包含信息
                        if cpe_match.get('versionEndExcluding'):
                            versions.append(f"before {cpe_match['versionEndExcluding']}")
                        if cpe_match.get('versionEndIncluding'):
                            versions.append(f"up to {cpe_match['versionEndIncluding']}")
                        if cpe_match.get('versionStartIncluding'):
                            versions.append(f"from {cpe_match['versionStartIncluding']}")
        
        return ", ".join(versions) if versions else "unknown versions"
    except:
        return "unknown versions"

def extract_version_from_uri(uri):
    # 从CPE URI中提取版本信息
    match = re.search(r':([\d\.]+)[:*]', uri)
    return match.group(1) if match else None

def extract_patch_links(references, vendor):
    if not references:
        return "Not provided"
    
    try:
        ref_data = json.loads(references)
        patch_links = set()
        
        for ref in ref_data.get('reference_data', []):
            url = ref.get('url', '')
            name = ref.get('name', '')
            tags = ref.get('tags', [])
            
            # 优先选择厂商链接
            if vendor and vendor.lower() in url.lower():
                patch_links.add(url)
            # 其次选择安全公告链接
            elif any(keyword in name.lower() for keyword in ['advisory', 'patch', 'security']):
                patch_links.add(url)
            # 最后选择任何包含厂商名称的链接
            elif vendor and vendor.lower() in name.lower():
                patch_links.add(url)
        
        return ' | '.join(patch_links) if patch_links else "Not provided"
    except:
        return "Not provided"

def clean_product_name(product):
    if not product:
        return "Unknown"
    
    # 移除转义字符和_firmware后缀
    product = re.sub(r'\\(.)', r'\1', product)  # 处理转义字符
    product = re.sub(r'_firmware$', '', product, flags=re.IGNORECASE)
    product = re.sub(r'firmware:$', '', product, flags=re.IGNORECASE)
    return product.strip()

def determine_device_type(product):
    if not product:
        return "Unknown"
    
    product_lower = product.lower()
    if 'hub' in product_lower:
        return "IoT Hub"
    elif 'router' in product_lower or 'er' in product_lower:
        return "Router"
    elif 'camera' in product_lower:
        return "Camera"
    elif 'switch' in product_lower:
        return "Switch"
    elif 'tapo' in product_lower:
        return "Smart Home Device"
    elif 'omada' in product_lower:
        return "Business Networking"
    else:
        return "Networking Device"

def extract_vendor(record):
    # 优先使用vendor字段
    if record.get('vendor'):
        return record['vendor']
    
    # 尝试从描述中提取
    description = record.get('description_main', '')
    if 'TP-Link' in description:
        return 'tp-link'
    
    # 尝试从产品名称中提取
    product = record.get('product', '')
    if 'tapo' in product.lower() or 'omada' in product.lower():
        return 'tp-link'
    
    return "tp-link"

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
                # 提取和清理数据
                vendor = extract_vendor(record).title()
                product = clean_product_name(record.get('product', ''))
                cve = record.get('cve', '')
                description = record.get('description_main', '')
                attack_vector = record.get('access_vector', '').replace('_', ' ').title()
                patch_links = extract_patch_links(record.get('references', ''), vendor)
                affected_versions = extract_affected_versions(record.get('cpe_configurations', ''))
                published_date = format_date(record.get('published_date', ''))
                
                # 确定设备类型
                device_type = determine_device_type(product)
                
                # 对于没有产品的记录，尝试从描述中推断
                if not product and "TP-Link" in description:
                    product = "Inferred from description"
                
                # 写入行
                writer.writerow([
                    vendor,
                    device_type,
                    product,
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
    
    input_json = "C:\\Users\\Asus\\Desktop\\build\\1.json"
    output_csv = "C:\\Users\\Asus\\Desktop\\build\\1.csv"
    
    if not main(input_json, output_csv):
        sys.exit(1)