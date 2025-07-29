import random

answer = random.randint(0, 100)
low = 0
high = 100

while True:
    guess = int(input(f"請輸入{low}~{high}的整數:"))
    if guess == answer:
        print("恭喜猜中!")
        break
    elif guess > answer:
        print("再小一點")
        if guess < high:
            high = guess
    else:
        print("再大一點")
        if guess > low:
            low = guess
