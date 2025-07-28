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
6. not
7. and
8. or
"""

# 密碼門檢查
password = input("請輸入密碼：")
if password == "1234":
    print("密碼正確，歡迎duck進入系統！")
elif password == "5678":
    print("密碼正確，歡迎joyce進入系統！")
else:
    print("密碼錯誤，請重新輸入！")
# elif 可以用來檢查多個條件，排除前面有判斷過的條件後，執行符合的條件
