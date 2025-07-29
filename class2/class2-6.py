fruits = {"蘋果": 25, "香蕉": 20, "橘子": 30}

while True:
    print("=== 水果店價格查詢系統 ===\n")
    print("目前水果價格：")
    for name, price in fruits.items():
        print(f"{name}: {price}元")
    print("\n1. 新增水果價格")
    print("2. 修改水果價格")
    print("3. 刪除水果")
    print("4. 離開系統")
    choice = input("請選擇功能 (1-4): ")
    print("==========================")
    if choice == "1":
        name = input("請輸入要新增的水果名稱: ")
        if name in fruits:
            print(f"{name} 已存在，價格為 {fruits[name]}元")
        else:
            price = input(f"請輸入{name}的價格: ")
            fruits[name] = int(price)
            print(f"{name}已新增，價格 {price}元")
    elif choice == "2":
        name = input("請輸入要修改的水果名稱: ")
        if name in fruits:
            price = input(f"請輸入{name}的新價格: ")
            fruits[name] = int(price)
            print(f"{name}價格已修改為 {price}元")
        else:
            print(f"{name} 不存在")
    elif choice == "3":
        name = input("請輸入要刪除的水果名稱: ")
        if name in fruits:
            fruits.pop(name)
            print(f"{name}已刪除")
        else:
            print(f"{name} 不存在")
    elif choice == "4":
        print("感謝使用水果店價格查詢系統！")
        break
    else:
        print("請輸入1-4之間的數字")
    print("==========================")
