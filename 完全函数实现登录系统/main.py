from unittest import result


def initialize_uesrs():
    """初始化数据库"""
    users = {
        "admin": "admin123",
        "user1": "password1",
        "guest": "guest123",
        "alice": "alice123",
        "allen": "allen123"
    }
    return users

def display_login_header():
    """显示登录界面标题"""
    print("="*30)
    print("        用户登录系统")
    print("="*30)

def get_username_input():
    """获取用户名输入"""
    username = input("用户名：").strip()
    return username

def get_password_input():
    """获取用户密码输入"""
    password = input("密码：").strip()
    return password

def validate_username(username, users):
    """验证用户名是否存在"""
    return username in users

def validate_password(username, password, users):
    """验证密码是否正确"""
    if username in users:
        return users[username] == password
    return False

def validate_credentials(username, password, users):
    """综合验证用户名和密码"""
    return validate_username(username, users) and validate_password(username, password, users)

def display_login_success(username):
    """显示成功登录信息"""
    print(f"\n 🍏 登录成功！欢迎{username}")

def display_login_failure():
    """显示失败登录信息"""
    print("\n😌😌😌😌登录失败！用户名或密码错误。")

def create_result(status, username):
    """创建返回结果字典"""
    return {"status": status, "username": username}

def process_login_result(result):
    """处理登录结果"""
    if result["status"]:
        print(f"正在加载{result['username']}的个性化界面...")
        # 这里可以调用更多功能函数
        show_user_dashboard(result["username"])
    else:
        print("请检查用户名和密码后重试。")

def show_user_dashboard(username):
    """显示用户仪表板（可扩展）"""
    print(f"\n==={username}的个人中心===")
    print("1. 查看个人信息")
    print("2. 修改密码")
    print("3. 退出系统")

def login_system():
    """主登录系统函数""" 
    # 1. 初始化
    users = initialize_uesrs()

    # 2. 显示界面
    display_login_header()

    # 3. 获取输入
    username = get_username_input()
    password = get_password_input()

    # 4. 验证登录
    if validate_credentials(username, password, users):
        display_login_success(username)
        return create_result(True, username)
    else:
        display_login_failure()
        return create_result(False, username)
    
    # 使用登录系统
if __name__ == "__main__":
    result = login_system()
    process_login_result(result)

