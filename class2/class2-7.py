# file:class2-7 錯誤處理與函數定義

# ============================================
# 主題1: Try-Except 錯誤處理
# ============================================
# 語法: try: 可能出錯的程式碼  except: 錯誤處理
# 用途: 避免程式因錯誤而中斷執行

try:
    n = int(input("請輸入一個數字: "))
except:
    print("發生錯誤！")

# ============================================
# 主題2: 函數定義與呼叫
# ============================================
# 語法: def 函數名稱():
# 用途: 將重複使用的程式碼包裝成函數


# 2-1 基本函數定義（無參數）
def hello():
    print("Hello, World!")


# 2-2 函數呼叫 - 迴圈中重複執行
for i in range(5):
    hello()  # 呼叫函數

# ============================================
# 主題3: 有參數的函數
# ============================================
# 語法: def 函數名稱(參數名稱):
# 用途: 讓函數可以接收外部資料進行處理


def hello(name):
    print(f"Hello, {name}!")


# 3-1 函數呼叫並傳入不同參數
hello("Alice")  # 呼叫函數，傳入參數
hello("Bob")  # 呼叫函數，傳入參數
hello("Charlie")  # 呼叫函數，傳入參數

# ============================================
# 主題4: 基本迴圈複習
# ============================================
# range(10) 產生 0~9 的數字
for i in range(10):
    print(i)

# ============================================
# 主題5: 有回傳值的函數
# ============================================
# 語法: def 函數名稱(): return 回傳值
# 用途: 讓函數可以回傳計算結果


# 5-1 單一回傳值
def add(a, b):
    return a + b


result = add(5, 3)
print(result)  # 輸出: 8


# 5-2 多個回傳值
def add_and_subtract(a, b):
    return a + b, a - b


sum_result, diff_result = add_and_subtract(5, 3)
print(sum_result)  # 輸出: 8
print(diff_result)  # 輸出: 2
print(f"和: {sum_result}, 差: {diff_result}")  # 輸出: 和: 8, 差: 2

# ============================================
# 主題6: 預設參數值
# ============================================
# 語法: def 函數名稱(參數, 參數=預設值):
# 用途: 當沒有傳入參數時使用預設值


def hello(name, message="Hello"):
    print(f"{message}, {name}!")


hello("Alice")  # 使用預設值
hello("Bob", "Hi")  # 使用自訂值

# ============================================
# 主題7: 型態註解
# ============================================
# 語法: def 函數名稱(參數:型態) -> 回傳型態:
# 用途: 標明參數和回傳值的型態（建議）


def add(a: int, b: int) -> int:
    return a + b


print(add(5, 3))  # 輸出: 8
print(add("hello", "world"))  # 這行不會報錯 但會輸出字串相加結果

# ============================================

# def區域變數

length = 10  # 全域變數


def calculate_square_area():
    area = length**2
    # area是區域變數
    # length是全域變數
    print("面積是", area)  # 輸出: 面積是 100


calculate_square_area()  # 呼叫函數


length = 10  # 全域變數


def calculate_square_area():
    area = length**2
    print("面積是", area)  # 輸出: 面積是 100


length = 20  # 修改全域變數
calculate_square_area()  # 呼叫函數，輸出: 面積是 400


length = 10  # 全域變數
area = 20  # 全域變數


def calculate_square_area():
    area = length**2  # 區域變數


calculate_square_area()
print("面積是", area)  # 輸出: 面積是 20
# 指令內部的area變數不影響全域變數area


length = 10  # 全域變數
area = 20  # 全域變數


def calculate_square_area() -> int:
    area = length**2  # 區域變數
    return area


area = calculate_square_area()  # 呼叫函數並取得回傳值
print("面積是", area)  # 輸出: 面積是 100


length = 10  # 全域變數
area = 20  # 全域變數


def calculate_square_area():
    global area  # 使用全域變數area
    area = length**2  # 修改全域變數area


calculate_square_area()  # 呼叫函數
print("面積是", area)  # 輸出: 面積是 100


def hello(name: str):
    """
    你好的意思(ˊ・ω・ˋ)
    """
    print(f"Hello, {name}!")  # 輸出: Hello, name!
