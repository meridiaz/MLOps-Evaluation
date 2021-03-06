# this cript is based on 
# https://www.kaggle.com/youssefadem/data-cleaning-and-ploting-detailed-prediction

# modules we'll use
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os
import yaml
from sklearn.model_selection import train_test_split
import sys

# currently not used
def find_min_top(data):
    #this function calculates max top per year and then the minimum top for all years
    a = data.groupby(['year']).max()
    return a['world_rank'].min()

if len(sys.argv) != 3:
    sys.stderr.write("Arguments error. Usage:\n")
    sys.stderr.write("\tpython train.py features model\n")
    sys.exit(1)

path_to_files = sys.argv[1]
path_to_write_files = sys.argv[2]

params = yaml.safe_load(open("params.yaml"))["featurize"]

le = LabelEncoder()


file_names = ["val_x", "val_y", "train_x", "train_y"]

# create dest dir
if not os.path.isdir(path_to_write_files):
    os.mkdir(path_to_write_files)

# read in all our data
education_expenditure_supplementary_data = pd.read_csv(os.path.join(path_to_files,"education_expenditure_supplementary_data.csv" 
                                            ), engine='python')
education_expenditure_supplementary_data.name='education_expenditure_supplementary_data'

shanghaiData = pd.read_csv(os.path.join(path_to_files, "shanghaiData.csv"))
shanghaiData.name='shanghaiData'

timesData= pd.read_csv(os.path.join(path_to_files,"timesData.csv"))
timesData.name='timesData'

cwurData = pd.read_csv(os.path.join(path_to_files,"cwurData.csv"))
cwurData.name='cwurData'

school_and_country_table= pd.read_csv(os.path.join(path_to_files,"school_and_country_table.csv"))
school_and_country_table.name='school_and_country_table'

# count missing values
data_list = [education_expenditure_supplementary_data, shanghaiData,timesData, 
             cwurData, school_and_country_table]

for data in data_list:
    #totale values in our dataset
    total_cells = np.product(data.shape)

    #description of  missing values in each column
    missing_values_count = data.isnull().sum()
    #print("Data Frame :",'\033[1m' + data.name + '\033[0m')
    #print('Data Frame :',data.name)
    #print(missing_values_count.sort_values(ascending=False))
    
    #totale missing values in our dataset
    total_missing = missing_values_count.sum()

    # percent of data that is missing
    percent_missing = (total_missing/total_cells) * 100
    #print('Data shape :',data.shape[0],'by', data.shape[1])
    #print('% of data that is missing :',"{:.2f}".format(percent_missing),'\n')

# --------------- CLEANING SUPPLEMENTARY DATA ---------------
cols_with_missing = [col for col in education_expenditure_supplementary_data.columns
                     if education_expenditure_supplementary_data[col].isnull().any()]
#print('dropped Columns :',cols_with_missing)

# drop cols with missing values
education_expenditure_supplementary_data = education_expenditure_supplementary_data.drop(cols_with_missing, axis=1)

# clean country col
education_expenditure_supplementary_data['country'] = education_expenditure_supplementary_data['country'].str.strip()
countries = education_expenditure_supplementary_data['country'].unique()
# sort them alphabetically and then take a closer look
countries.sort()
#print(countries)

# --------------- CLEANING SHANGHAI DATA ---------------
# dropping Totale score column with the most missing values (70%+)
shanghaiData = shanghaiData.drop(['total_score'], axis = 1)
#replacing all the NaN's in the shanghaiData data with the one that comes directly after it 
#and then replacing any remaining NaN's with 0
shanghaiData = shanghaiData.fillna(method='bfill', axis=0).fillna(0)

# Number of missing values in each column of data
missing_val_count_by_column = (shanghaiData.isnull().sum())
#print(missing_val_count_by_column[missing_val_count_by_column > 0])

# clean world_rank col:
shanghaiData['world_rank'] = shanghaiData['world_rank'].str.strip('=')
# Drop columns with - in world_rank col
cols = shanghaiData['world_rank'].str.contains('-')
shanghaiData = shanghaiData[~cols]
shanghaiData = shanghaiData.astype({"world_rank": int})

#print('shangai data---------------')
#print(shanghaiData.head(10), shanghaiData.loc[shanghaiData['world_rank'] > params['max_rank']])

# --------------- CLEANING TIMES DATA ---------------
#replacing all the NaN's in the timesData data with the one that comes directly after it 
timesData = timesData.fillna(method='bfill', axis=0)
# Number of missing values in each column of data
missing_val_count_by_column = (timesData.isnull().sum())
#print(missing_val_count_by_column[missing_val_count_by_column > 0])


# Replacing '-' with NaN
timesData=timesData.replace('-', np.NaN)
#replacing all the NaN's in the timesData with the one that comes directly after it 
timesData = timesData.fillna(method='bfill', axis=0)

#removing white space from left and right!
timesData['female_male_ratio'] = timesData['female_male_ratio'].str.strip()
# new data frame with split value columns
new = timesData["female_male_ratio"].str.split(":", n = 1, expand = True)

# making separate female ratio from new data frame and making sure no white space exist,
#making sure it has a good datatype for ploting
timesData["Female_ratio"]= new[0]  
timesData["Female_ratio"]=timesData['Female_ratio'].str.strip()

#changing column type
timesData = timesData.astype({"Female_ratio": int})

# making separate male ratio from new data frame and making sure no white space exist ,
#making sure it has a good datatype for ploting
timesData["male_ratio"]= new[1]  
timesData["male_ratio"]=timesData['male_ratio'].str.strip()
#changing column type
timesData = timesData.astype({"male_ratio": int})

# Dropping old female_male_ratio columns
timesData.drop(columns=["female_male_ratio"], inplace = True)

# get ride of % in the international_students col
timesData['international_students'] = timesData['international_students'].str.strip()
new2 = timesData["international_students"].str.split("%", n = 1, expand = True)
timesData["international_students"] = new2[0]
timesData["international_students"] = timesData['international_students'].str.strip()
timesData = timesData.astype({"international_students": int})

# change names
timesData.rename(columns={'international_students': 'international_students %', 
                'Female_ratio': 'female_ratio %', 'male_ratio': 'male_ratio %',
                'student_staff_ratio': 'student_staff_ratio %'}, inplace=True)


# change cols type:
#timesData = timesData.astype({"international": float , "income":float , "total_score":float})
timesData["num_students"] = timesData["num_students"].str.replace(',','.')
timesData["num_students"] = timesData["num_students"].apply(pd.to_numeric)

# clean world_rank col:
timesData['world_rank'] = timesData['world_rank'].str.strip('=')
# Drop columns with - in world_rank col
cols = timesData['world_rank'].str.contains('-')
timesData = timesData[~cols]
timesData = timesData.astype({"world_rank": int})

#print('times data---------------')
#print(timesData.head(10), timesData.loc[timesData['world_rank'] > params['max_rank']])

# --------------- CLEANING CWUR DATA ---------------
# Checking the datatype of the each column of the cwurData DataFrame to make 
# sure we are looking good so far ....
dataTypeSeries = cwurData.dtypes
#print('Data type of each column of timesData Dataframe :')
#print(dataTypeSeries)

# dropping the broad_impact column with the most missing values
cwurData=cwurData.drop(['broad_impact'], axis = 1)

# rename score col
cwurData.rename(columns={'score': 'total_score'})
#print('cwur data---------------')
#print(cwurData.head(10), cwurData.loc[cwurData['world_rank'] > params['max_rank']])

# Drop rows which world_rank > max_rank
# find max top--currently not used:
max_rank = [find_min_top(shanghaiData), find_min_top(timesData), find_min_top(cwurData)]
max_rank = min(max_rank)

shanghaiData = shanghaiData.loc[shanghaiData['world_rank'] <= params['max_rank']]
timesData = timesData.loc[timesData['world_rank'] <= params['max_rank']] 
cwurData = cwurData.loc[cwurData['world_rank'] <= params['max_rank']]

# LABEL COUNTRY 
cwurData['country'] = le.fit_transform(cwurData['country'])
timesData['country'] = le.fit_transform(timesData['country'])


data_list = [cwurData, timesData, shanghaiData]
shanghaiData.name ='shanghaiData'
timesData.name ='timesData'
cwurData.name = 'cwurData'


# features to feed the model
features = {
            cwurData.name: ['alumni_employment', 'publications', 'citations', 'quality_of_education', 'country'
                            , 'national_rank'],
            timesData.name: ['country', 'teaching', 'international', 'research', 'citations', 'income', 'male_ratio %',
                            'num_students', 'student_staff_ratio %', 'international_students %', 'female_ratio %'],
            shanghaiData.name: ['alumni', 'award', 'hici', 'ns', 'pub', 'pcp', 'national_rank']
}

# add new col in order to make a classification problem

for data in data_list:
    data.insert(data.shape[1]-1, "chances", 0, True)
    data.loc[data['world_rank']>params['world_rank'], ['chances']] = 0 #no est?? en el top
    data.loc[data['world_rank']<params['world_rank'], ['chances']] = 1 #esta en el top

    #if 'country' in data.columns:--not used
    #    data.join(education_expenditure_supplementary_data.set_index('country'), on='country')

    #split train and test data by last year avaliable
    val = data.loc[data['year'] == data['year'].unique()[-1]]
    train = data.loc[data['year'] != data['year'].unique()[-1]]

    #check max features
    if len(features[data.name]) > params['max_features']:
        #print("entro en el if de las caractetisticas")
        features[data.name] = features[data.name][0:params['max_features']]

    val_X = val[features[data.name]] 
    val_y = val[['chances']]
    train_X = train[features[data.name]] 
    #train_y = train.chances
    train_y = train[['chances']]
    data_arr = [val_X, val_y, train_X, train_y]

    # convert to csv test and train data:
    for i in range(len(data_arr)):
        data_arr[i].to_csv(path_or_buf=os.path.join(path_to_write_files, data.name + "-" + file_names[i] + ".csv"),
                            index_label=False)
    #print(data.name)
    #print(data.head(10))
    #print(data.tail(10))