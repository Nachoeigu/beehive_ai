from utils import get_sensor_data, get_external_data, get_sensor_metadata, get_external_metadata, cleaning_llm_output
import asyncio
import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from constants import *
import json


class Agent:
    def __init__(self, model, beehive_data: pd.DataFrame, external_realtime_data: pd.DataFrame, external_forcast_data: pd.DataFrame, beehive_metadata: dict, external_realtime_metadata: dict, external_forecast_metadata: dict):
        self.model = model
        self.beehive_data = beehive_data
        self.external_realtime_data = external_realtime_data
        self.external_forcast_data = external_forcast_data
        self.beehive_metadata = beehive_metadata
        self.external_realtime_metadata = external_realtime_metadata
        self.external_forecast_metadata = external_forecast_metadata


    def analyze(self):
        llm_output = self.model.invoke(
            [
                SystemMessage(content = AGENT_SYSTEM_PROMPT.format(
                    beehive_metadata = json.dumps(self.beehive_metadata, indent = 4),
                    beehive_sensor_data = json.dumps(self.beehive_data.to_dict(orient='records'), indent = 4),
                    realtime_weather_metadata = json.dumps(self.external_realtime_metadata, indent = 4),
                    realtime_weather_data = json.dumps(self.external_realtime_data.to_dict(orient='records')[0], indent = 4),
                    forecast_weather_metadata = json.dumps(self.external_forecast_metadata, indent = 4),
                    forecast_weather_data = json.dumps(self.external_forcast_data.to_dict(orient='records')[:48], indent = 4),
                    positive_example_format = json.dumps({"status": "OK"}, indent = 4),
                    negative_example_format = json.dumps({"status": "ALERT","action": "...","reason": "..."}, indent = 4),
                    negative_example_output = json.dumps({"status": "ALERT","action": "Increase ventilation in the beehive","reason": "The beehive is currently experiencing high humidity levels, which can lead to mold growth and bee health issues. The forecast indicates a rise in temperature and humidity over the next 24 hours, exacerbating the situation. Increasing ventilation will help regulate the humidity levels and prevent adverse health effects on the bees."}, indent = 4)
                )),
                HumanMessage(content = "Could you analyze the current state of the beehive?")
            ]
        )

        cleaned_llm_output = cleaning_llm_output(llm_output)

        return cleaned_llm_output


if __name__ == '__main__':
    beehive_data = asyncio.run(get_sensor_data(testing_data = True))
    external_realtime_data, external_forecast_data = asyncio.run(get_external_data(testing = True))
    beehive_metadata = asyncio.run(get_sensor_metadata())
    external_realtime_metadata, external_forecast_metadata = asyncio.run(get_external_metadata())

    agent = Agent(
        #model = ChatGroq(temperature=0, model="deepseek-r1-distill-llama-70b"),
        model = ChatGoogleGenerativeAI(temperature=0, model="gemini-2.0-flash-thinking-exp-01-21"),
        beehive_data = beehive_data,
        external_realtime_data = external_realtime_data,
        external_forcast_data = external_forecast_data,
        beehive_metadata = beehive_metadata,
        external_realtime_metadata = external_realtime_metadata,
        external_forecast_metadata = external_forecast_metadata
    )

    output = agent.analyze()

    print(output)