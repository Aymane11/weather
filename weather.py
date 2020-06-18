key = "d230cf1e880887c0a615e0e6fa9c7053"

import datetime
import json
import urllib.request
import sys
import pprint
from configparser import ConfigParser,NoOptionError

def save_config():
    city = input("City Name : ")
    lang = input("Language : ")
    units = input("Units system (metric or imperial):")
    save = input("Save config ? [Y/N] ")
    if save.upper() == 'Y':
        config = ConfigParser()
        config.read('config.ini')
        config.add_section('main')
        config.set('main','city',city)
        config.set('main','units',units)
        config.set('main','lang',lang)
        config.set('main','key',key)
        with open('config.ini', 'w') as f:
            config.write(f)
    fetch_and_display(city,units,lang,key)

def load_config():
    try:
        config = ConfigParser()
        config.read('config.ini')
        city = config.get('main','city')
        units = config.get('main','units')
        lang = config.get('main','lang')
        key = config.get('main','key')
        fetch_and_display(city,units,lang,key)

    except AttributeError as missing_data:
        print('Missing data in config file!', missing_data)

    except urllib.error.HTTPError as apiError:
        print('Error: Missing or Unauthorized API!', apiError)

    except IOError as e:
        print('Error: No internet! ', e)

    except NoOptionError as fi:
        print('Configuration file is missing or corrupted! \nTo fix it, use --c or --config to fix it.')

def build_url(city,unit,lang,key):
    api_url = 'http://api.openweathermap.org/data/2.5/weather?q='
    full_url = api_url + city + '&mode=json&units=' + unit + '&APPID=' + key
    return full_url

def fetch_data(full_url):
    with urllib.request.urlopen(full_url) as url:
        data = url.read().decode('utf-8')
        data_dict = json.loads(data)
    #print("data_dict :")
    #pprint.pprint(data_dict)
    return data_dict

def convert_time(time,format):
    if format == "h":
        return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')

def build_dict(data):
    sys = data.get('sys')
    main = data.get('main')
    weather = data.get('weather')
    coord = data.get('coord'),
    final_data = dict(
    dt = convert_time(data.get('dt'),'h'),
    day = convert_time(data.get('dt'),'d'),
    city_id = data.get('id'),
    country = sys.get('country'),
    lat = data['coord']['lat'],
    lon = data['coord']['lon'],
    weather_desc = weather[0].get("description").capitalize(),
    temp = main.get('temp'),
    temp_max = main.get('temp_max'),
    temp_min = main.get('temp_min'),
    clouds = data.get('clouds')['all'],
    rain = data.get('rain'),
    sunrise = convert_time(sys.get('sunrise'),'h'),
    sunset = convert_time(sys.get('sunset'),'h')
    )
    return final_data

def display(data,city):
    print('---------------------------------------')
    print(f"Current weather in: {city.capitalize()}, {data['country']} on {data['day']} :")
    print(f"{data['temp']}°C - {data['weather_desc']}")
    print(f"Max: {data['temp_max']}, Min: {data['temp_min']}")
    print('')
    print(f"Cloud: {data['clouds']}%")
    print(f"Sunrise at: {data['sunrise']}")
    print(f"Sunset at: {data['sunset']}")
    print('')
    print(f"Last update from the server: {data['dt']}")
    print('---------------------------------------')

def fetch_and_display(city,units,lang,key):
    url = build_url(city,units,lang,key)
    data = fetch_data(url)
    final_data = build_dict(data)
    display(final_data,city)

def args():
    args = sys.argv
    args.pop(0)
    if len(args) == 0:
        load_config()
    else:
        if args[0] == '--config' or args[0] == '--c':
            save_config()
        elif args[0] == '--help' or args[0] == '--h':
            print(__doc__)
            exit()
        else:
            print("Unknown Command, available command: --help and --config")
            exit(1)

def main():
    args()

if __name__ == "__main__":
    main()