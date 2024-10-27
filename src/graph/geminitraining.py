import pandas as pd
import json
import requests

arr = []
for i in range(0, 250):
    arr.append("")

def call_gemini_api(prompt):
    """
    Calls the Gemini API to get Engel score and explanation.
    :param prompt: The input prompt for the Gemini API.
    :return: Response from the Gemini API.
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=YAIzaSyDHWaeH-sr83M36jjfFDtG0rK7iS14V1C0"  # Replace with the actual Gemini API endpoint
    headers = {
        "Authorization": "AIzaSyDHWaeH-sr83M36jjfFDtG0rK7iS14V1C0",  # Replace with your Gemini API key
        "Content-Type": "application/json"
    }

    data = {
        "prompt": prompt,
        "max_tokens": 500  # Adjust based on your requirements
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

def traininiggemini(csv_path, arr):
    iter = 0
    data = pd.read_csv(csv_path)
    for row in data.iterrows():
        reasoning = row['reasoning']
        prompt = arr[iter]
        call_gemini_api(prompt)



