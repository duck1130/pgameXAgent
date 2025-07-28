# --- list 基本介紹 ---
# list（串列）是一種可變動的序列，可以存放多個元素，元素型態可以不同

# --- 建立 list（Create）---
numbers = [1, 2, 3]  # 建立一個有三個元素的 list
print(numbers)  # 輸出 [1, 2, 3]

# list 可以存放不同型別的元素
L = [10, "apple", 3.14]
print(L)  # 輸出 [10, 'apple', 3.14]

# --- 讀取 list 元素（Read）---
print(L[0])  # 輸出 10
print(L[1])  # 輸出 apple
print(L[2])  # 輸出 3.14
print(L[-1])  # 輸出 3.14（最後一個）

# --- list 切片（slice）---
print(L[0:2])  # [10, 'apple']
print(L[:2])  # [10, 'apple']
print(L[1:])  # ['apple', 3.14]
print(L[:])  # [10, 'apple', 3.14]
print(L[-2:])  # ['apple', 3.14]

# --- 用 for 迴圈讀取所有元素 ---
for item in L:
    print(item)  # 依序輸出 10, apple, 3.14

# --- 新增元素（Update-新增）---
L.append("banana")  # 新增元素到最後
print(L)  # [10, 'apple', 3.14, 'banana']

# --- 移除元素（Delete）---
L.remove("apple")  # 移除指定元素
print(L)  # [10, 3.14, 'banana']

# --- for 迴圈與 range 的差異 ---
# 第一段只印出索引0和2的元素（每隔2個取一次），輸出 10, 3.14
# 第二段依序印出所有元素，輸出 10, apple, 3.14, banana
L = [10, "apple", 3.14, "banana"]
for i in range(0, len(L), 2):
    print(L[i])
for i in L:
    print(i)

# --- 修改 list 中的元素（Update-修改）---
L[1] = "orange"  # 修改索引1的元素
print(L)  # [10, 'orange', 3.14, 'banana']

L[0:2] = [20, "grape"]  # 一次修改多個元素
print(L)  # [20, 'grape', 3.14, 'banana']

# --- 變數的傳遞方式（call by value/reference）---
# 數值型態是 call by value
a = 10
b = a
b = 20
print(a)  # 10
print(b)  # 20

# list 是 call by reference
a = [1, 2, 3]
b = a
b[0] = 10
print(a)  # [10, 2, 3]

# 若要複製 list（避免影響原本的 list）
a = [1, 2, 3]
b = a.copy()
b[0] = 10
print(a)  # [1, 2, 3]
print(b)  # [10, 2, 3]

# call by reference
a = [1, 2, 3]
b = a  # b 會指向 a 的同一個 list
b[0] = 10  # 修改 b 的第一個元素
print(a)  # 輸出 [10, 2, 3]，a 也被修改了

a = [1, 2, 3]
b = a.copy()  # 使用 copy() 方法複製 list
b[0] = 10  # 修改 b 的第一個元素
print(a)  # 輸出 [1, 2, 3]，a 沒有改變
print(b)  # 輸出 [10, 2, 3]，b 被修改了

# list的append
L = [1, 2, 3]
L.append(4)  # 在 list 的末尾新增元素 4
print(L)  # 輸出 [1, 2, 3, 4]

L = ["a", "b", "b", "c"]
L.remove("b")  # 移除第一個出現的 "b"
# 代表remove() 只會移除第一個找到的元素
for i in L:
    if i == "b":
        L.remove(i)

# 使用pop可以移除指定的index元素
L = ["a", "b", "b", "c"]
L.pop(0)  # 移除索引0的元素 "a"
print(L)  # 輸出 ['b', 'b', 'c']
