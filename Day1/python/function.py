#매개변수가 가변하는 예시
def sum_numbers(*args):
    total = 0
    for num in args:
        total += num
    return total

print(sum_numbers(1,2,3,4,5)) # 15
print(sum_numbers(1,2,3))

# 함수 정의 예시
def greet(name):
    print(f"안녕하세요,{name}님".format(name))
greet("정익상") # 안녕하세요, 정익상님

def multiply_numbers(a, b=2):
    return a * b
print(multiply_numbers(2,10)) # 
print(multiply_numbers(3)) # 6

#재귀 함수 예시
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
print(factorial(9)) 

#내부 함수
def outer_function():
    x = 10

    def inner_function():
        print(x)
    inner_function()

outer_function()