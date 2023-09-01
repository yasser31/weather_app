import requests
import json
import geocoder
from decouple import config
from datetime import datetime


class Weather():
    """
    this class instantiate a weather object and defines
    methods to call the openweathermap Api
    """

    def __init__(self):
        self.params = ["dt", "sunrise", "sunset", "temp", "feels_like", "pressure",
                       "humidity", "uvi", "visibility", "wind_speed", "summary", "weather"]
        self.current_location = self.get_current_location()
        self.metric_data = None
        self.imperial_data = None

    def get_current_location(self):
        """
        this function gets the default location usin the ip address
        """
        location = geocoder.ip("me") # we use geocoder to get lat, lon from the ip address 
        if location.latlng:
            lat, long = location.latlng
            return lat, long
        else:
            print("failed to get location")
            return None, None

    def get_weather(self, location, units, api_key=config("API_KEY")):
        """
        this function gets current, hourly, daily weather data
        """
        lat, lon = location
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units={units}&appid={api_key}"
        response = requests.get(url)
        data = json.loads(response.content)
        if units == "metric":
            self.metric_data = data
        elif units == "imperial":
            self.imperial_data = data
        return data
    

    def extract_needed_data(self, data_source):
        """
        this function extract the exact data that we want to use later
        """
        filtered_data = {}
        for param in self.params:
            if param == "weather" and data_source.get(param):
                filtered_data["icon"] = data_source["weather"][0]["icon"]
                filtered_data["description"] = data_source["weather"][0]["description"]
            elif param in ("dt", "sunrise", "sunset") and data_source.get(param):
                filtered_data[param] = datetime.fromtimestamp(data_source[param]).strftime("%A, %B %d, %Y %I:%M:%S")
            elif param != "weather" and data_source.get(param):
                filtered_data[param] = data_source[param]
        return filtered_data

    
    def get_current_weather(self, weather):
        """
        this function gets current weather data
        """
        data_source = weather["current"]
        return self.extract_needed_data(data_source)
    

    def get_hourly_weather(self, weather):
        """this function gets hourly weather data
        """
        hourly_weather = weather["hourly"]
        filtered_data_list = [self.extract_needed_data(data_source) for data_source in hourly_weather]
        return filtered_data_list

    
    def get_daily_weather(self, weather):
        """this function gets daily weather data
        """
        daily_weather = weather["daily"]
        filtered_data_list = [self.extract_needed_data(data_source) for data_source in daily_weather]
        return filtered_data_list
