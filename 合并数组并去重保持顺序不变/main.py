def input_array():
    """定义一个数组"""
    numbers = input("请在此输入数字（以空格分隔）：").split()
    return [int(x) for x in numbers]

def remove_duplicates(arr):
    """去掉重复的元素但是保持顺序"""
    seen = set()
    result = []
    for num in arr:
        if num not in seen:
            seen.add(num)
            result.append(num)
    return result


def main():
    arr1 = input_array()
    arr2 = input_array()

    print("第一个数组是：",arr1)
    print("第二个数组是：",arr2)

    merged_array = arr1 + arr2
    print("合并后的数组是：",merged_array)

    new_array = remove_duplicates(merged_array)
    print("去重后的新数组为：",new_array)


# 调用程序
main()

