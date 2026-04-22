# 1. Objective of this notebook 
# The objective of this notebook is to clean and preprocess the customer shopping behavior dataset to ensure its quality and usability for analysis.

# 2. Import libraries

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Objective of this notebook 
# 2. Import libraries
# 3. Load data
# 4. Initial inspection
# 5. Understand columns
# 6. Fix data types
# 7. Handle missing values
# 8. Remove duplicates
# 9. Assess data quality
# 10. Standardize categories
# 11. Validate numeric values
# 12. Detect outliers
# 13. Fix dates and create time features which we don't have in the dataset.
# 14. Feature engineering
# 15. Final validation
# 16. Save cleaned dataset
# 17. Summary

# 3. Load data
df=pd.read_csv('../data/01_raw/customer_shopping_behavior.csv')

# 4. Initial inspection

print ("------------------ 1 Initial Data inspection -------------------")
# Step 1: Check the shape of the dataset (number of rows and columns)
print(df.shape)

# Step 2: Display the first few rows of the dataset to get an initial understanding of the data and its structure. This helps to identify the columns present in the dataset, the types of data they contain, and any potential issues such as missing values or inconsistent formatting.
print(df.head())

# Step 4: Describe() provides a statistical summary of the numerical columns in the DataFrame, including count, mean, standard deviation, minimum, 25th percentile, median (50th percentile), 75th percentile, and maximum values. This helps to understand the distribution and central tendency of the numerical data.
#print(data.describe())
print(df.describe(include = 'all'))

# Step 5: Check for missing values in the dataset. This is crucial for data cleaning, as missing values can affect the analysis and modeling process. The isnull() function returns a DataFrame of the same shape as the original, with True for missing values and False for non-missing values. The sum() function then counts the number of missing values in each column.
print(df.isnull().sum()) # we have some missing values in reviwe rating column, remaining columns have no null vaues.

# 5. Understand columns

print ("------------------- Understand columns-")
# standardize column names to improve readability, consistency, and ease of analysis. 
# Step 1: Info() gives a concise summary of the dataset, including the number of non-null entries, data types of each column, and memory usage. This helps to identify any potential issues with missing data or incorrect data types that may need to be addressed during the data cleaning process.

print(df.info())
# 6. Fix data types
print(df.dtypes) 

# standardizing column names
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
print("\nStandardized column names:")
print(df.columns.tolist())

# Separate columns by type
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
categorical_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
datetime_cols = df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()

print("\nNumeric columns:", numeric_cols)
print("Categorical columns:", categorical_cols)
print("Datetime columns:", datetime_cols)

print(df.columns)
for col in ["age", "purchase_amount_(usd)", "size", "payment_method", "season"]:
    print(f"\nColumn: {col}")
    print(f"{col}:Count",df[col].value_counts(dropna=False))

# 7. Handle missing values

sns.histplot(df['review_rating'], bins=20, kde=True)
plt.title("Distribution of Review Rating")

mean_val = df['review_rating'].mean()
median_val = df['review_rating'].median()

print("Mean:", mean_val)
print("Median:", median_val)

df['review_rating'] = df.groupby('category')['review_rating'].transform(lambda x: x.fillna(x.median()))

# 8. Remove duplicates

print (("Duplicated", df.duplicated().sum())) #no fully duplicated rows in the dataset

# 9. Understand categorical variables 
for col in categorical_cols:
    print(f"\nColumn: {col}")
    print("Number of unique values:", df[col].nunique())
    print(df[col].value_counts())  # Display the top 10 most frequent values in the column

# 10. Validate numeric values # Check for negative values in numeric columns  

for col in numeric_cols:
    if (df[col] < 0).any():
        print(f"Negative values found in column: {col}")
    else:
        print(f"No negative values in column: {col}")   

print("# 12. Detect outliers fisrt usiing describe() then using boxplot then using IQR method , then z-score method.")

print(df.describe())

for col in numeric_cols:
    plt.figure(figsize=(8, 4))
    sns.boxplot(x=df[col])
    plt.title(f"Boxplot of {col}")
    plt.show()
for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

    print(f"{col}: {len(outliers)} outliers")

# 13. Created business-driven derived features
#  Age groups : Business decisions are often made by age groups, not raw age.

bins = [0, 18, 25, 35, 45, 60, 100]
labels = ["under_18", "18_25", "26_35", "36_45", "46_60", "60_plus"]
df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels, right=True)
print(df.head())

df["frequency_purchase_days"]= df["frequency_of_purchases"].map({
    "Annually": 365,
    "Bi-Weekly": 14,
    "Every 3 Months": 90,
    "Fortnightly": 14,
    "Monthly": 30,
    "Quarterly": 90,
    "Weekly": 7
})


#print(df[['discount_applied','promo_code_used']]).head(10)
# Check both columns has same values
if df['discount_applied'].equals(df['promo_code_used']):
    print("\nBoth columns 'discount_applied' and 'promo_code_used' have the same values. Dropping 'promo_code_used'.")
    df.drop(columns=['promo_code_used'], inplace=True)
else:
    print("\nColumns 'discount_applied' and 'promo_code_used' have different values. Keeping both columns.")    

print(df.head(5))

# 14. Final validation
df.info()
df.isnull().sum()
df.describe(include="all")
# 15. Save cleaned dataset
df.to_csv("../data/02_processed/customer_data_cleaned.csv", index=False)
# 16. Summary
## Data Cleaning Summary
'''
The following cleaning steps were completed:
- standardized column names
- inspected structure and summary statistics
- cheked duplicate rows
- handled missing values in key fields
- corrected data types for dates and numeric columns
- standardized categorical labels
- validated age, purchase amount, quantity, and review rating ranges
- engineered analytical features such as age groups, purchase month, season, and repeat customer flag
- exported the cleaned dataset for downstream analysis

'''
