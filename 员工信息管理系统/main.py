import mysql.connector
from mysql.connector import Error
from datetime import datetime
import re

class DatabaseManager:
    """数据库管理类"""

    def __init__(self, host="localhost", user="root", password="", database="employee_management"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.connect()
        self.create_tables()

    def connect(self):
        """连接数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("数据库连接成功")
        except Error as e:
            print(f"数据库连接失败:{e}")
            self.create_database()

    def create_database(self):
        """创建数据库"""
        try:
            temp_conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password

            )    
            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"数据库{self.database}创建成功")
            cursor.close()
            temp_conn.close()
            self.connect()
        except Error as e:
            print(f"创建数据库失败: {e}") 

    def create_tables(self):
        """创建数据库""" 
        try:
            cursor = self.connection.cursor()

            # 创建部门表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departments(
                    department_id INT AUTO_INCREMENT PRIMARY KEY,
                    department_name VARCHAR(100) NOT NULL UNIQUE,
                    manager VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)  

            # 创建员工表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees(
                    employee_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    gender ENUM('男', '女') NOT NULL,
                    age INT NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    phone VARCHAR(20),
                    position VARCHAR(100) NOT NULL,
                    salary DECIMAL(10,2) NOT NULL,
                    department_id INT,
                    hire_date DATE NOT NULL,
                    status ENUM('在职', '离职', '休假') DEFAULT '在职', 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL    
                    )
                           """)
            
            # 创建考勤表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                    employee_id INT NOT NULL,
                    attendance_date DATE NOT NULL,
                    check_in_time TIME,
                    check_out_time TIME,
                    status ENUM('正常', '迟到', '早退', '缺勤', '休假') DEFAULT '正常',
                    notes TEXT,
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
                     )
                    """)
            # 插入默认部门数据
            cursor.execute("""
                INSERT IGNORE INTO departments (department_name, manager) VALUES
                ('技术部', 'lily'),
                ('销售部', 'kate'),
                ('人事部', 'winslate'),
                ('财务部', 'Tommy'),
                ('行政部', 'Trump')         

            """)

            self.connection.commit()
            cursor.close()
            print("数据表创建成功")
        except Error as e:
            print(f"创建数据表失败：{e}")

    def execute_query(self, query, params=None):
        """执行查询"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())

            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                cursor.close()
                return True
        except Error as e:
            print(f"执行查询失败:{e}")
            return False


    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("数据库已关闭")

class Employee:
    """员工类"""

    def __init__(self, employee_id=None, name="", gender="", age=0, email="", phone="",
                 position="", salary=0.0, department_id=None, hire_date="", status="在职",
                 db_manager=None):
        self.employee_id = employee_id
        self.name = name 
        self.gender = gender
        self.age = age
        self.email = email
        self.salary = salary
        self.phone = phone
        self.position = position
        self.department_id = department_id
        self.hire_date = hire_date
        self.status = status
        self.db_manager = db_manager

    def save_to_db(self):
        """保存员工信息到数据库"""
        if not self.db_manager:
            return False
        
        if self.employee_id:
            query = """
                UPDATE employees SET name=%s, gender=%s, age=%s, email=%s, phone=%s,
                position=%s, salary=%s, department_id=%s, hire_date=%s, status=%s
                WHERE employee_id=%s
            """
            params = (self.name, self.gender, self.age, self.email, self.phone,
                      self.position, self.salary, self.department_id, self.hire_date,
                      self.status, self.employee_id)
        else:
            query = """
                INSERT INTO employees (name, gender, age, email, phone, position,
                salary, department_id, hire_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (self.name, self.gender, self.age, self.email, self.phone,
                      self.position, self.salary, self.department_id, self.hire_date,
                      self.status)
            
        result = self.db_manager.execute_query(query, params)
        if result and not self.employee_id:
            # 获取新插入的员工ID
            id_query = "SELECT LAST_INSERT_ID()"
            id_result = self.db_manager.execute_query(id_query)
            if id_result:
                self.employee_id = id_result[0][0]
        return result
    
    def delete_from_db(self):
        """从数据库删除员工"""
        if not self.employee_id or not self.db_manager:
            return False
        query = "DELETE FROM employees WHERE employee_id = %s"
        return self.db_manager.execute_query(query, (self.employee_id,))
    
    def get_employee_info(self):
        """获取员工信息"""
        dept_name = self.get_department_name()
        info = f"\n 员工信息（ID:{self.employee_id}):\n"
        info += "="*50 + "\n"
        info += f"姓名:{self.name}\n"
        info += f"性别:{self.gender}\n"
        info += f"年龄:{self.age}\n"
        info += f"邮箱:{self.email}\n"
        info += f"电话:{self.phone}\n"
        info += f"职位:{self.position}\n"
        info += f"薪资:{self.salary}元\n"
        info += f"部门:{dept_name}\n"
        info += f"入职日期: {self.hire_date}\n"
        info += f"状态:{self.status}\n"
        info += "="*50
        return info
    
    def get_department_name(self):
        """获取部门名称"""
        if not self.department_id or not self.db_manager:
            return "未分配"
        query = "SELECT department_name FROM departments WHERE department_id = %s"
        result = self.db_manager.execute_query(query, (self.department_id,))
        return result[0][0] if result else "未分配"

    @classmethod
    def load_from_db(cls, db_manager, employee_id):
        """从数据库加载员工"""
        query = """
            SELECT employee_id, name, gender, age, email, phone, position,
                    salary, department_id, hire_date, status

            FROM employees WHERE employee_id = %s
            """
        result = db_manager.execute_query(query, (employee_id,))
        if result:
            data = result[0]
            return cls(
                employee_id=data[0],
                name=data[1],
                gender=data[2],
                age=data[3],
                email=data[4],
                phone=data[5],
                position=data[6],
                salary=float(data[7]),
                department_id=data[8],
                hire_date=data[9].strftime('%Y-%m-%d') if data[9] else "",
                status=data[10],
                db_manager=db_manager

            )
        return None
    
class Department:
    """部门类"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all_departments(self):
        """获取所有部门"""
        query = "SELECT department_id, department_name, manager FROM departments ORDER BY department_id"
        return self.db_manager.execute_query(query)
    
    def display_departments(self):
        """显示部门列表"""
        departments = self.get_all_departments()
        print("\n 部门列表:")
        print("="*60)
        print(f"{'ID':<5}{'部门名称':<15}{'负责人':<10}{'员工数量':<10}")
        print("-"*60)

        for dept in departments:
            employee_count = self.get_employee_count(dept[0])
            print(f"{dept[0]:<5} {dept[1]:<15} {dept[2]:<10} {employee_count:<10}")
        print("="*60)

    def get_employee_count(self, department_id):
        """获取部门员工数量"""
        query = "SELECT COUNT(*) FROM employees WHERE department_id = %s AND status = '在职'"
        result = self.db_manager.execute_query(query, (department_id,))
        return result[0][0] if result else 0

class AttendanceSystem:
    """考勤系统类"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def record_attendance(self, employee_id, date, check_in=None, check_out=None, status="正常", notes=""):
        """记录考勤"""
        query = """
            INSERT INTO attendance (employee_id, attendance_date, check_in_time, check_out_time, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            check_in_time = VALUES(check_in_time),
            check_out_time = VALUES(check_out_time),
            status = VALUES(status),
            notes = VALUES(notes)
        """
        params = (employee_id, date, check_in, check_out, status, notes)
        return self.db_manager.execute_query(query, params)
    
    def get_attendance_report(self, employee_id, start_date, end_date):
        """获取考勤报告"""
        query = """
            SELECT attendance_date, check_in_time, check_out_items, status, notes
            FROM attendance
            WHERE employee_id = %s AND attendance_date BETWEEN %s AND %s
            ORDER BY attendance_date
        """
        return self.db_manager.execute_query(query, (employee_id, start_date, end_date))
    
class EmployeeManagementSystem:
    """员工管理系统界面类"""

    def __init__(self):
        self.db_manager = DatabaseManager(
            host="localhost",
            user="root",
            password="Password2025",
            database="employee_management"
        )
        self.department = Department(self.db_manager)
        self.attendance_system = AttendanceSystem(self.db_manager)
        self.running = True

    def display_menu(self):
        """显示主菜单"""
        print("\n" + "="*60)
        print("             员工管理系统")
        print("="*60)
        print("1. 添加员工")
        print("2. 查看员工信息")
        print("3. 修改员工信息")
        print("4. 删除员工")
        print("5. 查看所有员工")
        print("6. 部门管理")
        print("7. 考勤管理")
        print("8. 统计报告")
        print("0. 退出系统")
        print("="*60)

    def get_input(self, prompt, input_type=str, allow_empty=False):
        """获取输入并进行类型验证"""
        while True:
            try:
                user_input = input(prompt).strip()
                if not user_input and not allow_empty:
                    print("输入不能为空，请重新输入")
                    continue

                if input_type == int:
                    return int(user_input)

                elif input_type == float:
                    return float(user_input)

                else:
                    return user_input
            except ValueError:
                print("输入格式错误，请重新输入")

    def validate_email(self, email):
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-0.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    def validate_phone(self, phone):
        """验证手机号格式"""
        pattern = r'^1[3-9]\d{9}$'
        return re.match(pattern, phone) is not None
    
    def add_employee(self):
        """添加员工"""
        print("\n 添加新员工")

        # 显示部门列表
        self.department.display_departments()
        name = self.get_input("姓名: ")
        # 性别选择
        print("\n性别选择:")
        print("1. 男")
        print("2. 女")
        gender_choice = self.get_input("请选择(1-2):", int)
        gender = "男" if gender_choice == 1 else "女"

        age = self.get_input("年龄:", int)

        # 邮箱验证
        while True:
            email = self.get_input("邮箱:", allow_empty=True)
            if not email or self.validate_email(email):
                break
            print("邮箱格式不正确，请重新输入")

        # 手机号验证
        while True:
            phone = self.get_input("手机号:")
            if self.validate_phone(phone):
                break
            print("手机号格式不正确，请重新输入")

        position = self.get_input("职位: ")
        salary = self.get_input("薪资: ", float)
        department_id = self.get_input("部门ID: ", int)
        hire_date = self.get_input("入职日期(YYYY-MM-DD): ")

        # 创建员工对象并保存
        employee = Employee(
            name=name, gender=gender, age=age, email=email, phone=phone,
            position=position, salary=salary, department_id=department_id,
            hire_date=hire_date, db_manager=self.db_manager
        )
        if employee.save_to_db():
            print(f"员工{name}添加成功！员工ID:{employee.employee_id}")
        else:
            print("添加员工失败")

    def view_employee(self):
        """查看员工信息"""
        employee_id = self.get_input("请输入员工ID: ", int)
        employee = Employee.load_from_db(self.db_manager, employee_id)

        if employee:
            print(employee.get_employee_info())
        else:
            print("员工不存在")

    def update_employee(self):
        """修改员工信息"""
        employee_id = self.get_input("请输入要修改的员工ID: ", int)
        employee = Employee.load_from_db(self.db_manager, employee_id)
        if not employee:
            print("员工不存在")
            return
        
        print(employee.get_employee_info())
        print("\n请选择要修改的信息:")
        print("1. 姓名")
        print("2. 年龄")
        print("3. 邮箱")
        print("4. 手机号")
        print("5. 职位")
        print("6. 薪资")
        print("7. 部门")
        print("8. 状态")
        print("9. 全部信息")

        choice = self.get_input("请选择(1-9): ", int)
        if choice == 1:
            employee.name = self.get_input("新姓名: ")
        elif choice == 2:
            employee.age = self.get_input("新年龄: ", int)
        elif choice == 3:
            while True:
                email = self.get_input("新邮箱: ", allow_empty=True)
                if not email or self.validate_email(email):
                    employee.email = email
                    break
                print("邮箱格式不正确")
        elif choice == 4:
            while True:
                phone = self.get_input("新手机号:")
                if self.validate_phone(phone):
                    employee.phone = phone
                    break
                print("手机号格式不正确")

        elif choice == 5:
            employee.salary = self.get_input("新薪资: ", float)
        elif choice == 7:
            self.department.display_departments()
            employee.department_id = self.get_input("新部门ID: ", int)
        elif choice == 8:
            print("\n状态选择:")
            print("1. 在职")
            print("2. 离职")
            print("3. 休假") 
            status_choice = self.get_input("请选择(1-3): ", int)
            status_map = {1: "在职", 2: "离职", 3: "休假"}
            employee.status = status_map.get(status_choice, "在职")

        elif choice == 9:
            # 修改全部信息
            return self.add_employee() # 简化处理

        if employee.save_to_db():
            print("员工信息更新成功")
        else:
            print("更新员工信息失败") 

    def delete_employee(self):
        """删除员工"""
        employee_id = self.get_input("请输入要删除的员工ID: ", int)
        employee = Employee.load_from_db(self.db_manager, employee_id)

        if not employee:
            print("员工不存在")
            return

        print(employee.get_employee_info())
        confirm = input("确定删除此员工? (y/n): ").lower()

        if confirm == 'y':
            if employee.delete_from_db():
                print("员工删除成功")
            else:
                print("删除员工失败")
        else:
            print("已取消删除")

    def view_all_employees(self):
        """查看所有员工"""
        query = """
            SELECT e.employee_id, e.name, e.position, e.salary, d.department_name, e.status
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.department_id
            ORDER BY e.employee_id
        """   
        results = self.db_manager.execute_query(query)

        if not results:
            print("暂无员工数据")
            return
        
        print("\n 所有员工列表:")
        print("="*80)
        print(f"{'ID':<5} {'姓名':<10} {'职位':<15} {'薪资':<10} {'部门':<15} {'状态':<8}")
        print("="*80)

        for emp in results:
            print(f"{emp[0]:<5} {emp[1]:<10} {emp[2]:<15} {emp[3]:<10} {emp[4]:<15} {emp[5]:<8}")
            print("="*80)

    def department_management(self):
        """部门管理"""
        print("\n 部门管理")
        self.department.display_departments()

        print("\n1. 查看部门员工")
        print("2. 返回")

        choice = self.get_input("请选择: ", int)
        if choice == 1:
            department_id = self.get_input("请输入部门ID: ", int)
            self.view_department_employees(department_id)

    def view_department_employees(self, department_id):
        """查看部门员工"""
        query = """
            SELECT employee_id, name, position, salary, status
            FROM employees
            WHERE department_id = %s
            ORDER BY employee_id
        """
        results = self.db_manager.execute_query(query, (department_id,))
        if not results:
            print("该部门暂无员工")
            return
        
        dept_query = "SELECT department_name FROM departments WHERE department_id = %s"
        dept_result = self.db_manager.execute_query(dept_query, (department_id,))
        dept_name = dept_result[0][0] if dept_result else "未知部门"

        print(f"\n {dept_name} 员工列表:")
        print("="*60)
        print(f"{'ID':<5} {'姓名':<10} {'职位':<15} {'薪资':<10} {'状态':<8}")
        print("-"*60)

        for emp in results:
            print(f"{emp[0]:<5} {emp[1]:<10} {emp[2]:<15} {emp[3]:<10} {emp[4]:<8}")
        print("="*60)

    def attendance_management(self):
        """考勤管理"""
        print("\n 考勤管理" )
        print("1. 记录考勤") 
        print("2. 查看考勤记录")
        print("3. 返回") 

        choice = self.get_input("请选择: ", int)
        if choice == 1:
            self.record_attendance()
        elif choice == 2:
            self.view_attendance()

    def record_attendance(self):
        """记录考勤"""
        employee_id = self.get_input("员工ID: ", int)
        date = self.get_input("日期(YYYY-MM-DD): ")

        print("\n考勤状态:")
        print("1. 正常")
        print("2. 迟到")
        print("3. 早退")
        print("4. 缺勤")
        print("5. 休假")
        status_choice = self.get_input("请选择(1-5): ", int)
        status_map = {1: "正常", 2: "迟到", 3: "早退", 4: "缺勤", 5: "休假"}
        status = status_map.get(status_choice, "正常")

        check_in = self.get_input("上班时间(HH:MM:SS, 可选): ", allow_empty=True)
        check_out = self.get_input("下班时间(HH:MM:SS, 可选): ", allow_empty=True)
        notes = self.get_input("备注: ", allow_empty=True)
        if self.attendance_system.record_attendance(employee_id, date, check_in, check_out, status, notes):
            print("考勤记录成功")
        else:
            print("考勤记录失败")

    def view_attendance(self):
        """查看考勤记录"""
        employee_id = self.get_input("员工ID: ", int)
        start_date = self.get_input("开始日期(YYYY-MM-DD): ")
        end_date = self.get_input("结束日期(YYYY-MM-DD): ")

        results = self.attendance_system.get_attendance_report(employee_id, start_date, end_date)
        if not results:
            print("该时间段无考勤记录")
            return

        print(f"\n 考勤记录 ({start_date} 至 {end_date}):")
        print("="*70)
        print(f"{'日期':<12} {'上班时间':<10} {'下班时间':<10} {'状态':<8} {'备注':<20}")
        print("="*70)

        for record in results:
            check_in = record[1] if record[1] else "未打卡"
            check_out = record[2] if record[2] else "未打卡"  
            notes= record[4] if record[4] else "无"
            print(f"{record[0]:<12} {str(check_in):<10} {str(check_out):<10} {record[3]:<8} {notes:<20}")
            print("="*70)

    def generate_reports(self):
        """生成统计报表"""
        print("\n 统计报表")
        print("1. 员工统计")
        print("2. 薪资统计")
        print("3. 部门统计")
        print("4. 返回")

        choice = self.get_input("请选择: ", int)
        if choice == 1:
            self.employee_statistics()

        elif choice == 2:
            self.salary_statistics()
        elif choice == 3:
            self.department_statistics()


    def employee_statistics(self):
        """员工统计"""
        query = """
            SELECT
                COUNT(*) as total_employees,
                SUM(CASE WHEN gender = '男' THEN 1 ELSE 0 END) as male_count,
                SUM(CASE WHEN gender = '女' THEN 1 ELSE 0 END) as female_count,
                SUM(CASE WHEN status = '在职' THEN 1 ELSE 0 END) as active_count,
                SUM(CASE WHEN status = '离职' THEN 1 ELSE 0 END) as resign_count,
                SUM(CASE WHEN status = '休假' THEN 1 ELSE 0 END) as vacation_count
            FROM employees
        """
        result = self.db_manager.execute_query(query)

        if result:
            data = result[0]
            print("\n 员工统计:")
            print("="*40)
            print(f"总员工数: {data[0]}")
            print(f"男性员工: {data[1]}")
            print(f"女性员工: {data[2]}")
            print(f"在职员工: {data[3]}") 
            print(f"离职员工: {data[4]}")
            print(f"休假员工: {data[5]}")
            print("="*40) 


    def salary_statistics(self):
        """薪资统计"""
        query = """
            SELECT 
                COUNT(*) as total,
                AVG(salary) as avg_salary,
                MAX(salary) as max_salary,
                MIN(salary) as min_salary,
                SUM(salary) as total_salary
            FROM employees
            WHERE status = '在职'
        """
        result = self.db_manager.execute_query(query)

        if result:
            data = result[0]
            print("\n 薪资统计:")
            print("="*40)
            print(f"在职员工数: {data[0]}")
            print(f"平均薪资: {float(data[1]):.2f}元")
            print(f"最高薪资: {float(data[2]):.2f}元")
            print(f"最低薪资: {float(data[3]):.2f}元")
            print(f"薪资总额: {float(data[4]):.2f}元")
            print("="*40)
    
    def department_statistics(self):
        """部门统计"""
        query = """
            SELECT d.department_name COUNT(e.employee_id) as employee_count,
                    AVG(e.salary) as avg_salary
            FROM departments d
            LEFT JOIN employees e ON d.department_id = e.department_id AND e.status = '在职'
            GROUP BY d.department_id, d.department_name
            ORDER BY employee_count DESC
        """
        results = self.db_manager.execute_query(query)
        if not results:
            print("暂无部门数据")
            return
        
        print("\n 部门统计:")
        print("="*50)
        print(f"{'部门':<15} {'员工数':<8} {'平均薪资':<12}")
        print("-"*50)

        for dept in results:
            avg_salary = float(dept[2]) if dept[2] else 0
            print(f"{dept[0]:<15} {dept[1]:<8} {avg_salary:<12.2f}")
        print("="*50)

    def run(self):
        """运行系统"""
        print("欢迎使用员工管理系统")
        while self.running:
            self.display_menu()
            choice = self.get_input("请选择操作(0-8):", int)

            if choice == 0:
                print("感谢使用，再见")
                self.db_manager.close()
                self.running = False

            elif choice == 1:
                self.add_employee()

            elif choice == 2:
                self.view_employee()

            elif choice == 3:
                self.update_employee()

            elif choice == 4:
                self.delete_employee()

            elif choice == 5:
                self.view_all_employees()

            elif choice == 6:
                self.department_management()

            elif choice == 7:
                self.attendance_management()

            elif choice == 8:
                self.generate_reports()
            else:
                print("无效选择，请重新输入")

            if self.running:
                input("\n按回车键继续...")

# 运行系统
if __name__ == "__main__":
    system = EmployeeManagementSystem()
    system.run()

