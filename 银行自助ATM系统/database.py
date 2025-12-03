import mysql.connector
from mysql.connector import Error
import hashlib
import secrets
import string


class Database:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'Hellokity@20222022',
            'port': 3306
        }
        self.connection = None
        self.database_name = 'bank_db'
        self.connect_and_setup()

    def connect_and_setup(self):
        """连接数据库并自动创建数据库和表"""
        try:
            # 首先连接到MySql服务器(不指定数据库)
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print("成功连接到mysql服务器")

                # 创建数据库
                self.create_database()

                # 切换到新数据库
                self.connection.database = self.database_name

                # 创建所有表
                self.create_tables()

                # 插入示例数据
                self.insert_sample_data()

        except Error as e:
            print(f"数据库连接/设置错误:{e}")
            raise

    def create_database(self):
        """创建数据库"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database_name}")
            print(f"数据库 '{self.database_name}' 已就绪")
            cursor.close()

        except Error as e:
            print(f"创建数据库错误:{e}")

    
    def create_tables(self):
        """创建所有需要的表"""
        try:
            cursor = self.connection.cursor()

            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
             """)
            print("用户表已就绪")

            # 创建账户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    account_number VARCHAR(20) UNIQUE NOT NULL,
                    balance DECIMAL(15,2) DEFAULT 0.00,
                    create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE 
                )
            """)
            print("账户表已就绪")

            # 创建交易记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    account_id INT NOT NULL,
                    transaction_type ENUM('DEPOSIT', 'WITHDRAW', 'TRANSFER', 'BALANCE_CHECK') NOT NULL,
                    amount DECIMAL(15,2),
                    description VARCHAR(255),
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
                )
            """)
            print("交易记录表已就绪")

            cursor.close()
            self.connection.commit()

        except Error as e:
            print(f"创建表错误: {e}")


    def insert_sample_data(self):
        """插入示例数据（可选)"""
        try:
            cursor = self.connection.cursor(dictionary=True)

            # 检查是否已有数据
            cursor.execute("SELECT COUNT(*) as count FROM users")
            result = cursor.fetchone()

            if result and result['count'] == 0:
                print("正在创建示例用户...")

                # 修正示例数据格式
                sample_users = [
                    ('lily', 'lily123', 'lily.li'),
                    ('kate', 'kate123', 'kate.zhang'),
                    ('lucy', 'lucy123', 'lucy.wang'),
                    ('allen', 'allen123', 'allen.ma')
                ]

                for username, password, full_name in sample_users:
                    # 注册用户
                    success, message = self.register_user(username, password, full_name)
                    if success:
                        print(f" - 创建用户: {username} ({full_name})")

                        # 为新用户存款
                        cursor.execute("SELECT id FROM accounts WHERE user_id = (SELECT id FROM users WHERE username = %s)", (username,))
                        account = cursor.fetchone()
                        if account:
                            # 初始存款
                            cursor.execute("UPDATE accounts SET balance = balance + 10000 WHERE id = %s", (account['id'],))
                            self._record_transaction(account['id'], 'DEPOSIT', 10000, "初始存款")
            
                self.connection.commit()
                print("示例数据插入完成")
            else:
                print(f"数据库中已有 {result['count']} 条用户记录，跳过示例数据插入")

            cursor.close()
        except Error as e:
            print(f"插入示例数据错误: {e}")
           

                    
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """执行SQL查询"""
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 确保 params 正确处理
            if params is None:
                params = ()
            elif not isinstance(params, (tuple, list)):
                params = (params,)  # 单个参数转为元组
            
            print(f"调试[SQL]: 执行查询: {query}")  # 添加调试信息
            print(f"调试[SQL]: 参数: {params}")    # 添加调试信息
            
            # 特殊处理：对于有DATE_FORMAT的查询，使用不同的方法
            if 'DATE_FORMAT' in query and '%Y-%m-%d %H:%i:%s' in query:
                # 方法3：先替换 % 为特殊标记，执行后再替换回来
                query = query.replace('%Y', '{YEAR}').replace('%m', '{MONTH}').replace('%d', '{DAY}')
                query = query.replace('%H', '{HOUR}').replace('%i', '{MINUTE}').replace('%s', '{SECOND}')
                print(f"调试[SQL]: 替换后查询: {query}")
                
                cursor.execute(query, params)
                
                # 获取结果并恢复格式
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                else:
                    self.connection.commit()
                    result = cursor.lastrowid
                
                # 恢复日期格式
                if fetch_all and result:
                    for row in result:
                        if 'date' in row and isinstance(row['date'], str):
                            row['date'] = row['date'].replace('{YEAR}', '%Y').replace('{MONTH}', '%m').replace('{DAY}', '%d')
                            row['date'] = row['date'].replace('{HOUR}', '%H').replace('{MINUTE}', '%i').replace('{SECOND}', '%s')
            else:
                cursor.execute(query, params)
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                    if result is None:
                        result = []
                else:
                    self.connection.commit()
                    result = cursor.lastrowid

            if fetch_one:
                print(f"调试[SQL]: fetch_one 结果: {result}")
            elif fetch_all:
                print(f"调试[SQL]: fetch_all 结果数量: {len(result) if result else 0}")
            else:
                print(f"调试[SQL]: lastrowid: {result}")
                
            return result
        except Error as e:
            print(f"查询执行错误: {e}")
            import traceback
            traceback.print_exc()  # 打印完整的错误堆栈
            return None
        finally:
            if cursor:
                cursor.close()

    # 用户相关操作 
    def register_user(self, username, password, full_name):
        """注册新用户"""
        # 检查用户名是否存在
        check_query = "SELECT id FROM users WHERE username = %s"
        existing_user = self.execute_query(check_query, (username,), fetch_one=True)
        if existing_user:
            return False, "用户名已存在"
        # 生成密码哈希
        password_hash = self._hash_password(password)

        # 插入用户
        query = """
        INSERT INTO users (username, password_hash, full_name)
        VALUES (%s, %s, %s)
        """

        user_id = self.execute_query(query, (username, password_hash, full_name))
        if user_id:
            # 为用户创建账户
            account_number = self._generate_account_number()
            account_query = """
            INSERT INTO accounts (user_id, account_number, balance)
            VALUES (%s, %s, %s)           
            """
            self.execute_query(account_query, (user_id, account_number, 0.00))
            return True, "注册成功"
        else:
            return False, "注册失败"
        
    def authenticate_user(self, username, password):
        """验证用户登录"""
        print(f"调试: 尝试认证用户 {username}") # 添加调试信息
        query = "SELECT id, username, password_hash, full_name FROM users WHERE username = %s"
        user = self.execute_query(query, (username,), fetch_one=True)

        print(f"调试: 查询结果: {user}")

        if not user:
            print(f"调试: 用户{username} 不存在")
            return False, "用户名不存在"
        # 验证密码
        print(f"调试: 开始验证密码")
        if self._verify_password(password, user['password_hash']):
            print(f"调试: 密码验证成功")
            # 获取用户账户信息
            account_query = """
            SELECT a.id, a.account_number, a.balance
            FROM accounts a
            WHERE a.user_id = %s
            """
            account = self.execute_query(account_query, (user['id'],), fetch_one=True)
            print(f"调试: 账户查询结果 {account}")
            
            if not account:
                print(f"调试: 用户 {username} 没有找到账户")
                return False, "账户不存在"
                
            user_info = {
                'user_id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'account_id': account['id'],
                'account_number': account['account_number'],
                'balance': float(account['balance'])
            }
            return True, user_info
        else:
            print(f"调试: 密码验证失败")
            return False, "密码错误"
        
    def _hash_password(self, password):
        """密码哈希处理"""
        salt = secrets.token_hex(16)

        # 使用PBKDF2 算法
        iterations = 100000
        key_length = 64
        hash_algorithm = 'sha256'

        # 生成秘钥
        key = hashlib.pbkdf2_hmac(
            hash_algorithm,
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations,
            dklen=key_length
        )
        # 组合salt和秘钥
        return f"pbkdf2:{hash_algorithm}:{iterations}${salt}${key.hex()}"
    
    def _verify_password(self, password, stored_hash):
        """验证密码"""
        try:
            print(f"调试验证: 存储的哈希 = {stored_hash[:50]}...") # 显示前50个字符
            print(f"调试验证: 输入的密码 = '{password}'")
            # 解析存储的哈希
            parts = stored_hash.split('$')
            print(f"调试验证: parts = {parts}")

            if len(parts) != 3 or not parts[0].startswith('pbkdf2'):
                print(f"调试验证: 哈希格式错误, parts长度={len(parts)}")
                return False
            # 解析算法信息
            algorithm_info = parts[0].split(':')
            if len(algorithm_info) != 3:
                print(f"调试验证: 算法信息格式错误")
                return False
            hash_algorithm = algorithm_info[1]
            iterations = int(algorithm_info[2])
            salt = parts[1]
            stored_key = parts[2]

            print(f"调试验证: 算法={hash_algorithm}, 迭代={iterations}")
            print(f"调试验证: 盐={salt}")
            print(f"调试验证: 存储的秘钥长度={len(stored_key)}")

            # 计算输入密码的哈希
            key = hashlib.pbkdf2_hmac(
                hash_algorithm,
                password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations,
                dklen=64
            )
            key_hex = key.hex()
            print(f"调试验证: 计算的密钥长度={len(key_hex)}")
            print(f"调试验证: 存储的秘钥(前20) ={stored_key[:20]}...")
            print(f"调试验证: 计算的密钥(前20) ={key_hex[:20]}...")

            result = key_hex == stored_key
            print(f"调试验证: 结果={result}")
            return result
        
        except Exception as e:
            print(f"调试验证: 验证过程中出错:{e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_account_number(self):
        """生成账户号码"""
        import time
        timestamp = int(time.time() * 1000)
        random_part = ''.join(secrets.choice(string.digits) for _ in range(6))
        return f"6228{timestamp % 10000:04d}{random_part}"

    # 账户操作
    def get_account_balance(self, account_id):
        """获取账户余额"""
        query = "SELECT balance FROM accounts WHERE id = %s"
        result = self.execute_query(query, (account_id,), fetch_one=True)
        return float(result['balance']) if result else 0.00

    def deposit(self, account_id, amount):
        """存款"""
        try:
            # 更新余额
            query = "UPDATE accounts SET balance = balance + %s WHERE id = %s"
            self.execute_query(query, (amount, account_id))

            # 记录交易
            self._record_transaction(account_id, 'DEPOSIT', amount, "存款")

            # 获取新的余额
            new_balance = self.get_account_balance(account_id)
            return True, f"存款成功！当前余额:{new_balance:.2f}元"
        except Error as e:
            return False, f"存款失败：{e}"

    def withdraw(self, account_id, amount):
        """取款"""
        try:
            # 检查余额是否足够
            current_balance = self.get_account_balance(account_id)
            if current_balance < amount:
                return False, "余额不足" 

            # 更新余额
            query = "UPDATE accounts SET balance = balance - %s WHERE id = %s"
            self.execute_query(query, (amount, account_id))

            # 记录交易
            self._record_transaction(account_id, 'WITHDRAW', amount, "取款")

            # 获取新的余额
            new_balance = self.get_account_balance(account_id)
            return True, f"取款成功！当前余额: {new_balance:.2f}元"
        except Error as e:
            return False, f"取款失败: {e}"
            
    def transfer(self, from_account_id, to_account_number, amount):
        """转账"""
        try:
            # 检查收款账户是否存在
            query = "SELECT id, user_id, balance FROM accounts WHERE account_number = %s"
            to_account = self.execute_query(query, (to_account_number,), fetch_one=True)

            if not to_account:
                return False, "收款账户不存在"
            if to_account['id'] == from_account_id:
                return False, "不能转账给自己"
            # 检查余额是否足够
            current_balance = self.get_account_balance(from_account_id)
            if current_balance < amount:
                return False, "余额不足"
            # 开始事务
            self.connection.start_transaction()

            try:
                # 从转出账户扣款
                withdraw_query = "UPDATE accounts SET balance = balance - %s WHERE id = %s"
                self.execute_query(withdraw_query, (amount, from_account_id))
                # 向收款账户存款
                deposit_query = "UPDATE accounts SET balance = balance + %s WHERE id = %s"
                self.execute_query(deposit_query, (amount, to_account['id']))

                # 记录交易
                self._record_transaction(from_account_id, 'TRANSFER', amount, f"转账给账户{to_account_number}")
                self._record_transaction(to_account['id'], 'TRANSFER', amount, f"收到来自账户的转账")
                # 提交事务
                self.connection.commit()

                # 获取新余额
                new_balance = self.get_account_balance(from_account_id)
                return True, f"转账成功！当前余额:{new_balance:.2f}元"
            except Error as e:
                self.connection.rollback()
                return False, f"转账失败:{e}"
            
        except Error as e:
            return False, f"转账失败:{e}"
        
    def get_transaction_history(self, account_id, limit=10):
        """获取交易记录"""
        print(f"调试[交易记录]: 开始查询，account_id={account_id}, limit={limit}")
        
        # 先检查账户是否存在
        check_query = "SELECT id, account_number FROM accounts WHERE id = %s"
        account = self.execute_query(check_query, (account_id,), fetch_one=True)
        
        if not account:
            print(f"调试[交易记录]: 账户 {account_id} 不存在")
            return []
        
        print(f"调试[交易记录]: 查询账户 {account['account_number']} 的交易记录")
        
        # 使用新的方法：避免在 DATE_FORMAT 中使用 % 字符
        query = "SELECT transaction_type, amount, description, transaction_date FROM transactions WHERE account_id = %s ORDER BY transaction_date DESC LIMIT %s"
        
        try:
            # 使用 execute_query 方法
            result = self.execute_query(query, (account_id, limit), fetch_all=True)

            if result is None:
                print("调试[交易记录]: 查询返回 None")
                return []
            elif isinstance(result, list):
                print(f"调试[交易记录]: 返回列表，长度={len(result)}")
                # 在Python中格式化日期
                for row in result:
                    if 'transaction_date' in row and row['transaction_date']:
                        row['date'] = row['transaction_date'].strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        row['date'] = ''
                    # 删除原始的transaction_date字段
                    if 'transaction_date' in row:
                        del row['transaction_date']
                
                if result:
                    for i, trans in enumerate(result[:3]):  # 只显示前3条调试信息
                        print(f"调试[交易记录]: 记录{i+1}: {trans}")
                else:
                    print("调试[交易记录]: 查询结果为空列表")
                return result
            else:
                print(f"调试[交易记录]: 意外的返回类型: {type(result)}, 值: {result}")
                return []
        except Exception as e:
            print(f"调试[交易记录]: 获取交易记录时出错: {e}")
            import traceback
            traceback.print_exc()
            return []
        
    def _record_transaction(self, account_id, transaction_type, amount, description):
        """记录交易"""
        query = """
        INSERT INTO transactions (account_id, transaction_type, amount, description)
        VALUES (%s, %s, %s, %s)
        """
        self.execute_query(query, (account_id, transaction_type, amount, description))

    def update_user_info(self, user_id, full_name):
        """更新用户信息"""
        query = "UPDATE users SET full_name = %s WHERE id = %s"
        result = self.execute_query(query, (full_name, user_id))
        return bool(result)
    
    def change_password(self, user_id, new_password):
        """修改密码"""
        password_hash = self._hash_password(new_password)
        query = "UPDATE users SET password_hash = %s WHERE id = %s"
        result = self.execute_query(query, (password_hash, user_id))
        return bool(result)
