import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.preprocessing import LabelEncoder

def calculate_correctness_rate(user_attempts):
    correct_answers = sum(user_attempts)
    total_attempts = len(user_attempts)
    return correct_answers / total_attempts if total_attempts>0 else 0


def calculate_confidence_level(row):

    if row['answer'] == 1:
        if(row['time_taken']<60):
            ttC = 1
        else:
            ttC = 0
        return min(5,3 + (row['attempt_number'] < 3) + (not row['marked_for_review']) + ttC)
    else:
        if(row['time_taken']<60):
            ttC = 0
        else:
            ttC = 1
        return max(1,3 - (row['marked_for_review']) - row['attempt_number']-ttC)



def determine_label(row):
    if(row['attempt_number'] > 2 and row['correctness_rate'] < 0.7) or row['confidence_level'] < 3 or row['answer'] == 0:
        return 1 #repeat the same question
    else:
        return 0 #move on from the question


################################################
#GENERATING A SAMPLE DATASET TO TRAIN THE MODEL AND TEST THE MODEL
################################################
np.random.seed(41)
QuestionBank = pd.read_csv("questionBank.csv")

qb_dbms_df = QuestionBank[QuestionBank['domain']=='DBMS']
qb_dsa_df = QuestionBank[QuestionBank['domain']=='DSA']

domains = ["DBMS","Data Structures"]
subdomains_dbms = list(qb_dbms_df['subdomain'].unique())
subdomains_ds = list(qb_dsa_df['subdomain'].unique())
subdomains = subdomains_dbms + subdomains_ds

#initialize an empty list to collect rows

data = []


#generate data for users and questions

for user_id in range(1,9): # 5 users
    user_attempts = []
    for question_id in range(100,400): # 300 questions
        domain = np.random.choice(domains)
        subdomain = np.random.choice(subdomains_dbms if domain == "DBMS" else subdomains_ds)
        for attempt_number in range(1,np.random.randint(2,5)): # 1 to 3 attempts for questions
            time_taken = np.random.randint(30,120) #20 to 120 seconds
            answer = np.random.randint(0,2) # 0 or 1 (incorrect or correct)
            marked_for_review = np.random.randint(0,2) # 0 or 1 (unmarked or marked)

            #update user attempts and calculate correctness rate

            user_attempts.append(answer)
            correctness_rate = calculate_correctness_rate(user_attempts)

            #Calculate teh confidence level

            confidence_level = calculate_confidence_level({
                'answer':answer,
                'attempt_number':attempt_number,
                'marked_for_review':marked_for_review,
                'time_taken':time_taken
            })

            # Determine the label

            label = determine_label({
                'attempt_number' : attempt_number,
                'correctness_rate':correctness_rate,
                'marked_for_review':marked_for_review,
                'confidence_level' : confidence_level,
                'answer' : answer
            })

            #append the row to the Dataframe

            row ={
                'user_id':user_id,
                'question_id':question_id,
                'domain':domain,
                'subdomain':subdomain,
                'attempt_number':attempt_number,
                'time_taken':time_taken,
                'answer':answer,
                'marked_for_review':marked_for_review,
                'correctness_rate':correctness_rate,
                'confidence_level':confidence_level,
                'label':label
            }
            data.append(row)

#check the dataset now
df = pd.DataFrame(data)
# print(df.head())

df.to_csv('dummyData.csv',index = False)

###################################################################################
#CREATING OUR CLASSIFICATION MODEL NOW
###################################################################################

# Load the dataset
df = pd.read_csv('dummyData.csv')

# Prepare the feature set and labels
X = df.drop(columns=['label', 'user_id', 'question_id', 'domain', 'subdomain'])
y = df['label']

# Feature scaling
scaler = StandardScaler()
x_scaled = scaler.fit_transform(X)

# Initialize the models

knn = KNeighborsClassifier(n_neighbors=5, weights='distance')
svm = SVC(probability = True)
logReg = LogisticRegression()

# combine models into an ensemble using soft voting

ensemble_model_QC = VotingClassifier(estimators=[
    ('knn',knn),
    ('svm',svm),
    ('logReg',logReg)
], voting='soft')

# K-folds cross validation

kf = StratifiedKFold(n_splits = 5, shuffle=True, random_state = 32)

# evaluate ensemble models with cross validation

cv_scores = cross_val_score(ensemble_model_QC, x_scaled, y, cv = kf, scoring='accuracy')
print("Mean Cross Validation Score for Question Classification model : ",cv_scores)
print("Mean Cross Validation Score for Question Classification model : ",cv_scores.mean())

#confusion matrix

# # Initialize an empty confusion matrix
# cumulative_conf_matrix = np.zeros((2, 2))  # Adjust for binary classification (2 classes)

# # Perform k-fold cross-validation
# for train_index, test_index in kf.split(x_scaled, y):
#     X_train, X_test = x_scaled[train_index], x_scaled[test_index]
#     y_train, y_test = y.iloc[train_index], y.iloc[test_index]

#     # Train the voting classifier on the training fold
#     ensemble_model_QC.fit(X_train, y_train)

#     # Predict the labels for the test fold
#     y_pred = ensemble_model_QC.predict(X_test)

#     # Compute confusion matrix for the current fold
#     fold_conf_matrix = confusion_matrix(y_test, y_pred)

#     # Accumulate confusion matrices
#     cumulative_conf_matrix += fold_conf_matrix

# # Calculate the average confusion matrix (optional, or just use cumulative one)
# average_conf_matrix = cumulative_conf_matrix / 5  # Divide by number of folds if needed

# # Print the confusion matrix
# print("Cumulative Confusion Matrix:")
# print(cumulative_conf_matrix)

# # Visualize the confusion matrix
# plt.figure(figsize=(6,4))
# sns.heatmap(cumulative_conf_matrix, annot=True, fmt='g', cmap='Blues', xticklabels=['Class 0', 'Class 1'], yticklabels=['Class 0', 'Class 1'])
# plt.title('Confusion Matrix (K-Folds)')
# plt.xlabel('Predicted Label')
# plt.ylabel('True Label')
# plt.show()

# Print cross-validation scores
# print(f'Cross-validation scores: {cv_scores}')
# print(f'Mean accuracy: {cv_scores.mean
# Fit ensemble model to the entire training set

ensemble_model_QC.fit(x_scaled, y)

##########################################################################################################################
# New input data
# new_data = pd.DataFrame({
#     'attempt_number': [1],
#     'time_taken': [85],
#     'answer': [1],
#     'marked_for_review': [1],
#     'correctness_rate': [0.7],
#     'confidence_level': [3]
# })

# # Scale the new data using the same scaler
# new_data_scaled = scaler.transform(new_data)

# # Predict using the model
# prediction = knn.predict(new_data_scaled)

# # Print the result
# print(f'Predicted label for the new input: {prediction[0]}')
##########################################################################################################################

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


# Select the specified columns
selected_columns = ['user_id', 'question_id', 'domain', 'subdomain', 'label']
df_selected = df[selected_columns]

# Print the selected DataFrame
# print(df_selected)

# Calculate percentages for each subdomain
subdomain_stats = df_selected.groupby('subdomain')['label'].agg(['mean', 'count']).reset_index()
subdomain_stats['percent_repeat'] = subdomain_stats['mean'] * 100

subdomain_stats['category'] = subdomain_stats.apply(assign_category, axis=1)

# print(subdomain_stats)

# The new dataset
classified_data = subdomain_stats[['subdomain', 'category']]

# print(classified_data)

# Encoding the categories
label_encoder = LabelEncoder()
# Properly using .loc to avoid the warning
# Make an explicit copy to avoid the warning
classified_data = classified_data.copy()

classified_data.loc[:, 'category_encoded'] = label_encoder.fit_transform(classified_data['category'])


# Features and labels
X2 = subdomain_stats[['percent_repeat']]
y2 = classified_data['category_encoded']

#Feature Scaling
scaler2= StandardScaler()
x2_scaled = scaler2.fit_transform(X2)
x2_scaled = pd.DataFrame(x2_scaled, columns=X2.columns) #to avoid the fitted without feature names warning


knn_model = KNeighborsClassifier(n_neighbors=5, weights='distance')
svm_model = SVC(probability = True)
logReg_model = LogisticRegression()


#creating the second ensemble model which is using soft voting
ensemble_model_TC = VotingClassifier(estimators = [
    ('knn', knn_model),
    ('svm', svm_model),
    ('logreg', logReg_model)
], voting = 'soft')


# K-folds cross validation

kf2 = StratifiedKFold(n_splits = 5, shuffle=True, random_state = 32)


# Evaluate the ensemble model with cross-validation
cv_scores_TC = cross_val_score(ensemble_model_TC, x2_scaled, y2, cv=kf2, scoring='accuracy')
print("Cross Validation Score for Topic Classification model : ",cv_scores_TC)
print("Mean Cross Validation Score for Topic Classification model : ",cv_scores_TC.mean())

# Fit the ensemble model to the entire dataset
ensemble_model_TC.fit(x2_scaled, y2)