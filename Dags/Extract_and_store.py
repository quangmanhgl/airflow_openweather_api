from Postgresoperator import Postgres
import requests
import pandas as pd 
from pytz import timezone


pg = Postgres("postgres")


class Extract_and_store:
    def __init__(self, api_key):
        self.api_key = api_key 

    def connect_api(self):
        data = []
        locations = [
        # Major cities
        {"lat": 10.7769, "lon": 106.7009},  # Ho Chi Minh City
        {"lat": 21.0285, "lon": 105.8542},  # Hanoi
        {"lat": 13.9833, "lon": 108.0000},  # Pleiku
        {"lat": 16.4637, "lon": 107.5909},  # Hue
        {"lat": 13.7758, "lon": 109.2314},  # Quy Nhon
    
    ]


        for location in locations: 

            lat = location["lat"]
            lon = location["lon"]
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={self.api_key}"
            response = requests.get(url)
            data.append(response.json())
        return data
    


    def extract_api_to_df(self):
        all_data = self.connect_api()
        weather = []
        
        for city_data in all_data:
            city_name = city_data["city"]["name"]
            for forecast in city_data["list"]:
                weather.append({
                    'time': forecast["dt_txt"],
                    'temperature': forecast['main']['temp'] - 273.15,  # Convert Kelvin to Celsius
                    'humidity': forecast['main']['humidity'],
                    'weather_des': forecast['weather'][0]['description'],
                    'wind_deg': forecast['wind']['deg'],
                    'wind_gust': forecast['wind'].get('gust', 0),
                    'wind_speed': forecast['wind']['speed'],
                    'city': city_name,
                    'lat': city_data['city']['coord']['lat'],
                    'lon': city_data['city']['coord']['lon']
                })     
        df = pd.DataFrame(weather)
        return df



    def load_extracted_to_data_postgres(self):
        df = self.extract_api_to_df()
        pg.save_data_to_postgres(df, table_name='weather') 


