# 定义一个登录系统函数
def login():
    """简单的登录系统"""
    # 预定有的用户名和密码
    correct_username = "allen"
    correct_pasword = "123456"

    print("===登录系统===")

    # 获取用户输入
    username = input("请在此输入用户名：")
    password = input("请在此输入密码：")

    # 验证用户名和密码
    if username == correct_username and password == correct_pasword:
        print("登录成功！欢迎使用",username)
        return True
    
    else:
        print("登录失败！用户名或密码错误。")
        return False
    
# 调用登录函数
if login():
    print("进入系统主界面...")
else:
    print("请重新尝试登录。")
