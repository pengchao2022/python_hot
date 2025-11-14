# 定义一个字典
users = {
    "allen": "allen345",
    "jim": "jim345",
    "lily": "lily345",
    "kate": "kate345",
    "wusong": "wusong345"
}

# 打印所有用户名
for username in users.keys():
    print(f"用户名是：{username}")

for password in users.keys():
    print(f"密码是：{password}")

# 打印所有用户名和对应的密码
for username,password in users.items():
    print(f"用户名为：{username},密码为：{password}")

    
