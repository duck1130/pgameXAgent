# open()
# r 讀取模式 檔案必須存在
# w 寫入模式 檔案不存在會自動建立
# a 附加模式 檔案不存在會自動建立
# r+ 讀+寫模式 檔案必須存在
# w+ 寫+讀模式 檔案不存在會自動建立
# a+ 附加+讀模式 檔案不存在會自動建立

f = open("class3-1.txt", "w")  # 開啟檔案 class3-1.txt，若不存在則建立
content = f.read()  # 讀取檔案內容
print(content)  # 印出檔案內容
f.close()  # 關閉檔案

with open("class3-1.txt", "w") as f:  # 使用 with 語句自動管理檔案開啟與關閉
    content = f.read()  # 讀取檔案內容
    print(content)  # 印出檔案內容

# 不用寫 f.close()，因為 with 語句會自動關閉檔案
