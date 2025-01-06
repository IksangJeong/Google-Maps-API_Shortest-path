import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score, GridSearchCV
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.ensemble import VotingRegressor, StackingRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------------------------
# [목적과 의도 설명]
# 이 스크립트는 다양한 회귀 모델(XGBoost, LightGBM, CatBoost)을 기반으로 스태킹 앙상블을 수행하여
# 전기차(또는 특정 차량) 가격을 예측하는 것을 목표로 한다.
# 수집된 데이터에서 결측치를 처리하고, 새로운 특성을 추가하고, 범주형 변수를 인코딩 및 스케일링한 뒤
# 여러 모델을 결합(stack)해 예측 성능을 높이는 구조로 작성하였다.

# ---------------------------------------------------------------------------------------------
# 1. 데이터 로드
# 왜 이렇게 작성했는가?
# - 학습 데이터를 포함해 여러 CSV 파일을 사용하기 때문에, 명시적으로 경로를 지정하여 데이터를 로드.
# - 경로가 하드코딩되어 있지만, 이 실험에서는 고정된 디렉토리 구조를 가정하고 진행한다.
# - 운영 환경이 달라질 경우, 아래 경로를 유연하게 수정할 수 있도록 코드에서 분리하였다.
train = pd.read_csv('Electric vehicle price prediction/data/train.csv')
test = pd.read_csv('Electric vehicle price prediction/data/test.csv')
submit = pd.read_csv('Electric vehicle price prediction/data/sample_submission.csv')

# ---------------------------------------------------------------------------------------------
# 2. 데이터 전처리 함수 정의
# "어떤 로직을 처리하고 있는가" 보다는 "왜 그런 로직을 사용했는가"를 중점으로 설명한다.

def preprocess_data(df, is_train=True):
    """
    [왜 필요한가?]
    - 원본 데이터에 직접 가공을 가하면 추적이 어려워지므로, copy()로 안전하게 복제 후 전처리를 실시.
    - 결측치 처리, 새로운 특성 생성, 그리고 실험적으로 도움이 된다고 여겨지는 파생 변수를 만든다.
    
    [주요 의도]
    - 결측치 처리: '배터리용량'의 경우 중앙값/최빈값도 고려했으나, 분포 특성상 평균 대체가 간편하면서도
      baseline 성능이 일정 수준 이상 보장되어 채택하였다.
    - 배터리_효율: 단순히 배터리용량과 주행거리를 따로 보는 것보다, 이 둘의 비율이 예측력 향상에
      도움이 될 것으로 가정하였다.
    - 차량연식: 2024년을 기준으로 차량의 사용 연수를 파악해 추가적인 예측 정보로 활용한다.
    - price_per_km(훈련 데이터만): 분석 과정에서 예측 성능을 높이기 위해 직접 사용하는 값은 아니지만,
      데이터 이해용 지표로 사용한다.
    """
    df = df.copy()
    
    # 평균값 대체는 간단하면서도 이탈값이 크지 않은 상황에 적합하다고 판단하였다.
    df['배터리용량'].fillna(df['배터리용량'].mean(), inplace=True)
    
    # 배터리 효율이라는 파생 변수 추가
    # 수치형 변수를 다양하게 조합함으로써 모델이 비선형적인 상호 작용을 학습하기 쉽도록 한다.
    df['배터리_효율'] = df['배터리용량'] / df['주행거리(km)']
    
    # 차량연식 = 기준연도(2024) - 차량등록연도
    # 단순히 '연식' 자체보다 "얼마나 오랫동안 사용했는가"가 더 직관적인 feature라고 보았다.
    df['차량연식'] = 2024 - df['연식(년)']
    
    if is_train:
        # train 데이터에만 존재하는 값(가격)을 이용해 참고 특성을 생성하여 EDA 때 분석에 활용.
        df['price_per_km'] = df['가격(백만원)'] / df['주행거리(km)']
    
    # 제조사와 모델을 결합한 범주형 특성 생성
    # 제조사와 모델의 조합이 유의미한 차이를 나타낼 수 있으므로 결합 특성을 추가.
    df['제조사_모델'] = df['제조사'] + '_' + df['모델']
    
    return df

def encode_categorical_features(df_train, df_test):
    """
    [왜 필요한가?]
    - 모델이 범주형 데이터를 직접 처리할 수 있는 방법도 있지만,
      여기서는 모든 모델에서 통일된 방식으로 학습하기 위해 LabelEncoder를 적용했다.
    - 만약 CatBoost처럼 범주형 변수 처리를 잘하는 모델만 사용한다면, 이 과정을 생략할 수도 있음.
    
    [주요 의도]
    - 이 함수를 통해 train과 test 데이터가 동일한 범주 인코딩 스페이스를 공유하게 함.
    - 새로운 범주(오탈자 등)가 있을 경우에도 유연하게 처리하기 위해 test 데이터의 범주를
      train의 인코더 클래스에 추가해주도록 하였다.
    """
    categorical_features = ['제조사', '모델', '차량상태', '제조사_모델', '구동방식', '사고이력']
    
    encoders = {}
    for feature in categorical_features:
        le = LabelEncoder()
        
        # train에 등장한 범주를 기준으로 인코더를 먼저 학습한다.
        le = le.fit(df_train[feature])
        
        # train 데이터 인코딩
        df_train[feature] = le.transform(df_train[feature])
        
        # test 데이터에 train에 없는 새 범주가 등장할 경우, le.classes_에 추가
        # 이렇게 하지 않으면 transform 과정에서 에러가 발생한다.
        for case in np.unique(df_test[feature]):
            if case not in le.classes_:
                le.classes_ = np.append(le.classes_, case)
        
        df_test[feature] = le.transform(df_test[feature])
        encoders[feature] = le
        
    return df_train, df_test, encoders

def scale_numeric_features(df_train, df_test):
    """
    [왜 필요한가?]
    - 트리 계열 모델은 스케일링에 영향을 적게 받는 편이지만,
      스태킹에서 추가되는 회귀 모델이 있을 경우 스케일링이 도움이 될 수 있음.
    - 또한, 관습적으로 수치형 변수 범위를 일정하게 맞춰주는 편이 다양한 실험에서 성능이 더 안정적이었다.
    
    [주요 의도]
    - StandardScaler를 사용하여 평균 0, 분산 1이 되도록 변환하고,
      train 데이터에 학습된 스케일러를 test 데이터에도 동일하게 적용한다.
    """
    numeric_features = ['배터리용량', '주행거리(km)', '배터리_효율', '차량연식', 
                       '보증기간(년)', '연식(년)']
    scaler = StandardScaler()
    
    df_train[numeric_features] = scaler.fit_transform(df_train[numeric_features])
    df_test[numeric_features] = scaler.transform(df_test[numeric_features])
    
    return df_train, df_test, scaler

# ---------------------------------------------------------------------------------------------
# 3. 데이터 전처리 실행
# 예측에 직접적으로 활용되는 train, test 데이터에 위에서 정의한 전처리 과정을 동일하게 적용.
# is_train=True일 때만 train 데이터 전용 특성(예: price_per_km)을 생성하도록 했다.
train_processed = preprocess_data(train, is_train=True)
test_processed = preprocess_data(test, is_train=False)

# 타깃과 불필요한 컬럼을 제거
# ID는 인덱스로서만 사용되는 컬럼, price_per_km은 파생 지표이므로 X에서는 제거
X_train = train_processed.drop(['ID', '가격(백만원)', 'price_per_km'], axis=1)
y_train = train_processed['가격(백만원)']
X_test = test_processed.drop(['ID'], axis=1)

# 범주형 변수 인코딩
X_train, X_test, encoders = encode_categorical_features(X_train, X_test)

# 수치형 변수 스케일링
X_train, X_test, scaler = scale_numeric_features(X_train, X_test)

# ---------------------------------------------------------------------------------------------
# 4. 모델 정의
# 트리 계열(XGB, LGB, CatBoost)을 세 가지 골고루 선택하여 스태킹에 활용.
# 이렇게 한 이유?
# - XGB, LGB, CatBoost는 모두 트리 기반 부스팅 모델이지만, 내부 최적화와 처리 방식이 조금씩 다르다.
# - 데이터셋 특성이나 하이퍼파라미터 설정에 따라 각 모델 간 예측 편향이 달라 서로를 보완 가능.
xgb_model = XGBRegressor(
    n_estimators=1000,
    learning_rate=0.01,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

lgb_model = LGBMRegressor(
    n_estimators=1000,
    learning_rate=0.01,
    num_leaves=31,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

cat_model = CatBoostRegressor(
    iterations=1000,
    learning_rate=0.01,
    depth=6,
    random_state=42,
    verbose=False
)

# ---------------------------------------------------------------------------------------------
# 5. 스태킹 앙상블 모델 생성
# Base models: XGBoost, LightGBM, CatBoost
# Final estimator: LightGBM
# 왜 이런 조합인가?
# - 세 가지 서로 다른 트리 부스팅 모델을 결합해 다양성을 확보하고, 최종 메타 모델로는 가벼우면서도
#   빠른 LGBM을 선택하였다(반복적인 스택 학습 단계에서 자원 소모 완화).
# - cv=5를 통해 과적합을 방지하면서 메타 모델을 훈련시킨다.
base_models = [
    ('xgb', xgb_model),
    ('lgb', lgb_model),
    ('cat', cat_model)
]

stacking_regressor = StackingRegressor(
    estimators=base_models,
    final_estimator=LGBMRegressor(),
    cv=5
)

# ---------------------------------------------------------------------------------------------
# 6. 모델 학습
# 스태킹 회귀 모델 전체 파이프라인을 fit.
# 많은 fold(cross-validation)로 학습하면 오버피팅을 줄이고, 다양한 시나리오를 학습한다.
print("스태킹 모델 학습 시작...")
stacking_regressor.fit(X_train, y_train)

# ---------------------------------------------------------------------------------------------
# 7. 교차 검증 점수 계산
# 왜 이렇게 진행했는가?
# - cross_val_score를 통해 모델의 일반화 성능을 안정적으로 추정.
# - neg_mean_squared_error를 사용하고, 결과값은 - 로 나오므로, RMSE를 구하기 위해 -를 다시 붙여줌.
cv_scores = cross_val_score(
    stacking_regressor, 
    X_train, 
    y_train, 
    cv=5, 
    scoring='neg_mean_squared_error'
)
rmse_scores = np.sqrt(-cv_scores)
print(f"5-fold CV RMSE: {rmse_scores.mean():.4f} (+/- {rmse_scores.std() * 2:.4f})")

# ---------------------------------------------------------------------------------------------
# 8. 테스트 데이터 예측
# 최종 학습된 스태킹 모델을 이용해 test 데이터에 대한 예측 수행.
# 리더보드 제출을 위해 final_predictions에 저장.
final_predictions = stacking_regressor.predict(X_test)

# ---------------------------------------------------------------------------------------------
# 9. 제출 파일 생성
# 왜 필요한가?
# - 대회나 실제 운영에서 예측 결과물을 전달하기 위해 제출 양식(sample_submission)을 사용한다.
# - 아래와 같은 방식으로 결과물을 csv로 저장하면 리더보드 평가에 바로 활용 가능.
submit['가격(백만원)'] = final_predictions
submit.to_csv('/home/oem/jejuMotor/iksang/open/advanced_submission.csv', index=False)
print("예측 완료 및 제출 파일 생성됨")

# ---------------------------------------------------------------------------------------------
# 10. 특성 중요도 시각화 (XGBoost 모델 기준)
# 스태킹에 포함된 모델 중, XGBoost에 관해 특성 중요도를 시각화하여
# 어떤 feature가 중요한지 참고 차원에서 확인한다.
# 왜 XGBoost만 했는가?
# - 다른 모델에도 중요도 시각화가 있지만, XGBoost의 feature_importances_를 활용하면
#   비교적 손쉽게 빠른 이해가 가능하다.
xgb_model.fit(X_train, y_train)
feature_importance = pd.DataFrame({
    'feature': X_train.columns,
    'importance': xgb_model.feature_importances_
})
feature_importance = feature_importance.sort_values('importance', ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(data=feature_importance.head(10), x='importance', y='feature')
plt.title('Top 10 Feature Importance (XGBoost)')
plt.tight_layout()
plt.show()

