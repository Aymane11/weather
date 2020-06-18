import datetime
import json
import urllib.request
import sys
import pprint
from configparser import ConfigParser, NoSectionError
import argparse
from os import path
import getpass 
  
def save_config():
    city = input("City Name : ")
    units = input("Units system metric or imperial [m/i]: ")
    while True:
        if units.lower() not in ['m', 'i']:
            units = input('Wrong input. Units system (metric or imperial): ')
            continue
        else:
            break
    config = ConfigParser()
    config.read('config.ini')
    config.remove_section('MAIN')
    config.add_section('MAIN')
    if config.has_section('API') == False:
        config.add_section('API')
    if config.has_option('API', 'key') == False:
        key = getpass.getpass("API key:") 
        config.set('API', 'key', key)
    key = config.get('API', 'key')
    config.set('MAIN', 'city', city)
    config.set('MAIN', 'units', units)
    with open('config.ini', 'w') as f:
        config.write(f)
    fetch_and_display(city, units, key)


def load_config():
    if path.exists('config.ini') == False:
        save_config()
    else :
        try:
            config = ConfigParser()
            config.read('config.ini')
            city = config.get('MAIN', 'city')
            units = config.get('MAIN', 'units')
            key = config.get('API', 'key')
            fetch_and_display(city, units, key)

        except AttributeError as missing_data:
            while True:
                save = input(
                    'Missing data in config file! Create config now [Y/N] ? ').upper()
                if save not in ['Y', 'N']:
                    save = input('Wrong input. Create config now [Y/N] ? ').upper()
                    continue
                else:
                    if save == 'Y':
                        save_config()
                    else:
                        exit(1)

        except urllib.error.HTTPError as apiError:
            print('Error: Missing or Unauthorized API!', apiError)
            exit(1)

        except IOError as e:
            print('Error: No internet! ', e)
            exit(1)

        except NoSectionError as fi:
            while True:
                save = input(
                    'Configuration file is missing or corrupted! Create config now [Y/N] ? ').upper()
                if save not in ['Y', 'N']:
                    save = input('Wrong input. Create config now [Y/N] ? ').upper()
                    continue
                else:
                    if save == 'Y':
                        save_config()
                        break
                    else:
                        exit(1)


def build_url(city, unit, key):
    api_url = 'http://api.openweathermap.org/data/2.5/weather?q='
    if unit == 'm':
        units = 'metric'
    else:
        units = 'imperial'
    full_url = api_url + city + '&mode=json&units=' + units + '&APPID=' + key
    return full_url


def fetch_data(full_url):
    with urllib.request.urlopen(full_url) as url:
        data = url.read().decode('utf-8')
        data_dict = json.loads(data)
    return data_dict


def convert_time(time, format):
    if format == "h":
        return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')


def build_dict(data, units):
    sys = data.get('sys')
    main = data.get('main')
    weather = data.get('weather')
    coord = data.get('coord'),
    if units == 'm':
        unit = chr(176)+"C"
    else:
        unit = chr(176)+"F"
    final_data = dict(
        unit = unit,
        dt = convert_time(data.get('dt'), 'h'),
        day = convert_time(data.get('dt'), 'd'),
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
        sunrise = convert_time(sys.get('sunrise'), 'h'),
        sunset = convert_time(sys.get('sunset'), 'h')
    )
    return final_data


def display(data, city):
    print('---------------------------------------')
    print(
        f"Current weather in: {city.capitalize()}, {data['country']} on {data['day']} :")
    print(f"{data['temp']}{data['unit']} - {data['weather_desc']}")
    print(f"Max: {data['temp_max']}, Min: {data['temp_min']}")
    print('')
    print(f"Cloud: {data['clouds']}%")
    print(f"Sunrise at: {data['sunrise']}")
    print(f"Sunset at: {data['sunset']}")
    print('')
    print(f"Last update from the server: {data['dt']}")
    print('---------------------------------------')


def fetch_and_display(city, units, key):
    url = build_url(city, units, key)
    data = fetch_data(url)
    final_data = build_dict(data, units)
    display(final_data, city)


def args():
    parser = argparse.ArgumentParser(description="Weather via command line ")
    parser.add_argument('-c', '--config', action='store_true',
                        help='Create config file (city - units - API key)')
    args = parser.parse_args()
    if args.config == True:
        save_config()
    else:
        load_config()


def main():
    args()


if __name__ == "__main__":
    main()
