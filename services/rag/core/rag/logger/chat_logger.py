import json
import os
import datetime
import pandas as pd

from .const import (
    chatlog_savepath
)

def log_query_response_json(llm_choice, query_str, query_str_preprocess, response_text):
    """
    Logs the query and its response in a JSON format into a folder for each LLM choice.

    Args:
        llm_choice (str): The LLM model used for processing the query.
        query_str (str): The user's query.
        response_text (str): The response generated by the LLM.
    """
    # Define the base directory for logs and a subdirectory for the specific LLM
    base_log_dir = chatlog_savepath
    llm_log_dir = os.path.join(base_log_dir, llm_choice)
    
    # Create the directories if they don't exist
    os.makedirs(llm_log_dir, exist_ok=True)
    
    # Define the filename using the current date to separate logs by day
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{llm_log_dir}/{date_str}_log.json"
    
    # Prepare the log entry
    log_entry = {
        "llm": llm_choice,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query_str,
        "query_preprocess": query_str_preprocess,
        "response": response_text
    }
    
    # Check if the log file exists and is not empty
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        # Read the existing data and append the new log entry
        with open(filename, 'r+', encoding='utf-8') as file:
            data = json.load(file)
            data.append(log_entry)
            file.seek(0)
            json.dump(data, file, ensure_ascii=False, indent=4)
    else:
        # Create a new file or overwrite an empty file with the new log entry in a list
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump([log_entry], file, ensure_ascii=False, indent=4)
            
def generate_excel_from_logs(output_filename='chatlogs_summary.xlsx'):
    """
    Generate an Excel file from JSON log files, with one sheet per LLM model.
    
    Args:
        base_log_dir (str): The base directory where the LLM log directories are stored.
        output_filename (str): The name of the output Excel file.
    """
    # Initialize ExcelWriter for the output file
    excel_writer = pd.ExcelWriter(os.path.join(chatlog_savepath, output_filename), engine='xlsxwriter')

    # Iterate over each LLM log directory
    for llm_choice in os.listdir(chatlog_savepath):
        llm_log_dir = os.path.join(chatlog_savepath, llm_choice)
        
        if not os.path.isdir(llm_log_dir):  # Skip files, process only directories
            continue

        # Initialize a list to hold all logs for the current LLM
        all_logs = []
        
        # Iterate over each log file for the current LLM
        for log_file in os.listdir(llm_log_dir):
            log_file_path = os.path.join(llm_log_dir, log_file)
            
            # Read the log file and extend the all_logs list
            with open(log_file_path, 'r', encoding='utf-8') as file:
                logs = json.load(file)
                all_logs.extend(logs)
        
        # Convert the logs to a DataFrame
        df_logs = pd.DataFrame(all_logs)
        
        # Write the DataFrame to a new sheet in the Excel file
        df_logs.to_excel(excel_writer, sheet_name=llm_choice[:31], index=False)  # Excel sheet names limited to 31 characters

    # Save the Excel file
    excel_writer.close()
    print(f"Excel file '{output_filename}' has been generated with logs.")