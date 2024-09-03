import random
import pandas as pd
from eva01.analyseUsr import knn,knn_model,calculate_confidence_level,calculate_correctness_rate,scaler, selected_columns
from .models import questionBank

def adjust_weights(weights, subdomain, adjustment):
        if subdomain in weights:
            weights[subdomain] += adjustment
            if weights[subdomain] < -1:
                weights[subdomain] = -1
            elif weights[subdomain] > 1:
                weights[subdomain] = 1
        return weights

def generateQIDS(QuestionBank,weights_updated=None):
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
    if(weights_updated is not None):
        weights = weights_updated
    else:
        weights = dict.fromkeys(selected_subdomain, 0)

    # Function to adjust weights
    

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

    return selected_QIDS


def analyse_usr(data):
    df_data_list = []

    for i in range(len(data)):
        attCnt = len(data.iloc[i,1])
        correctness_rate = calculate_correctness_rate(data.iloc[i,1])
        confidence_level = calculate_confidence_level({
            'answer':data.iloc[i,4],
            'attempt_number':attCnt,
            'marked_for_review':data.iloc[i,2],
            'time_taken':data.iloc[i,3]
        })
        
        row = {
            'question_id':data.iloc[i,0],
            'attempt_number':attCnt,
            'time_taken':data.iloc[i,3],
            'answer':data.iloc[i,4],
            'marked_for_review':data.iloc[i,2],
            'correctness_rate':correctness_rate,
            'confidence_level':confidence_level,
        }

        df_data_list.append(row)

    dataFramePrimary = pd.DataFrame(df_data_list)

    #now to get the data to send to model

    inpData = dataFramePrimary.drop(columns=['question_id'])

    # print(inpData)
    #scale the above data and then make predictions and store them in original df
    inpDataScale = scaler.transform(inpData)

    # print(type(inpDataScale))

    predict=knn.predict(inpDataScale)

    QuestionLabelledData = []
    for index,rows in inpData.iterrows():
        
        nRow = {
            'question_id':df_data_list[index].get('question_id'),
            'subdomain':questionBank.objects.get(qID = df_data_list[index].get('question_id')).subdomain,
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
    select_columns = ['question_id', 'subdomain', 'label']
    toLabelTopicDataFrame = questionLabeledDataFrame[select_columns]

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

    return finalClassificationDataFrame