# 定义生成列表的函数
def get_list():
    numbers = input("请在此输入数字(数字之间以空格隔开):").split()
    return [int(x) for x in numbers]


# 定义一个去重并保持列表元素顺序的函数
def remove_duplicates_perverse_orders(my_lst):
    seen = set()
    result = []
    for i in my_lst:
        if i not in seen:
            seen.add(i)
            result.append(i)
    return result

# 定义一个两个列表相加生成新列表的函数
def new_list(lst1, lst2):
    result = lst1 + lst2
    return result

# 定义一个列出列表索引和对应的元素的函数
def get_index_values(lst):
    for index, values in enumerate(lst):
        print(f"索引为{index}, 对应的元素为:{values}")

# 定义 main 函数
def main():
    lst1 = get_list()
    lst2 = get_list()
    my_new_list = new_list(lst1, lst2)
    print(my_new_list)
    unique_list = remove_duplicates_perverse_orders(my_new_list)
    print(unique_list)
    get_index_values(unique_list)

# 调用main 函数

main()


    
    


