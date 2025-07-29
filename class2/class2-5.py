# dict是透過鍵值對（key-value pair）來儲存資料，key是唯一的，value可以重複
# dict是無序的，不能使用索引來存取元素
# 可以透過key來存取對應的value
# dict的value可以是任意資料型態，包括list、tuple、dict等
# dict的key必須是不可變的資料型態，如字串、數字
# key:value
d = {"a": 1, "b": 2, "c": 3}  # 建立一個字典

# 取得dict的key
print(d.keys())  # dict_keys(['a', 'b', 'c'])

# 取得dict的key
print(d.get("a"))  # 1

# 取得dict的value
print(d.values())  # dict_values([1, 2, 3])

# 取得dict的key-value對
print(d.items())  # dict_items([('a', 1), ('b', 2), ('c', 3)])

# 新增/修改dict的key-value對
d = {"a": 1, "b": 2, "c": 3}
d["d"] = 4  # 新增一個key-value對
d["a"] = 5  # 修改一個key-value對

# 如果資料不存在，就回傳預設值
print(d.pop("e", 0))  # 0

# 檢查dict是否包含某個key
# in不能用來檢查value是否存在
# 跟list比，in是用來檢查list的元素和dict的key是否存在
print("a" in d)  # True # 檢查key是否存在
print("M" in d)  # False # 檢查key是否存在

# 比較複雜的dict
d = {
    "a": [1, 2, 3],
    "b": {"c": 4, "d": 5},
}

# value可以是list或dict
print(d["a"])  # [1, 2, 3]
print(d["a"][0])  # 1 # 取得list的第一個元素

print(d["b"])  # {"c": 4, "d": 5} # 取得"b"的value
print(d["b"]["c"])  # 4 # 取得"b"和"c"的value

# 成績登記系統，key是學生姓名，value是成績
grades = {
    "Alice": {"math": [85, 90, 95], "english": [90, 85, 80], "science": [95, 90, 85]},
    "Bob": {"math": [78, 82, 80], "english": [88, 84, 86], "science": [80, 78, 82]},
    "Charlie": {"math": [92, 89, 94], "english": [95, 92, 90], "science": [90, 88, 85]},
}

# 取得alice的數學成績
print(grades["Alice"]["math"])  # [85, 90, 95]

# 取得alice的第一次英文成績
print(grades["Alice"]["english"][0])  # 90

# 每一位學生的平均成績
for student, subjects in grades.items():
    # 逐一取得各科目成績
    # 取得數學成績
    math_scores = subjects["math"]
    avg = sum(math_scores) / len(math_scores)
    print(f"{student} 的數學成績: {math_scores}，平均: {avg:.2f}")
