import json
import re
import pandas as pd
from datetime import datetime

# 加载JSON数据
with open('无标题.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 设备类型映射字典
device_type_mapping = {
    'archer': '路由器',
    'tl-wr': '路由器',
    'tl-wdr': '路由器',
    'er': '路由器',
    'omada': '路由器',
    're': '无线扩展器',
    'ipc': '摄像头',
    'h100': '智能集线器',
    'p125': '智能插座',
    'kp125': '智能插座',
    'tapo': '智能家居设备',
    'kasa': '智能家居设备',
    'deco': 'Mesh系统',
    'mr200': '移动路由器',
    'sg': '交换机'
}

# 攻击向量映射
vector_mapping = {
    "NETWORK": "网络",
    "ADJACENT_NETWORK": "相邻网络",
    "LOCAL": "本地",
    "PHYSICAL": "物理"
}

# 优化补丁链接提取函数
def extract_patch_links(references):
    """提取TP-Link官方固件下载链接"""
    try:
        ref_data = json.loads(references).get('reference_data', [])
    except:
        return ""
    
    # 收集所有可能的固件链接
    firmware_links = []
    
    for ref in ref_data:
        url = ref.get('url', '')
        name = ref.get('name', '')
        
        # 检查是否是TP-Link官方固件链接
        if ('tp-link.com' in url and 
            ('download' in url or 'firmware' in url or '#Firmware' in url)):
            firmware_links.append(url)
        
        # 检查名称中是否包含固件信息
        elif ('firmware' in name.lower() or 
              'download' in name.lower() or 
              'update' in name.lower()):
            firmware_links.append(url)
    
    # 去重并返回前3个链接
    unique_links = list(set(firmware_links))
    return '; '.join(unique_links[:3])

# 提取函数
def extract_info(record):
    # 设备品牌
    vendor = record.get('vendor', 'tp-link').upper()
    if not vendor:
        vendor = "TP-LINK"
    
    # 设备类型推断
    device_type = "其他"
    product = record.get('product', '').lower()
    for key, dtype in device_type_mapping.items():
        if key in product:
            device_type = dtype
            break
    
    # 产品型号清理
    model = re.sub(r'[\\\(\)\_]firmware|\d+\.\d+', '', product.split(',')[0])
    model = re.sub(r'_+', ' ', model).strip().upper()
    
    # CVE编号
    cve = record.get('cve', '')
    
    # 漏洞描述（优先中文）
    description = record.get('description_main_zh') or record.get('description_main', '')
    
    # 攻击向量
    access_vector = vector_mapping.get(record.get('access_vector', ''), "")
    
    # 厂商补丁链接提取（优化版）
    patch_link = extract_patch_links(record.get('references', ''))
    
    # 受影响版本
    affected_versions = ""
    if 'description_main_zh' in record:
        match = re.search(r'版本(.*?之前)', record['description_main_zh'])
        if match:
            affected_versions = match.group(1)
    
    # 公开日期格式化
    pub_date = record.get('published_date', '')
    if pub_date:
        pub_date = datetime.strptime(pub_date.split('+')[0], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    
    return [
        vendor,
        device_type,
        model,
        cve,
        description,
        access_vector,
        patch_link,
        affected_versions,
        pub_date
    ]

# 处理所有记录 - 只提取2020年及以后的CVE
results = []
for record in data['RECORDS']:
    # 提取CVE年份
    cve = record.get('cve', '')
    if cve:
        try:
            year = int(cve.split('-')[1])  # 格式: CVE-YYYY-XXXXX
            if year >= 2020:  # 只处理2020年及以后的CVE
                results.append(extract_info(record))
        except (IndexError, ValueError):
            # 如果CVE格式不正确，跳过
            continue

# 创建DataFrame
df = pd.DataFrame(results, columns=[
    "设备品牌",
    "设备类型",
    "产品型号",
    "CVE编号",
    "漏洞描述",
    "攻击向量",
    "厂商补丁链接",
    "受影响版本",
    "公开日期"
])

# 保存为Excel
df.to_excel('tplink_vulnerabilities_2020+.xlsx', index=False)
print(f"已生成Excel文件，包含{len(results)}条2020年及以后的CVE记录: tplink_vulnerabilities_2020+.xlsx")