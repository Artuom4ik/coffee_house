from pprint import pprint
from geopy import distance
from flask import Flask
from dotenv import load_dotenv
import json
import os
import requests
import folium


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url,
                            params={
                              "geocode": address,
                              "apikey": apikey,
                              "format": "json",
                            })
    response.raise_for_status()
    found_places = response.json(
    )['response']['GeoObjectCollection']['featureMember']

    if not found_places:
      return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def min_distance(coffee):
    return coffee['distance']


def rendor_html():
    with open('кофейни.html') as file:
        return file.read()


def main():
    load_dotenv()
    with open("coffee.json", "r", encoding="CP1251") as my_file:
        file_contents = my_file.read()
        coffee_shops = json.loads(file_contents)

    user_address = input('Где вы находитесь? ')
    apikey = os.environ['APIkey']
    user_coords = fetch_coordinates(apikey, user_address)

    coffee_houses = []

    for coffee_shop in coffee_shops:
        coffee_house = dict()
        coffee_house['title'] = coffee_shop['Name']
        coffee_house['distance'] = distance.distance(
          user_coords,
          (coffee_shop['Latitude_WGS84'], coffee_shop['Longitude_WGS84'])).km
        coffee_house['latitude'] = coffee_shop['Latitude_WGS84']
        coffee_house['longitude'] = coffee_shop['Longitude_WGS84']
        coffee_houses.append(coffee_house)
    sorted_coffee_shops = sorted(coffee_houses, key=min_distance)

    m = folium.Map(location=list(user_coords), zoom_start=600, tiles="Stamen Terrain")

    for cafe in sorted_coffee_shops[:5]:
        coords_cafe = []
        coords_cafe.append(cafe['latitude'])
        coords_cafe.append(cafe['longitude'])
        tooltip = cafe['title']
        folium.Marker(
            coords_cafe, 
            popup="<i>Mt. Hood Meadows</i>",   
            tooltip=tooltip,
        ).add_to(m)
    m.save("кофейни.html") 
    app = Flask(__name__)
    app.add_url_rule('/', 'Кофейни', rendor_html)
    app.run('0.0.0.0')


if __name__ == "__main__":
    main()
