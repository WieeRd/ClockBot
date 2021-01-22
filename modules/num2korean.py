# From https://m.blog.naver.com/wideeyed/221771836059
# Modified lil bit

"""숫자를 자릿수 한글단위와 함께 리턴한다 """
def num2korean(num_amount, ndigits_round=0):
    if(num_amount>=10e52):
        return "읽을 수 있는 최대 숫자, 1 항하사(恒河沙) 초과"
    
    str_result = "" # 결과
    minus = False

    if(num_amount==0):
        return '영'
    elif(num_amount<0):
        minus = True
        num_amount = -num_amount

    num_names = ['영', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구']
    maj_units = ['만', '억', '조', '경', '해', '자', '양', '구', '간', '정', '재', '극'] # 10000 단위
    units     = [' '] # 시작은 일의자리로 공백으로하고 이후 십, 백, 천, 만...
    for mm in maj_units:
        units.extend(['십', '백', '천']) # 중간 십,백,천 단위
        units.append(mm)
    
    list_amount = list(str(round(num_amount, ndigits_round))) # 라운딩한 숫자를 리스트로 바꾼다
    list_amount.reverse() # 일, 십 순서로 읽기 위해 순서를 뒤집는다
    
    num_len_list_amount = len(list_amount)
    
    for i in range(num_len_list_amount):
        str_num = list_amount[i]
        num = int(str_num)
        # 만, 억, 조 단위에 천, 백, 십, 일이 모두 0000 일때는 생략
        if num_len_list_amount >= 9 and i >= 4 and i % 4 == 0 and ''.join(list_amount[i:i+4]) == '0000':
            continue
        if str_num == '0': # 0일 때
            if i % 4 == 0: # 4번째자리일 때(만, 억, 조...)
                str_result = units[i] + str_result # 단위만 붙인다
        elif str_num == '1': # 1일 때
            if i % 4 == 0: # 4번째자리일 때(만, 억, 조...)
                str_result = num_names[num] + units[i] + str_result # 숫자와 단위를 붙인다
            else: # 나머지자리일 때
                str_result = units[i] + str_result # 단위만 붙인다
        else: # 2~9일 때
            str_result = num_names[num] + units[i] + str_result # 숫자와 단위를 붙인다
    str_result = str_result.strip() # 문자열 앞뒤 공백을 제거한다 
    if len(str_result) == 0:
        return None
    
    if(minus):
        str_result = "마이너스 " + str_result
    return str_result
