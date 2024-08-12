import joblib
import pandas as pd
from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb


class Machine:
    """
    A class to handle machine learning model operations including initialization,
    predictions, model saving/loading, and providing model information.

    Attributes:
    -----------
    name : str
        The name of the machine learning model.
    timestamp : pd.Timestamp
        The timestamp of when the model was initialized.
    model : sklearn.ensemble.StackingClassifier
        The trained stacking classifier model.
    """
    def __init__(self, df=None):
        """
        Initializes the Machine class, trains the stacking classifier model, and stores it as an attribute.

        Parameters:
        -----------
        df : pd.DataFrame
            The input DataFrame containing features and target variable.
            It should include a 'Rarity' column as the target and other columns as features.
        """
        self.name = "Stacking Classifier"
        self.timestamp = pd.Timestamp.now()

        if df is not None:
            # Train model with provided DataFrame
            target = df["Rarity"]
            features = df.drop(columns=["Rarity"])

            # Define base models
            xgboost_model = xgb.XGBClassifier(objective='multi:softprob', eval_metric='mlogloss')
            rf_model = RandomForestClassifier(class_weight='balanced')

            # Define and train stacking classifier
            self.model = StackingClassifier(
                estimators=[
                    ('xgboost', xgboost_model),
                    ('randomforest', rf_model)
                ],
                final_estimator=LogisticRegression()
            )
            self.model.fit(features, target)
        else:
            self.model = None

    def __call__(self, pred_basis: pd.DataFrame):
        """
        Makes predictions and computes prediction probabilities using the trained model.

        Parameters:
        -----------
        pred_basis : pd.DataFrame
            The input DataFrame containing feature data for making predictions.

        Returns:
        --------
        tuple
            A tuple containing the predicted classes and prediction probabilities.
        """
        if pred_basis.empty:
            raise ValueError("Input DataFrame is empty.")

            # Make predictions and get probabilities
        prediction = self.model.predict(pred_basis)
        probabilities = self.model.predict_proba(pred_basis)

        # Debugging information
        print("Prediction:", prediction)
        print("Probabilities shape:", probabilities.shape)
        print("Prediction shape:", prediction.shape)
        print("Probabilities dtype:", probabilities.dtype)
        print("Prediction dtype:", prediction.dtype)
        print("First few probabilities:", probabilities[:5])  # Show first few rows of probabilities for inspection
        print("First few predictions:", prediction[:5])  # Show first few predictions for inspection

        # Map class labels to indices if necessary
        class_labels = self.model.classes_
        label_to_index = {label: idx for idx, label in enumerate(class_labels)}

        # Convert prediction to indices
        try:
            indices = [label_to_index[label] for label in prediction]
        except KeyError as e:
            print("KeyError:", e)
            print("Label to index mapping:", label_to_index)
            raise

        # Extract probabilities for the predicted class
        try:
            predicted_class_probs = [probabilities[i, idx] for i, idx in enumerate(indices)]
        except IndexError as e:
            print("IndexError:", e)
            print("Probabilities array:", probabilities)
            print("Indices:", indices)
            raise

        return prediction, predicted_class_probs

    def save(self, filepath):
        """
        Saves the trained model to a file using joblib.

        Parameters:
        -----------
        filepath : str
            The path where the model file will be saved.
        """
        if self.model is None:
            raise ValueError("No model to save.")
        joblib.dump(self.model, filepath)

    @staticmethod
    def open(filepath):
        """
        Loads a trained model from a file using joblib.

        Parameters:
        -----------
        filepath : str
            The path from which the model file will be loaded.

        Returns:
        --------
        Machine
            An instance of the Machine class with the loaded model.
        """
        model = joblib.load(filepath)
        machine = Machine()
        machine.model = model
        return machine

    def info(self):
        """
        Provides information about the model including its name and initialization timestamp.

        Returns:
        --------
        str
            A string containing the model's name and initialization timestamp.
        """
        return f"Model Name: {self.name}, Initialized At: {self.timestamp}"

