import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, RobustScaler
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
import xgboost as xgb
from xgboost import XGBRegressor
from catboost import CatBoostRegressor
import warnings
warnings.filterwarnings('ignore')

# 데이터 로드
print("=== 데이터 로드 ===")
train = pd.read_csv('/home/oem/jejuMotor/iksang/open/train.csv')
test = pd.read_csv('/home/oem/jejuMotor/iksang/open/test.csv')
submit = pd.read_csv('/home/oem/jejuMotor/iksang/open/sample_submission.csv')

# 개선된 이상치 처리 함수
def handle_outliers(df, columns):
    df_clean = df.copy()
    for col in columns:
        q1 = df_clean[col].quantile(0.25)
        q3 = df_clean[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        df_clean[col] = df_clean[col].clip(lower_bound, upper_bound)
    return df_clean

def create_features(df):
    # 기존 특성
    df['차량연식'] = 2025 - df['연식(년)']
    df['차량연식'] = df['차량연식'].replace(0, 1)
    
    # 기존 특성들
    df['배터리_효율'] = df['배터리용량'] / (df['주행거리(km)'] + 1)
    df['주행거리_연식_비율'] = df['주행거리(km)'] / df['차량연식']
    df['연식_보증_비율'] = df['연식(년)'] / df['보증기간(년)']
    df['배터리_연식_비율'] = df['배터리용량'] / df['차량연식']
    df['주행거리_배터리_비율'] = df['주행거리(km)'] / (df['배터리용량'] + 1)
    df['연식_주행거리_효율'] = df['주행거리(km)'] / (df['차량연식'] * df['배터리용량'] + 1)
    df['보증_배터리_비율'] = df['보증기간(년)'] / (df['배터리용량'] + 1)
    
    # 추가된 새로운 특성들
    df['배터리_주행거리_비'] = df['배터리용량'] / df['주행거리(km)']
    df['연식_배터리_효율'] = df['배터리용량'] / (2025 - df['연식(년)'])
    df['주행거리_연식_효율'] = df['주행거리(km)'] / (2025 - df['연식(년)'])
    df['보증_연식_비율'] = df['보증기간(년)'] / (2025 - df['연식(년)'])
    df['배터리_보증_효율'] = df['배터리용량'] * df['보증기간(년)']
    
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

# 데이터 전처리
print("\n=== 데이터 전처리 시작 ===")
# 결측치 처리
train['배터리용량'].fillna(train['배터리용량'].median(), inplace=True)
test['배터리용량'].fillna(train['배터리용량'].median(), inplace=True)

# 특성 생성
train = create_features(train)
test = create_features(test)

# 이상치 처리
numeric_columns = ['배터리용량', '주행거리(km)', '배터리_효율', '주행거리_연식_비율', 
                  '배터리_주행거리_비', '연식_배터리_효율', '주행거리_연식_효율']
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
X = train.drop(['ID', '가격(백만원)'], axis=1)
y = train['가격(백만원)']
X_test = test.drop('ID', axis=1)

# K-fold 교차 검증 설정 (10-fold)
n_splits = 10
kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

# 예측값 저장을 위한 배열 초기화
oof_predictions_xgb = np.zeros(len(X))
oof_predictions_cat = np.zeros(len(X))
test_predictions_xgb = np.zeros((len(X_test), n_splits))
test_predictions_cat = np.zeros((len(X_test), n_splits))

print("\n=== 교차 검증 및 모델 학습 시작 ===")
for fold, (train_idx, val_idx) in enumerate(kf.split(X), 1):
    print(f"\nFold {fold} 학습 중...")
    
    X_train_fold = X.iloc[train_idx]
    y_train_fold = y.iloc[train_idx]
    X_val_fold = X.iloc[val_idx]
    y_val_fold = y.iloc[val_idx]
    
    # XGBoost 모델
    xgb_model = XGBRegressor(
        max_depth=8,
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
    
    # CatBoost 모델
    cat_model = CatBoostRegressor(
        depth=8,
        learning_rate=0.005,
        iterations=3000,
        l2_leaf_reg=3,
        random_strength=0.8,
        random_state=42,
        task_type='GPU',
        verbose=False
    )
    
    # XGBoost 학습 및 예측
    xgb_model.fit(
        X_train_fold, y_train_fold,
        eval_set=[(X_val_fold, y_val_fold)],
        verbose=100
    )
    
    # CatBoost 학습 및 예측
    cat_model.fit(
        X_train_fold, y_train_fold,
        eval_set=(X_val_fold, y_val_fold),
        verbose=False
    )
    
    # 검증 데이터 예측
    xgb_val_pred = xgb_model.predict(X_val_fold)
    cat_val_pred = cat_model.predict(X_val_fold)
    
    oof_predictions_xgb[val_idx] = xgb_val_pred
    oof_predictions_cat[val_idx] = cat_val_pred
    
    # 테스트 데이터 예측
    test_predictions_xgb[:, fold-1] = xgb_model.predict(X_test)
    test_predictions_cat[:, fold-1] = cat_model.predict(X_test)
    
    # 각 모델의 RMSE 계산
    xgb_rmse = np.sqrt(mean_squared_error(y_val_fold, xgb_val_pred))
    cat_rmse = np.sqrt(mean_squared_error(y_val_fold, cat_val_pred))
    
    # 앙상블 예측의 RMSE 계산
    ensemble_pred = 0.6 * xgb_val_pred + 0.4 * cat_val_pred
    ensemble_rmse = np.sqrt(mean_squared_error(y_val_fold, ensemble_pred))
    
    print(f"Fold {fold} - XGBoost RMSE: {xgb_rmse:.4f}")
    print(f"Fold {fold} - CatBoost RMSE: {cat_rmse:.4f}")
    print(f"Fold {fold} - Ensemble RMSE: {ensemble_rmse:.4f}")

# 전체 OOF RMSE 계산
oof_ensemble = 0.6 * oof_predictions_xgb + 0.4 * oof_predictions_cat
oof_rmse = np.sqrt(mean_squared_error(y, oof_ensemble))
print(f"\n전체 OOF RMSE: {oof_rmse:.4f}")

# 최종 예측값 계산 (앙상블)
final_predictions_xgb = test_predictions_xgb.mean(axis=1)
final_predictions_cat = test_predictions_cat.mean(axis=1)
final_predictions = 0.6 * final_predictions_xgb + 0.4 * final_predictions_cat

# 제출 파일 생성
submit['가격(백만원)'] = final_predictions
submit.to_csv('/home/oem/jejuMotor/iksang/open/sample_submission.csv', index=False)
print("\n예측 완료! sample_submission.csv 파일이 저장되었습니다.")

# 시각화
plt.figure(figsize=(15, 5))
plt.subplot(1, 2, 1)
plt.scatter(y, oof_predictions_xgb, alpha=0.5, label='XGBoost')
plt.scatter(y, oof_predictions_cat, alpha=0.5, label='CatBoost')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
plt.xlabel('실제 가격')
plt.ylabel('예측 가격')
plt.title('실제 가격 vs 예측 가격')
plt.legend()

plt.subplot(1, 2, 2)
plt.hist(y - oof_ensemble, bins=50)
plt.title('예측 오차 분포')
plt.xlabel('오차')
plt.ylabel('빈도')
plt.show()