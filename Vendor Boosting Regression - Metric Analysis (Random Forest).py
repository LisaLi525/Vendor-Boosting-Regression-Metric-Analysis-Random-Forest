# Vendor Boosting Regression - Metric Analysis (Random Forest)

# Importing libraries
import numpy as np
import pandas as pd
import pyodbc
import psycopg2
import seaborn as sns
sns.set(style="white")
sns.set(style="whitegrid", color_codes=True)
import matplotlib.pyplot as plt
plt.rc("font", size=14)

# Connecting to the database
import getpass
database_password = getpass.getpass('Enter your database password:')

import sqlalchemy as sa
from sqlalchemy.engine.url import URL

# build the sqlalchemy URL with placeholder values
url = URL.create(
    drivername='postgresql+psycopg2',  # postgresql driver and dialect
    host='your_database_host',  # database host
    port=5432,  # database port
    database='your_database_name',  # database name
    username='your_database_username',  # database username
    password=database_password  # database password
)

engine = sa.create_engine(url)

# Prepare the model by getting all the factors from the vendor table.
vendor_query = """
with vendor_data as (
    select
        vendor_id,
        count(distinct session_id || product_id)::numeric as website_traffic
    from your_table
    where request_date::date >= current_date - interval '6 months'
    and vendor_id <> ''
    and page_type_group in ('detail', 'details')
    group by vendor_id
)
select * from vendor_data;
"""

vendor_data = pd.read_sql_query(vendor_query, engine)

# Replace 'Y/N' with 1/0
vendor_data_f = vendor_data.replace(to_replace={'Y': 1, 'N': 0})
print(vendor_data_f.head())
print(vendor_data_f.describe())

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

# Scaling the data
scaler = StandardScaler()
vendor_data_f_scale = scaler.fit_transform(vendor_data_f)
vendor_data_f_scale = pd.DataFrame(vendor_data_f_scale, columns=vendor_data_f.columns)

# Select columns for X and Y
y_column = 'your_target_column'
x_columns = [col for col in vendor_data_f.columns if col != y_column]

# Random Forest Regressor
rf = RandomForestRegressor(n_jobs=-1, n_estimators=15, max_features="log2", verbose=1, random_state=42)
rf.fit(vendor_data_f_scale[x_columns], vendor_data_f_scale[y_column])

# Feature Importance
importance = rf.feature_importances_
important_features_dict = {x_columns[i]: importance[i] for i in range(len(x_columns))}
sorted_features = sorted(important_features_dict.items(), key=lambda x: x[1], reverse=True)
for feature in sorted_features:
    print(feature)

# Visualizing feature importance
plt.figure(figsize=(10, 5))
plt.bar(important_features_dict.keys(), important_features_dict.values())
plt.xticks(rotation=90)
plt.ylabel('importance')
plt.title('Random Forest Regressor Feature Importance')
plt.show()

## Notes
## 1. Database Connection: The database connection details have been replaced with placeholders (`your_database_host`, `your_database_username`, etc.). You need to replace these with actual values.
## 2. QL Query: The SQL query has been simplified and placeholders (`your_table`, `your_target_column`) are used. Modify the query according to your actual database schema.
## 3. Feature Selection: Adjust the feature selection (`x_columns`, `y_column`) based on your dataset.
## 4. Random Forest Regressor: I've set random_state to 42 for reproducibility, and you might want to adjust the parameters of `RandomForestRegressor` based on your specific needs.
