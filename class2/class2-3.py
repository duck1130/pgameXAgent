# 匯入 random 模組，並以 r 作為別名，方便後續呼叫
import random as r

# random.randrange() 設定抽籤範圍的方式與 range() 相同
# 產生一個指定範圍內的隨機整數（不包含上限值）
print(r.randrange(10))  # 會印出 0~9 之間的隨機整數

# 指定起始值與終止值，產生 1~9 之間的隨機整數（不包含 10）
print(r.randrange(1, 10))  # 會印出 1~9 之間的隨機整數

# 指定起始值、終止值與步進值，產生 1~9 之間的隨機奇數（不包含 10，步進為 2）
print(r.randrange(1, 10, 2))  # 會印出 1~9 之間的隨機奇數

# random.randint() 設定抽籤範圍的方式與 randrange() 相同
# 但 randint() 產生的隨機整數是「包含」上限值的
print(r.randint(1, 10))  # 會印出 1~10 之間的隨機整數
