import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import LinearRegression, LassoCV
from sklearn.model_selection import train_test_split
from sklearn.impute import KNNImputer
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
import pickle
from CustomTransformer import CustomTransformer
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = 'data'
file_name = 'properties.csv'
file_path = os.path.join(script_dir, data_dir, file_name)

df = pd.read_csv(file_path)
df = df[df["price"] <= 1200000]
df["zip_code"] = df["zip_code"].astype(str)


# Making a pipeline class to put in scikit pipeline
class Preprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, columns_to_drop, rows_to_drop, column_outliers):
        self.columns_to_drop = columns_to_drop
        self.rows_to_drop = rows_to_drop
        self.column_outliers = column_outliers

    def fit(self, X, y=None):
        return self

    def remove_outliers_in_columns(self, df):
        # Calculate z-scores for the specified columns
        z_scores = df[self.column_outliers].apply(lambda x: np.abs((x - x.mean()) / x.std()))

        # Define a threshold for z-score
        threshold = 3  # You can adjust this threshold as needed

        # Remove rows where any specified column has a z-score greater than the threshold
        cleaned_df = df[(z_scores < threshold).all(axis=1)]

        return cleaned_df

    def transform(self, X, y=None):
        # Drop specified columns
        X = X.drop(labels=self.columns_to_drop, axis=1)

        # Drop rows with missing values
        X = X.dropna(subset=self.rows_to_drop)

        # Remove outliers in specified columns
        X = self.remove_outliers_in_columns(X)

        # Conditional replacement of surface_land_sqm
        condition = "APARTMENT"  # Assuming you have a variable named condition defined somewhere
        X.loc[X['property_type'] == condition, 'surface_land_sqm'] = X.loc[X['property_type'] == "APARTMENT", 'total_area_sqm']

        return X



# Decide which columns to drop
columns_to_drop = ['id', 'region', 'province',
       'locality', 'latitude', 'longitude',
       'construction_year',
       'nbr_frontages', 'equipped_kitchen', 'fl_furnished',
       'fl_open_fire', 'fl_terrace', 'fl_garden',
       'fl_swimming_pool', 'fl_floodzone',
       'epc', 'heating_type',
       'fl_double_glazing', 'cadastral_income']
rows_to_drop = ["terrace_sqm", "garden_sqm","primary_energy_consumption_sqm","total_area_sqm"]
column_outliers = ["terrace_sqm", "garden_sqm", "primary_energy_consumption_sqm"]

# Define pipeline
pipeline = Pipeline([
    ('preprocessor', Preprocessor(columns_to_drop, rows_to_drop, column_outliers))
])

save_preprocess = pipeline.fit(df)

# Save the pipeline to possibly reuse
data_dir = 'model'
file_name = 'preprocess.pkl'
file_path = os.path.join(script_dir, data_dir, file_name)

with open(file_path, 'wb') as f:
    pickle.dump(save_preprocess, f)

df = save_preprocess.transform(df)
# Split data into features (X) and target (y)
X = df.drop(columns=["price"])
y = df["price"]

#Split X and y into training and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=50, test_size=0.2)

# Find the numerical columns
numerical_columns = X_train.select_dtypes(include=['int', 'float']).columns
# Find the categorical columns
categorical_columns = X_train.select_dtypes(include=['object']).columns.tolist()
categorical_columns.remove("zip_code")

print(X_train.dtypes)
# Create pipelines for numerical and categorical transformations

postal_pipeline = Pipeline([
    ('customTransform', CustomTransformer("postal_zone")),
    ('onehot', OneHotEncoder())
])

numerical_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('imputer', KNNImputer(n_neighbors=5)) # You can adjust n_neighbors as needed
])

categorical_pipeline = Pipeline([
    ('onehot', OneHotEncoder())
])

# Combine numerical and categorical pipelines using ColumnTransformer
preprocessor = ColumnTransformer([
    ('postal', postal_pipeline, ["zip_code"]),
    ('numerical', numerical_pipeline, numerical_columns),
    ('categorical', categorical_pipeline, categorical_columns)
])

model = RandomForestRegressor(n_estimators=45, max_depth=50)
# Create the final pipeline
final_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('model', model)
])

# Fit the pipeline (this will select the best model automatically)
training = final_pipeline.fit(X_train, y_train)

print(training.score(X_test, y_test))


data_dir = 'model'
file_name = 'model.pkl'
file_path = os.path.join(script_dir, data_dir, file_name)

with open(file_path, 'wb') as f:
    pickle.dump(training, f)
