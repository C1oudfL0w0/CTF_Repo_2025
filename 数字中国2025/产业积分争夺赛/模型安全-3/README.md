# 蓝色商城

这是一个简洁美观的零售商城网站，包含两个主要页面：商品列表页（首页）和商品详情页。采用蓝色主题设计，给用户带来舒适精致的视觉体验。

## 功能特点

### 首页功能
- 展示商品列表，包含以下信息：
  - 商品ID
  - 商品名称
  - 商品价格
  - 商品销量
- 分页功能，方便浏览更多商品
- 点击商品可跳转至详情页

### 商品详情页功能
- 显示商品详细信息，包括：
  - 商品ID
  - 商品名称
  - 商品价格
  - 商品详细文本描述
  - 月销量
  - 用户评价列表
    - 每条评价包含用户ID、用户名和手机号
    - 显示用户使用的设备信息（User Agent）
    - 评价内容前面显示用户ID，便于识别
- 添加评价功能
  - 用户可提交姓名、手机号和评价内容
  - 系统自动生成唯一的用户ID
  - 系统自动记录用户的设备信息（User Agent）

## 项目结构

### MVC架构
项目采用PHP MVC (Model-View-Controller)架构，目录结构如下：

```
/商城网站根目录
  /config         - 配置文件
    config.php    - 网站和数据库配置
  /controllers    - 控制器文件
    HomeController.php    - 处理首页和分类相关请求
    ProductController.php - 处理商品详情和评价相关请求
  /lib            - 辅助库文件
    Database.php  - 数据库连接类
    Controller.php - 基础控制器类
    Router.php    - URL路由解析类
  /models         - 数据模型
    ProductModel.php - 商品相关数据操作
    CategoryModel.php - 分类相关数据操作
    ReviewModel.php   - 评价相关数据操作
  /public         - 公共资源文件
    /css
      styles.css  - 全局样式表
    /js
      script.js   - 全局JavaScript文件
    /images       - 图片资源
  /views          - 视图模板
    /home
      index.php   - 首页模板
    /product
      detail.php  - 商品详情页模板
    /error
      not_found.php - 404错误页面
    /templates
      header.php  - 页面头部模板
      footer.php  - 页面底部模板
  .htaccess       - URL重写规则
  index.php       - 入口文件
  README.md       - 项目说明文档
```

### 数据库结构
项目使用MySQL数据库，包含以下表：

1. **products** - 商品表
   - id: int (主键)
   - name: varchar - 商品名称
   - price: decimal - 商品价格
   - sales: int - 销量
   - category_id: int - 分类ID
   - description: text - 商品描述

2. **categories** - 分类表
   - id: int (主键)
   - name: varchar - 分类名称
   - code: varchar - 分类代码

3. **reviews** - 评价表
   - id: int (主键)
   - product_id: int - 商品ID
   - user_id: varchar - 用户ID
   - username: varchar - 用户名
   - phone: varchar - 手机号码
   - content: text - 评价内容
   - user_agent: text - 用户设备信息
   - created_at: datetime - 创建时间

## 技术实现
- 前端：HTML、CSS、JavaScript
- 后端：PHP 7.4+
- 数据库：MySQL 5.7+
- 架构：MVC (Model-View-Controller)
- 设计模式：单例模式、工厂模式

## 部署指南

### 环境要求
- PHP 7.4 或更高版本
- MySQL 5.7 或更高版本
- Apache 服务器（开启mod_rewrite模块）或 Nginx

### 安装步骤

1. **克隆或下载项目到服务器**
   ```
   git clone https://github.com/yourusername/blue-mall.git
   ```

2. **创建数据库**
   ```sql
   CREATE DATABASE blue_mall CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **导入数据库结构和示例数据**
   ```
   mysql -u username -p blue_mall < database.sql
   ```

4. **配置网站**
   - 编辑 `config/config.php` 文件，设置数据库连接信息和网站URL
   ```php
   // 数据库配置
   define('DB_HOST', 'localhost');
   define('DB_NAME', 'blue_mall');
   define('DB_USER', 'root');
   define('DB_PASS', 'your_password');
   
   // 网站配置
   define('SITE_URL', 'http://yourdomain.com');
   define('SITE_NAME', '蓝色商城');
   ```

5. **配置Web服务器**
   
   **Apache配置**
   - 确保mod_rewrite模块已启用
   - .htaccess文件已包含在项目中，无需额外配置
   
   **Nginx配置**
   ```
   server {
       listen 80;
       server_name yourdomain.com;
       root /path/to/blue-mall;
       
       location / {
           try_files $uri $uri/ /index.php?url=$uri&$args;
       }
       
       location ~ \.php$ {
           include snippets/fastcgi-php.conf;
           fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
       }
   }
   ```

6. **设置文件权限**
   ```
   chmod -R 755 /path/to/blue-mall
   ```

7. **访问网站**
   打开浏览器，输入配置的网址即可访问商城首页

## 使用说明
1. 首页浏览商品列表
2. 使用底部分页控件浏览更多商品
3. 点击任意商品查看详情
4. 在详情页可查看该商品的完整信息和用户评价
5. 使用评价表单添加新的商品评价

## 设计特点
- 蓝色主题设计，给人清新舒适的视觉体验
- 精心设计的卡片式布局，突显商品信息
- 响应式设计，适应不同设备的屏幕尺寸
- 平滑的过渡动画，增强用户体验
- MVC架构，代码结构清晰，易于维护和扩展

## 未来功能规划
1. 用户注册和登录系统
2. 购物车功能
3. 订单管理系统
4. 商品搜索功能
5. 商品收藏功能
6. 后台管理系统 