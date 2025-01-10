'''
반복문 : for, while
for 문의 구조
for 조건:
    수행문 . . .
'''
for x in (1,2,3,4,5):
    print(f"{x}번째 반복입니다.")

'''while 문의 구조 
while 조건:
    수행문1 
    수행문2
    . . .
'''
i = 0 
while i < 5:
    print(i)
    i += 1
print(i)
'''
while문을 이용한 무한루프

while True:
    print("무한루프입니다. 종료하려면 Ctrl + C를 누르세요.")
'''
#break 문읠 사용한 방복 중단
for i in range(1, 11):
    if i > 5:
        break
    print(i)    

#이중반복문을 이용한 구구단 출력
for i in range(2, 10):
    for j in range(1,10):
        print(f"{i}*{j}={i*j}")
    print("-" *10)