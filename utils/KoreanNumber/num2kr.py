digit_name = ['영', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구']
unit = ['', '십', '백', '천']
unit_10k = ['', '만', '억', '조', '경', '해', '자', '양', '구', '간', '정', '재', '극', '항하사', '아승기', '나유타', '불가사의', '무량대수']

# (1234, 100) -> [34, 12]
def split_digit(num:int, div:int = 10) -> list:
	ret = []
	while num!=0:
		num, rem = divmod(num, div)
		ret.append(rem)
	return ret

def num2kr(num : int, mode=0) -> str:
	if num>=pow(10000, len(unit_10k)+1):
		raise ValueError("Value exceeds 10e72; cannot be read")

	digit_10k = split_digit(num, 10000)

	if mode==1:
		for i in range(len(digit_10k)):
			digit = split_digit(digit_10k[i])
			tmp = []
			for j in range(len(digit)):
				if digit[j]!=0:
					tmp.append(digit_name[digit[j]] + unit[j])
			digit_10k[i] = ''.join(reversed(tmp))

	kr_str = []
	for i in range(len(digit_10k)):
		if digit_10k[i]!=0:
			kr_str.append(str(digit_10k[i]) + unit_10k[i])

	glue = '' if mode==1 else ' '
	kr_str = glue.join(reversed(kr_str))

	return kr_str