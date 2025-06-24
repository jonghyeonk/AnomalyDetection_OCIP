
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
import random

def filter_time(x, filter_time_start, filter_time_end):
    time_key = x.parameters['time_name']
    if filter_time_start == None:
        filter_time_start = min(x.log.log[time_key])
    if filter_time_end == None:
        filter_time_end = max(x.log.log[time_key])
    return x.log.log.loc[(filter_time_start <= x.log.log[time_key]) & (x.log.log[time_key] <= filter_time_end )]

def label(x, text , post=True, list = True):
    if pd.isna(x):
        return ''
    else:
        if type(x) == float:
            if post == True:
                s = str(x) + text
            else:
                s = text + str(x)
            return s
        else:
            if len(x)>0:
                if post == True:
                    s = x[0] + text
                else:
                    s = text + x[0]

                if list == True:
                    s = [s]
            else:
                if list == True:
                    s = x
                else:
                    s = ''
            return s

def get_unique(df):
    out_dict = dict()
    for col in df.columns:
        if len(df[col].dropna())>0:
            ele = np.unique(df[col].dropna())
        else:
            ele = np.nan
        
        # print(ele)
        if type(ele) == float:
            pass
        else:
            if len(ele) == 1 :
                if pd.isna(ele):
                    pass
                if str(ele) == '[list([])]':
                    pass
                elif str(ele) == '['']':
                    pass
                else:
                    out_dict[col] = ele
                    
            else:
                out_dict[col] = max(ele)
                    

    res = pd.DataFrame(out_dict)
    return res


def calculate_classification_metrics(df, pred_col='pred', label_col='label'):
    """
    Calculates precision, recall, accuracy, and F1-score for binary classification.

    Args:
        df (pd.DataFrame): DataFrame containing prediction and label columns.
        pred_col (str): Name of the prediction column (containing 0s or 1s).
        label_col (str): Name of the true label column (containing 0s or 1s).

    Returns:
        dict: A dictionary containing TP, TN, FP, FN,
              precision, recall, accuracy, and F1-score.
              Returns metrics as 0.0 if denominators are zero for precision/recall.
    """
    # Ensure predictions and labels are integer type (0 or 1)
    # This helps prevent issues if they are, for example, boolean
    predictions = df[pred_col].astype(int)
    labels = df[label_col].astype(int)

    # True Positives (TP): Correctly predicted positive
    tp = ((predictions == 1) & (labels == 1)).sum()
    # True Negatives (TN): Correctly predicted negative
    tn = ((predictions == 0) & (labels == 0)).sum()
    # False Positives (FP): Incorrectly predicted positive (Type I error)
    fp = ((predictions == 1) & (labels == 0)).sum()
    # False Negatives (FN): Incorrectly predicted negative (Type II error)
    fn = ((predictions == 0) & (labels == 1)).sum()

    # Calculate metrics
    # Precision: TP / (TP + FP)
    if (tp + fp) > 0:
        precision = tp / (tp + fp)
    else:
        precision = 0.0  # Or float('nan') if you prefer for undefined cases

    # Recall (Sensitivity or True Positive Rate): TP / (TP + FN)
    if (tp + fn) > 0:
        recall = tp / (tp + fn)
    else:
        recall = 0.0  # Or float('nan')

    # Accuracy: (TP + TN) / (TP + TN + FP + FN)
    total_samples = tp + tn + fp + fn
    if total_samples > 0:
        accuracy = (tp + tn) / total_samples
    else:
        accuracy = 0.0 # Should not happen if df is not empty

    # F1-score: 2 * (Precision * Recall) / (Precision + Recall)
    if (precision + recall) > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0

    metrics = {
        'TP': tp,
        'TN': tn,
        'FP': fp,
        'FN': fn,
        'Precision': precision,
        'Recall': recall,
        'Accuracy': accuracy,
        'F1-score': f1_score
    }
    return metrics


def detect_outliers_iqr(series):

    q1 = series.quantile(0.25)  
    q3 = series.quantile(0.75) 
    iqr = q3 - q1  # IQR (Interquartile Range)

    lower_bound = q1 - 1.5 * iqr  
    upper_bound = q3 + 1.5 * iqr 
    outliers = ((series < lower_bound) | (series > upper_bound))

    return outliers


def get_column_sums(matrix):
    result = [0] * len(matrix[0])
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            result[j] += matrix[i][j]
            
    return result

def unlist(x):
    if len(x) > 0:
        return x[0]
    else:
        return ''
    

def inconsistency_categorical(trace, valid_idx, df, x_col, y_col, level ='event' ,confidence = 0.999):

    y_train = df[y_col].tolist()

    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)  # sparse=False for compatibility
    encoder.fit(df[[x_col]])
    encoded_x = encoder.transform(df[[x_col]])
    feature = encoder.get_feature_names_out([x_col])
    X_train = pd.DataFrame(encoded_x, columns=encoder.get_feature_names_out([x_col]))  # More descriptive column names

    X_test = trace[x_col]
    
    # encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)  # sparse=False for compatibility
    encoded_x = encoder.transform(trace.loc[valid_idx,[x_col]] )
    X_test = pd.DataFrame(encoded_x, columns=feature)  # More descriptive column names

    # 3. Train the Linear Regression Model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 4. Predictions
    y_pred = model.predict(X_train)

    # 5. Calculate Confidence Intervals
    n = len(X_train)
    se = np.sqrt(np.sum((y_train - y_pred)**2) / (n - 2)) # Standard error of the regression

    t_critical = np.abs(np.percentile(np.random.standard_t(n - 2, size=10000), (1 + confidence) / 2)) #t-statistic

    # margin_of_error = se * t_critical * np.sqrt(1 + 1/n + (X_test - X_train.mean()).values @ np.linalg.inv(X_train.T @ X_train) @ (X_test - X_train.mean()).values.reshape(-1,1)) #Margin of error calculation
    
    # 4. Predictions on test sets
    n = len(X_test)
    y_pred = model.predict(X_test)

    # 핵심 수정: X_test와 X_train의 차원을 맞춰줍니다.
    X_test_values = X_test.values  # numpy array로 변환
    X_train_mean = X_train.mean().values.reshape(1, -1) # reshape for broadcasting

    margin_of_error = se * t_critical * np.sqrt(1 + 1/n + np.sum((X_test_values - X_train_mean) @ np.linalg.inv(X_train.T @ X_train) * (X_test_values - X_train_mean), axis=1))

    lower_bound = y_pred - margin_of_error.flatten()
    upper_bound = y_pred + margin_of_error.flatten()
    
    if level =='event':
        res = pd.DataFrame( {'l':lower_bound, 'u':upper_bound}).apply(lambda x: random.sample(list(x), 1)[0], 1).tolist()
    else:
        if random.sample([0,1], 1) == 1:
            res = list(upper_bound)
        else:
            res = list(lower_bound)
    return res



def inconsistency_numeric(trace, valid_idx, df, x_col, y_col, level ='event' ,confidence = 0.999):

    X_train = df[[x_col]].values.reshape(-1, 1)
    y_train = df[y_col].values


    X_test = trace.loc[valid_idx, [x_col]].values.reshape(-1, 1)
    y_test = trace.loc[valid_idx, y_col].values

    # 3. Train the Linear Regression Model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 4. Predictions on the test set
    y_pred = model.predict(X_train)

    # 5. Calculate Confidence Intervals
    n = len(X_train)
    se = np.sqrt(np.sum((y_train - y_pred)**2) / (n - 2))  # Standard error of the regression

    t_critical = np.abs(np.percentile(np.random.standard_t(n - 2, size=10000), (1 + confidence) / 2))

    # 6. Predictions on test sets
    n = len(X_test)
    y_pred = model.predict(X_test)

    # Calculate leverage (hat values)
    H = X_test @ np.linalg.inv(X_train.T @ X_train) @ X_test.T
    leverage = np.diag(H)

    margin_of_error = se * t_critical * np.sqrt(1 + leverage + 1/n) # More accurate Margin of Error

    lower_bound = y_pred - margin_of_error.flatten()
    upper_bound = y_pred + margin_of_error.flatten()
    
    if level =='event':
        res = pd.DataFrame( {'l':lower_bound, 'u':upper_bound}).apply(lambda x: random.sample(list(x), 1)[0], 1).tolist()
    else:
        if random.sample([0,1], 1) == 1:
            res = list(upper_bound)
        else:
            res = list(lower_bound)
    return res


