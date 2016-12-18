#!/usr/bin/env python

import sys
import json
import requests
import time

if len(sys.argv) != 4:
    print("\nusage: python weatherclock.py \"wunderground_api_key\" \"country\" \"city\" \npress CTRL-C to exit\n")
    sys.exit(0)

def get_wunderground_data(api_key, feature, country, city):
    url = 'http://api.wunderground.com/api/'+ api_key +'/'+ feature +'/q/'+ country +'/'+ city +'.json'
    result = requests.get(url)

    if(result.status_code == 200):
        return json.loads(result.text)
    else:
        return {}

def forecast_text_for_today(weather_forecast):
    day = weather_forecast['forecast']['txt_forecast']['forecastday'][0]
    day_text = day['title'] +': '+ day['fcttext_metric']
    night = weather_forecast['forecast']['txt_forecast']['forecastday'][1]
    night_text = night['title'] +': '+ night['fcttext_metric']
    return  day_text +' '+ night_text

def sunrise_and_sunset_text(astronomy):
    sunrise = astronomy['sun_phase']['sunrise']
    sunset = astronomy['sun_phase']['sunset']
    return 'Sunrise: '+ sunrise['hour'] +':'+ sunrise['minute'] +', Sunset: '+ sunset['hour'] +':'+ sunset['minute'] +'.'

# Displays the current time for 60 seconds
def display_time_for_sixty_seconds():
    sixty_seconds_from_now = time.time() + 60
    while time.time() < sixty_seconds_from_now:
        print(time.strftime("%H:%M"))
        time.sleep(1)

# Scrolls the sunrise, sunset and current forecast once
def display_astronomy_and_forecast(weather_forecast, astronomy):
    if(weather_forecast != {} and astronomy != {}):
        print(sunrise_and_sunset_text(astronomy) +' '+ forecast_text_for_today(weather_forecast))

# Display the current time for 60 seconds, scroll the forecast, go back to the current time
# Forecast is refreshed once per hour
def run(api_key, country, city):
    weather_forecast = get_wunderground_data(api_key, 'forecast', country, city)
    astronomy = get_wunderground_data(api_key, 'astronomy', country, city)
    while True:
        refresh_time = time.time() + 60 * 60
        new_weather_forecast = get_wunderground_data(api_key, 'forecast', country, city)
        new_astronomy = get_wunderground_data(api_key, 'astronomy', country, city)

        if(new_weather_forecast == {} or new_astronomy == {}):
            refresh_time = time.time() + 30
        else:
            weather_forecast = new_weather_forecast
            astronomy = new_astronomy

        while time.time() < refresh_time:
            display_time_for_sixty_seconds()
            display_astronomy_and_forecast(weather_forecast, astronomy)

run(sys.argv[1], sys.argv[2], sys.argv[3])
