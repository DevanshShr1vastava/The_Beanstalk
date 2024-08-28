import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
import random


#Category assign function based on percentage of repeat same type of question
def assign_category(row):
    # Extract the percentage of repeats
    percent_repeat = row['percent_repeat']
    
    # Define thresholds for categorization
    if percent_repeat > 60:
        return 2
    elif percent_repeat < 50:
        return 0
    else:
        return 1

df = pd.read_csv('dummyData.csv')

# Select the specified columns
selected_columns = ['user_id', 'question_id', 'domain', 'subdomain', 'label']
df_selected = df[selected_columns]

# Print the selected DataFrame
# print(df_selected)

# Calculate percentages for each subdomain
subdomain_stats = df_selected.groupby('subdomain')['label'].agg(['mean', 'count']).reset_index()
subdomain_stats['percent_repeat'] = subdomain_stats['mean'] * 100

subdomain_stats['category'] = subdomain_stats.apply(assign_category, axis=1)

print(subdomain_stats)

# The new dataset
classified_data = subdomain_stats[['subdomain', 'category']]

print(classified_data)



# Encoding the categories
label_encoder = LabelEncoder()
classified_data.loc[:,'category_encoded'] = label_encoder.fit_transform(classified_data['category'])
print (classified_data)
# Features and labels
X = subdomain_stats[['percent_repeat']]
y = classified_data['category_encoded']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=47)

# Train Weighted KNN
knn_model = KNeighborsClassifier(weights='distance')
knn_model.fit(X_train, y_train)

# Evaluate the models

knn_accuracy = knn_model.score(X_test, y_test)


print(f'\nWeighted KNN Accuracy: {knn_accuracy}')
