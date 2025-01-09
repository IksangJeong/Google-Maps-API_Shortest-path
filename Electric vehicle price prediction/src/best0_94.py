import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, RobustScaler
from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import mean_squared_error
import xgboost as xgb
from xgboost import XGBRegressor
import warnings
warnings.filterwarnings('ignore')

# 데이터 로드
print("=== 데이터 로드 ===")
train = pd.read_csv('/home/oem/jejuMotor/iksang/open/train.csv')
test = pd.read_csv('/home/oem/jejuMotor/iksang/open/test.csv')
submit = pd.read_csv('/home/oem/jejuMotor/iksang/open/sample_submission.csv')

# 이상치 처리 함수
def handle_outliers(df, columns, n_sigmas=3):
    df_clean = df.copy()
    for col in columns:
        mean = df_clean[col].mean()
        std = df_clean[col].std()
        df_clean[col] = df_clean[col].clip(mean - n_sigmas * std, mean + n_sigmas * std)
    return df_clean

# 데이터 전처리
print("\n=== 데이터 전처리 시작 ===")
# 결측치 처리
train['배터리용량'].fillna(train['배터리용량'].median(), inplace=True)
test['배터리용량'].fillna(train['배터리용량'].median(), inplace=True)

def create_features(df):
    # 기존 특성
    df['차량연식'] = 2025 - df['연식(년)']
    df['차량연식'] = df['차량연식'].replace(0, 1)
    
    # 새로운 특성 추가
    df['배터리_효율'] = df['배터리용량'] / (df['주행거리(km)'] + 1)
    df['주행거리_연식_비율'] = df['주행거리(km)'] / df['차량연식']
    df['연식_보증_비율'] = df['연식(년)'] / df['보증기간(년)']
    df['배터리_연식_비율'] = df['배터리용량'] / df['차량연식']
    
    # 새로운 고급 특성
    df['주행거리_배터리_비율'] = df['주행거리(km)'] / (df['배터리용량'] + 1)
    df['연식_주행거리_효율'] = df['주행거리(km)'] / (df['차량연식'] * df['배터리용량'] + 1)
    df['보증_배터리_비율'] = df['보증기간(년)'] / (df['배터리용량'] + 1)
    
    # 제곱항 추가
    df['배터리용량_제곱'] = df['배터리용량'] ** 2
    df['주행거리_제곱'] = df['주행거리(km)'] ** 2
    
    # 교차항 추가
    df['배터리_주행거리_교차'] = df['배터리용량'] * df['주행거리(km)']
    
    # 로그 변환 특성
    df['주행거리_로그'] = np.log1p(df['주행거리(km)'])
    df['배터리용량_로그'] = np.log1p(df['배터리용량'])
    
    # 무한대 값 처리
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)
        df[col] = df[col].fillna(df[col].median())
    
    return df

# 특성 생성
train = create_features(train)
test = create_features(test)

# 이상치 처리
numeric_columns = ['배터리용량', '주행거리(km)', '배터리_효율', '주행거리_연식_비율']
train = handle_outliers(train, numeric_columns)

# 범주형 변수 인코딩
categorical_features = ['제조사', '모델', '차량상태', '구동방식', '사고이력']
encoders = {}

for feature in categorical_features:
    le = LabelEncoder()
    le = le.fit(train[feature])
    train[feature] = le.transform(train[feature])
    
    for case in np.unique(test[feature]):
        if case not in le.classes_:
            le.classes_ = np.append(le.classes_, case)
    test[feature] = le.transform(test[feature])
    encoders[feature] = le

# 스케일링을 위한 numeric_features 정의 (target 변수 제외)
numeric_features = [col for col in train.select_dtypes(include=[np.number]).columns 
                   if col not in ['ID', '가격(백만원)']]

# 스케일링 적용
scaler = RobustScaler()
train[numeric_features] = scaler.fit_transform(train[numeric_features])
test[numeric_features] = scaler.transform(test[numeric_features])

# 특성과 타겟 분리
X_train = train.drop(['ID', '가격(백만원)'], axis=1)
y_train = train['가격(백만원)']
X_test = test.drop('ID', axis=1)

# 학습 데이터와 검증 데이터 분리
X_train_final, X_val, y_train_final, y_val = train_test_split(
    X_train, y_train, test_size=0.2, random_state=42
)

print("\n=== 모델 학습 시작 ===")
# XGBoost 모델 정의
model = XGBRegressor(
    max_depth=8,                # 여기만 6→8로 변경
    learning_rate=0.005,
    n_estimators=3000,
    min_child_weight=5,
    subsample=0.85,
    colsample_bytree=0.85,
    reg_alpha=0.2,
    reg_lambda=1.2,
    random_state=42,
    tree_method='gpu_hist',
    early_stopping_rounds=100
)

# 학습 및 검증 데이터 설정
model.fit(
    X_train_final, y_train_final,
    eval_set=[(X_val, y_val)],  # 검증 데이터 추가
    verbose=100
)

# 전체 데이터로 학습 후 예측
print("\n=== 최종 모델 학습 및 예측 ===")
model.fit(
    X_train, y_train,  # 전체 데이터 사용
    eval_set=[(X_val, y_val)],  # 추가적으로 검증 데이터를 설정 가능
    verbose=100
)

# 예측 및 제출 파일 생성
predictions = model.predict(X_test)
submit['가격(백만원)'] = predictions
submit.to_csv('/home/oem/jejuMotor/iksang/open/sample_submission.csv', index=False)

print("예측 완료! sample_submission.csv 파일이 저장되었습니다.")