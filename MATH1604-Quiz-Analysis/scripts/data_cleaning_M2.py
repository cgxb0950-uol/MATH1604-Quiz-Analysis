import requests
import os
import csv
from io import StringIO
from datetime import datetime

def import_data(url):
    #download earthquake data
    response = requests.get(url)
    if response.status_code == 200:
        data_text = response.text
    else:
        raise Exception("Failed to download data.")
    #make sure 'data' folder exists
    if not os.path.exists("data"):
        os.makedirs("data")
    #save downloaded data
    team_member_id = "M2"
    file_path = os.path.join("data", f"dataset_{team_member_id}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data_text)
    #return data as list of lines
    with open(file_path, "r", encoding="utf-8") as f:
        data_lines = f.readlines()
    return data_lines

def clean_data(data_text_list):
    #go through the CSV data
    data_str = "".join(data_text_list)
    csv_reader = csv.reader(StringIO(data_str))
    header = next(csv_reader)
    date_index = header.index("time")
    #process each row and convert date into new format
    cleaned_rows = [header]
    for row in csv_reader:
        try:
            original_date = row[date_index]
            original_date = original_date.rstrip("Z")
            dt = datetime.fromisoformat(original_date)
            formatted_date = dt.strftime("%d-%m-%Y %H:%M:%S")
            row[date_index] = formatted_date
        except Exception as e:
            print(f"Error processing row: {e}")
        cleaned_rows.append(row)

    #make sure 'output' folder exists and save
    if not os.path.exists("output"):
        os.makedirs("output")

  team_member_id = "M2"
    output_file = os.path.join("output", f"cleaned_data_{team_member_id}.txt")
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(cleaned_rows)

    #return cleaned data as list of strings
    cleaned_text_lines = [",".join(row) + "\n" for row in cleaned_rows]
    return cleaned_text_lines

#run functions
url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2023-01-01&endtime=2023-01-02"
raw_lines = import_data(url)
cleaned_lines = clean_data(raw_lines)
