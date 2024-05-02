from sklearn.base import BaseEstimator, TransformerMixin

class CustomTransformer(TransformerMixin, BaseEstimator):
    def __init__(self, prefix=None):
        self.prefix = prefix

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        transformed_X = X.copy()  # Create a copy of the input data
        for column in transformed_X.columns:
            new_column_name = f"{self.prefix}" if self.prefix else column
            transformed_X[new_column_name] = transformed_X[column].str[:2]  # Extract first two elements
            transformed_X.drop(columns=[column], inplace=True)  # Drop the original column
        return transformed_X