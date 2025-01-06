# # 데이터 타입은 컴퓨터가 데이터를 처리할 때 그 값을 어떻게 해석하고 저장할지 정해주는 분류 체계다.
# 예를 들어 숫자 '1'과 문자 '1' 은 겉보기에 같지만 컴퓨터는 다르게 처리한다. 
# int형 1 은 숫자로 계산이 가능하지만 (1 + 1 = 2)
# str형 "1" 은 문자로 인식되어 다르게 처리된다 ("1"+"1" = "11")

# 그래서 우리가 코딩할 때 변수에 어떤 종류(타입)의 데이터를 저장하는지 이해하고 있어야한다.

#None Type : 값이 없음을 나타냄
result = None # 아직 값이 할당되지 않은 상태

#Bool: True 또는 False 값을 가지는 논리형 데이터 타입
is_student = True
has_passport = False

#int, float, complex : 숫자형
# 정수 (Integer) 1, -5, 100 과 같은 정수를 나타내는 데이터 타입
age = 24
count = -10
# 실수 (Float) 3.14, -0.001 과 같은 소수점이 있는 실수를 나타내는 데이터 타입
pi =  3.14159
temperature = -5.2
# 복소수 (Complex) 3+4j와 같은 복소수를 나타내는 데이터타입
z = 3 + 4j

#str : 문자열
name = "정익상"
message = "안녕하세요!"

#list, tuple : 시퀀스형(Sequence Type)
# 리스트 (List) - 변경 가능
fruits = ['사과', '바나나', '오렌지']
numbers = [1, 2, 3, 4, 5]

#튜플(Tuple) - 변경 불가능
coordinates = (3, 4)
rgb = (255, 0, 0)

#function: def로 정의하는 함수 타입으로, 특정 동작을 수행하는 코드블록
# 1. 일반적인 함수 정의
def hello():
    print("안녕하세요!")

# 2. 함수의 데이터 타입
print(type(hello)) # <class 'function'>

# 3. 함수를 변수에 담기
my_func = hello
my_func() # 안녕하세요! 출력

# 4. 함수를 리스트에 담기
func_list = [hello, my_func]
func_list[0]() # 안녕하세요! 출력