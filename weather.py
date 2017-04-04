import argparse, urllib.request, json, datetime
from concurrent.futures import ThreadPoolExecutor

keys = {
  'geocode': 'AIzaSyAdVa34ZaHjA86YfvLKQ6rRTzLYVrKnFsQ',
  'weather': '58f91c991fa8e020bd4785395a1ce966'
}

#coordinate_list needs to be lat, long
def make_weather_request(coordinate_list):
  with urllib.request.urlopen('https://api.darksky.net/forecast/{}/{},{}'.format(keys['weather'], coordinate_list[0], coordinate_list[1])) as response:
    return json.loads(response.read().decode('UTF-8'))


def get_lat_long(future):
  response = future.result()
  decoded = response.read().decode('UTF-8')
  data = json.loads(decoded)
  latitude = data['results'][0]['geometry']['location']['lat']
  longitude = data['results'][0]['geometry']['location']['lng']

  return [latitude, longitude]


def get_current_weather(future):
  coordinate_list = get_lat_long(future)
  current_weather_data = make_weather_request(coordinate_list)
  temperature = current_weather_data['currently']['temperature']
  summary = current_weather_data['currently']['summary']
  print('It is {} degrees, {}'.format(temperature, summary))


def get_hourly_weather(future):
  coordinate_list = get_lat_long(future)
  hourly_weather_data = make_weather_request(coordinate_list)['hourly']

  summary = hourly_weather_data['summary']
  print(summary)
  for x in hourly_weather_data['data'][0:13]:
    time = x['time']
    time = datetime.datetime.fromtimestamp(time)
    time = time.strftime('%m-%d-%Y %H:%M')
    summary = x['summary']
    temperature = x['temperature']
    print('{} {}, {} degrees'.format(time, summary, temperature))


def get_daily_weather(future):
  coordinate_list = get_lat_long(future)
  daily_weather_data = make_weather_request(coordinate_list)['daily']

  summary = daily_weather_data['summary']
  print(summary)
  print()
  for x in daily_weather_data['data']:
    time = x['time']
    time = datetime.datetime.fromtimestamp(time)
    time = time.strftime('%m-%d-%Y')
    summary = x['summary']
    min_temperature = x['temperatureMin']
    max_temperature = x['temperatureMax']
    print('{} {} Low of {}, High of {}'.format(time, summary, min_temperature, max_temperature))


parser = argparse.ArgumentParser(description='Get current, hourly, or daily weather forecast')
group = parser.add_mutually_exclusive_group()
group.add_argument('-ah', '--hourly', help='get weather conditions by the hour', action='store_true')
group.add_argument('-d', '--daily', help='get weather conditions for the next several days', action='store_true')
parser.add_argument('postal_code', help='get weather information for this postal code', type=str)
args = parser.parse_args()

geocode_request = 'https://maps.googleapis.com/maps/api/geocode/json?components=postal_code:{}&key={}'.format(args.postal_code, keys['geocode'])
executor = ThreadPoolExecutor(max_workers=5)
future = executor.submit(urllib.request.urlopen, geocode_request)

if args.hourly:
  future.add_done_callback(get_hourly_weather)
elif args.daily:
  future.add_done_callback(get_daily_weather)
else:
  future.add_done_callback(get_current_weather)


