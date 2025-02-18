import pandas as pd
import httpx
from dotenv import load_dotenv
import os
import asyncio
import json
from datetime import datetime
import aiofiles
import yaml
import re

load_dotenv()

class NoImplemented(Exception):
    pass

class NoJson(Exception):
    pass

class BadFormattedJson(Exception):
    pass


async def get_sensor_metadata() -> dict:
    """
    Get metadata about the beehive sensor data.
    """
     
    async with aiofiles.open("./data/sample_beehive_data_metadata.yaml", mode='r') as file:
        data = await file.read()
        return yaml.load(data, Loader=yaml.FullLoader)



async def get_external_metadata() -> dict:
    """
    Get metadata about the external data.
    """
    async with aiofiles.open("./data/sample_external_data_realtime_metadata.yaml", mode='r') as file:
        realtime_metadata = yaml.load(await file.read(), Loader=yaml.FullLoader)
    
    async with aiofiles.open("./data/sample_external_data_forecasting_metadata.yaml", mode='r') as file:
        forecasting_metadata = yaml.load(await file.read(), Loader=yaml.FullLoader)
        

    return realtime_metadata, forecasting_metadata

async def get_sensor_data(testing_data: bool = False) -> pd.DataFrame:
    """
    Get sensor data about the beehive.
    """
    if testing_data:
        return pd.read_csv("./data/sample_beehive_data.csv")
    else:
        NoImplemented("You should implement the data extraction from your own sensor")

def formatting_current_weatherapi_data(data: dict) -> dict:
    """
    Formats the current data from WeatherAPI into a Pandas DataFrame.

    Args:
        data (dict): The JSON response data from WeatherAPI current endpoint.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the formatted current data.
    """
    flattened_data = {}


    for key, value in data.items():
        if key == 'condition':
            flattened_data[f'current_condition'] = value['text']
        else:
            flattened_data[f'current_{key}'] = value

    return pd.DataFrame(flattened_data, index=[0])

def formatting_forecast_weatherapi_data(data: dict, current_time: str) -> pd.DataFrame:
    """
    Formats the forecast data from WeatherAPI into a Pandas DataFrame.

    Args:
        data (dict): The JSON response data from WeatherAPI forecast endpoint.
        current_time (str): A string representing the current time in "%Y-%m-%d %H:%M" format.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the formatted forecast data.
    """
    current_time_dt = datetime.strptime(current_time, "%Y-%m-%d %H:%M")

    forecastday_data = data.get('forecastday', [])
    structured_final_output = []

    for n_day, day_data in enumerate(forecastday_data):
        hourly_data = day_data.get('hour', [])

        if n_day == 0:
            hourly_data = [hour for hour in hourly_data if datetime.strptime(hour['time'], "%Y-%m-%d %H:%M") > current_time_dt]

        for hour_data in hourly_data:
            flattened_data = {}
            for key, value in hour_data.items():
                if key == 'condition':
                    flattened_data[f'forecast_condition'] = value['text']
                else:
                    flattened_data[f'forecast_{key}'] = value
            structured_final_output.append(flattened_data)

    return pd.DataFrame(structured_final_output)

def cleaning_weatherapi_response(data: dict) -> dict:
    """
    Cleans the JSON response data from WeatherAPI.
    """
    current_data = formatting_current_weatherapi_data(data['current'])
    forecast_data = formatting_forecast_weatherapi_data(data = data['forecast'], current_time = data['current']['last_updated'])

    return current_data, forecast_data

async def get_external_data(testing:bool = False, lat: float = 0, lon: float = 0) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Retrieves real-time and forecast weather data for a location (latitude, longitude).

    Fetches current and future hourly weather information from an external API, 
    including temperature, climate, wind, humidity, and UV index, 
    to provide environmental context for beehive monitoring. 
    Returns the data as Pandas DataFrames.

    """
    if testing:
        return pd.read_csv("./data/sample_external_data_realtime.csv"), pd.read_csv("./data/sample_external_data_forecasting.csv")

    timeout = httpx.Timeout(
        connect=120.0,
        read=120.0,
        write=120.0,
        pool=120.0
    )
    async with httpx.AsyncClient(timeout=timeout) as client:
        
        response = await client.get(f"http://api.weatherapi.com/v1/forecast.json?key={os.getenv('WEATHER_API_KEY')}&q={lat},{lon}&days=14")
        data = response.json()

        return cleaning_weatherapi_response(data)


def cleaning_llm_output(llm_output):

    content = llm_output.content
    
    # Phase 1: JSON Extraction
    try:
        match = re.search(r"```json\s*([\s\S]*?)\s*```", content)
        if not match:
            match_inline = re.search(r"({.*?}|\[.*?\])", content, re.DOTALL)
            if match_inline:
                json_content = match_inline.group(0).strip()
            else:
                raise NoJson("The output does not contain a JSON code block")
        else: 
            json_content = match.group(1)
        
    except re.error as e:
        print(f"Regex error during extraction: {str(e)}")
        return content

    # Phase 2: Content Cleaning
    try:
        # Remove remaining backticks and normalize whitespace
        try:
            json_content = re.sub(r"```", "", json_content)
            parsed = json.loads(json_content)                                
            return parsed
        except:
            pass
        try:
            json_content = re.sub(r"\s+", " ", json_content)
            parsed = json.loads(json_content)
            return parsed
        except:
            pass
        
        json_content = json_content.replace('\\', '')
        json_content = json_content.strip()

    except re.error as e:
        print(f"Regex error during cleaning: {str(e)}")
        return content

    # Phase 3: JSON Validation
    try:
        # Fix common JSON issues
        json_content = re.sub(
            r',\s*([}\]])', r'\1',  # Remove trailing commas
            json_content
        )
        json_content = re.sub(
            r"([{:,])\s*'([^']+)'\s*([,}])",  # Convert single quotes to double
            r'\1"\2"\3', 
            json_content
        )
        
    except re.error as e:
        return content

    # Phase 4: Parsing
    try:
        parsed = json.loads(json_content)
        return parsed
    except:
        try:
            def escape_value_quotes(match):
                value = match.group(1)
                return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'

            # Improved regex to handle whitespace and escaped quotes in values
            pattern = r'(?<=:)\s*"(.*?[^\\])"(?=\s*[,}\]])'

            json_content = re.sub(pattern, escape_value_quotes, json_content)

            return json.loads(json_content)

        except json.JSONDecodeError as e:
            raise BadFormattedJson({"error": f"While trying to format the JSON object you have generated we detect the following error: {e.args[0]}", "detail": f"Error location: Line {e.lineno}, Column {e.colno}", "context": f"{e.doc[e.pos-50:e.pos+50]}"})

