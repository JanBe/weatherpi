#!/usr/bin/env python

import sys
import json
import requests
import time
import scrollphat

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

def weather_text_for_today(weather):
    day = weather['forecast']['txt_forecast']['forecastday'][0]
    day_text = day['title'] +': '+ day['fcttext_metric']
    night = weather['forecast']['txt_forecast']['forecastday'][1]
    night_text = night['title'] +': '+ night['fcttext_metric']
    return  day_text +' '+ night_text

def sunrise_and_sunset_text(astronomy):
    sunrise = astronomy['sun_phase']['sunrise']
    sunset = astronomy['sun_phase']['sunset']
    return 'Sunrise: '+ sunrise['hour'] +':'+ sunrise['minute'] +', Sunset: '+ sunset['hour'] +':'+ sunset['minute'] +'.'

# Returns the current time in a mixed hexadecimal and decimal representation.
# The hours are between 0 and 12. For hours > 9, hexadecimal representation is used.
# Minutes are displayed in the decimal system. No symbol seperates hours and minutes.
# Examples: 3:20 = 320, 14:20 = 220, 10:15 = A15, 11:40 = B40, 12:25 = C25
# This is done because the scrollphat can only display 3 digits without scrolling.
def current_time():
    current_time = time.localtime()
    hours = '%X' % (current_time.tm_hour % 12)
    minutes = '%02d' % current_time.tm_min
    return hours + minutes

# Display the current time for 60 seconds, scroll the forecast, go back to the current time
# Forecast is refreshed once per hour
def run(api_key, country, city):
    scrollphat.set_brightness(2)
    scrollphat.set_rotate(True)
    weather = {}
    astronomy = {}
    forecast_refresh_time = time.time()
    while True:
        try:
            if forecast_refresh_time < time.time():
                new_weather = get_wunderground_data(api_key, 'forecast', country, city)
                new_astronomy = get_wunderground_data(api_key, 'astronomy', country, city)

                if(new_weather == {} or new_astronomy == {}):
                    forecast_refresh_time = time.time()
                else:
                    weather = new_weather
                    astronomy = new_astronomy
                    forecast_refresh_time = time.time() + 60 * 60

            # Display current time for 60 seconds
            scrollphat.write_string(current_time())
            time.sleep(60)

            # Scroll forecast once
            if(weather != {} and astronomy != {}):
                scrollphat.write_string(sunrise_and_sunset_text(astronomy) +' '+ weather_text_for_today(weather))
                length = scrollphat.buffer_len()

                for i in range(length):
                    scrollphat.scroll()
                    time.sleep(0.1)

        except KeyboardInterrupt:
            scrollphat.clear()
            sys.exit(-1)

run(sys.argv[1], sys.argv[2], sys.argv[3])
