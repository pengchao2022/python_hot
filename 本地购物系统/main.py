import mysql.connector
from mysql.connector import Error
import json

class DatabaseManager:
    """数据库管理类"""

    def __init__(self, host="localhost", user="root", password="Password2025", database="apple_shop"):
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
                host = self.host,
                user = self.user,
                password = self.password,
                database = self.database
            )

            if self.connection.is_connected():
                print("数据库连接成功")
        except Error as e:
            print(f"数据库连接失败:{e}")
            # 尝试连接数据库
            self.create_database()

    def create_database(self):
        """创建数据库"""
        try:
            # 先连接并不指定数据库 
            temp_conn = mysql.connector.connect(
                host = self.host,
                user = self.user,
                password = self.password
            )
            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"数据库{self.database}创建成功")
            cursor.close()
            temp_conn.close()

            # 创新链接指定数据库
            self.connect()
        except Error as e:
            print(f"数据库创建失败：{e}")

    def create_tables(self):
        """创建数据表"""
        try:
            cursor = self.connection.cursor()

            # 创建商品表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products(
                           product_id VARCHAR(50) PRIMARY KEY,
                           name VARCHAR(50) NOT NULL,
                           price DECIMAL(10,2) NOT NULL,
                           stock INT NOT NULL,
                           category VARCHAR(50),
                           create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                
                           )  
                        """)
            
            # 创建订单表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders(
                    order_id INT AUTO_INCREMENT PRIMARY KEY,
                    total_amount DECIMAL(10,2) NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'completed'
                )
             """)
            
            # 创建订单详情表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items(
                    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id INT,
                    product_id VARCHAR(50),
                    quantity INT NOT NULL,  
                    price DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE     
                           ) 
                           """)
            self.connection.commit()
            cursor.close()
            print("数据表创建成功")
        except Error as e:
            print(f"数据表创建失败：{e}")

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
            print(f"执行查询失败：{e}")
            return False

    def close(self):
        """关闭数据库连接""" 
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("数据库连接已经关闭")

class Product:
    """商品类"""

    def __init__(self, product_id, name, price, stock, category="", db_manager=None):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category
        self.db_manager = db_manager


    def save_to_db(self):
        """保存商品到数据库"""
        if not self.db_manager:
            return False
        
        query = """
            INSERT INTO products (product_id, name, price, stock, category)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name), 
                price = VALUES(price),
                stock = VALUES(stock),
                category = VALUES(category)
            """
        params = (self.product_id, self.name, self.price, self.stock, self.category)
        return self.db_manager.execute_query(query, params)
    
    def update_price(self, new_price):
        """更新价格"""
        if new_price >= 0:
            old_price = self.price
            self.price = new_price
            print(f"{self.name}价格从{old_price}元更新为:{new_price}元")

            # 更新数据库
            if self.db_manager:
                query = "Update products SET price = %s WHERE product_id = %s"
                self.db_manager.execute_query(query, (new_price, self.product_id))
            return True
        else:
            print("价格不能为负数")
            return False
        
    def update_stock(self, quantity):
        """更新库存"""
        new_stock = self.stock + quantity
        if new_stock >= 0:
            self.stock = new_stock
            print(f"{self.name}库存更新为:{self.stock}")

            # 更新数据库
            if self.db_manager:
                query = "UPDATE products SET stock = %s WHERE product_id = %s"
                self.db_manager.execute_query(query, (new_stock, self.product_id))
            return True
        else:
            print("库存不能为负数")
            return False
        
    def get_product_info(self):
        """获取商品信息"""
        if self.stock > 0:
            status = "有货"
        else:
            status = "缺货"
        return f"{self.name} | 价格: {self.price}元 | 库存: {self.stock}| {status}| 分类:{self.category}"

    @classmethod
    def load_from_db(cls, db_manager, product_id):
        """从数据库加载商品"""
        query = "SELECT product_id, name, price, stock, category FROM products WHERE product_id = %s"
        result = db_manager.execute_query(query, (product_id,))

        if result:
            product_data = result[0]
            return cls(
                product_id = product_data[0],
                name = product_data[1],
                price = float(product_data[2]),
                stock = product_data[3],
                category = product_data[4],
                db_manager = db_manager

            )
        return None
    
class ShoppingCart:
    """购物车类"""

    def __init__(self, db_manager=None):
        self.items = {} # 商品对象: 数量
        self.total_amount = 0
        self.db_manager = db_manager

    def _calculate_total(self):
        """计算总金额"""
        self.total_amount = sum(product.price * quantity for product, quantity in self.items.items())

    def add_item(self, product, quantity=1):
        """添加商品到购物车"""
        if quantity <= 0:
            print("数量必须大于0")
            return False
        
        if product.stock < quantity:
            print(f"库存不足！当前库存{product.stock}")
            return False
        
        if product in self.items:
            self.items[product] += quantity
        else:
            self.items[product] = quantity

        self._calculate_total()
        print(f"已添加{quantity}件{product.name}到购物车")
        return True

    def remove_item(self, product, quantity=None):
        """从购物车移除商品"""
        if product not in self.items:
            print("购物车无此商品")
            return False

        if quantity is None or quantity >= self.items[product]:
            # 移除全部
            removed_quantity = self.items[product]
            del self.items[product]
            print(f"已从购物车移除{removed_quantity}件{product.name}")

        else:
            # 移除部分
            self.items[product] -= quantity
            print(f"已从购物车移除{quantity}件{product.name}")

        self._calculate_total()
        return True

    def update_quantity(self, product, new_quantity):
        """更新商品数量"""
        if new_quantity <= 0:
            self.remove_item(product)
            return True

        if product.stock < new_quantity:
            print(f"库存不足！ 当前库存:{product.stock}")
            return False

        self.items[product] = new_quantity
        self._calculate_total()
        print(f"已更新{product.name} 数量为:{new_quantity}")
        return True

    def get_cart_info(self):
        """获取购物车信息""" 
        if not self.items:
            return "购物车为空" 

        info = "\n 购物车内容:\n"
        info += "="*50 + "\n"
        for product, quantity in self.items.items():
            subtotal = product.price * quantity
            info += f"{product.name}x{quantity} = {subtotal}元\n" 

        info += "="*50 + "\n"
        info += f"总金额:{self.total_amount}元\n"
        return info

    def clear_cart(self):
        """清空购物车"""
        self.items.clear()
        self.total_amount = 0
        print("购物车已经清空")

    def save_order_to_db(self):
        """保存订单到数据库"""
        if not self.db_manager or not self.items:
            return None
        try:
            # 插入订单
            order_query = "INSERT INTO orders (total_amount) VALUES (%s)"
            order_params = (self.total_amount,) 
            self.db_manager.execute_query(order_query, order_params)

            # 获取刚插入的订单ID
            order_id_query = "SELECT LAST_INSERT_ID()"
            order_id_result = self.db_manager.execute_query(order_id_query)
            order_id = order_id_result[0][0] if order_id_result else None

            # 插入订单详情
            for product, quantity in self.items.items():
                item_query = """
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """  
                item_params = (order_id, product.product_id, quantity, product.price)
                self.db_manager.execute_query(item_query, item_params)

            print(f"订单 #{order_id}已经保存到数据库")
            return order_id
        except Error as e:
            print(f"保存订单失败:{e}")
            return None
        
    def checkout(self):
        """结算"""
        if not self.items:
            print("购物车为空，无法结算")
            return False
        
        print("\n" + "="*50)
        print("            结算订单")
        print("="*50)
        print(self.get_cart_info())
        print("="*50)

        # 检查库存
        for product, quantity in self.items.items():
            if product.stock < quantity:
                print(f"{product.name}库存不足，当前库存:{product.stock}")
                return False
        
        # 确认购买
        confirm = input("确认购买?(y/n):").lower()
        if confirm != 'y':
            print("已取消购买")
            return False
        
        # 更新库存
        for product, quantity in self.items.items():
            product.update_stock(-quantity)

        
        # 保存订单到数据库
        order_id = self.save_order_to_db()

        if order_id:
            print(f"购买成功！订单号: #{order_id}, 感谢您的光临！")
            self.clear_cart()
            return True
        
        else:
            print("订单保存失败")
            return False
        
class ProductManager:
    """商品管理类"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.products = {}
        self.categories = set()
        self.load_products_from_db()

    def load_products_from_db(self):
        """从数据库加载所有商品"""
        query = "SELECT product_id, name, price, stock, category FROM products"
        results = self.db_manager.execute_query(query)

        for  product_data in results:
            product = Product(
                product_id=product_data[0],
                name=product_data[1],
                price=float(product_data[2]),
                stock=product_data[3],
                category=product_data[4],
                db_manager=self.db_manager

            )
            self.products[product_data[0]] = product
            if product_data[4]:
                self.categories.add(product_data[4])

        print(f"从数据库加载了{len(self.products)}个商品")


    def add_product(self, product_id, name, price, stock, category=""):
        """添加商品"""
        if product_id in self.products:
            print("商品ID已经存在")
            return False

        product = Product(product_id, name, price, stock, category, self.db_manager)

        # 保存到数据库
        if product.save_to_db():
            self.products[product_id] = product
            if category:
                self.categories.add(category)
                return True
            else:
                print("保存到数据库失败")
                return False

    def remove_product(self, product_id):
        """移除商品"""
        if product_id not in self.products:
            print("商品不存在")
            return False

        # 从数据库中删除
        query = "DELETE FROM products WHERE product_id = %s"
        if self.db_manager.execute_query(query, (product_id,)):
            product_name = self.products[product_id].name
            del self.products[product_id]
            print(f"商品{product_name}已移除") 
            return True
        else:
            print("从数据库删除失败")
            return False

    def find_product(self, product_id):
        """查找商品"""
        return self.products.get(product_id)

    def display_products(self, category=None):
        """显示商品列表"""
        if not self.products:
            print("暂时没有该商品")
            return

        print(f"\n商品列表{'-' + category if category else ''}")
        print("="*60)

        displayed = False
        for product in self.products.values():
            if category is None or product.category == category:
                print(f"{product.product_id}|{product.get_product_info()}")
                displayed = True

        if not displayed:
            print("暂无此类商品") 
        print("="*60)

    def display_categries(self):
        """显示分类""" 
        if not self.categories:
            print("暂无分类")
            return
        print("\n商品分类")
        for i, category in enumerate(self.categories, 1):
            print(f"{i}.{category}")

    def view_order_history(self):
        """查看订单历史"""
        query = """
            SELECT o.order_id, o.total_amount, o.order_date,
                   GROUP_CONCAT(CONCAT(p.name, 'x', oi.quantity) SEPARATOR ', ') as items
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN products p ON oi.product_id = p.product_id
            GROUP BY o.order_id
            ORDER BY o.order_date DESC
            LIMIT 10
        """   
        results = self.db_manager.execute_query(query)

        if not results:
            print("暂无订单记录")
            return
        print("\n最近订单记录:")
        print("="*70)
        for order in results:
            print(f"订单号: #{order[0]} | 总金额: {order[1]}元 | 时间: {order[2]}")  
            print(f"商品: {order[3]}")
            print("-"*70)


class ECommerceSystem:
    """电商系统类界面"""

    def __init__(self):
        # 数据库配置 - 请根据您的mysql 设置修改这些参数
        self.db_manager = DatabaseManager(
            host="localhost",
            user="root",
            password="Password2025",
            database="apple_shop"
        )      

        self.product_manager = ProductManager(self.db_manager)
        self.shopping_cart = ShoppingCart(self.db_manager)
        self.running = True

    def display_menu(self):
        """显示主菜单"""
        print("\n" + "="*60)
        print("            Apple购物系统")
        print("="*60)
        print("1. 浏览商品")
        print("2. 添加商品到购物车")
        print("3. 查看购物车")
        print("4. 管理购物车")
        print("5. 结算订单")
        print("6. 商品管理")
        print("7. 查看订单历史")
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
                print("输入格式有误，请重新输入")

    
    def browse_products(self):
        """浏览商品"""
        print("\n1. 浏览所有商品")
        print("2. 按分类浏览")
        print("3. 返回")

        choice = self.get_input("请选择:", int)

        if choice == 1:
            self.product_manager.display_products()
        elif choice == 2:
            self.product_manager.display_categries()
            category = self.get_input("请输入分类名称:", allow_empty=True)
            self.product_manager.display_products(category)

        elif choice == 3:
            return
        else:
            print("无效选择")

    def add_to_cart(self):
        """添加商品到购物车"""
        self.product_manager.display_products()

        product_id = self.get_input("\n请输入要添加的商品ID:")
        product = self.product_manager.find_product(product_id)

        if not product:
            print("商品不存在")
            return
        if product.stock <= 0:
            print("该商品已售罄")
            return
        print(f"\n商品信息:{product.get_product_info()}")
        quantity = self.get_input("请输入购买数量:", int)
        self.shopping_cart.add_item(product, quantity)

    def manage_cart(self):
        """管理购物车"""
        if not self.shopping_cart.items:
            print("购物车为空")
            return
        
        print(self.shopping_cart.get_cart_info())
        print("\n1. 修改数量")
        print("2. 移除商品")
        print("3. 清空购物车")
        print("4. 返回")

        choice = self.get_input("请选择:", int)
        if choice == 1:
            product_id = self.get_input("请输入商品ID:")
            product = self._find_product_in_cart(product_id)
            if product:
                new_quantity = self.get_input("请输入新数量:", int)
                self.shopping_cart.update_quantity(product, new_quantity)

            elif choice == 2:
                product_id = self.get_input("请输入商品ID:")
                product = self._find_product_in_cart(product_id)
                if product:
                    self.shopping_cart.remove_item(product)
            elif choice == 3:
                confirm = input("确定清空购物车？(y/n):").lower()
                if confirm == 'y':
                    self.shopping_cart.clear_cart()

            elif choice == 4:
                return
            else:
                print("无效选择")

    def _find_product_in_cart(self, product_id):
        """在购物车中查找商品"""
        for product in self.shopping_cart.items.keys():
            if product.product_id == product_id:
                return product
        print("购物车中无此商品")
        return None
    
    def product_management(self):
        """商品管理"""
        print("\n1. 添加商品")
        print("2. 移除商品")
        print("3. 修改价格")
        print("4. 更新库存")
        print("5. 返回")

        choice = self.get_input("请选择:", int)
        if choice == 1:
            self._add_product()

        elif choice == 2:
            self._remove_product()

        elif choice == 3:
            self._update_price()

        elif choice == 4:
            self._update_stock()

        elif choice == 5:
            return
        else:
            print("无效选择")

    def _add_product(self):
        """添加商品"""
        print("\n 添加商品")
        product_id = self.get_input("商品ID:")
        name = self.get_input("商品名称:")
        price = self.get_input("商品价格:", float)
        stock = self.get_input("库存:", int)
        category = self.get_input("分类（可选）:", allow_empty=True)

        self.product_manager.add_product(product_id, name, price, stock, category)

    def _remove_product(self):
        """移除商品"""
        self.product_manager.display_products()
        product_id = self.get_input("\n请输入要溢出的商品ID:")
        self.product_manager.remove_product(product_id)

    def _update_price(self):
        """修改价格"""
        self.product_manager.display_products()
        product_id = self.get_input("\n 请输入要修改价格的商品ID:")
        product = self.product_manager.find_product(product_id)

        if product:
            new_price = self.get_input("请输入新价格:", float)
            product.update_price(new_price)

        else:
            print("商品不存在")

    def _update_stock(self):
        """更新库存"""
        self.product_manager.display_products()
        product_id = self.get_input("\n请输入要更新库存的商品ID:")
        product = self.product_manager.find_product(product_id)

        if product:
            quantity = self.get_input("请输入库存变化量(正数增加，负数减少):", int)
            product.update_stock(quantity)
        else:
            print("商品不存在")

    def run(self):
        """运行系统"""
        print("欢迎使用Apple购物系统")
        while self.running:
            self.display_menu()
            choice = self.get_input("请选择操作(0-7):", int)

            if choice == 0:
                print("感谢使用, 再见！")
                self.db_manager.close()
                self.running = False

            elif choice == 1:
                self.browse_products()

            elif choice == 2:
                self.add_to_cart()

            elif choice == 3:
                print(self.shopping_cart.get_cart_info())

            elif choice == 4:
                self.manage_cart()

            elif choice == 5:
                self.shopping_cart.checkout()

            elif choice == 6:
                self.product_management()

            elif choice == 7:
                self.product_manager.view_order_history()
            
            else:
                print("无效选择，请重新输入")

            # 暂停一下让用户看到结果
            if self.running:
                input("\n按回车键继续...")

# 运行系统
if __name__ == "__main__":
    system = ECommerceSystem()
    system.run()
