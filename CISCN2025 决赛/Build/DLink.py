import json
import csv
import re
import sys
from datetime import datetime

def extract_affected_versions(cpe_configurations, description):
    """提取受影响版本信息"""
    versions = set()
    
    # 如果CPE配置存在，优先从中提取版本
    if cpe_configurations:
        try:
            cpe_data = json.loads(cpe_configurations)
            for node in cpe_data.get('nodes', []):
                for cpe_match in node.get('cpe_match', []):
                    if cpe_match.get('vulnerable', False):
                        uri = cpe_match.get('cpe23Uri', '')
                        # 从URI中提取版本
                        version_match = re.search(r':([\d\w\.\-]+)[:*]', uri)
                        if version_match:
                            versions.add(version_match.group(1))
                
                for child in node.get('children', []):
                    for cpe_match in child.get('cpe_match', []):
                        if cpe_match.get('vulnerable', False):
                            uri = cpe_match.get('cpe23Uri', '')
                            # 从URI中提取版本
                            version_match = re.search(r':([\d\w\.\-]+)[:*]', uri)
                            if version_match:
                                versions.add(version_match.group(1))
        except:
            pass
    
    # 如果CPE配置为空或未提取到版本，尝试从描述中提取版本
    if not versions:
        version_patterns = [
            r'(\d+\.\d+\.\d+[\w\.\-]*)',  # 标准版本号 (1.06B01)
            r'(\d+\.\d+[\w\.\-]*)',       # 简写版本号 (1.10)
            r'version\s*(\d+\.\d+\.\d+[\w\.\-]*)',  # "version X.X.X"格式
            r'before\s*(\d+\.\d+\.\d+[\w\.\-]*)',   # "before X.X.X"格式
            r'up\s*to\s*(\d+\.\d+\.\d+[\w\.\-]*)'   # "up to X.X.X"格式
        ]
        
        for pattern in version_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                versions.add(match)
    
    return ", ".join(versions) if versions else "unknown versions"

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
            tags = ref.get('tags', [])
            
            # 优先选择D-Link官网链接
            if "dlink.com" in url.lower() or "d-link.com" in url.lower():
                patch_links.add(url)
            # 选择包含"advisory"、"patch"或"support"的链接
            elif "advisory" in name.lower() or "patch" in name.lower() or "support" in name.lower():
                patch_links.add(url)
            # 选择包含"security"的链接
            elif "security" in name.lower():
                patch_links.add(url)
            # 选择厂商公告链接
            elif "vendor advisory" in " ".join(tags).lower():
                patch_links.add(url)
        
        return ' | '.join(patch_links) if patch_links else "Not provided"
    except:
        return "Not provided"

def extract_product_models(description, product_field):
    """从描述和product字段中提取D-Link产品型号"""
    models = set()
    
    # 首先检查product字段
    if product_field:
        # 处理多个产品用逗号分隔的情况
        for product in product_field.split(','):
            # 清理产品名称中的_firmware后缀
            product = re.sub(r'_firmware$', '', product, flags=re.IGNORECASE)
            models.add(product.strip().upper())
    
    # 如果product字段没有提供足够信息，从描述中提取
    if not models:
        # 匹配D-Link产品型号 (如DIR-859, DNS-320等)
        dlink_model_pattern = r'\b(?:D-Link\s+)?([A-Z]{2,4}[\-\_][A-Z\d]{2,5}[A-Z]?)\b'
        matches = re.findall(dlink_model_pattern, description, re.IGNORECASE)
        
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
        elif "nas" in description.lower() or "storage" in description.lower():
            models.add("NAS")
        elif "camera" in description.lower():
            models.add("Camera")
    
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
    elif "nas" in description_lower or "storage" in description_lower:
        return "Network Storage"
    elif "camera" in description_lower:
        return "Security Camera"
    elif "modem" in description_lower:
        return "Modem"
    elif "extender" in description_lower:
        return "Wi-Fi Extender"
    # 根据产品型号前缀判断
    elif any(model.startswith('DIR-') for model in product_models.split(",")):
        return "Router"
    elif any(model.startswith('DGS-') for model in product_models.split(",")):
        return "Switch"
    elif any(model.startswith('DAP-') for model in product_models.split(",")):
        return "Access Point"
    elif any(model.startswith('DNS-') for model in product_models.split(",")):
        return "Network Storage"
    elif any(model.startswith('DCS-') for model in product_models.split(",")):
        return "Security Camera"
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
                # 设备品牌默认为D-Link
                vendor = "D-Link"
                
                # 提取产品型号
                description = record.get('description_main', '')
                product_field = record.get('product', '')
                product_models = extract_product_models(description, product_field)
                
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
    input_json = "C:\\Users\\Asus\\Desktop\\build\\4.json"
    output_csv = "C:\\Users\\Asus\\Desktop\\build\\4.csv"
    
    if not main(input_json, output_csv):
        sys.exit(1)