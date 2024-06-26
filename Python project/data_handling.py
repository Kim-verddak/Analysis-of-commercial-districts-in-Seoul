import pandas as pd

df = pd.read_csv("Data_Rowdata.csv")
df_pop = pd.read_csv("Population_Rowdata.csv")
df_str = pd.read_csv("Streetpop_Rowdata.csv")

df_str['기준_년분기_코드'] = df_str['기준_년분기_코드'].astype(int)

df_20231 = df[df['기준_년분기_코드'] == 20231]
df_pop_20231 = df_pop[df_pop['기준_년분기_코드'] == 20231]
df_str_20231 = df_str[df_str['기준_년분기_코드'] == 20231]

df_pop_20231 = df_pop_20231.drop(columns=['기준_년분기_코드','상권_구분_코드','상권_구분_코드_명','상권_코드_명'])
df_str_20231 = df_str_20231.drop(columns = ['기준_년분기_코드','상권_구분_코드','상권_구분_코드_명','상권배후지_코드_명'])

df_20231.to_csv("20231_data.csv", index=False)
df_pop_20231.to_csv('20231_population.csv', index=False)
df_str_20231.to_csv('20231_Streetpop.csv', index=False)

df = pd.merge(df_20231, df_pop_20231, on='상권배후지_코드', how='left')

df = pd.merge(df, df_str_20231, on='상권배후지_코드', how='left')

df = df[['상권배후지_코드','상권배후지_코드_명','서비스_업종_코드','서비스_업종_코드_명','당월_매출_금액', '총_직장_인구_수','총_유동인구_수']]

df.to_csv("merged.csv")

walking_avg = int(df_str['총_유동인구_수'].mean())
company_avg = int(df_pop['총_직장_인구_수'].mean())

jeompo = pd.read_csv("Jeompo.csv")
jeompo['기준_년분기_코드'] = jeompo['기준_년분기_코드'].astype(int)

# jeompo.to_csv('Jeompo.csv')
jeompo = jeompo[jeompo['기준_년분기_코드'] == 20231]
jeompo = jeompo[['서비스_업종_코드_명','점포_수']]
jeompo = jeompo.groupby('서비스_업종_코드_명')['점포_수'].sum()
jeompo.to_csv('J_test.csv')
# print(type(jeompo))

filtered_jeompo = jeompo[jeompo >= 10000]
Above_list = list(filtered_jeompo.index.tolist())

target_services = [
    '노래방', '미용실', '반찬가게', '부동산중개업', '분식전문점', '슈퍼마켓', '양식음식점', '예술학원',
    '육류판매', '의약품', '일반교습학원', '일반의류', '일반의원', '전자상거래업', '커피-음료',
    '컴퓨터및주변장치판매', '피부관리실', '한식음식점', '호프-간이주점', '화장품' ]

merged_df = df # 아까 merge했던거.
result_df = pd.DataFrame()

unique_codes = merged_df['상권배후지_코드'].unique()

for code in unique_codes:
    
    subset = merged_df[merged_df['상권배후지_코드'] == code]
    
    for service in target_services:
        service_subset = subset[subset['서비스_업종_코드_명'] == service]
        
        if not service_subset.empty:
            # If the service exists, add it to the result
            result_df = pd.concat([result_df, service_subset])
        
        else:
            new_row = pd.Series({
                '상권배후지_코드': code,
                '상권배후지_코드_명': subset['상권배후지_코드_명'].iloc[0],
                '서비스_업종_코드': subset['서비스_업종_코드'].iloc[0],
                '서비스_업종_코드': None,
                '서비스_업종_코드_명': service,
                '당월_매출_금액': 0,
                '총_직장_인구_수': subset['총_직장_인구_수'].iloc[0],
                '총_유동_인구_수': subset['총_유동인구_수'].iloc[0]            
                })
            
            result_df = pd.concat([result_df, new_row.to_frame().T])
            
result_df.to_csv('20rows.csv')

print('Succesful JeonCheoRi.. professor...')