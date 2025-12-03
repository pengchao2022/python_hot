import sys
import os
import time
from database import Database

class ATMSystem:
    def __init__(self):
        self.db = Database()
        self.current_user = None
        self.is_running = True

    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        """打印标题"""
        print("="*50)
        print(f"{title:^50}")
        print("="*50)

    def wait_for_enter(self):
        """等待用户按回车"""
        input("\n按回车键继续...")
    
    def main_menu(self):
        """主菜单"""
        while self.is_running:
            self.clear_screen()
            self.print_header("ATM银行系统")
            print("1. 用户登录")
            print("2. 用户注册")
            print("3. 退出系统")
            print("="*50)

            choice = input("请选择操作(1-3): ").strip()

            if choice == '1':
                self.login()
            elif choice == '2':
                self.register()

            elif choice == '3':
                self.exit_system()

            else:
                print("无效选择，请重新输入")
                time.sleep(1)

    def login(self):
        """用户登录"""
        self.clear_screen()
        self.print_header("用户登录")

        username = input("请输入用户名: ").strip()
        password = input("请输入密码: ").strip()

        if not username or not password:
            print("用户名和密码不能为空")
            return
        
        success, result = self.db.authenticate_user(username, password)

        if success:
            self.current_user = result
            print(f"\n登录成功！欢迎您，{self.current_user['full_name']}!")
            print(f"您的账户号码: {self.current_user['account_number']}")
            time.sleep(2)
            self.user_menu()

        else:
            print("\n登录失败！{result}")
            self.wait_for_enter()

    def register(self):
        """用户注册"""
        self.clear_screen()
        self.print_header("用户注册")
        
        username = input("请输入用户名(4-20位):").strip()
        if len(username) < 4 or len(username) > 20:
            print("用户名长度必须在4-20位之间")
            self.wait_for_enter()
            return
        
        password = input("请输入密码(6-30位): ").strip()
        if len(password) < 6 or len(password)  > 30:
            print("密码长度必须在6-30位之间")
            self.wait_for_enter()
            return 
        
        confirm_password = input("请确认密码: ").strip()
        if password != confirm_password:
            print("两次输入的密码不一致")
            self.wait_for_enter()
            return 
        
        full_name = input("请输入您的全名: ").strip()
        if not full_name:
            print("全名不能为空")
            self.wait_for_enter()
            return
        
        success, message = self.db.register_user(username, password, full_name)
        if success:
            print(f"\n{message}")
            print("请使用哪个新注册的账号登录")
        else:
            print(f"\n注册失败: {message}")
        self.wait_for_enter()

    def user_menu(self):
        """用户功能菜单"""
        while self.current_user:
            self.clear_screen()
            self.print_header(f"欢迎, {self.current_user['full_name']}")
            print(f"账号号码: {self.current_user['account_number']}")
            print(f"当前余额: CNY{self.current_user['balance']:.2f}")
            print("-" * 50)
            print("1. 存款")
            print("2. 取款")
            print("3. 转账")
            print("4. 查询余额")
            print("5. 交易记录")
            print("6. 修改个人信息")
            print("7. 修改密码")
            print("8. 退出登录")
            print("="*50)

            choice = input("请选择操作(1-8): ").strip()

            if choice == '1':
                self.deposit()
            elif choice == '2':
                self.withdraw()
            elif choice == '3':
                self.transfer()
            elif choice == '4':
                self.check_balance()
            elif choice == '5':
                self.view_transaction_history()
            elif choice == '6':
                self.update_profile()
            elif choice == '7':
                self.change_password()
            elif choice == '8':
                self.logout()
                break
            else:
                print("无效选择，请重新输入")
                time.sleep(1)

    def deposit(self):
        """存款操作"""
        self.clear_screen()
        self.print_header("存款")
        try:
            amount = float(input("请输入存款金额: ").strip())
            if amount <= 0:
                print("存款金额必须大于0")
                self.wait_for_enter()
                return
            success, message = self.db.deposit(self.current_user['account_id'], amount)
            print(f"\n{message}")

            if success:
                # 更新当前用户余额
                self.current_user['balance'] = self.db.get_account_balance(
                    self.current_user['account_id']
                )
        except ValueError:
            print("请输入有效的金额")
        except Exception as e:
            print(f"操作失败: {e}")

        self.wait_for_enter()

    def withdraw(self):
        """取款操作"""
        self.clear_screen()
        self.print_header("取款")
        try:
            amount = float(input("请输入取款金额: ").strip())
            if amount <= 0:
                print("取款金额必须大于0")
                self.wait_for_enter()
                return
            success, message = self.db.withdraw(self.current_user['account_id'], amount)
            print(f"\n{message}")

            if success:
                # 更新当前用户余额
                self.current_user['balance'] = self.db.get_account_balance(
                    self.current_user['account_id']
                )
        except ValueError:
            print("请输入有效的金额")
        except Exception as e:
            print(f"操作失败:{e}")

        self.wait_for_enter()

    def transfer(self):
        """转账操作"""
        self.clear_screen()
        self.print_header("转账")
        try:
            to_account = input("请输入收款账户号码: ").strip()
            if not to_account:
                print("账户号码不能为空")
                self.wait_for_enter()
                return

            amount = float(input("请输入转账金额: ").strip())
            if amount <= 0:
                print("转账金额必须大于0")
                self.wait_for_enter()
                return

            success, message = self.db.transfer(
                self.current_user['account_id'],
                to_account,
                amount
            )
            print(f"\n{message}")
            if success:
                # 更新当前用户余额
                self.current_user['balance'] = self.db.get_account_balance(
                    self.current_user['account_id']
                )
        except ValueError:
            print("请输入有效的金额")

        except Exception as e:
            print(f"操作失败: {e}")

        self.wait_for_enter()

    def check_balance(self):
        """查询余额"""
        self.clear_screen()
        self.print_header("账户余额")

        balance = self.db.get_account_balance(self.current_user['account_id'])
        print(f"\n账户号码: {self.current_user['account_number']}")
        print(f"账户余额: CNY{balance:.2f}")

        self.wait_for_enter()

    def view_transaction_history(self):
        """查看交易记录"""
        self.clear_screen()
        self.print_header("交易记录")

        transactions = self.db.get_transaction_history(self.current_user['account_id'], 15)
        if not transactions:
            print("\n暂无交易记录")
        else:
            print(f"\n{'类型':<8}{'金额':<12}{'描述':<25}{'时间':<20}")
            print("-"*70)

            for trans in transactions:
                trans_type = {
                    'DEPOSIT': '存款',
                    'WITHDRAW': '取款',
                    'TRANSFER': '转账',
                    'BALANCE_CHECK': '查询'
                }.get(trans['transaction_type'], trans['transaction_type'])

                amount = f"CNY{float(trans['amount']):.2f}" if trans['amount'] else "N/A"
                description = trans['description'][:20] + "..." if len(trans['description']) > 20 else trans['description']

                print(f"{trans_type:<8} {amount:>12} {description:<25} {trans['date']:<20}")

        self.wait_for_enter()

    def update_profile(self):
        """修改个人信息"""
        self.clear_screen()
        self.print_header("修改个人信息")

        print(f"当前姓名: {self.current_user['full_name']}")
        new_name = input("请输入新姓名 (直接回车保持原样): ").strip()

        if new_name:
            success = self.db.update_user_info(self.current_user['user_id'], new_name)
            if success:
                self.current_user['full_name'] = new_name
                print("个人信息更新成功")

            else:
                print("个人信息更新失败")
        else:
            print("姓名未修改")

        self.wait_for_enter()

    def change_password(self):
        """修改密码"""
        self.clear_screen()
        self.print_header("修改密码")
        old_password = input("请输入原密码: ").strip()

        # 验证原密码
        success, _ = self.db.authenticate_user(
            self.current_user['username'],
            old_password
        )
        if not success:
            print("原密码错误")
            self.wait_for_enter()
            return
        
        new_password = input("请输入新密码(6-32位): ").strip()
        if len(new_password) < 6 or len(new_password) > 30:
            print("密码长度必须在6-30位之间")
            self.wait_for_enter()
            return
        
        confirm_password = input("请确认新密码: ").strip()
        if new_password != confirm_password:
            print("两次输入的密码不一致")
            self.wait_for_enter()
            return
        success = self.db.change_password(self.current_user['user_id'], new_password)
        if success:
            print("密码修改成功，请重新登录")
            time.sleep(2)
            self.logout()
        else:
            print("密码修改失败")
            self.wait_for_enter()
    def logout(self):
        """退出登录"""
        self.current_user = None
        print("\n已成功退出登录")
        time.sleep(1)

    def exit_system(self):
        """退出系统"""
        self.clear_screen()
        self.print_header("感谢使用ATM银行系统")
        self.db.disconnect()
        self.is_running = False
        print("\n系统已退出")
        time.sleep(2)
        sys.exit(0)

def main():
    """主函数"""
    try:
        system = ATMSystem()
        system.main_menu()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        
if __name__ == "__main__":
    # 检查依赖
    try:
        import mysql.connector
    except ImportError:
        print("错误: 需要安装 mysql-connector-python")
        print("请运行: pip install mysql-connector-python")
        sys.exit(1)

    main()
