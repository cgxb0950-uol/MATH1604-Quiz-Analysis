"""
Data Extraction Module (Team Member 1)

This module provides functions to parse quiz answer files and extract respondent
answer sequences. It handles the extraction of answers from specially formatted
text files and saves them in a structured format for further analysis.

Author: Team Member 1
Module: MATH1604 - Modelling for Big Data
"""


def extract_answers_sequence(file_path):
    try:
        # Read the entire file
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        answers = []
        current_question_answers = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if this is a question line
            if line.startswith('Question'):
                if current_question_answers:
                    # Find which answer was selected (1-4), or 0 if none
                    selected_answer = 0
                    for idx, answer_line in enumerate(current_question_answers, start=1):
                        if answer_line.startswith('[x]'):
                            selected_answer = idx
                            break
                    answers.append(selected_answer)
                    current_question_answers = []
            
            # Check if this is an answer line (starts with [ ] or [x])
            elif line.startswith('['):
                current_question_answers.append(line)
        
        # Process the last question's answers
        if current_question_answers:
            selected_answer = 0
            for idx, answer_line in enumerate(current_question_answers, start=1):
                if answer_line.startswith('[x]'):
                    selected_answer = idx
                    break
            answers.append(selected_answer)
        
        # Validate that we have exactly 100 answers
        if len(answers) != 100:
            raise ValueError(
                f"Expected 100 questions, but found {len(answers)}. "
                f"The file format may be invalid."
            )
        
        return answers
    
    except FileNotFoundError:
        raise FileNotFoundError(
            f"The file '{file_path}' was not found. "
            f"Please check the file path and try again."
        )
    except IOError as e:
        raise IOError(
            f"An error occurred while reading the file '{file_path}': {str(e)}"
        )


def write_answers_sequence(answers, n):
    # Validate input types
    if not isinstance(answers, list):
        raise TypeError(
            f"Expected 'answers' to be a list, but got {type(answers).__name__}"
        )
    
    if not isinstance(n, int):
        raise TypeError(
            f"Expected 'n' to be an integer, but got {type(n).__name__}"
        )
    
    # Validate answers list length
    if len(answers) != 100:
        raise ValueError(
            f"Expected exactly 100 answers, but got {len(answers)}. "
            f"Please provide a complete answer sequence."
        )
    
    # Validate that all answers are in valid range (0-4)
    for idx, answer in enumerate(answers, start=1):
        if not isinstance(answer, int):
            raise ValueError(
                f"Answer at position {idx} is not an integer: {answer}"
            )
        if answer < 0 or answer > 4:
            raise ValueError(
                f"Answer at position {idx} is out of range (0-4): {answer}"
            )
    
    # Create the output filename
    output_filename = f"answers_list_respondent_{n}.txt"
    
    try:
        # Write the answers to the file
        with open(output_filename, 'w', encoding='utf-8') as file:
            for answer in answers:
                file.write(f"{answer}\n")
        
        print(f"Successfully wrote answer sequence to '{output_filename}'")
    
    except IOError as e:
        raise IOError(
            f"An error occurred while writing to '{output_filename}': {str(e)}"
        )


# Module-level test code (optional, for development/testing)
if __name__ == "__main__":
    """
    Test code to demonstrate module functionality.
    This code runs only when the module is executed directly, not when imported.
    """
    print("=" * 60)
    print("Data Extraction Module - Team Member 1")
    print("=" * 60)
    print("\nThis module provides two main functions:")
    print("1. extract_answers_sequence(file_path) - Parse quiz answer files")
    print("2. write_answers_sequence(answers, n) - Save extracted sequences")
    print("\nFor usage examples, see the function docstrings.")
    print("=" * 60)
