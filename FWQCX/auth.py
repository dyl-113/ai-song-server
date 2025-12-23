"""
用户认证模块 API 文档

此模块提供用户注册和登录的API接口。

======================= 注册接口 =======================
URL: POST /api/auth/register

请求格式 (JSON):
{
    "email": "123456789@qq.com",    # 必须是QQ邮箱，用户名部分为数字
    "password": "abc123456"          # 至少8位，包含至少1个字母和5个数字
}

成功响应:
{
    "success": true,
    "message": "注册成功！请记下您的验证密钥",
    "verification_key": "A1B2C3",    # 6位验证密钥（大写字母+数字）
    "user_id": 1,
    "email": "123456789@qq.com"
}

失败响应:
{
    "success": false,
    "message": "错误描述信息"
}

======================= 登录接口 =======================
URL: POST /api/auth/login

请求格式 (JSON):
{
    "email": "123456789@qq.com",
    "password": "abc123456",
    "verification_key": "A1B2C3",    # 可选，非注册设备时需要
    "hardware_id": "PC-001-XXXX"     # 可选，设备唯一标识
}

成功响应:
{
    "success": true,
    "message": "登录成功",
    "user": {
        "id": 1,
        "email": "123456789@qq.com",
        "is_member": false
    },
    "member": {                      # 如果有会员信息
        "vip_level": 2,
        "expire_time": "2024-12-31T23:59:59",
        "remaining_days": 30,
        "lyrics_remaining": 195,
        "music_remaining": 48,
        "lyrics_used": 5,
        "lyrics_limit": 200,
        "music_used": 2,
        "music_limit": 50
    }
}

失败响应:
{
    "success": false,
    "message": "错误描述信息"
}

======================= 设备绑定规则 =======================
1. 第一次登录：保存硬件ID，不需要验证密钥
2. 同一设备再次登录：直接通过，不需要验证密钥
3. 不同设备登录：需要提供验证密钥
4. 验证密钥验证成功后：更新硬件ID，下次可直接登录
"""

# auth.py - 用户认证模块
from flask import request, jsonify
import hashlib
import re
import random
import string
import os
import time
from datetime import datetime
from database import Database  # 注意：这里没有点，因为我们在同一个目录

# 创建数据库连接实例
db = Database()

class AuthAPI:
    """用户认证API类 - 处理注册和登录"""
    
    @staticmethod
    def hash_password(password, salt=None):
        """加盐哈希密码"""
        if salt is None:
            salt = os.urandom(16).hex()
        
        # 密码+盐值一起哈希
        hash_obj = hashlib.sha256()
        hash_obj.update(password.encode('utf-8'))
        hash_obj.update(salt.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        
        return password_hash, salt
    
    @staticmethod
    def register():
        """用户注册API"""
        print("\n" + "="*50)
        print("📝 收到注册请求")
        print("="*50)
        
        # 1. 获取用户发送的数据
        try:
            data = request.json
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请求数据为空'
                })
            
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()
            
            print(f"📧 邮箱: {email}")
            print(f"🔑 密码长度: {len(password)}")
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'解析请求数据失败: {str(e)}'
            })
        
        # 2. 验证邮箱格式（必须是QQ邮箱）
        if not re.match(r'^\d+@qq\.com$', email):
            print(f"❌ 邮箱格式错误: {email}")
            return jsonify({
                'success': False,
                'message': '请使用QQ邮箱（格式：数字@qq.com，例如：123456789@qq.com）'
            })
        
        # 3. 验证密码格式
        if len(password) < 8:
            print(f"❌ 密码太短: {len(password)}位")
            return jsonify({
                'success': False,
                'message': '密码长度不能少于8位'
            })
        
        # 检查是否包含字母
        has_letter = any(c.isalpha() for c in password)
        if not has_letter:
            print(f"❌ 密码没有字母")
            return jsonify({
                'success': False,
                'message': '密码必须包含至少1个英文字母'
            })
        
        # 检查是否包含足够的数字
        has_digit = sum(c.isdigit() for c in password)
        if has_digit < 5:
            print(f"❌ 密码数字不足: {has_digit}个")
            return jsonify({
                'success': False,
                'message': '密码必须包含至少5个数字'
            })
        
        # 4. 连接到数据库，检查邮箱是否已注册
        print("🔗 连接到数据库...")
        conn = db.get_connection()
        try:
            with conn.cursor() as cursor:
                # 查询数据库，看看这个邮箱是否已经存在
                print(f"🔍 检查邮箱是否已注册: {email}")
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    print(f"❌ 邮箱已注册: ID={existing_user[0]}")
                    return jsonify({
                        'success': False,
                        'message': '该邮箱已注册'
                    })
                
                print("✅ 邮箱可用")
                
                # 5. 密码加密（加盐哈希）
                print("🔐 加密密码...")
                password_hash, salt = AuthAPI.hash_password(password)
                print(f"   盐值: {salt[:10]}...")
                print(f"   哈希值: {password_hash[:20]}...")
                
                # 6. 生成6位验证密钥
                print("🔑 生成验证密钥...")
                # 使用大写字母和数字组合
                characters = string.ascii_uppercase + string.digits
                verification_key = ''.join(random.choices(characters, k=6))
                
                # 确保至少包含一个字母和一个数字
                if not any(c.isalpha() for c in verification_key):
                    verification_key = verification_key[:5] + 'A'
                if not any(c.isdigit() for c in verification_key):
                    verification_key = verification_key[:5] + '1'
                
                print(f"✅ 验证密钥: {verification_key}")
                
                # 7. 保存用户到数据库
                print("💾 保存用户到数据库...")
                current_time = datetime.now()
                
                cursor.execute("""
                    INSERT INTO users (
                        email, password_hash, salt, 
                        verification_key, created_at
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (email, password_hash, salt, verification_key, current_time))
                
                # 获取刚插入的用户的ID
                user_id = cursor.lastrowid
                
                # 提交事务（保存到数据库）
                conn.commit()
                
                print(f"🎉 用户注册成功: ID={user_id}, 邮箱={email}")
                
                # 8. 记录系统日志
                try:
                    cursor.execute("""
                        INSERT INTO system_logs (
                            level, module, action, 
                            details, created_at
                        ) VALUES (%s, %s, %s, %s, %s)
                    """, ('INFO', 'auth', 'register', 
                          f'用户注册成功: {email}', current_time))
                    conn.commit()
                except Exception as log_error:
                    print(f"⚠️ 记录日志失败（不影响注册）: {log_error}")
                
                # 9. 返回成功信息给客户端
                return jsonify({
                    'success': True,
                    'message': '注册成功！请务必记下验证密钥，后续换设备登录需要它。',
                    'verification_key': verification_key,
                    'user_id': user_id,
                    'email': email,
                    'created_at': current_time.strftime('%Y-%m-%d %H:%M:%S')
                })
                
        except Exception as e:
            print(f"❌ 注册失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return jsonify({
                'success': False,
                'message': f'注册失败: {str(e)}'
            })
        finally:
            # 不管成功还是失败，都要关闭数据库连接
            conn.close()
            print("🔌 数据库连接已关闭")
    
    @staticmethod
    def login():
        """用户登录API"""
        print("\n" + "="*50)
        print("🔐 收到登录请求")
        print("="*50)
        
        # 1. 获取用户发送的数据
        try:
            data = request.json
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请求数据为空'
                })
            
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()
            verification_key = data.get('verification_key', '').strip()
            hardware_id = data.get('hardware_id', '').strip()
            
            print(f"📧 邮箱: {email}")
            print(f"🔑 密码长度: {len(password)}")
            print(f"🔐 验证密钥: {'有' if verification_key else '无'}")
            print(f"💻 硬件ID: {hardware_id[:20] if hardware_id else '无'}")
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'解析请求数据失败: {str(e)}'
            })
        
        # 2. 检查必填字段
        if not email or not password:
            print("❌ 邮箱或密码为空")
            return jsonify({
                'success': False,
                'message': '邮箱和密码不能为空'
            })
        
        # 3. 连接到数据库
        print("🔗 连接到数据库...")
        conn = db.get_connection()
        try:
            with conn.cursor() as cursor:
                # 4. 查询用户信息
                print(f"🔍 查询用户: {email}")
                cursor.execute("""
                    SELECT id, password_hash, salt, verification_key, hardware_id
                    FROM users WHERE email = %s
                """, (email,))
                
                user = cursor.fetchone()
                
                # 5. 检查用户是否存在
                if not user:
                    print(f"❌ 用户不存在: {email}")
                    # 为了防止恶意攻击，这里稍微延迟一下
                    time.sleep(0.5)
                    return jsonify({
                        'success': False,
                        'message': '用户不存在或密码错误'
                    })
                
                # 6. 提取用户信息
                user_id, stored_hash, stored_salt, stored_key, stored_hardware_id = user
                print(f"✅ 找到用户: ID={user_id}")
                print(f"   存储的硬件ID: {stored_hardware_id}")
                
                # 7. 验证密码（使用盐值）
                print("🔐 验证密码...")
                input_hash, _ = AuthAPI.hash_password(password, stored_salt)
                
                if input_hash != stored_hash:
                    print(f"❌ 密码错误")
                    time.sleep(1)  # 增加延迟，防止暴力破解
                    return jsonify({
                        'success': False,
                        'message': '用户不存在或密码错误'
                    })
                
                print("✅ 密码验证通过")
                
                # 8. 检查硬件ID绑定
                current_time = datetime.now()
                
                # 如果数据库中有硬件ID记录
                if stored_hardware_id:
                    print(f"   数据库已有硬件ID: {stored_hardware_id}")
                    
                    # 但用户没有提供硬件ID，或者提供的硬件ID不匹配
                    if not hardware_id or hardware_id != stored_hardware_id:
                        print(f"⚠️ 硬件ID不匹配")
                        print(f"   用户提供的: {hardware_id}")
                        print(f"   数据库存储的: {stored_hardware_id}")
                        
                        # 需要验证密钥
                        if not verification_key:
                            print("❌ 需要验证密钥但未提供")
                            return jsonify({
                                'success': False,
                                'message': '检测到新设备登录，需要验证密钥'
                            })
                        
                        if verification_key != stored_key:
                            print(f"❌ 验证密钥错误")
                            print(f"   用户提供的: {verification_key}")
                            print(f"   正确的: {stored_key}")
                            return jsonify({
                                'success': False,
                                'message': '验证密钥错误'
                            })
                        
                        print("✅ 验证密钥正确")
                        
                        # 更新硬件ID（新设备验证通过）
                        if hardware_id:
                            cursor.execute("""
                                UPDATE users SET hardware_id = %s WHERE id = %s
                            """, (hardware_id, user_id))
                            print(f"💾 更新硬件ID: {hardware_id}")
                else:
                    # 如果数据库中没有硬件ID，说明是第一次登录
                    print("📝 首次登录或未绑定设备")
                    if hardware_id:
                        cursor.execute("""
                            UPDATE users SET hardware_id = %s WHERE id = %s
                        """, (hardware_id, user_id))
                        print(f"💾 保存硬件ID: {hardware_id}")
                
                # 9. 更新最后登录时间
                cursor.execute("""
                    UPDATE users SET last_login = %s WHERE id = %s
                """, (current_time, user_id))
                print(f"🕒 更新最后登录时间: {current_time.strftime('%H:%M:%S')}")
                
                # 10. 获取会员信息（如果有）
                print("👑 查询会员信息...")
                cursor.execute("""
                    SELECT vip_level, expire_time, 
                           total_lyrics_limit, lyrics_used,
                           total_music_limit, music_used
                    FROM members WHERE user_id = %s AND expire_time > %s
                    ORDER BY expire_time DESC LIMIT 1
                """, (user_id, current_time))
                
                member_info = cursor.fetchone()
                
                # 11. 提交所有更改
                conn.commit()
                
                # 12. 记录登录日志
                try:
                    log_details = f"用户登录成功: {email}"
                    if hardware_id:
                        log_details += f", 硬件ID: {hardware_id}"
                    
                    cursor.execute("""
                        INSERT INTO system_logs (
                            level, module, action, 
                            details, created_at
                        ) VALUES (%s, %s, %s, %s, %s)
                    """, ('INFO', 'auth', 'login', log_details, current_time))
                    conn.commit()
                except Exception as log_error:
                    print(f"⚠️ 记录日志失败（不影响登录）: {log_error}")
                
                print(f"🎉 登录成功: ID={user_id}, 是会员={bool(member_info)}")
                
                # 13. 准备返回数据
                result = {
                    'success': True,
                    'message': '登录成功',
                    'user': {
                        'id': user_id,
                        'email': email,
                        'is_member': bool(member_info),
                        'last_login': current_time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
                
                # 14. 如果有会员信息，添加到返回数据中
                if member_info:
                    vip_level, expire_time, lyrics_limit, lyrics_used, music_limit, music_used = member_info
                    
                    # 计算剩余次数
                    lyrics_remaining = max(0, lyrics_limit - lyrics_used)
                    music_remaining = max(0, music_limit - music_used)
                    
                    # 计算剩余天数
                    remaining_seconds = (expire_time - current_time).total_seconds()
                    if remaining_seconds > 0:
                        remaining_days = max(1, (expire_time - current_time).days)
                    else:
                        remaining_days = 0
                    
                    result['member'] = {
                        'vip_level': vip_level,
                        'expire_time': expire_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'remaining_days': remaining_days,
                        'lyrics_remaining': lyrics_remaining,
                        'music_remaining': music_remaining,
                        'lyrics_used': lyrics_used,
                        'lyrics_limit': lyrics_limit,
                        'music_used': music_used,
                        'music_limit': music_limit
                    }
                    
                    print(f"⭐ 会员信息: 等级{vip_level}, 剩余{remaining_days}天")
                    print(f"   歌词剩余: {lyrics_remaining}/{lyrics_limit}")
                    print(f"   音乐剩余: {music_remaining}/{music_limit}")
                
                # 15. 返回结果
                return jsonify(result)
                
        except Exception as e:
            print(f"❌ 登录失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return jsonify({
                'success': False,
                'message': f'登录失败: {str(e)}'
            })
        finally:
            conn.close()
            print("🔌 数据库连接已关闭")