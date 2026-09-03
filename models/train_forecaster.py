"""
Model Training Pipeline for Multi-Horizon Freight Rate Forecasting.
Trains XGBoost models with rich maritime feature engineering:
- Lagged indicators
- Rolling statistics (EMA, SMA, Volatility)
- Baltic spreads and Bunker Fuel elasticity
- Evaluates R2, RMSE, MAE across multiple forecast horizons (7d, 15d, 30d, 60d, 90d)
- Saves model artifacts and metrics for fast API inference.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "historical_freight.csv")
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models")

TARGET_ROUTES = {
    "freight_aus_paradip_cape": "Australia (Hay Point) -> Paradip (Capesize)",
    "freight_aus_vizag_cape": "Australia (Hay Point) -> Vizag (Capesize)",
    "freight_indo_paradip_panamax": "Indonesia (Taboneo) -> Paradip (Panamax)",
    "freight_rsa_vizag_cape": "South Africa (RBCT) -> Vizag (Capesize)",
    "freight_usa_paradip_cape": "USA (Hampton Roads) -> Paradip (Capesize)",
    "bdi": "Baltic Dry Index (BDI)",
    "bci": "Baltic Capesize Index (BCI)"
}

HORIZONS = [7, 15, 30, 60, 90]

def create_feature_matrix(df):
    """Generates rich maritime features from raw timeseries data."""
    data = df.copy()
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values('date').reset_index(drop=True)
    
    # 1. Calendar / Seasonality
    data['month'] = data['date'].dt.month
    data['day_of_year'] = data['date'].dt.dayofyear
    data['sin_doy'] = np.sin(2 * np.pi * data['day_of_year'] / 365.25)
    data['cos_doy'] = np.cos(2 * np.pi * data['day_of_year'] / 365.25)
    
    # 2. Rolling Statistics for Key Indicators
    base_indicators = ['bdi', 'bci', 'bpi', 'bsi', 'bunker_vlsfo_singapore', 'crude_brent', 'coking_coal_fob_aus']
    for col in base_indicators:
        data[f'{col}_sma7'] = data[col].rolling(7).mean()
        data[f'{col}_sma30'] = data[col].rolling(30).mean()
        data[f'{col}_ema14'] = data[col].ewm(span=14, adjust=False).mean()
        data[f'{col}_vol14'] = data[col].rolling(14).std()
        data[f'{col}_mom7'] = data[col] / (data[col].shift(7) + 1e-6) - 1.0
        data[f'{col}_lag1'] = data[col].shift(1)
        data[f'{col}_lag7'] = data[col].shift(7)
        data[f'{col}_lag14'] = data[col].shift(14)
        
    # 3. Market Spreads & Ratios
    data['spread_cape_panamax'] = data['bci'] / (data['bpi'] + 1e-6)
    data['spread_vlsfo_crude'] = data['bunker_vlsfo_singapore'] / (data['crude_brent'] + 1e-6)
    data['port_congestion_total'] = data['port_congestion_aus_days'] + data['port_congestion_indo_days'] + data['port_congestion_india_east_days']
    
    # 4. Route-specific lagged features
    for route in TARGET_ROUTES.keys():
        if route in data.columns:
            data[f'{route}_sma7'] = data[route].rolling(7).mean()
            data[f'{route}_sma30'] = data[route].rolling(30).mean()
            data[f'{route}_vol14'] = data[route].rolling(14).std()
            data[f'{route}_lag1'] = data[route].shift(1)
            data[f'{route}_lag7'] = data[route].shift(7)
            data[f'{route}_lag14'] = data[route].shift(14)
            data[f'{route}_mom7'] = data[route] / (data[route].shift(7) + 1e-6) - 1.0

    return data

def train_and_save_all_models():
    os.makedirs(MODEL_DIR, exist_ok=True)
    print("Loading historical maritime dataset...")
    df_raw = pd.read_csv(DATA_PATH)
    data = create_feature_matrix(df_raw)
    
    # Drop warm-up rows due to 30-day rolling windows
    data_clean = data.dropna().reset_index(drop=True)
    print(f"Data ready for training: {len(data_clean)} rows.")
    
    # Candidate feature columns (exclude raw dates and targets)
    all_target_names = list(TARGET_ROUTES.keys())
    excluded_cols = ['date'] + all_target_names
    feature_cols = [c for c in data_clean.columns if c not in excluded_cols and not any(c.startswith(t + '_target_h') for t in all_target_names)]
    
    print(f"Feature set size: {len(feature_cols)} features.")
    
    model_metadata = {
        "training_date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "features": feature_cols,
        "horizons": HORIZONS,
        "models": {}
    }
    
    # Train test split: 80% train, 20% test (chronological time-series split)
    split_idx = int(len(data_clean) * 0.82)
    
    for route_col in TARGET_ROUTES.keys():
        print(f"\n==========================================")
        print(f"Training models for target: {TARGET_ROUTES[route_col]} ({route_col})")
        print(f"==========================================")
        model_metadata["models"][route_col] = {
            "name": TARGET_ROUTES[route_col],
            "horizons": {}
        }
        
        for h in HORIZONS:
            # Create forward target
            y_target = data_clean[route_col].shift(-h)
            
            # Mask out last h rows where forward target is NaN
            valid_mask = ~y_target.isna()
            X_valid = data_clean.loc[valid_mask, feature_cols]
            y_valid = y_target[valid_mask]
            
            train_mask = valid_mask & (data_clean.index < split_idx)
            test_mask = valid_mask & (data_clean.index >= split_idx)
            
            X_train = data_clean.loc[train_mask, feature_cols]
            y_train = y_target[train_mask]
            X_test = data_clean.loc[test_mask, feature_cols]
            y_test = y_target[test_mask]
            
            # Fit XGBoost Regressor
            xgb = XGBRegressor(
                n_estimators=180,
                learning_rate=0.045,
                max_depth=5,
                subsample=0.85,
                colsample_bytree=0.85,
                random_state=42,
                n_jobs=-1
            )
            xgb.fit(X_train, y_train)
            
            # Evaluate on Test Set
            y_pred = xgb.predict(X_test)
            r2 = float(r2_score(y_test, y_pred))
            rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
            mae = float(mean_absolute_error(y_test, y_pred))
            mape = float(np.mean(np.abs((y_test - y_pred) / (y_test + 1e-6))) * 100)
            
            # Feature Importance
            importances = xgb.feature_importances_
            top_features_idx = np.argsort(importances)[::-1][:6]
            top_features = [
                {"feature": feature_cols[i], "importance": round(float(importances[i]), 4)}
                for i in top_features_idx
            ]
            
            # Residual std for confidence intervals (P10 / P90)
            residuals = y_test - y_pred
            residual_std = float(np.std(residuals))
            
            model_filename = f"xgb_{route_col}_h{h}.joblib"
            joblib.dump(xgb, os.path.join(MODEL_DIR, model_filename))
            
            model_metadata["models"][route_col]["horizons"][str(h)] = {
                "file": model_filename,
                "r2": round(r2, 4),
                "rmse": round(rmse, 4),
                "mae": round(mae, 4),
                "mape": round(mape, 2),
                "residual_std": round(residual_std, 4),
                "top_features": top_features
            }
            
            print(f"Horizon +{h:2d}d | R2: {r2:0.4f} | RMSE: {rmse:0.3f} | MAE: {mae:0.3f} | MAPE: {mape:0.2f}%")
            
    # Save metadata JSON
    meta_path = os.path.join(MODEL_DIR, "model_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(model_metadata, f, indent=2)
        
    print(f"\nTraining complete! All models & metadata saved to {MODEL_DIR}")
    return model_metadata

if __name__ == "__main__":
    train_and_save_all_models()
