#물건의 가격을 곱해 계산해보세요
#물건 가격 계산하기
apple_price = 500
apple_count = 7

total = apple_price * apple_count
print(f"사과{apple_count}개 가격은 " + str(total) + "원 입니다.")
# 본인 정보 입력받고 출력하기
name = input("이름을 입력해주세요:")
age = input("나이를 입력해주세요:")
height = input("키를 입력해주세요:")

print("제 이름은 " + name + "이고, " + age + "살 입니다. 키는 " + height + "cm 입니다.")

#문자열의 길이를 비교하기
string1 = "안녕하세요!"
string2 = "Python"
print(len(string1) > len(string2)) # True 출력
print(f"{string1}의 길이는 {len(string1)}입니다.")
print(f"{string2}의 길이는 {len(string2)}입니다.")