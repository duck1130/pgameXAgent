n = int(input("請輸入層數(1~9): "))
if n > 9:
    print("層數不能超過9")
else:
    for i in range(1, n + 1):
        print(str(i) * i)
