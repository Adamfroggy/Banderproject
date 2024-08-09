import pandas as pd
import joblib
import re


def load_your_data_function():
    data = pd.read_csv('data/monsters_data.csv')
    return data


def save_model(model, filepath):
    joblib.dump(model, filepath)


def load_model(filepath):
    return joblib.load(filepath)


def normalize_damage(value):
    """
    Normalize the Damage column value.
    This function should be updated based on how you want to handle different formats.
    """
    if isinstance(value, str):
        # Example normalization: Extract numbers and convert to float
        match = re.search(r'\d+', value)
        if match:
            return float(match.group())
    return float(value)  # Return as float if already numeric


def preprocess_data(df):
    df['Name'] = df['Name'].astype('category')

    # Normalize Damage column
    df['Damage'] = df['Damage'].apply(normalize_damage)

    # Convert categorical columns to string to handle fillna correctly
    df['Name'] = df['Name'].astype(str)

    # Handle cases where conversion to float failed
    df['Damage'] = pd.to_numeric(df['Damage'], errors='coerce')

    # Separate numeric and categorical columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # Fill missing values
    df[numeric_cols] = df[numeric_cols].fillna(0)
    # For categorical columns, you may choose an appropriate strategy, e.g., mode, or a specific value.
    df[categorical_cols] = df[categorical_cols].fillna('unknown')

    # Convert categorical columns back to category type if needed
    df['Name'] = df['Name'].astype('category')

    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Year'] = df['Timestamp'].dt.year
    df['Month'] = df['Timestamp'].dt.month
    df['Day'] = df['Timestamp'].dt.day
    df = df.drop(['Timestamp'], axis=1)

    return df
