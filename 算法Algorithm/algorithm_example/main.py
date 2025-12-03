# 我们来写一个不同算法情况下程序执行时间的比较

# 枚举式
import time

start_time = time.time()

for a in range(1, 1000):
    for b in range(1, 1000):
        for c in range(1, 1000):
            if a + b + c == 1000 and a**2 + b**2 == c**2:
                print(f"a={a}, b={b}, c={c}")

end_time = time.time()

running_time = end_time - start_time

print(f"总共运行时长为: {running_time}")

# 程序运行结果为
(my_ba_venv) pengchaoma@Pengchaos-MacBook-Pro test_09 % python3 main1.py 
a=200, b=375, c=425
a=375, b=200, c=425
总共运行时长为: 563.5402629375458
----------------------------------------
# 我们稍作改动 

import time

start_time = time.time()

for a in range(1, 1000):
    for b in range(1, 1000):
            c = 1000 - a - b # 将 c 用 1000 - a - b 代替
            if c > 0 and a**2 + b**2 == c**2: # c 是正数 
                print(f"a={a}, b={b}, c={c}")

end_time = time.time()

running_time = end_time - start_time

print(f"总共运行时长为: {running_time}")

# 程序运行解雇为
(my_ba_venv) pengchaoma@Pengchaos-MacBook-Pro test_09 % python3 main1.py 
a=200, b=375, c=425
a=375, b=200, c=425
总共运行时长为: 0.9553611278533936

----------------------------------------
对比总共运行时间，我们可以发现，下面的算法效率要远高于上面 ， 这就很好说明不同算法的效率有巨大差距



