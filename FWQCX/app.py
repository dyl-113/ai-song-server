"""
AI歌曲生成器 - 服务器主程序
版本: 2.0
作者：[你的名字]
描述：整合所有API接口的主服务器程序
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from auth import AuthAPI
from vip import VIPAPI
from database import Database
from datetime import datetime
import json

try:
    from config import DATABASE_CONFIG, SERVER_HOST, SERVER_PORT, DEBUG_MODE
    print("✅ 配置文件导入成功")
except ImportError as e:
    print(f"❌ 配置文件导入失败: {e}")
    print("请检查config.py文件是否包含DATABASE_CONFIG等配置项")
    exit(1)

IS_TENCENT_WEB_FUNC = os.environ.get('TENCENTCLOUD_RUNENV') == 'SCF'

# 1. 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

print("="*60)
print("🎵 AI歌曲生成器服务器 v2.0 启动中...")
print("="*60)

# 2. 初始化数据库
try:
    db = Database(DATABASE_CONFIG)
    db.init_database()
    print("✅ 数据库初始化完成")
except Exception as e:
    print(f"❌ 数据库初始化失败: {e}")

# 3. 主页 - 漂亮的Web界面
@app.route('/')
def home():
    """首页 - 显示服务器状态和API文档"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎵 AI歌曲生成器服务器</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 50px;
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                max-width: 800px;
                margin: 0 auto;
            }
            h1 {
                font-size: 3em;
                margin-bottom: 20px;
            }
            .status {
                background: rgba(0, 255, 0, 0.2);
                padding: 10px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .api-list {
                text-align: left;
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                margin-top: 30px;
            }
            .api-item {
                margin: 10px 0;
                padding: 10px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 5px;
            }
            code {
                background: rgba(0, 0, 0, 0.3);
                padding: 2px 5px;
                border-radius: 3px;
            }
            .method {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 4px;
                font-weight: bold;
                margin-right: 10px;
            }
            .method-get { background: #61affe; }
            .method-post { background: #49cc90; }
            .method-put { background: #fca130; }
            .method-delete { background: #f93e3e; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 AI歌曲生成器服务器</h1>
            <div class="status">
                <h2>✅ 服务器运行正常</h2>
                <p>版本: 2.0 | 状态: 在线</p>
                <p>启动时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            </div>
            
            <div class="api-list">
                <h3>📡 可用API接口:</h3>
                
                <div class="api-item">
                    <strong>🔐 用户认证</strong><br>
                    <span class="method method-post">POST</span> <code>/api/auth/register</code> - 用户注册<br>
                    <span class="method method-post">POST</span> <code>/api/auth/login</code> - 用户登录
                </div>
                
                <div class="api-item">
                    <strong>👑 VIP管理</strong><br>
                    <span class="method method-post">POST</span> <code>/api/vip/generate</code> - 生成卡密（管理员）<br>
                    <span class="method method-post">POST</span> <code>/api/vip/activate</code> - 激活VIP卡密<br>
                    <span class="method method-post">POST</span> <code>/api/vip/check</code> - 检查会员状态<br>
                    <span class="method method-post">POST</span> <code>/api/vip/record</code> - 记录使用次数
                </div>
                
                <div class="api-item">
                    <strong>🔧 系统功能</strong><br>
                    <span class="method method-get">GET</span> <code>/api/test</code> - 测试接口<br>
                    <span class="method method-get">GET</span> <code>/api/status</code> - 服务器状态
                </div>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;">
                <h3>📚 快速测试</h3>
                <p>使用以下命令测试API：</p>
                <code>curl -X GET http://localhost:5000/api/test</code><br>
                <code>curl -X POST http://localhost:5000/api/auth/register -H "Content-Type: application/json" -d '{"email":"test@qq.com","password":"12345678a"}'</code>
            </div>
            
            <p style="margin-top: 30px; opacity: 0.8;">
                🚀 服务已启动，等待客户端连接...
            </p>
        </div>
    </body>
    </html>
    """

# 4. 🔐 用户认证API
@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    print("\n" + "="*40)
    print("🌐 收到注册API请求")
    print("="*40)
    return AuthAPI.register()

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    print("\n" + "="*40)
    print("🌐 收到登录API请求")
    print("="*40)
    return AuthAPI.login()

# 5. 👑 VIP管理API
@app.route('/api/vip/generate', methods=['POST'])
def generate_key():
    """生成VIP卡密（管理员使用）"""
    print("\n" + "="*40)
    print("🔑 收到生成卡密请求")
    print("="*40)
    return VIPAPI.generate_card_key()

@app.route('/api/vip/activate', methods=['POST'])
def activate_key():
    """激活VIP卡密"""
    print("\n" + "="*40)
    print("🎫 收到激活卡密请求")
    print("="*40)
    return VIPAPI.activate_card()

@app.route('/api/vip/check', methods=['POST'])
def check_vip():
    """检查会员状态"""
    print("\n" + "="*40)
    print("👑 收到检查会员状态请求")
    print("="*40)
    return VIPAPI.check_membership()

@app.route('/api/vip/record', methods=['POST'])
def record_usage():
    """记录使用次数"""
    print("\n" + "="*40)
    print("📊 收到记录使用次数请求")
    print("="*40)
    return VIPAPI.record_usage()

# 6. 🔧 系统API
@app.route('/api/test', methods=['GET'])
def test_api():
    """测试接口 - 检查服务器是否正常"""
    return jsonify({
        'status': 'success',
        'message': '服务器运行正常',
        'version': '2.0',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'endpoints': [
            '/api/auth/register',
            '/api/auth/login',
            '/api/vip/generate',
            '/api/vip/activate',
            '/api/vip/check',
            '/api/vip/record'
        ]
    })

@app.route('/api/status', methods=['GET'])
def status_api():
    """服务器状态 - 显示详细系统信息"""
    db = Database(DATABASE_CONFIG)
    
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            # 获取用户数量
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            # 获取会员数量
            cursor.execute("SELECT COUNT(*) FROM members")
            member_count = cursor.fetchone()[0]
            
            # 获取VIP卡密数量
            cursor.execute("SELECT COUNT(*) FROM vip_keys")
            vip_count = cursor.fetchone()[0]
            
            # 获取各状态卡密数量
            cursor.execute("SELECT status, COUNT(*) FROM vip_keys GROUP BY status")
            vip_status = dict(cursor.fetchall())
            
        conn.close()
        
        return jsonify({
            'status': 'online',
            'version': '2.0',
            'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'database': {
                'users': user_count,
                'members': member_count,
                'total_vip_keys': vip_count,
                'vip_by_status': vip_status
            },
            'uptime': '刚刚启动',
            'memory_usage': 'N/A',
            'api_count': 8
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

# 7. 🔍 数据库检查API（可选）
@app.route('/api/db/check', methods=['GET'])
def db_check():
    """检查数据库连接和表结构"""
    db = Database(DATABASE_CONFIG)
    
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            # 获取所有表
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            # 获取表结构
            table_info = {}
            for table in tables:
                cursor.execute(f"DESCRIBE {table}")
                columns = []
                for col in cursor.fetchall():
                    columns.append({
                        'name': col[0],
                        'type': col[1],
                        'null': col[2],
                        'key': col[3],
                        'default': col[4],
                        'extra': col[5]
                    })
                table_info[table] = columns
            
            # 获取表行数
            row_counts = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_counts[table] = cursor.fetchone()[0]
                
        conn.close()
        
        return jsonify({
            'status': 'success',
            'tables': tables,
            'table_info': table_info,
            'row_counts': row_counts,
            'database': DATABASE_CONFIG['database']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

# 8. 🚨 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'API接口不存在',
        'path': request.path
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'status': 'error',
        'message': '不支持的请求方法',
        'allowed_methods': error.description.get('valid_methods', [])
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': '服务器内部错误',
        'error': str(error)
    }), 500

# 新增用于云函数入口的代码
import os
def main_handler(event, context):
    return app(event, context)

# 9. 🚀 启动服务器
if __name__ == '__main__':
    # 显示启动信息
    print("\n" + "="*60)
    print("🚀 启动服务器...")
    
    if IS_TENCENT_WEB_FUNC:
        # 云端Web函数模式
        print("🌥️  运行环境: 腾讯云Web函数")
        print(f"📡 监听端口: {SERVER_PORT}")
        # 腾讯云Web函数要求必须监听9000端口
        app.run(host='0.0.0.0', port=9000, debug=False)
    else:
        # 本地开发模式
        print("💻 运行环境: 本地开发")
        print(f"🌐 本地访问: http://localhost:{SERVER_PORT}")
        print(f"📡 API地址: http://localhost:{SERVER_PORT}/api/")
        print(f"📚 文档: http://localhost:{SERVER_PORT}/")
        print("="*60 + "\n")
        
        # 显示API列表
        print("📋 可用API接口列表:")
        print("  🔐 用户认证:")
        print("    POST /api/auth/register - 用户注册")
        print("    POST /api/auth/login   - 用户登录")
        print("  👑 VIP管理:")
        print("    POST /api/vip/generate - 生成卡密（管理员）")
        print("    POST /api/vip/activate - 激活VIP卡密")
        print("    POST /api/vip/check    - 检查会员状态")
        print("    POST /api/vip/record   - 记录使用次数")
        print("  🔧 系统功能:")
        print("    GET  /api/test         - 测试接口")
        print("    GET  /api/status       - 服务器状态")
        print("    GET  /api/db/check     - 数据库检查")
        print("\n" + "="*60)
        
        # 启动Flask应用（本地用你原来的配置）
        app.run(
            host=SERVER_HOST,
            port=SERVER_PORT,
            debug=DEBUG_MODE,
            threaded=True
        )