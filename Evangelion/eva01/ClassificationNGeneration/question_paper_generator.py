import pandas as pd
import random
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier

from question_label_model import *
from subdomain_label_model import *

data = [
    [1, 122, 'DBMS', 'SQL Basics', [1,1,1,1,1], 40, 1, 1],
    [1, 133, 'DBMS', 'Normalization', [0, 0, 1, 0], 85, 0, 0],
    [1, 144, 'DBMS', 'SQL Constraints', [1], 75, 1, 1],
    [1, 155, 'DBMS', 'Keys', [1,1,1,1,1], 90, 0, 0],
    [1, 166, 'DBMS', 'SQL Functions', [0, 0, 1, 0], 55, 1, 1],
    [1, 177, 'DBMS', 'Joins', [1], 100, 1, 0],
    [1, 188, 'DBMS', 'Stored Procedures', [1, 0, 1], 110, 0, 1],
    [1, 199, 'DBMS', 'Transactions', [1,1,1,1,1], 65, 1, 0],
    [1, 110, 'DBMS', 'Database Models', [1], 95, 0, 1],
    [1, 121, 'DBMS', 'Indexing', [1,1,1,1,1], 70, 1, 0],
    [1, 132, 'DBMS', 'Views', [1, 0, 1], 85, 0, 0],
    [1, 143, 'DBMS', 'Database Design', [1], 100, 1, 1],
    [1, 154, 'DBMS', 'Security', [0, 0, 1], 65, 0, 0],
    [1, 165, 'DBMS', 'Backup & Recovery', [1], 105, 1, 1],
    [1, 176, 'DSA', 'Searching', [0, 0, 1], 35, 0, 1],
    [1, 187, 'DSA', 'Stack', [1], 115, 1, 0],
    [1, 198, 'DSA', 'Sorting', [1, 0], 90, 0, 0],
    [1, 109, 'DSA', 'Queue', [0, 0, 1], 50, 1, 1],
    [1, 120, 'DSA', 'Graph', [1], 85, 0, 0],
    [1, 131, 'DSA', 'Heap', [1,1,1], 60, 1, 0],
    [1, 142, 'DSA', 'Tree', [1], 125, 0, 1],
    [1, 153, 'DSA', 'Algorithms', [1, 0], 45, 1, 0],
    [1, 164, 'DSA', 'Hashing', [1,1,1], 75, 0, 1],
    [1, 175, 'DSA', 'Linked List', [1], 55, 1, 0],
    [1, 186, 'DSA', 'Array', [1,1,1], 90, 0, 1],
    [1, 197, 'DSA', 'Algorithm', [1, 0], 80, 1, 0],
    [1, 108, 'DBMS', 'SQL Basics', [1, 0], 55, 1, 0],
    [1, 119, 'DBMS', 'Normalization', [1], 70, 0, 1],
    [1, 130, 'DBMS', 'SQL Constraints', [1,1,1], 60, 1, 0],
    [1, 141, 'DBMS', 'Keys', [1, 0], 110, 0, 1],
    [1, 152, 'DBMS', 'SQL Functions', [1], 50, 1, 0],
    [1, 163, 'DBMS', 'Joins', [0, 0, 1], 95, 1, 0],
    [1, 174, 'DBMS', 'Stored Procedures', [1], 80, 0, 1],
    [1, 185, 'DBMS', 'Transactions', [1, 0], 120, 1, 0],
    [1, 196, 'DBMS', 'Database Models', [0, 0, 1], 65, 0, 0],
    [1, 107, 'DBMS', 'Indexing', [1], 105, 1, 1],
    [1, 118, 'DBMS', 'Views', [1, 0], 70, 0, 0],
    [1, 129, 'DBMS', 'Database Design', [0, 0, 1], 130, 1, 1],
    [1, 140, 'DBMS', 'Security', [1], 60, 0, 0],
    [1, 151, 'DBMS', 'Backup & Recovery', [1, 0], 100, 1, 1],
    [1, 162, 'DSA', 'Searching', [0, 0, 1], 35, 0, 1],
    [1, 173, 'DSA', 'Stack', [1], 110, 1, 0],
    [1, 184, 'DSA', 'Sorting', [1, 0], 85, 0, 0],
    [1, 195, 'DSA', 'Queue', [0, 0, 1], 50, 1, 1],
    [1, 106, 'DSA', 'Graph', [1], 95, 0, 0],
    [1, 117, 'DSA', 'Heap', [1, 0, 1], 60, 1, 0],
    [1, 128, 'DSA', 'Tree', [1, 0], 120, 0, 1],
    [1, 139, 'DSA', 'Algorithms', [1, 0, 1], 45, 1, 0],
    [1, 150, 'DSA', 'Hashing', [1, 0], 75, 0, 1],
    [1, 161, 'DSA', 'Linked List', [1, 0, 1], 55, 1, 0],
    [1, 172, 'DSA', 'Array', [1], 90, 0, 1],
    [1, 183, 'DSA', 'Algorithm', [1, 0, 1], 80, 1, 0],
    [1, 201, 'DBMS', 'SQL Basics', [1, 0], 60, 1, 0],
    [1, 202, 'DBMS', 'Normalization', [1], 70, 0, 1],
    [1, 203, 'DBMS', 'SQL Constraints', [1, 0, 1], 65, 1, 0],
    [1, 204, 'DBMS', 'Keys', [1, 0], 80, 0, 1],
    [1, 205, 'DBMS', 'SQL Functions', [1], 75, 1, 0],
    [1, 206, 'DBMS', 'Joins', [1, 0,1,1], 90, 1, 0],
    [1, 207, 'DBMS', 'Stored Procedures', [1, 0, 1], 100, 0, 1],
    [1, 208, 'DBMS', 'Transactions', [1], 85, 1, 0],
    [1, 209, 'DBMS', 'Database Models', [1, 0,1,1], 95, 0, 1],
    [1, 210, 'DBMS', 'Indexing', [1], 110, 1, 0],
    [1, 211, 'DBMS', 'Views', [1, 0,1,1], 80, 0, 1],
    [1, 212, 'DBMS', 'Database Design', [0], 105, 1, 1],
    [1, 213, 'DBMS', 'Security', [1, 0, 1], 90, 0, 0],
    [1, 214, 'DBMS', 'Backup & Recovery', [0], 115, 1, 1],
    [1, 215, 'DSA', 'Searching', [1, 0,1,1], 45, 0, 1],
    [1, 216, 'DSA', 'Stack', [1, 1, 1, 1], 100, 1, 0],
    [1, 217, 'DSA', 'Sorting', [0], 80, 0, 1],
    [1, 218, 'DSA', 'Queue', [1, 0], 60, 1, 1],
    [1, 219, 'DSA', 'Graph', [1, 1, 1, 1], 90, 0, 0],
    [1, 220, 'DSA', 'Heap', [0], 70, 1, 0],
    [1, 221, 'DSA', 'Tree', [1, 1, 1, 1], 125, 0, 1],
    [1, 222, 'DSA', 'Algorithms', [0], 55, 1, 0],
    [1, 223, 'DSA', 'Hashing', [1, 0], 85, 0, 1],
    [1, 224, 'DSA', 'Linked List', [1, 1, 1, 1], 60, 1, 0],
    [1, 225, 'DSA', 'Array', [0], 95, 0, 1],
    [1, 226, 'DSA', 'Algorithm', [1, 0], 80, 1, 0],
    [1, 227, 'DBMS', 'SQL Basics', [1, 1, 1, 1], 50, 1, 1],
    [1, 228, 'DBMS', 'Normalization', [0], 65, 0, 0],
    [1, 229, 'DBMS', 'SQL Constraints', [1, 0], 70, 1, 1],
    [1, 230, 'DBMS', 'Keys', [1, 0, 1], 85, 0, 1],
    [1, 231, 'DBMS', 'SQL Functions', [0], 90, 1, 0],
    [1, 232, 'DBMS', 'Joins', [1, 0], 80, 1, 0],
    [1, 233, 'DBMS', 'Stored Procedures', [1], 95, 0, 1],
    [1, 234, 'DBMS', 'Transactions', [1, 0, 1], 75, 1, 0],
    [1, 235, 'DBMS', 'Database Models', [1], 110, 0, 1],
    [1, 236, 'DBMS', 'Indexing', [1, 0], 100, 1, 0],
    [1, 237, 'DBMS', 'Views', [1], 85, 0, 1],
    [1, 238, 'DBMS', 'Database Design', [1, 0], 105, 1, 1],
    [1, 239, 'DBMS', 'Security', [1], 95, 0, 0],
    [1, 240, 'DBMS', 'Backup & Recovery', [1, 0, 1], 115, 1, 1],
    [1, 241, 'DSA', 'Searching', [1], 50, 0, 1],
    [1, 242, 'DSA', 'Stack', [1, 0], 120, 1, 0],
    [1, 243, 'DSA', 'Sorting', [1, 0, 1], 85, 0, 1],
    [1, 244, 'DSA', 'Queue', [1], 65, 1, 1],
    [1, 245, 'DSA', 'Graph', [1, 0], 90, 0, 0],
    [1, 246, 'DSA', 'Heap', [1, 0, 1], 70, 1, 0],
    [1, 247, 'DSA', 'Tree', [1], 125, 0, 1],
    [1, 248, 'DSA', 'Algorithms', [1, 0], 55, 1, 0],
    [1, 249, 'DSA', 'Hashing', [1], 85, 0, 1],
    [1, 250, 'DSA', 'Linked List', [1, 0], 60, 1, 0],
    [1, 251, 'DSA', 'Array', [0, 0, 1, 0], 95, 0, 1],
    [1, 252, 'DSA', 'Algorithm', [1], 80, 1, 0],
    [1, 253, 'DBMS', 'SQL Basics', [1, 0], 55, 1, 1],
    [1, 254, 'DBMS', 'Normalization', [1], 75, 0, 1],
    [1, 255, 'DBMS', 'SQL Constraints', [0, 0, 1, 0], 70, 1, 0],
    [1, 256, 'DBMS', 'Keys', [1], 85, 0, 1],
    [1, 257, 'DBMS', 'SQL Functions', [1, 0], 80, 1, 0],
    [1, 258, 'DBMS', 'Joins', [1], 90, 1, 0],
    [1, 259, 'DBMS', 'Stored Procedures', [1, 0], 100, 0, 1],
    [1, 260, 'DBMS', 'Transactions', [1], 65, 1, 0],
    [1, 261, 'DBMS', 'Database Models', [0, 0, 1, 0], 95, 0, 1],
    [1, 262, 'DBMS', 'Indexing', [1], 105, 1, 0],
    [1, 263, 'DBMS', 'Views', [1, 0], 80, 0, 1],
    [1, 264, 'DBMS', 'Database Design', [1], 110, 1, 1],
    [1, 265, 'DBMS', 'Security', [1, 0], 90, 0, 0],
    [1, 266, 'DBMS', 'Backup & Recovery', [1], 115, 1, 1],
    [1, 267, 'DSA', 'Searching', [1, 0], 45, 0, 1],
    [1, 268, 'DSA', 'Stack', [1], 120, 1, 0]
]

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



df_data_list = []

for i in range(len(data)):
    attCnt = len(data[i][4])
    correctness_rate = calculate_correctness_rate(data[i][4])
    confidence_level = calculate_confidence_level({
        'answer':data[i][6],
        'attempt_number':attCnt,
        'marked_for_review':data[i][7],
        'time_taken':data[i][5]
    })
    
    row = {
        'user_id':data[i][0],
        'question_id':data[i][1],
        'domain':data[i][2],
        'subdomain':data[i][3],
        'attempt_number':attCnt,
        'time_taken':data[i][5],
        'answer':data[i][6],
        'marked_for_review':data[i][7],
        'correctness_rate':correctness_rate,
        'confidence_level':confidence_level,
    }

    df_data_list.append(row)

dataFramePrimary = pd.DataFrame(df_data_list)

#now to get the data to send to model

inpData = dataFramePrimary.drop(columns=['user_id','question_id','domain','subdomain'])

# print(inpData)
#scale the above data and then make predictions and store them in original df
inpDataScale = scaler.transform(inpData)

# print(type(inpDataScale))

predict=knn.predict(inpDataScale)

QuestionLabelledData = []

for index,rows in inpData.iterrows():
    
    nRow = {
        'user_id':df_data_list[index].get('user_id'),
        'question_id':df_data_list[index].get('question_id'),
        'domain':df_data_list[index].get('domain'),
        'subdomain':df_data_list[index].get('subdomain'),
        'attempt_number':df_data_list[index].get('attempt_number'),
        'time_taken':df_data_list[index].get('time_taken'),
        'answer':df_data_list[index].get('answer'),
        'marked_for_review':df_data_list[index].get('marked_for_review'),
        'correctness_rate':df_data_list[index].get('correctness_rate'),
        'confidence_level':df_data_list[index].get('confidence_level'),
        'label':predict[index]
    }
    QuestionLabelledData.append(nRow)

questionLabeledDataFrame = pd.DataFrame(QuestionLabelledData)

#now classifying the topics
#selecting the required columns for secondary classification

toLabelTopicDataFrame = questionLabeledDataFrame[selected_columns]

#calculating percentages for each subdomain

tolabelTopic_stats = toLabelTopicDataFrame.groupby('subdomain')['label'].agg(['mean','count']).reset_index()

tolabelTopic_stats['percent_repeat'] = tolabelTopic_stats['mean'] * 100
print(tolabelTopic_stats)
secondth = knn_model.predict(tolabelTopic_stats.drop(columns=['subdomain','mean','count']))

topic_classification = []

def Tclassify(lab):
    if(lab == 0):
        return 'Move on from the Topic'
    elif(lab==1):
        return 'Repeat Same Topic with Less Weightage'
    elif(lab==2):
        return 'Repeat Same Topic with More Weightage'
    else:
        return 'Invalid'

for i in range(len(secondth)):
    newRow = {
        'subdomain':tolabelTopic_stats.get('subdomain')[i],
        'category':Tclassify(secondth[i]),
        'category_encoded':secondth[i]
    }
    topic_classification.append(newRow)

finalClassificationDataFrame = pd.DataFrame(topic_classification)

print(finalClassificationDataFrame)


import pandas as pd
import random

# Load the question bank dataset
QuestionBank = pd.read_csv('questionBank.csv')

# List of selected subdomains
selected_subdomain = [
    'SQL Basics',
    'Normalization',
    'SQL Constraints',
    'Keys',
    'SQL Functions',
    'Joins',
    'Transactions',
    'Security',
    'Backup & Recovery'
]

# Mapping the difficulty for each subdomain with a numeric value
difficultyMap = {'Easy': 1, 'Medium': 2, 'Hard': 3}
QuestionBank['difficulty_numeric'] = QuestionBank['difficulty'].map(difficultyMap)

# Filter questions by selected subdomains
subdomainQB = QuestionBank[QuestionBank['subdomain'].isin(selected_subdomain)]

# Calculate the average difficulty for each subdomain
subdomainQB_difficulty = subdomainQB.groupby('subdomain')['difficulty_numeric'].mean().reset_index()
subdomainQB_difficulty.columns = ['subdomain', 'avg_difficulty']

# Initialize weights dynamically
weights = dict.fromkeys(selected_subdomain, 0)

# Function to adjust weights
def adjust_weights(weights, subdomain, adjustment):
    if subdomain in weights:
        weights[subdomain] += adjustment
        if weights[subdomain] < -1:
            weights[subdomain] = -1
        elif weights[subdomain] > 1:
            weights[subdomain] = 1
    return weights



# Add weight column to DataFrame
subdomainQB_difficulty['weight'] = subdomainQB_difficulty['subdomain'].map(weights)

# Calculate the number of questions to select from each subdomain
min_questions = 1
total_questions = random.randint(20, 26)
additional_questions = total_questions - min_questions * len(selected_subdomain)

# Adjust question calculation to include weights
subdomainQB_difficulty['weighted_difficulty'] = (
    (subdomainQB_difficulty['avg_difficulty'] + subdomainQB_difficulty['weight']) / 
    (subdomainQB_difficulty['avg_difficulty'].max() + 1)
)

subdomainQB_difficulty['questions'] = min_questions + (
    (subdomainQB_difficulty['weighted_difficulty'] / subdomainQB_difficulty['weighted_difficulty'].sum()) * additional_questions
).astype(int)

# Adjust to ensure the total number of questions is within the required range
if subdomainQB_difficulty['questions'].sum() > total_questions:
    while subdomainQB_difficulty['questions'].sum() > total_questions:
        max_index = subdomainQB_difficulty['questions'].idxmax()
        subdomainQB_difficulty.at[max_index, 'questions'] -= 1
elif subdomainQB_difficulty['questions'].sum() < total_questions:
    while subdomainQB_difficulty['questions'].sum() < total_questions:
        min_index = subdomainQB_difficulty['questions'].idxmin()
        subdomainQB_difficulty.at[min_index, 'questions'] += 1

# Ensure questions include all three difficulties and prioritize hard questions
selected_QIDS = []
for _, row in subdomainQB_difficulty.iterrows():
    subdomain = row['subdomain']
    num_questions = row['questions']

    subdomain_questions = subdomainQB[subdomainQB['subdomain'] == subdomain]

    easy_questions = subdomain_questions[subdomain_questions['difficulty'] == 'Easy']
    medium_questions = subdomain_questions[subdomain_questions['difficulty'] == 'Medium']
    hard_questions = subdomain_questions[subdomain_questions['difficulty'] == 'Hard']

    num_hard = min(num_questions // 2, len(hard_questions))
    num_easy_medium = num_questions - num_hard

    num_easy = min(num_easy_medium // 2, len(easy_questions))
    num_medium = num_easy_medium - num_easy

    if num_easy + num_medium + num_hard < num_questions:
        remaining = num_questions - (num_easy + num_medium + num_hard)
        num_hard += remaining

    # Now randomly selecting questions, ensuring they don't repeat frequently
    selected_QIDS += random.sample(list(hard_questions['qID']), min(num_hard, len(hard_questions)))
    selected_QIDS += random.sample(list(medium_questions['qID']), min(num_medium, len(medium_questions)))
    selected_QIDS += random.sample(list(easy_questions['qID']), min(num_easy, len(easy_questions)))        

# Adjust the number of selected questions to ensure it falls within the required range
while len(selected_QIDS) < 20:
    for _, row in subdomainQB_difficulty.iterrows():
        subdomain = row['subdomain']
        subdomain_questions = subdomainQB[subdomainQB['subdomain'] == subdomain]
        remaining_questions = subdomain_questions[~subdomain_questions['qID'].isin(selected_QIDS)]
        if len(remaining_questions) > 0:
            selected_QIDS.append(remaining_questions.sample(1)['qID'].values[0])
        if len(selected_QIDS) >= 20:
            break

while len(selected_QIDS) > 26:
    selected_QIDS.pop()

# Shuffle the selected qIDs to ensure a different order each run
random.shuffle(selected_QIDS)

print(selected_QIDS)
