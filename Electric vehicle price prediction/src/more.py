import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
import warnings
warnings.filterwarnings('ignore')

# 파일 경로 상수화
TRAIN_PATH = '/home/oem/jejuMotor/iksang/open/train.csv'
TEST_PATH = '/home/oem/jejuMotor/iksang/open/test.csv'
SUBMIT_PATH = '/home/oem/jejuMotor/iksang/open/sample_submission.csv'
OUTPUT_PATH = '/home/oem/jejuMotor/iksang/open/sample_submission.csv'

# 데이터 로드
def load_data(train_path, test_path, submit_path):
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    submit = pd.read_csv(submit_path)
    return train, test, submit

# 이상치 처리
def handle_outliers(df, columns, n_sigmas=3):
    for col in columns:
        mean, std = df[col].mean(), df[col].std()
        df[col] = df[col].clip(mean - n_sigmas * std, mean + n_sigmas * std)
    return df

# 특성 생성 함수
def create_features(df):
    df['차량연식'] = 2025 - df['연식(년)']
    df['차량연식'] = df['차량연식'].replace(0, 1)
    
    # 새로운 특성 추가
    df['배터리_효율'] = df['배터리용량'] / (df['주행거리(km)'] + 1)
    df['주행거리_연식_비율'] = df['주행거리(km)'] / df['차량연식']
    df['연식_보증_비율'] = df['연식(년)'] / df['보증기간(년)']
    df['배터리_연식_비율'] = df['배터리용량'] / df['차량연식']
    df['주행거리_배터리_비율'] = df['주행거리(km)'] / (df['배터리용량'] + 1)
    df['연식_주행거리_효율'] = df['주행거리(km)'] / (df['차량연식'] * df['배터리용량'] + 1)
    df['보증_배터리_비율'] = df['보증기간(년)'] / (df['배터리용량'] + 1)
    df['배터리용량_제곱'] = df['배터리용량'] ** 2
    df['주행거리_제곱'] = df['주행거리(km)'] ** 2
    df['배터리_주행거리_교차'] = df['배터리용량'] * df['주행거리(km)']
    df['주행거리_로그'] = np.log1p(df['주행거리(km)'])
    df['배터리용량_로그'] = np.log1p(df['배터리용량'])
    
    # 무한대 값 처리
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].replace([np.inf, -np.inf], np.nan)
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    return df

# 범주형 변수 인코딩
def encode_categorical(train, test, features):
    encoders = {}
    for feature in features:
        le = LabelEncoder()
        le.fit(train[feature])
        train[feature] = le.transform(train[feature])
        
        # Test 데이터의 새로운 카테고리 처리
        for case in np.unique(test[feature]):
            if case not in le.classes_:
                le.classes_ = np.append(le.classes_, case)
        test[feature] = le.transform(test[feature])
        encoders[feature] = le
    return train, test, encoders

# 데이터 전처리 함수
def preprocess_data(train, test, numeric_columns, categorical_features):
    train['배터리용량'].fillna(train['배터리용량'].median(), inplace=True)
    test['배터리용량'].fillna(train['배터리용량'].median(), inplace=True)

    train = create_features(train)
    test = create_features(test)
    
    train = handle_outliers(train, numeric_columns)
    
    train, test, encoders = encode_categorical(train, test, categorical_features)
    
    scaler = RobustScaler()
    train[numeric_columns] = scaler.fit_transform(train[numeric_columns])
    test[numeric_columns] = scaler.transform(test[numeric_columns])
    
    return train, test, scaler

# 모델 학습 함수
def train_model(X_train, y_train, X_val, y_val, params):
    model = XGBRegressor(**params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=100
    )
    return model

# 메인 실행
def main():
    print("=== 데이터 로드 ===")
    train, test, submit = load_data(TRAIN_PATH, TEST_PATH, SUBMIT_PATH)
    
    numeric_columns = ['배터리용량', '주행거리(km)', '배터리_효율', '주행거리_연식_비율']
    categorical_features = ['제조사', '모델', '차량상태', '구동방식', '사고이력']
    
    print("\n=== 데이터 전처리 시작 ===")
    train, test, _ = preprocess_data(train, test, numeric_columns, categorical_features)
    
    X_train = train.drop(['ID', '가격(백만원)'], axis=1)
    y_train = train['가격(백만원)']
    X_test = test.drop('ID', axis=1)
    
    X_train_final, X_val, y_train_final, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42
    )
    
    params = {
        'max_depth': 8,
        'learning_rate': 0.005,
        'n_estimators': 3000,
        'min_child_weight': 5,
        'subsample': 0.85,
        'colsample_bytree': 0.85,
        'reg_alpha': 0.2,
        'reg_lambda': 1.2,
        'random_state': 42,
        'tree_method': 'gpu_hist',
        'early_stopping_rounds': 100
    }
    
    print("\n=== 모델 학습 시작 ===")
    model = train_model(X_train_final, y_train_final, X_val, y_val, params)
    
    print("\n=== 최종 모델 학습 및 예측 ===")
    model.fit(X_train, y_train, verbose=100)
    predictions = model.predict(X_test)
    
    submit['가격(백만원)'] = predictions
    submit.to_csv(OUTPUT_PATH, index=False)
    print(f"예측 완료! {OUTPUT_PATH} 파일이 저장되었습니다.")

if __name__ == "__main__":
    main()