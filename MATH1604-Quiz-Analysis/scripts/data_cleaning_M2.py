'''
The function that imports data has been reused and adapted from the code provided in the brief.
The function that cleans data has been written using pandas, rather than the csv module approach.
'''
import requests
import os
import pandas as pd
from io import StringIO

def import_data(url):
    #download data
    response = requests.get(url)
    if response.status_code == 200:
        data_text = response.text
    else:
        raise Exception("Failed to download data.")
    #ensure 'data' folder exists
    if not os.path.exists("data"):
        os.makedirs("data")
    #save downloaded data
    team_member_id = "M2"
    file_path = os.path.join("data", f"dataset_{team_member_id}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data_text)
    #read back and return as a list of lines
    with open(file_path, "r", encoding="utf-8") as f:
        data_lines = f.readlines()
    return data_lines

def clean_data(data_text_list):
    #load list of lines into a pandas dataframe
    data_str = "".join(data_text_list)
    df = pd.read_csv(StringIO(data_str))
    #convert time column to datetime and reformat
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df["time"] = df["time"].dt.strftime("%d-%m-%Y %H:%M:%S")
    #ensure output folder exists and save
    if not os.path.exists("output"):
        os.makedirs("output")
    output_file = os.path.join("output", "cleaned_data_M2.txt")
    df.to_csv(output_file, index=False)
    #return cleaned data as list of strings
    cleaned_text_lines = df.to_csv(index=False).splitlines(keepends=True)
    return cleaned_text_lines

#run functions
url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2023-01-01&endtime=2023-01-02"
raw_lines = import_data(url)
cleaned_lines = clean_data(raw_lines)
