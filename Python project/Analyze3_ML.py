import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from Analyze2 import filtered_Data
import openpyxl


Sites = list(filtered_Data['상권배후지_코드_명'])
print(Sites)
df = pd.read_csv('Data_Rowdata.csv')

cond1 = df['상권배후지_코드_명'].isin(Sites)
cond2 = df['서비스_업종_코드_명'] == '호프-간이주점'

filtered_dfpop = df[cond1 & cond2]

filtered_dfpop = filtered_dfpop.drop(columns='상권_구분_코드_명')

print(filtered_dfpop.info())

# ML data 학습.

data = pd.read_csv('Data_Rowdata.csv')

# 필요한 컬럼만 선택
data = data[['기준_년분기_코드', '상권배후지_코드_명', '서비스_업종_코드_명','당월_매출_금액', "연령대_10_매출_금액","연령대_20_매출_금액","연령대_30_매출_금액","연령대_40_매출_금액","연령대_50_매출_금액","연령대_60_이상_매출_금액"]]

print(data.head())

# print(filtered_dfpop)
data['log_매출_금액'] = np.log1p(data['당월_매출_금액'])  # log1p는 log(1 + x)를 계산하여 0 값을 처리
grouped_data = data.groupby(['상권배후지_코드_명', '기준_년분기_코드']).sum().reset_index()



def create_features(df):
    df = df.sort_values(by='기준_년분기_코드')
    df['다음_분기_총_매출_금액'] = df['당월_매출_금액'].shift(-1)  # 다음 분기의 총 매출 금액을 예측 대상으로 설정
    return df.dropna()

processed_data = grouped_data.groupby('상권배후지_코드_명').apply(create_features).reset_index(drop=True)

X = processed_data[['기준_년분기_코드', '당월_매출_금액']]
y = processed_data['다음_분기_총_매출_금액']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)
     
# 파라미터 설정
params = {
    'max_depth': 6,
    'eta': 0.8,
    'objective': 'reg:squarederror',
    'eval_metric': 'rmse',
    'min_child_weight': 3,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'gamma': 0.1
}

num_rounds = 500
watchlist = [(dtrain, 'train'), (dtest, 'eval')]

# 모델 학습
bst = xgb.train(params, dtrain, num_rounds, watchlist)

y_pred = bst.predict(dtest)

# 평가
from sklearn.metrics import mean_squared_error

rmse = mean_squared_error(y_test, y_pred, squared=False)
print(f'RMSE: {rmse}') # -> 매출이 기본 몇십억 단위라 오차범위가 크게 남.

mean_sales = data['당월_매출_금액'].mean()

# 상대적인 RMSE 계산
relative_rmse = rmse / mean_sales
print(f'평균 매출 금액: {mean_sales}')
print(f'상대적인 RMSE: {relative_rmse}')
bst.save_model('xgb_model.json')
bst = xgb.Booster()
bst.load_model('xgb_model.json')

# 새로운 데이터 로드 및 전처리
new_data = filtered_dfpop
new_data = new_data[['기준_년분기_코드', '상권배후지_코드_명', '당월_매출_금액']]

# 데이터 그룹화 및 전처리
new_grouped_data = new_data.groupby(['상권배후지_코드_명', '기준_년분기_코드']).sum().reset_index()

def prepare_features(df):
    df = df.sort_values(by='기준_년분기_코드')
    df['다음_분기_총_매출_금액'] = df['당월_매출_금액'].shift(-1)
    return df.dropna()

new_processed_data = new_grouped_data.groupby('상권배후지_코드_명').apply(prepare_features).reset_index(drop=True)

# 예측을 위한 데이터 준비
X_new = new_processed_data[['기준_년분기_코드', '당월_매출_금액']]
dnew = xgb.DMatrix(X_new)

# 예측 수행
new_pred = bst.predict(dnew)

# 예측 결과를 새로운 컬럼으로 추가
new_processed_data['다음분기_예측_매출_금액'] = new_pred

# 결과 확인

print(new_processed_data.head())

# 결과 저장
new_processed_data.to_csv('new_data_with_predictions.csv', index=False)
new_processed_data.to_xlsx('TTTTT.xlsx', index=False)

# 그러나.. 저희가 생각했던 머신러닝 녹여내기 방식이 적절치 않았던 것 같습니다.
# 머신러닝을 사용하려면 기본적으로 빅 데이터 셋이 있어야 하고, 이를 예측하기 위한 features가 여러 개 있었어야 했는데,
# 저희의 머신러닝 데이터 예측에 사용한 feature가 상관관계도 부족했던 것 같고 예측치도 많이 벗어난 것을 확인할 수 있었습니다.
# 따라서 다음분기 예출매출금액 row는 Beta 상태로 남겨놓고자 합니다.
# Beta 상태로 남겨두어 이 프로그램을 사용하실 창업주님께 도움이 살짝이나마 되는 정보를 제시해 드리고자 합니다.


# Final Data로 합치기


df1 = filtered_Data

df2 = new_processed_data

# 공통 컬럼을 기준으로 두 DataFrame을 합치기
merged_df = pd.merge(df1, df2, on='상권배후지_코드_명', how='inner')  # '공통컬럼명'은 두 파일에서 공통으로 있는 컬럼 이름입니다.

import openpyxl
# 합쳐진 DataFrame을 새로운 xlsx 파일로 저장
merged_df.to_excel('FINAL.xlsx', index=False)  