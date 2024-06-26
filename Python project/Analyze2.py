import pandas as pd
import openpyxl

from data_handling import walking_avg, company_avg
from operator import itemgetter

data = pd.read_csv('20rows.csv')

correlation_df = pd.read_excel('Correlation_Table.xlsx', index_col=0)

# 피벗 테이블 생성: 행은 상권배후지_코드, 열은 서비스_업종_코드_명, 값은 당월_매출_금액
pivot_table = data.pivot_table(index='상권배후지_코드', columns='서비스_업종_코드_명', values='당월_매출_금액', fill_value=0)

# 서비스 목록 가져오기
services = pivot_table.columns.tolist()

# "호프-간이주점"과의 상관관계를 기준으로 정렬된 튜플 리스트 계산
correlation_tuples = [(service, correlation_df.loc["호프-간이주점", service]) for service in services if service != "호프-간이주점"]

sorted_correlation_tuples = sorted(correlation_tuples, key=itemgetter(1), reverse=True)[:10]

# "호프-간이주점"과 가장 높은 상관관계를 가진 상위 10개 서비스 가져오기
top_10_services = [(service, correlation_)for service, correlation_ in sorted_correlation_tuples]

top_10s = [service for service, _ in sorted_correlation_tuples]

# 각 상권마다 상위 10개 서비스의 매출액 계산
result_df = pivot_table.copy()

result_df['가중평균매출액'] = result_df[top_10s].sum(axis=1)

# 이제 그 데이터에 가중치 곱해주기

weights = {k:v for k, v in top_10_services}

for service, weight in weights.items():
    if service in result_df.columns:
        result_df[service] = result_df[service] * weight

# Step 3: 가중 평균 매출액 계산
result_df['가중평균매출액'] = result_df[list(weights.keys())].sum(axis=1)

# 각 상권마다 "호프-간이주점" 매출 비율 계산
result_df['가중평균매출액 대비 호프-간이주점 매출 비율'] = result_df['호프-간이주점'] / result_df['가중평균매출액']

# 소수점 4자리까지 반올림
result_df = result_df.round(4)


# 상권배후지 코드와 상권이 같이 있어야 읽기 편하니까
# result_df에 상권배후지_코드_명을 다 달아줬습니다.
# result_df의 row는 약 1000개(각 상권마다 1개)이므로
# merged의 상권배후지_코드_명을 그대로 합쳤다간 NaN값 도배가 돼서,
# .unique() 함수를 붙여 상권마다 1개씩 나오도록 해서 result_df의 row수와 기가막히게 맞춰줬습니다.

merged = pd.read_csv('merged.csv') # 상권배후지_코드_명이 있는 csv데이터 아무거나 호출했음.
result_df['상권_명'] = merged['상권배후지_코드_명'].unique()

# 결과를 새 엑셀 파일로 저장
# excel_file_path = 'Weighted_Avg_Sales_Ratio.xlsx'


# 호프주점이 아예 그 상권에 존재하지 않아서 '가중평균매출액 대비 호프-간이주점 비율이 0이 되는 row들을 제외
result_df = result_df[result_df['가중평균매출액 대비 호프-간이주점 매출 비율'] > 0]

result_df = result_df.sort_values(by=['가중평균매출액 대비 호프-간이주점 매출 비율'])
result_df.to_excel('Weighted_Avg_Ratio.xlsx')
result_df.to_csv('Weighted_Avg_csv')

#상위 5개만 볼까요? ㅋㅋ 장사잘될거같은 곳을 봅시다.
print(result_df.iloc[:5])

# 확인 완료 했습니다. 호프-간이주점 창업 추천 Top 5 상권은: 
# 마천1치안센터, 남가좌동현대아파트, 구로창업지원센터, 강남세브란스병원미래의학연구센터, 언주역 8번 입니다.

# 여기까지 가중평균매출액 이었습니다.


data = pd.read_csv('merged.csv')

result_df = result_df.iloc[:5]

Sites = list(result_df['상권_명'])

# print(Sites)

cond1 = data['상권배후지_코드_명'].isin(Sites)
cond2 = data['서비스_업종_코드_명'] == '호프-간이주점'

filtered_Data = data[cond1 & cond2]
print(filtered_Data)
filtered_Data['가중평균매출액 대비 호프-간이주점 매출 비율'] = list(result_df['가중평균매출액 대비 호프-간이주점 매출 비율'])

filtered_Data = filtered_Data.drop(columns=['서비스_업종_코드', '상권배후지_코드'])

# print(filtered_Data)

def compare_company_avg(row):
    return row['총_직장_인구_수'] / company_avg

def compare_walking_avg(row):
    return row['총_유동인구_수'] / walking_avg
    
# Apply the function to create the new column
filtered_Data['평균_대비_직장인구_비율'] = filtered_Data.apply(compare_company_avg, axis=1)
filtered_Data['평균_대비_유동인구_비율'] = filtered_Data.apply(compare_walking_avg, axis=1)


filtered_Data = filtered_Data.round(4)

print(filtered_Data)

filtered_Data.to_excel('without_ML.xlsx')


