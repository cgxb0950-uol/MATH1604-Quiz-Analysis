#download and collate

import requests
import os

def download_answer_files(cloud_url, path_to_data_folder, total_respondents):
    """
    aim of downloading answer files from cloud location and saving them locally
    parameters:
        cloud_url : base URL where the answer files are hosted
        path_to_data_folder : local folder to save downloaded files
        total_respondents : how many files to attempt to download
    returns:
        none
    """
    #create data folder if it does not already exist
    if not os.path.exists(path_to_data_folder):
        os.makedirs(path_to_data_folder)
    #loop through respondents starting from 1
    for n in range(1, total_respondents + 1):
        #build URL for this file
        file_url = cloud_url + f"/a{n}.txt"
        #try download file
        response = requests.get(file_url)
        if response.status_code == 200:
            #save with consistent local name
            local_filename = os.path.join(path_to_data_folder, f"answers_respondent_{n}.txt")
            with open(local_filename, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Downloaded: a{n}.txt saved as answers_respondent_{n}.txt")
        else:
            #file does not exist at that URL, skip it
            print(f"Warning: a{n}.txt not found, skipping")

def collate_answer_files(data_folder_path):
    """
    combines all respondent answer files into a single collated file
    saved as output/collated_answers.txt, with each respondent's section
    parameters:
        data_folder_path (str): path to folder containing individual respondent files
    returns:
        none
    """

    #create output folder if it does not already exist
    if not os.path.exists("output"):
        os.makedirs("output")
    output_file_path = os.path.join("output", "collated_answers.txt")
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        n = 1
        while True:
            #build path for this respondent's file
            respondent_file = os.path.join(data_folder_path, f"answers_respondent_{n}.txt")
            #stop when no more files exist
            if not os.path.exists(respondent_file):
                break
            #read and write this respondent's answers into the collated file
            with open(respondent_file, "r", encoding="utf-8") as f:
                output_file.write(f.read())
            #separate each respondent with single asterisk on its own line
            output_file.write("*\n")
            print(f"Collated: answers_respondent_{n}.txt")
            n += 1

    print(f"All answers saved to output/collated_answers.txt")
