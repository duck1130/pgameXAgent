# sort:將list中的元素進行排列，預設是由小到大
L = [1, 3, 4, 2, 5]
L.sort()
print(L)  # [1, 2, 3, 4, 5]
# 從大到小(降序排列)
L.sort(reverse=True)
print(L)  # [5, 4, 3, 2, 1]

# 算術指定運算子
a = 5
a += 2  # a = a + 2
print(a)  # 7
a -= 3  # a = a - 3
print(a)  # 4
a *= 2  # a = a * 2
print(a)  # 8
a /= 4  # a = a / 4
print(a)  # 2.0
a %= 2  # a = a % 2
print(a)  # 0.0
a **= 3  # a = a ** 3
print(a)  # 0.0
a //= 2  # a = a // 2
print(a)  # 0.0

# while 迴圈
# while loop
# while = true 會造成無限迴圈
# while = false 會直接跳過

a = 1
while a < 5:
    a += 1
    print(a)
    a += 1  # a = a + 1
    # 輸出 2, 4, 6

# break可以跳出迴圈
# 先判斷break屬於哪個迴圈，然後跳出該迴圈
while a < 5:
    print(a)

    for i in range(5):
        print(i)

    if a == 4:
        break  # 跳出迴圈，屬於外層的 while 迴圈
    a += 1

for i in range(5):
    print(i)
    if i == 3:
        break  # 跳出迴圈，屬於內層的 for 迴圈
