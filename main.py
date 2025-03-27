import json
import requests
from geopy import distance
import folium
import os
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = 'https://geocode-maps.yandex.ru/1.x'
    response = requests.get(base_url, params={
        'geocode': address,
        'apikey': apikey,
        'format': 'json',
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_min_distance(list_ch):
    return list_ch['distance']


def map(coords_rev, sorted_list):
    m = folium.Map([coords_rev[0], coords_rev[1]], zoom_start=12)

    folium.Marker(
        location=[coords_rev[0], coords_rev[1]],
        tooltip="Click me!",
        popup="Ваше местоположение",
        icon=folium.Icon(color='red'),
    ).add_to(m)

    for sorted_list in sorted_list:
        folium.Marker(
            location=[sorted_list['latitude'], sorted_list['longitude']],
            tooltip="Click me!",
            popup=sorted_list['title'],
            icon=folium.Icon(color='green'),
        ).add_to(m)

        m.save('index.html')


def main():
    load_dotenv()
    apikey = os.getenv('APIKEY')
    question = input("Введите местоположение: ")
    coords = fetch_coordinates(apikey, question)
    coords_rev = coords[1], coords[0]

    with open('coffee.json', 'r', encoding='windows-1251') as my_file:
        file_contents = my_file.read()
    coffee_houses = json.loads(file_contents)

    not_sorted_list = []
    for coffee_house in coffee_houses:
        name = coffee_house['Name']
        latitude = coffee_house['Latitude_WGS84']
        longitude = coffee_house['Longitude_WGS84']
        ch_coords_rev = latitude, longitude
        my_distance = distance.distance(coords_rev, ch_coords_rev).km
        coffee_house_dict = {
            'title': name,
            'distance': my_distance,
            'latitude': latitude,
            'longitude': longitude
        }
        not_sorted_list.append(coffee_house_dict)

    sorted_list = sorted(not_sorted_list, key=get_min_distance)[:5]
    map(coords_rev, sorted_list)


if __name__ == '__main__':
    main()
