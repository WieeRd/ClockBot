# KoreanNumber

한글 <-> 숫자 변환 라이브러리

## Number -> Korean

```python

import num2kr

# num = int(input("Integer: "))
num = 12345678
print(num2kr.num2kr(num)) # same as num2kr(num, 0)
print(num2kr.num2kr(num, 1))

# >>> 1234만 5678
# >>> 일천이백삼십사만오천육백칠십팔

```

## Korean -> Number

```python

import kr2num

# kr_str = input("Korean: ")
kr_str = "일조삼천육백칠십일억이천구백삼십칠만사천오백십일"
print(kr2num.kr2num(kr_str))

# >>> 1367129374511

```


## Credit

kr2num: forked from https://github.com/codertimo/korean2num  
num2kr: inspired by https://m.blog.naver.com/wideeyed/221771836059
