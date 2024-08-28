import random

def generateQIDS(QuestionBank):
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

    return selected_QIDS
