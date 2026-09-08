from flask import Flask, request, redirect, jsonify, send_from_directory, render_template_string
import math

app = Flask(__name__)

short_link_storage = {
    "CB6R8pq": "https://www.bilibili.com/video/BV1tT421e7r3/?from_url={from_base}secret/find_my_password&buvid={{buvid}}&from_spmid={{from_spmid}}&is_story_h5=false&p=1&plat_id=116&share_from=ugc&share_medium=android&share_plat=android&share_session_id={{share_session_id}}&share_source=COPY&share_tag=s_i&spmid=united.player-video-detail.0.0&timestamp=1751785740&unique_k=CB6R8pq&up_id=552601798",
    "F996Mn3": "https://www.bilibili.com/video/BV1GJ411x7h7/?from_url=https://www.bilibili.com/&buvid={{buvid}}&from_spmid={{from_spmid}}&is_story_h5=false&p=1&plat_id=116&share_from=ugc&share_medium=android&share_plat=android&share_session_id={{share_session_id}}&share_source=COPY&share_tag=s_i&spmid=united.player-video-detail.0.0&timestamp=1751785740&unique_k=F996Mn3&up_id=552601798"
}

def haversine_distance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(math.radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) 
    r = 6371
    return c * r * 1000


@app.route('/go/<string:short_code>')
def redirect_to_url(short_code):
    destination_url = short_link_storage.get(short_code)
    if destination_url:
        if "{from_base}" in destination_url:
            destination_url = destination_url.replace("{from_base}", request.host_url)
        buvid = "XU729158D436618067C9318686801E96CB45D"
        from_spmid = "tm.recommend.0.0"
        share_session_id = "422b97e2-06ad-4b22-a034-6f23ac237e51"
        destination_url = render_template_string(destination_url, buvid=buvid, from_spmid=from_spmid, share_session_id=share_session_id)
        return redirect(destination_url, code=302)
    else:
        return "目标 URL 未设置。", 404

@app.route('/secret/find_my_password', methods=['GET', 'POST'])
def find_my_password():
    if request.method == 'POST':
        account = request.form.get('account')
        lat_lon_str = request.form.get('lat_lon')
        city = request.form.get('city')
        english_name = request.form.get('english_name')

        correct_lat_lon_str = "114.176051,30.624245"
        correct_city = "福州"
        correct_english_name = "Leland"
        correct_account = "leland@l3hsec.com"

        is_location_correct = False
        distance = -1
        try:
            user_lon, user_lat = map(float, lat_lon_str.split(','))
            correct_lon, correct_lat = map(float, correct_lat_lon_str.split(','))
            distance = haversine_distance(user_lon, user_lat, correct_lon, correct_lat)
            if distance <= 200:
                is_location_correct = True
        except (ValueError, TypeError, AttributeError) as e:
            print(e)

        if (account == correct_account and
            is_location_correct and
            correct_city in city and
            english_name.lower() == correct_english_name.lower()):
            return jsonify(success=True, next="/secret/my_lovely_photos")
        else:
            return jsonify(success=False, message="密保问题答案错误，请重试！"), 400

    return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>找回密码</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 40px; }
        .container { background: #fff; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        label { display: block; margin-top: 10px; }
        input[type="text"] { width: 100%; padding: 8px; margin-top: 5px; border-radius: 4px; border: 1px solid #ddd; box-sizing: border-box; }
        button { background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; margin-top: 20px; }
        button:hover { background-color: #0056b3; }
        #response { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>找回密码</h1>
        <form id="password-form">
            <label for="account">邮箱:</label>
            <input type="text" id="account" name="account" required>

            <label for="lat_lon">我家里店铺的经纬度 (格式: 经度,纬度，接近即可):</label>
            <input type="text" id="lat_lon" name="lat_lon" required>

            <label for="city">老家在哪个城市:</label>
            <input type="text" id="city" name="city" required>

            <label for="english_name">我的英文姓名:</label>
            <input type="text" id="english_name" name="english_name" required>

            <button type="submit">提交</button>
        </form>
        <div id="response"></div>
    </div>

    <script>
        document.getElementById('password-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const responseDiv = document.getElementById('response');

            fetch('/secret/find_my_password', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.next) {
                        window.location.href = data.next;
                    }
                } else {
                    responseDiv.innerHTML = `<p style=\"color: red;\">${data.message || '验证失败'}</p>`;
                }
            })
            .catch(error => {
                responseDiv.innerHTML = `<p style=\"color: red;\">请求失败: ${error}</p>`;
            });
        });
    </script>
</body>
</html>
'''

@app.route('/secret/my_lovely_photos')
def secret_photos():
    photos = [
        'airport.png',
        'head.png',
        'xiaoshuo1.png',
        'xiaoshuo2.png',
        'xiaoshuo3.png',
    ]
    photo_tags = '\n'.join([
        f'<div><img src="/secret/my_lovely_photo?name={p}" style="max-width:300px;"><p>{p}</p></div>' for p in photos
    ])
    return f'''
    <html><head><title>照片墙</title></head><body>
    <h1>我的照片墙</h1>
    {photo_tags}
    </body></html>
    '''

@app.route('/secret/my_lovely_photo')
def get_photo():
    name = request.args.get('name', '')
    name = "dist/images/" + name
    try:
        with open(name, 'rb') as f:
            data = f.read()
        # 简单判断图片类型
        if name.lower().endswith('.png'):
            mimetype = 'image/png'
        elif name.lower().endswith('.jpg') or name.lower().endswith('.jpeg'):
            mimetype = 'image/jpeg'
        elif name.lower().endswith('.gif'):
            mimetype = 'image/gif'
        else:
            mimetype = 'application/octet-stream'
        return data, 200, {'Content-Type': mimetype}
    except Exception as e:
        return f"读取文件失败: {e}", 404

@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_vue_app(path):
    return send_from_directory('dist', path)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=False)