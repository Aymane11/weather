# -*- coding: utf-8 -*-
"""
CLI tool fetching weather in a city using openweathermap API.

usage: weather.py [-h] [-c]
optional arguments:
	-h, --help    show this help message and exit
	-c, --config  Create or edit config file (city - units - [API key])


<Open Weather Map> http://openweathermap.org/.
"""

import datetime
import json
import urllib.request
from configparser import ConfigParser, NoSectionError
import argparse
from os import path
from rich import print
from rich.prompt import Prompt


def save_config() -> None:
	"""
	Create and save configuration file
	"""
	city = Prompt.ask("City Name")
	units = Prompt.ask("Units system", choices=["metric", "m", "imperial", "i"])
	config = ConfigParser()
	config.read('config.ini')
	config.remove_section('MAIN')
	config.add_section('MAIN')
	if config.has_section('API') == False:
		config.add_section('API')
	if config.has_option('API', 'key') == False:
		key = Prompt.ask("API key", password=True)
		config.set('API', 'key', key)
	key = config.get('API', 'key')
	config.set('MAIN', 'city', city)
	config.set('MAIN', 'units', units[0])
	with open('config.ini', 'w') as f:
		config.write(f)
	fetch_and_display(city, units, key)


def load_config() -> None:
	"""
	Load configuration file.
	"""
	if path.exists('config.ini') == False:
		save_config()
	else:
		try:
			config = ConfigParser()
			config.read('config.ini')
			city = config.get('MAIN', 'city')
			units = config.get('MAIN', 'units')
			key = config.get('API', 'key')
			if len(city)==0 or len(units)!=1 or len(key)==0:
				raise AttributeError
			fetch_and_display(city, units, key)

		except AttributeError:
			save = Prompt.ask("Missing data in config file! Create config now?", choices=["Y", "N"])
			save_config() if save == 'Y' else print("[bold red]Exiting...[/bold red]");exit(1)
			
		except urllib.error.HTTPError:
			save = Prompt.ask("[bold red]Please check your API key, you can get it from [/bold red][bold blue]https://openweathermap.org/api[/bold blue].[bold red] Edit config now?[/bold red]", choices=["Y", "N"])
			save_config() if save == 'Y' else print("[bold red]Exiting...[/bold red]");exit(1)

		except IOError:
			print("[bold red]Please check your internet connection.\nExiting...[/bold red]")
			exit(1)

		except NoSectionError:
			save = Prompt.ask("Configuration file is missing or corrupted! Create config now?", choices=["Y", "N"])
			save_config() if save == 'Y' else print("[bold red]Exiting...[/bold red]");exit(1)


def build_url(city: str, unit: str, key: str) -> str:
	"""
	Build API call url.

	Parameters:
	city (str): City name.
	unit (str): Units system (metric or imperial).
	key (str): API key.

	Returns:
	full_url (str): API call URL.
	"""
	api_url = 'http://api.openweathermap.org/data/2.5/weather?q='
	if unit == 'm':
		units = 'metric'
	else:
		units = 'imperial'
	full_url = api_url + city + '&mode=json&units=' + units + '&APPID=' + key
	return full_url


def fetch_data(full_url: str) -> dict:
	"""
	Sends request to API and recieves weather data, converts it from JSON to dict.

	Parameters:
	full_url (str): API call URL.

	Returns:
	data_dict (dict): Data dictionary.
	"""
	try:
		with urllib.request.urlopen(full_url) as url:
			data = url.read().decode('utf-8')
			data_dict = json.loads(data)
		return data_dict
	except urllib.error.HTTPError as e:
		if e.code == 404:
			save = Prompt.ask("[bold red]Please check the city name, use [/bold red][bold blue]https://openweathermap.org/find[/bold blue][bold red] to find city names.[bold red] Edit config now?[/bold red]", choices=["Y", "N"])
			save_config() if save == 'Y' else print("[bold red]Exiting...[/bold red]");exit(1)
		elif e.code == 401:
			save = Prompt.ask("[bold red]Please check your API key, you can get it from [/bold red][bold blue]https://openweathermap.org/api[/bold blue].[bold red] Edit config now?[/bold red]", choices=["Y", "N"])
			save_config() if save == 'Y' else print("[bold red]Exiting...[/bold red]");exit(1)
	else:
		print("[bold red]An error has occurred.\nExiting...[/bold red]")
		exit(1)


def convert_time(time: str, format: str) -> str:
	"""
	Converts UNIX timestamp to readable format.

	Parameters:
	time (str): UNIX timestamp.
	format (str): Day(d) or Full time(h)

	Returns:
	(str): Readable time format.
	"""
	if format == "h":
		return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
	else:
		return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')


def get_icon(icon: str) -> str:
	"""
	Get icon unicode from dictionary.

	Parameters:
	icon (str): icon code from API response.

	Returns:
	(str): icon unicode.
	"""
	icons = {"01": ":sun:",
			 "02": ":sun_behind_cloud:",
			 "03": ":cloud:",
			 "04": ":cloud:",
			 "09": ":cloud_with_rain:",
			 "10": ":sun_behind_rain_cloud:",
			 "11": ":cloud_with_lightning:",
			 "13": ":snowflake:",
			 "50": ":droplet:"}
	return icons[icon[:-1]]


def get_color(temp: float, unit: str) -> str:
	"""
	Get temperature color.

	Parameters:
	temp (int): Temperature value.
	unit (str): Units system.
	city (str): City name.

	Returns:
	(str): color name.
	"""
	if unit == "F":
		temp = (temp-32)/1.8
	if temp < 4:
		return 'bright_cyan'
	if temp > 3 and temp < 16:
		return 'bright_green'
	if temp > 15 and temp < 21:
		return 'bright_yellow'
	if temp > 20 and temp < 31:
		return 'dark_orange3'
	if temp > 30:
		return 'red3'


def build_dict(data: dict, units: str, city: str) -> dict:
	"""
	Get necessary data from dictionary.

	Parameters:
	data (dict): Data dictionary.
	units (str): Units system.
	city (str): City name.

	Returns:
	final_data (dict): final data dictionary.
	"""
	sys = data.get('sys')
	main = data.get('main')
	weather = data.get('weather')
	coord = data.get('coord'),
	if units == 'm':
		units = [chr(176)+'C', 'm/s']
	else:
		units = [chr(176)+'F', 'miles/h']
	final_data = dict(
		city=city.capitalize(),
		lat=coord[0]['lat'],
		lon=coord[0]['lon'],
		country=sys.get('country'),
		day=convert_time(data.get('dt'), 'd'),
		temp=main.get('temp'),
		temp_color=get_color(main.get('temp'), units[0][-1]),
		unit=units[0],
		weather_desc=weather[0].get("description").capitalize(),
		weather_icon=get_icon(weather[0].get("icon")),
		temp_max=main.get('temp_max'),
		temp_max_color=get_color(main.get('temp_max'), units[0][-1]),
		temp_min=main.get('temp_min'),
		temp_min_color=get_color(main.get('temp_min'), units[0][-1]),
		wind_speed=f"{data.get('wind')['speed']} {units[1]}",
		clouds=data.get('clouds')['all'],
		sunrise=convert_time(sys.get('sunrise'), 'h'),
		sunset=convert_time(sys.get('sunset'), 'h'),
		update_time=convert_time(data.get('dt'), 'h'),
	)
	if 'rain' in data:
		if '1h' in data['rain']:
			final_data['rain_1h'] = data.get('rain')['1h']
		if '3h' in data['rain']:
			final_data['rain_3h'] = data.get('rain')['3h']
	if 'snow' in data:
		if '1h' in data['snow']:
			final_data['snow_1h'] = data.get('snow')['1h']
		if '3h' in data['snow']:
			final_data['snow_3h'] = data.get('snow')['3h']
	return final_data


def display(data: dict) -> None:
	"""
	Displays weather info.

	Parameters:
	data (dict): Weather data dictionary.
"""

	print('---------------------------------------')
	print(	f"Current weather in: [bold blue]"\
				f"{data['city']}, {data['country']} "\
			f"[/bold blue]on {data['day']} :")
	print(	f"[{data['temp_color']} bold]"
				f"{data['temp']}{data['unit']}"
			f"[/{data['temp_color']} bold]"

			f" - [bold]{data['weather_desc']}[/bold] {data['weather_icon']}")
	print(	f"Max: "
			f"[{data['temp_max_color']} bold]"
				f"{data['temp_max']}{data['unit']}"
			f"[/{data['temp_max_color']} bold]"

			f", Min: "
			f"[{data['temp_min_color']} bold]"
				f"{data['temp_min']}{data['unit']}"
			f"[/{data['temp_min_color']} bold]")
	print(f"\nClouds: {data['clouds']}%")
	print(f"Sunrise at: {data['sunrise']} :sunrise:")
	print(f"Sunset at: {data['sunset']} :sunset:")
	print('')
	print(f"Last update from the server: {data['update_time']}")
	print('---------------------------------------')


def fetch_and_display(city: str, units: str, key: str) -> None:
	"""
	Fetch, format and display weather data.

	Parameters:
	data (dict): Data dictionary.
	units (str): Units system.
	key (str): API key.
	"""
	url = build_url(city, units, key)
	data = fetch_data(url)
	final_data = build_dict(data, units, city)
	display(final_data)


def args() -> None:
	"""
	Parse arguments to load or save config.
	"""
	parser = argparse.ArgumentParser(description="Weather via command line")
	parser.add_argument('-c', '--config', action='store_true',
						help='Create config file (city - units - API key)')
	args = parser.parse_args()
	if args.config == True:
		save_config()
	else:
		load_config()


def main() -> None:
	args()


if __name__ == "__main__":
	main()
