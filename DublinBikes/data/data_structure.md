# Data Structures

### Bike Station Data

CSV: 'bikes_data.csv'
number,contract_name,name,address,position,banking,bonus,bike_stands,available_bike_stands,available_bikes,status,last_update

ex: 42,dublin,SMITHFIELD NORTH,Smithfield North,"{'lat': 53.349562, 'lng': -6.278198}",False,False,30,26,4,OPEN,1739960189000

Show per all bike stations:
    - name, address, bike stands


### Temperature Data

CSV: 'weather_data.csv'
coord,weather,base,main,visibility,wind,clouds,dt,sys,timezone,id,name,cod

ex: "{'lon': -6.2672, 'lat': 53.344}","[{'id': 803, 'main': 'Clouds', 'description': 'broken clouds', 'icon': '04d'}]",stations,"{'temp': 7.31, 'feels_like': 3.42, 'temp_min': 6.99, 'temp_max': 7.54, 'pressure': 1015, 'humidity': 89, 'sea_level': 1015, 'grnd_level': 1000}",6000,"{'speed': 7.2, 'deg': 140}",{'all': 75},1739878592,"{'type': 2, 'id': 2046043, 'country': 'IE', 'sunrise': 1739864224, 'sunset': 1739900472}",0,2964574,Dublin,200

Show for the first row of the CSV:
    - temperature, description, sunrise, sunset


