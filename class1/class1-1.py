# Python 輸出、註解與基本型態

# --- 輸出與註解 ---
print("hello")  # 輸出字串 "hello" 到螢幕

"""
這是多行註解
可以寫多行說明，通常用於區塊註解
"""

# 這是單行註解：用於說明某一行程式碼
# 在大多數編輯器可用 ctrl + / 快速註解

"""
--- 基本型態 ---
Python 常見資料型態有：整數、浮點數、字串、布林
"""
print(1)  # 整數 int，輸出 1
pi = 3.14  # 浮點數 float，帶小數點
name = "Joyce"  # 字串 str，用引號包住的文字
is_student = True  # 布林 bool，只有 True 或 False

print(pi)  # 輸出 3.14
print(name)  # 輸出 Joyce
print(is_student)  # 輸出 True

"""
--- 變數 ---
變數用來儲存資料，名稱可自訂，等號=用來指定值
"""
A = 1  # 整數變數
B = 2.5  # 浮點數變數
C = "Hello"  # 字串變數
D = False  # 布林變數
print(A, B, C, D)  # 一次輸出多個變數

"""
--- 運算子 ---
算術運算子：+ 加、- 減、* 乘、/ 除、// 整數除、% 餘數、** 次方
"""
a = 10
b = 3
print(a + b)  # 加法，輸出 13
print(a - b)  # 減法，輸出 7
print(a * b)  # 乘法，輸出 30
print(a / b)  # 除法，輸出 3.333...
print(a // b)  # 整數除法，輸出 3
print(a % b)  # 取餘數，輸出 1
print(a**b)  # 次方，輸出 1000

"""
比較運算子：用來比較大小，結果為布林值
"""
print(a > b)  # 大於，True
print(a < b)  # 小於，False
print(a == b)  # 等於，False
print(a != b)  # 不等於，True
print(a >= b)  # 大於等於，True
print(a <= b)  # 小於等於，False

"""
邏輯運算子：用於布林值運算
"""
x = True
y = False
print(x and y)  # 且，兩者都為 True 才是 True，這裡輸出 False
print(x or y)  # 或，有一個為 True 就是 True，這裡輸出 True
print(not x)  # 非，將 True 變成 False，這裡輸出 False

"""
--- 運算子優先順序 ---
當一行有多個運算子時，會依照優先順序計算
1. 括號 ()
2. 次方 **
3. 乘除 * / // %
4. 加減 + -
5. 比較 < <= > >= == !=
6. 邏輯 and
7. 邏輯 or
"""
result1 = 2 + 3 * 4  # 先算 3*4=12，再加2，結果為14
result2 = (2 + 3) * 4  # 先算2+3=5，再乘4，結果為20
result3 = 2**3 * 2  # 先算2**3=8，再乘2，結果為16
result4 = 10 - 3 + 2  # 從左到右，10-3=7，再加2，結果為9

print(result1)  # 輸出 14
print(result2)  # 輸出 20
print(result3)  # 輸出 16
print(result4)  # 輸出 9

"""
--- 字串運算 ---
"""
str1 = "Hello"
str2 = "World"
print(str1 + " " + str2)  # 字串相加，輸出 "Hello World"
print(str1 * 3)  # 字串重複，輸出 "HelloHelloHello"

"""
--- 字串格式化 ---
f-string 是 Python 3.6 以上的字串格式化方式，可以在字串前加 f，並用大括號 {} 放入變數或運算式
"""
age = 20
print(f"我今年 {age} 歲")  # 正確：輸出 "我今年 20 歲"

# 錯誤示範：忘記加 f，變數不會被取代
print("我今年 {age} 歲")  # 輸出 "我今年 {age} 歲"（變數未被帶入）

# 注意：大括號內只能放變數或運算式，不能直接放字串引號
# print(f"我今年 {"age"} 歲")  # 這樣會出錯，因為 "age" 是字串，不能直接放在大括號內

# 正確：可以放運算式
print(f"明年我 {age + 1} 歲")  # 輸出 "明年我 21 歲"

"""
--- 其他常用函數 ---
"""
print(len("Hello"))  # 字串長度，輸出 5
print(len(str1 + " " + str2))  # 輸出 11，因為有空格
print(len(","))  # len是個函數,可以計算字串長度

# type() 函數可以檢查變數的型態
print(type(pi))  # 輸出 <class 'float'>，表示 pi 是浮點數
print(type(name))  # 輸出 <class 'str'>，表示 name 是字串
print(type(is_student))  # 輸出 <class 'bool'>，表示 is_student 是布林值

"""
--- 型態轉換 ---
可以用 int()、float()、str()、bool() 來轉換型態
"""
print(int(3.14))  # float 轉 int，輸出 3
print(float(1))  # int 轉 float，輸出 1.0
print(str(100))  # int 轉 str，輸出 "100"
print(bool(0))  # 0 轉 bool，輸出 False
print(bool(1))  # 1 轉 bool，輸出 True

# 更多型態轉換例子
print(int("123"))  # 字串轉 int，輸出 123
print(float("3.14"))  # 字串轉 float，輸出 3.14
print(str(3.14))  # float 轉 str，輸出 "3.14"
print(bool(""))  # 空字串轉 bool，輸出 False
print(bool("abc"))  # 非空字串轉 bool，輸出 True
print(int(True))  # 布林轉 int，True 變 1
print(int(False))  # 布林轉 int，False 變 0
print(float(False))  # 布林轉 float，False 變 0.0
print(str(False))  # 布林轉 str，輸出 "False"
print(bool([]))  # 空串列轉 bool，輸出 False
print(bool([1, 2, 3]))  # 非空串列轉 bool，輸出 True

# 錯誤示範（執行會報錯，僅供參考）
# print(int("abc"))    # 字串 "abc" 不能轉成 int，會產生 ValueError
# print(float("hi"))   # 字串 "hi" 不能轉成 float，會產生 ValueError
# print(int("3.14"))   # 字串 "3.14" 不能直接轉 int，會產生 ValueError


print("輸入開始")  # 開始輸入
# input()是一個函數，可以讓使用者輸入資料
A = input("請輸入一個數字：")  # 等待使用者輸入
print(int(A) + 10)  # 將輸入的字串轉成整數並輸出
print(type(A))  # 證明透過input()得到的A是字串型態
