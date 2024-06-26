import pandas as pd
import numpy as np
import itertools
import openpyxl
from operator import itemgetter

data = pd.read_csv('20rows.csv')


# 피벗 테이블 생성: 행은 상권배후지_코드, 열은 서비스_업종_코드_명, 값은 당월_매출_금액
pivot_table = data.pivot_table(index='상권배후지_코드', columns='서비스_업종_코드_명', values='당월_매출_금액', fill_value=0)

# 상관관계 계산
correlation_matrix = np.corrcoef(pivot_table.T)

# 상관관계 행렬을 DataFrame으로 변환하여 보기 좋게 출력
correlation_df = pd.DataFrame(correlation_matrix, index=pivot_table.columns, columns=pivot_table.columns)

correlation_df = correlation_df.round(2)
correlation_df.to_excel('Correlation_Table.xlsx')
# 상관관계 행렬 출력
# print(correlation_df)

correlation_tuples = []

# 모든 업종 쌍에 대해 상관관계 추출. (업종1, 업종2, 상관계수) 형식으로 출력 if 업종1 == 업종2 이면 리스트에서 제외
for (service1, service2) in itertools.combinations(correlation_df.columns, 2):
    correlation = correlation_df.loc[service1, service2]
    correlation_tuples.append((service1, service2, round(correlation, 2)))

# 상관관계 튜플 리스트 출력
# print(correlation_tuples)

correlation_tuples.sort(key=itemgetter(2), reverse=True)

print(correlation_tuples[:3]) # 결과: ('한식음식점', '호프-간이주점', 0.67), ('노래방', '한식음식점', 0.66), ('분식전문점', '한식음식점', 0.61)]
# 따라서 저 중 하나를 골라, 호프-간이주점의 창업을 추천해보겠습니다.
