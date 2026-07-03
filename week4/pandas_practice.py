# CLASS_SN B1


# # Exercise 1
import pandas as pd
import numpy as np

print(pd.__version__) 


# Exsercise 2
# Create a DataFrame from a list of 5 dicts(name,score,city)
work_ld = [
    {"name":"Udochukwu M","score": 92, "city":"Aba"},
    {"name":"Abigail S","score": 72, "city":"Owerri"},
    {"name":"Winner D","score": 85, "city":"Awka"},
    {"name":"Nancy R","score": 90, "city":"Umuahia"},
    {"name":"Adaugo I","score": 89, "city":"Aba"}
]
dfw=pd.DataFrame(work_ld)
print(dfw.shape)

# Create the same DataFrame from a dict of lists
# work_dl = {
#     ["name":"Udochukwu M","score": 92, "city":"Aba"],
#     ["name":"Abigail S","score": 72, "city":"Owerri"],
#     ["name":"Winner D","score": 85, "city":"Awka"],
#     ["name":"Nancy R","score": 90, "city":"Umuahia"],
#     ["name":"Adaugo I","score": 89, "city":"Aba"]
#     }

# dfwl = pd.DataFrame(work_dl)
# print(dfwl.shape)

# # Load a csv with pd.read_csv()
# workcs = pd.read_csv(r'C:\Users\HomePC\Desktop\Techrise\week4\dataset\workcsv.csv')
# print(workcs.shape)

dataset = pd.read_csv(r'https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv')
dataset.to_csv("titan.csv",index= False)
print(dataset.shape)
# # Exploring

print(dataset.head())
print(dataset.info())
print(dataset.describe())
print(dataset.isnull().sum())
print(dataset.dtypes)
print(dataset['Sex'].value_counts())


# Selecting and filtering
print(dataset[['Name','Ticket']])

average_fare= sum(dataset['Fare'])/len(dataset['Fare'])
dataset[dataset['Fare']> average_fare]

dataset[(dataset['Fare']> average_fare)& (dataset['Sex']=='female')]

thia = dataset[dataset['Cabin'].isin(['C85','B42','C148'])]
print(thia)


# Sorting a DataFrame
dataset.sort_values('Fare',ascending=True)
dataset.nlargest(5,'Fare')
dataset['Rank'] = dataset['Fare'].rank(ascending=False, method ='dense')
dataset = dataset.sort_values('Fare',ascending=False).reset_index(drop=True)
