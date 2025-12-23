"""
VIP管理系统 - 会员卡密和权益管理
文件名：vip.py

功能说明：
1. 生成会员卡密（像银行发行信用卡）
2. 激活卡密（用户使用卡密开通会员）
3. 检查会员状态（看用户是不是会员）
4. 记录使用次数（用户每生成一次歌词或音乐就记录一次）
"""

# 导入工具包
from flask import request, jsonify
import random
import string
from datetime import datetime, timedelta

# 导入数据库模块 - 修复这里！
try:
    # 方式1：直接导入（从当前目录）
    from database import Database
except ImportError:
    try:
        # 方式2：尝试相对导入
        from .database import Database
    except ImportError:
        # 方式3：创建简单的Database类（仅用于测试）
        class Database:
            def __init__(self):
                print("⚠️  使用测试版Database类")
            
            def get_connection(self):
                # 这里需要实现真正的数据库连接
                # 暂时返回None，让后续代码能运行测试
                return None

# 创建数据库实例
db = Database()

print("✅ VIP管理系统模块加载成功！")

class VIPAPI:
    # 会员权益配置 - 就像菜单一样
    VIP_BENEFITS = {
        1: {  # 体验会员（就像试吃套餐）
            'name': '体验会员',
            'days': 7,          # 有效期7天
            'lyrics': 50,       # 可以生成50次歌词
            'music': 10,        # 可以生成10次音乐
            'price': 0,         # 价格：免费
            'description': '免费体验所有功能'
        },
        2: {  # 月度会员（普通套餐）
            'name': '月度会员',
            'days': 30,         # 有效期30天
            'lyrics': 200,      # 可以生成200次歌词
            'music': 50,        # 可以生成50次音乐
            'price': 29.9,      # 价格：29.9元
            'description': '适合轻度创作者'
        },
        3: {  # 季度会员（豪华套餐）
            'name': '季度会员',
            'days': 90,         # 有效期90天
            'lyrics': 600,      # 可以生成600次歌词
            'music': 150,       # 可以生成150次音乐
            'price': 79.9,      # 价格：79.9元
            'description': '性价比最高的选择'
        },
        4: {  # 年度会员（尊享套餐）
            'name': '年度会员',
            'days': 365,        # 有效期365天
            'lyrics': 2400,     # 可以生成2400次歌词
            'music': 600,       # 可以生成600次音乐
            'price': 299.9,     # 价格：299.9元
            'description': '专业创作者的最佳选择'
        }
    }
    
    print(f"✅ 会员权益表加载完成，共有{len(VIP_BENEFITS)}个等级")

    @staticmethod
    def generate_card_key():
        """
        生成VIP卡密 - 管理员专用
        就像银行发行信用卡一样
        
        输入：会员等级、生成数量
        输出：生成的卡密列表
        
        卡密格式：VIP-XXXX-XXXX-XXXX-XXXX
        例如：VIP-A1B2-C3D4-E5F6-G7H8
        """
        
        # 1. 从请求中获取数据（就像收银员收钱一样）
        data = request.json  # request.json 就是用户发来的数据
        
        # 2. 检查数据是否完整
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供卡密生成信息'
            })
        
        # 3. 获取会员等级（默认是2级，月度会员）
        vip_level = data.get('vip_level', 2)  # 如果没有提供，就用默认值2
        
        # 4. 获取生成数量（默认是1张）
        quantity = data.get('quantity', 1)    # 如果没有提供，就用默认值1
        
        # 5. 验证会员等级是否有效
        if vip_level not in VIPAPI.VIP_BENEFITS:
            return jsonify({
                'success': False,
                'message': f'无效的会员等级：{vip_level}（有效等级：1-4）'
            })
        
        # 6. 获取该等级的权益配置
        benefits = VIPAPI.VIP_BENEFITS[vip_level]
        
        print(f"🎫 开始生成卡密：等级={vip_level}，数量={quantity}")
        print(f"📊 权益配置：天数={benefits['days']}，歌词={benefits['lyrics']}次，音乐={benefits['music']}次")
        
        # 7. 准备一个空列表，存放生成的卡密
        generated_keys = []
        
        # 8. 连接数据库（就像打开银行金库）
        conn = db.get_connection()
        
        try:
            # 9. 创建数据库游标（就像拿一个写字板）
            with conn.cursor() as cursor:
                
                # 10. 循环生成指定数量的卡密
                for i in range(quantity):
                    print(f"🔄 正在生成第 {i+1}/{quantity} 张卡密...")
                    
                    # 11. 生成唯一的卡密（防止重复）
                    while True:
                        # 生成卡密的4个部分
                        segments = []
                        for segment_num in range(4):
                            # 每个部分由4个随机字符组成
                            segment = ''.join(random.choices(
                                string.ascii_uppercase + string.digits,  # 用大写字母和数字
                                k=4  # 每个部分4个字符
                            ))
                            segments.append(segment)
                        
                        # 组合成完整的卡密
                        card_key = 'VIP-' + '-'.join(segments)
                        
                        # 检查卡密是否已存在（就像检查银行卡号是否重复）
                        cursor.execute("SELECT id FROM vip_keys WHERE card_key = %s", (card_key,))
                        if not cursor.fetchone():  # 如果没有找到相同的卡密
                            break  # 跳出循环，使用这个卡密
                        else:
                            print(f"⚠️  卡密重复，重新生成...")
                    
                    print(f"✅ 生成卡密：{card_key}")
                    
                    # 12. 准备卡密信息（就像填写银行卡信息）
                    key_info = {
                        'card_key': card_key,
                        'vip_level': vip_level,
                        'days': benefits['days'],
                        'lyrics_limit': benefits['lyrics'],
                        'music_limit': benefits['music'],
                        'status': '未激活',  # 初始状态
                        'created_at': datetime.now()  # 创建时间
                    }
                    
                    # 13. 保存到数据库
                    cursor.execute("""
                        INSERT INTO vip_keys 
                        (card_key, vip_level, days, lyrics_limit, music_limit, status, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        key_info['card_key'],
                        key_info['vip_level'],
                        key_info['days'],
                        key_info['lyrics_limit'],
                        key_info['music_limit'],
                        key_info['status'],
                        key_info['created_at']
                    ))
                    
                    # 14. 添加到生成的卡密列表
                    generated_keys.append({
                        'key': card_key,
                        'level': benefits['name'],
                        'days': benefits['days'],
                        'lyrics': benefits['lyrics'],
                        'music': benefits['music']
                    })
                
                # 15. 提交到数据库（就像保存文件）
                conn.commit()
                
                print(f"🎉 成功生成 {len(generated_keys)} 张卡密！")
                
                # 16. 返回结果给用户
                return jsonify({
                    'success': True,
                    'message': f'成功生成 {quantity} 张卡密',
                    'keys': generated_keys
                })
                
        except Exception as e:
            # 17. 如果出错了，返回错误信息
            print(f"❌ 生成卡密时出错：{e}")
            return jsonify({
                'success': False,
                'message': f'生成卡密失败：{str(e)}'
            })
        finally:
            # 18. 关闭数据库连接（就像锁上银行金库）
            conn.close()

    @staticmethod
    def activate_card():
        """
        激活VIP卡密 - 用户使用卡密开通会员
        就像用充值卡给游戏账号充值
        
        输入：卡密、用户邮箱、硬件ID
        输出：激活结果和会员信息
        """
        
        # 1. 获取用户提交的数据
        data = request.json
        
        # 2. 提取必要信息
        card_key = data.get('card_key', '').strip()  # 去掉两边的空格
        email = data.get('email', '').strip()
        hardware_id = data.get('hardware_id', '').strip()
        
        print(f"🔑 用户 {email} 尝试激活卡密：{card_key}")
        
        # 3. 检查输入是否完整
        if not card_key or not email:
            return jsonify({
                'success': False,
                'message': '请提供卡密和邮箱'
            })
        
        # 4. 连接数据库
        conn = db.get_connection()
        
        try:
            with conn.cursor() as cursor:
                # 5. 查询卡密信息
                cursor.execute("""
                    SELECT id, vip_level, days, lyrics_limit, music_limit, status, activated_by
                    FROM vip_keys WHERE card_key = %s
                """, (card_key,))
                
                # 6. 获取查询结果
                key_info = cursor.fetchone()
                
                # 7. 检查卡密是否存在
                if not key_info:
                    return jsonify({
                        'success': False,
                        'message': '卡密不存在，请检查输入'
                    })
                
                # 8. 分解卡密信息
                # key_info是一个元组：(id, vip_level, days, lyrics_limit, music_limit, status, activated_by)
                key_id = key_info[0]          # 卡密ID
                vip_level = key_info[1]       # 会员等级
                days = key_info[2]            # 有效天数
                lyrics_limit = key_info[3]    # 歌词次数
                music_limit = key_info[4]     # 音乐次数
                status = key_info[5]          # 状态
                activated_by = key_info[6]    # 激活用户
                
                print(f"📋 卡密信息：等级{vip_level}，天数{days}，歌词{lyrics_limit}次，音乐{music_limit}次，状态{status}")
                
                # 9. 检查卡密状态
                if status != '未激活':
                    if status == '已激活':
                        return jsonify({
                            'success': False,
                            'message': f'卡密已被激活（激活用户：{activated_by}）'
                        })
                    elif status == '已使用':
                        return jsonify({
                            'success': False,
                            'message': '卡密已使用'
                        })
                    elif status == '已冻结':
                        return jsonify({
                            'success': False,
                            'message': '卡密已被冻结'
                        })
                
                # 10. 查询用户是否存在
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if not user:
                    return jsonify({
                        'success': False,
                        'message': '用户不存在，请先注册'
                    })
                
                user_id = user[0]  # 获取用户ID
                
                # 11. 检查用户是否已有会员
                current_time = datetime.now()
                cursor.execute("""
                    SELECT id, lyrics_used, music_used, total_lyrics_limit, total_music_limit, expire_time
                    FROM members WHERE user_id = %s AND expire_time > %s
                """, (user_id, current_time))
                
                existing_member = cursor.fetchone()
                
                # 12. 处理会员信息（区分新会员和老会员）
                if existing_member:
                    # 老会员：叠加次数和延长有效期
                    member_id, lyrics_used, music_used, old_lyrics_limit, old_music_limit, old_expire = existing_member
                    
                    # 处理过期时间，确保是datetime对象
                    if isinstance(old_expire, str):
                        old_expire = datetime.fromisoformat(old_expire)
                    print(f"👤 老会员续费：原有歌词{old_lyrics_limit}次，音乐{old_music_limit}次")
                    print(f"🎁 新卡密提供：歌词+{lyrics_limit}次，音乐+{music_limit}次")
                    
                    # 计算新的过期时间
                    if old_expire > current_time:
                        # 如果还没过期，在原有基础上增加天数
                        new_expire = old_expire + timedelta(days=days)
                        print(f"⏰ 原有效期至：{old_expire}，增加{days}天，新有效期至：{new_expire}")
                    else:
                        # 如果已过期，从现在开始计算
                        new_expire = current_time + timedelta(days=days)
                        print(f"⏰ 原会员已过期，从今天开始计算{days}天，新有效期至：{new_expire}")
                    
                    # 计算新的总次数（原有剩余次数 + 新卡密次数）
                    old_lyrics_remaining = max(0, old_lyrics_limit - lyrics_used)
                    old_music_remaining = max(0, old_music_limit - music_used)
                    
                    new_lyrics_limit = old_lyrics_remaining + lyrics_limit
                    new_music_limit = old_music_remaining + music_limit
                    
                    print(f"🧮 总次数计算：歌词={old_lyrics_remaining}+{lyrics_limit}={new_lyrics_limit}次")
                    print(f"🧮 总次数计算：音乐={old_music_remaining}+{music_limit}={new_music_limit}次")
                    
                    # 更新会员等级（取较高的等级）
                    new_vip_level = max(vip_level, existing_member[0])
                    
                    # 更新会员信息
                    cursor.execute("""
                        UPDATE members SET
                            vip_level = %s,
                            total_lyrics_limit = %s,
                            total_music_limit = %s,
                            expire_time = %s
                        WHERE id = %s
                    """, (new_vip_level, new_lyrics_limit, new_music_limit, new_expire, member_id))
                    
                else:
                    # 新会员：创建新的会员记录
                    new_expire = current_time + timedelta(days=days)
                    
                    print(f"👤 新会员激活：有效期{days}天，至{new_expire}")
                    print(f"🎁 获得次数：歌词{lyrics_limit}次，音乐{music_limit}次")
                    
                    cursor.execute("""
                        INSERT INTO members 
                        (user_id, email, vip_level, total_lyrics_limit, total_music_limit, 
                         lyrics_used, music_used, expire_time, activate_time)
                        VALUES (%s, %s, %s, %s, %s, 0, 0, %s, %s)
                    """, (user_id, email, vip_level, lyrics_limit, music_limit, new_expire, current_time))
                
                # 13. 更新卡密状态
                cursor.execute("""
                    UPDATE vip_keys SET
                        status = '已激活',
                        activated_by = %s,
                        activated_time = %s,
                        expire_time = %s
                    WHERE id = %s
                """, (email, current_time, new_expire, key_id))
                
                # 14. 提交数据库
                conn.commit()
                
                print(f"🎉 卡密激活成功！用户：{email}，有效期至：{new_expire}")
                
                # 15. 返回成功信息
                return jsonify({
                    'success': True,
                    'message': '🎉 激活成功！',
                    'member': {
                        'email': email,
                        'vip_level': vip_level,
                        'vip_name': VIPAPI.VIP_BENEFITS.get(vip_level, {}).get('name', '会员'),
                        'expire_time': new_expire.isoformat(),
                        'lyrics_added': lyrics_limit,
                        'music_added': music_limit,
                        'days_added': days
                    }
                })
                
        except Exception as e:
            print(f"❌ 激活卡密时出错：{e}")
            return jsonify({
                'success': False,
                'message': f'激活失败：{str(e)}'
            })
        finally:
            conn.close()


    @staticmethod
    def check_membership():
        """
        检查会员状态 - 查询用户是否是会员
        """
        
        # 1. 获取用户邮箱
        data = request.json
        email = data.get('email', '').strip()
        
        print(f"🔍 检查用户会员状态：{email}")
        
        if not email:
            return jsonify({
                'success': False,
                'message': '请提供邮箱地址'
            })
        
        # 2. 连接数据库
        conn = db.get_connection()
        
        try:
            with conn.cursor() as cursor:
                # 3. 查询用户ID
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if not user:
                    return jsonify({
                        'success': False,
                        'message': '用户不存在'
                    })
                
                user_id = user[0]
                
                # 4. 查询会员信息 - 修复：查询所有需要的字段
                current_time = datetime.now()
                cursor.execute("""
                    SELECT 
                        m.vip_level,            # 会员等级
                        m.expire_time,          # 过期时间
                        m.total_lyrics_limit,   # 总歌词次数
                        m.lyrics_used,          # 已用歌词次数
                        m.total_music_limit,    # 总音乐次数
                        m.music_used            # 已用音乐次数
                    FROM members m
                    WHERE m.user_id = %s 
                      AND m.expire_time > %s
                    ORDER BY m.expire_time DESC 
                    LIMIT 1
                """, (user_id, current_time))
                
                member = cursor.fetchone()
                
                # 5. 判断是否有有效的会员
                if not member:
                    print(f"❌ 用户 {email} 不是会员或会员已过期")
                    return jsonify({
                        'success': True,
                        'is_member': False,
                        'message': '您不是会员或会员已过期'
                    })
                
                # 6. 分解会员信息 - 注意字段顺序要和SELECT一致
                # SELECT顺序：vip_level, expire_time, total_lyrics_limit, lyrics_used, total_music_limit, music_used
                vip_level = member[0]           # 会员等级
                expire_time = member[1]         # 过期时间（已经是datetime对象）
                total_lyrics_limit = member[2]  # 总歌词次数
                lyrics_used = member[3]         # 已用歌词次数
                total_music_limit = member[4]   # 总音乐次数
                music_used = member[5]          # 已用音乐次数
                
                print(f"📊 查询到的会员数据：")
                print(f"  vip_level: {vip_level} ({type(vip_level)})")
                print(f"  expire_time: {expire_time} ({type(expire_time)})")
                print(f"  total_lyrics_limit: {total_lyrics_limit} ({type(total_lyrics_limit)})")
                print(f"  lyrics_used: {lyrics_used} ({type(lyrics_used)})")
                print(f"  total_music_limit: {total_music_limit} ({type(total_music_limit)})")
                print(f"  music_used: {music_used} ({type(music_used)})")
                
                # 7. 检查会员是否已过期（再次确认）
                if isinstance(expire_time, str):
                    # 如果是字符串，转换为datetime
                    expire_time = datetime.fromisoformat(expire_time.replace(' ', 'T'))
                
                if expire_time < current_time:
                    print(f"⚠️  用户 {email} 的会员已过期")
                    return jsonify({
                        'success': True,
                        'is_member': False,
                        'message': '您的会员已过期'
                    })
                
                # 8. 计算剩余天数
                time_difference = expire_time - current_time
                remaining_seconds = time_difference.total_seconds()
                
                if remaining_seconds > 0:
                    # 计算剩余天数（向上取整）
                    remaining_days = max(1, time_difference.days)
                    # 如果还有小时，也算一天
                    if time_difference.seconds > 0:
                        remaining_days = max(1, time_difference.days + 1)
                else:
                    remaining_days = 0
                
                # 9. 计算剩余次数
                lyrics_remaining = max(0, total_lyrics_limit - lyrics_used)
                music_remaining = max(0, total_music_limit - music_used)
                
                print(f"✅ 用户 {email} 是会员")
                print(f"📊 会员等级：{vip_level}，过期时间：{expire_time}")
                print(f"📊 剩余天数：{remaining_days}")
                print(f"📊 歌词：已用{lyrics_used}/{total_lyrics_limit}，剩余{lyrics_remaining}")
                print(f"📊 音乐：已用{music_used}/{total_music_limit}，剩余{music_remaining}")
                
                # 10. 更新最后检查时间
                cursor.execute("""
                    UPDATE members SET last_check = %s 
                    WHERE user_id = %s
                """, (current_time, user_id))
                conn.commit()
                
                # 11. 返回会员信息
                return jsonify({
                    'success': True,
                    'is_member': True,
                    'member': {
                        'email': email,
                        'vip_level': vip_level,
                        'vip_name': VIPAPI.VIP_BENEFITS.get(vip_level, {}).get('name', '会员'),
                        'expire_time': expire_time.isoformat(),
                        'remaining_days': remaining_days,
                        'lyrics_remaining': lyrics_remaining,
                        'music_remaining': music_remaining,
                        'lyrics_used': lyrics_used,
                        'lyrics_limit': total_lyrics_limit,
                        'music_used': music_used,
                        'music_limit': total_music_limit
                    }
                })
                
        except Exception as e:
            print(f"❌ 检查会员状态时出错：{e}")
            import traceback
            traceback.print_exc()  # 打印详细的错误信息
            return jsonify({
                'success': False,
                'message': f'查询失败：{str(e)}'
            })
        finally:
            conn.close()

    @staticmethod
    def record_usage():
        """
        记录使用次数 - 用户每生成一次歌词或音乐就记录一次
        就像刷卡消费一样，每次使用扣除一次次数
        
        输入：用户邮箱、使用类型（lyrics/music）
        输出：是否成功、剩余次数
        """
        
        # 1. 获取用户数据
        data = request.json
        email = data.get('email', '').strip()
        usage_type = data.get('type', 'lyrics')  # 默认是歌词
        
        print(f"📝 记录使用：用户={email}，类型={usage_type}")
        
        if not email:
            return jsonify({
                'success': False,
                'message': '请提供邮箱地址'
            })
        
        # 2. 验证使用类型
        if usage_type not in ['lyrics', 'music']:
            return jsonify({
                'success': False,
                'message': '使用类型必须是lyrics或music'
            })
        
        # 3. 连接数据库
        conn = db.get_connection()
        
        try:
            with conn.cursor() as cursor:
                # 4. 查询用户和会员信息 - 修复SQL查询字段名
                current_time = datetime.now()
                cursor.execute("""
                    SELECT u.id, 
                           m.id as member_id,
                           m.lyrics_used, m.total_lyrics_limit,  # 修复：改为total_lyrics_limit
                           m.music_used, m.total_music_limit     # 修复：改为total_music_limit
                    FROM users u
                    LEFT JOIN members m ON u.id = m.user_id 
                        AND m.expire_time > %s
                    WHERE u.email = %s
                """, (current_time, email))
                
                result = cursor.fetchone()
                
                if not result:
                    return jsonify({
                        'success': False,
                        'message': '用户不存在'
                    })
                
                # 5. 分解结果 - 修正变量名
                # 注意：这个顺序必须和SQL查询的SELECT字段顺序完全一致！
                # SELECT的顺序是：u.id, m.id, lyrics_used, total_lyrics_limit, music_used, total_music_limit
                user_id, member_id, lyrics_used, total_lyrics_limit, music_used, total_music_limit = result
                
                # 6. 检查是否是会员
                if not member_id:
                    return jsonify({
                        'success': False,
                        'message': '您不是会员，请先激活会员'
                    })
                
                # 7. 根据使用类型进行处理
                if usage_type == 'lyrics':
                    # 检查歌词次数是否用完
                    if lyrics_used >= total_lyrics_limit:
                        return jsonify({
                            'success': False,
                            'message': f'歌词生成次数已用完（{total_lyrics_limit}次）'
                        })
                    
                    # 增加已用次数
                    new_lyrics_used = lyrics_used + 1
                    
                    print(f"📝 歌词使用记录：{lyrics_used} → {new_lyrics_used}（总限制：{total_lyrics_limit}）")
                    
                    # 更新数据库
                    cursor.execute("""
                        UPDATE members SET
                            lyrics_used = %s
                        WHERE id = %s
                    """, (new_lyrics_used, member_id))
                    
                    # 计算剩余次数
                    remaining = total_lyrics_limit - new_lyrics_used
                    
                else:  # usage_type == 'music'
                    # 检查音乐次数是否用完
                    if music_used >= total_music_limit:
                        return jsonify({
                            'success': False,
                            'message': f'音乐生成次数已用完（{total_music_limit}次）'
                        })
                    
                    # 增加已用次数
                    new_music_used = music_used + 1
                    
                    print(f"📝 音乐使用记录：{music_used} → {new_music_used}（总限制：{total_music_limit}）")
                    
                    # 更新数据库
                    cursor.execute("""
                        UPDATE members SET
                            music_used = %s
                        WHERE id = %s
                    """, (new_music_used, member_id))
                    
                    # 计算剩余次数
                    remaining = total_music_limit - new_music_used
                
                # 8. 记录使用日志（可选，用于分析）
                cursor.execute("""
                    INSERT INTO usage_logs 
                    (user_id, email, action_type, action_time)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, email, usage_type, current_time))
                
                # 9. 提交数据库
                conn.commit()
                
                print(f"✅ 使用记录成功！剩余次数：{remaining}")
                
                # 10. 返回结果
                return jsonify({
                    'success': True,
                    'message': '使用记录成功',
                    'remaining': remaining,
                    'usage_type': usage_type
                })
                
        except Exception as e:
            print(f"❌ 记录使用次数时出错：{e}")
            return jsonify({
                'success': False,
                'message': f'记录失败：{str(e)}'
            })
        finally:
            conn.close()
        



if __name__ == "__main__":
    main()













