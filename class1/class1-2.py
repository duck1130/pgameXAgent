# 讓使用者輸入半徑，計算圓形面積

r = input("請輸入圓的半徑：")
r = float(r)  # 轉成浮點數
pi = 3.14
area = pi * r * r
print(f"半徑為 {r} 的圓形面積為 {area}")
