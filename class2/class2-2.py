shopping_list = []

while True:
    # 顯示購物清單
    print("\n🛒 目前購物清單：")
    if len(shopping_list) == 0:
        print("（清單是空的）")
    if len(shopping_list) > 0:
        i = 0
        while i < len(shopping_list):
            print(str(i) + ": " + shopping_list[i])
            i = i + 1
    print("-" * 20)

    print("請選擇動作：")
    print("1️⃣ 新增東西")
    print("2️⃣ 修改東西")
    print("3️⃣ 刪除東西")
    print("4️⃣ 離開程式")
    choice = input("輸入選項（1/2/3/4）：")

    if choice == "1":
        item = input("請輸入要加入的東西：")
        if item != "":
            shopping_list.append(item)
            print("✅ 已加入：" + item)
            # shopping_list.sort()
        if item == "":
            print("⚠️ 請輸入有效的名稱。")
    elif choice == "2":
        if len(shopping_list) == 0:
            print("⚠️ 清單是空的，無法修改。")
        else:
            idx_str = input("請輸入要修改的編號：")
            is_num = True
            for c in idx_str:
                found_num = False
                j = 0
                while j < len("0123456789"):
                    if c == "0123456789"[j]:
                        found_num = True
                    j = j + 1
                if found_num == False:
                    is_num = False
            if is_num and idx_str != "":
                idx = int(idx_str)
                if idx >= 0 and idx < len(shopping_list):
                    new_item = input("請輸入新的名稱：")
                    if new_item != "":
                        print("✏️ " + shopping_list[idx] + " → " + new_item)
                        shopping_list[idx] = new_item
                    if new_item == "":
                        print("⚠️ 請輸入有效的名稱。")
                else:
                    print("⚠️ 編號超出範圍。")
            else:
                print("⚠️ 請輸入正確的數字編號。")
    elif choice == "3":
        if len(shopping_list) == 0:
            print("⚠️ 清單是空的，無法刪除。")
        else:
            print("選擇刪除方式：")
            print("a. 用名稱刪除（remove）")
            print("b. 用位置刪除（pop）")
            sub_choice = input("輸入 a 或 b：")
            if sub_choice == "a":
                name = input("請輸入要刪除的名稱：")
                found = False
                i = 0
                while i < len(shopping_list):
                    if shopping_list[i] == name:
                        shopping_list.remove(name)
                        print("❌ 已刪除：" + name)
                        found = True
                        break
                    i = i + 1
                if found == False:
                    print("⚠️ 清單中沒有這個項目。")
            elif sub_choice == "b":
                idx_str = input("請輸入要刪除的編號：")
                is_num = True
                for c in idx_str:
                    found_num = False
                    j = 0
                    while j < len("0123456789"):
                        if c == "0123456789"[j]:
                            found_num = True
                        j = j + 1
                    if found_num == False:
                        is_num = False
                if is_num and idx_str != "":
                    idx = int(idx_str)
                    if idx >= 0 and idx < len(shopping_list):
                        removed = shopping_list[idx]
                        shopping_list.pop(idx)
                        print("🗑️ 已刪除：" + removed)
                    else:
                        print("⚠️ 編號超出範圍。")
                else:
                    print("⚠️ 請輸入正確的數字編號。")
            else:
                print("⚠️ 請輸入 a 或 b。")
    elif choice == "4":
        print("👋 掰掰！回家囉～")
        break
    else:
        print("⚠️ 請輸入 1、2、3 或 4。")
        print("⚠️ 請輸入 1、2、3 或 4。")
