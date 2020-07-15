import reverse_geocoder as rg

def get_location(message_latitude, message_longitude):
    coordinates = (message_latitude, message_longitude)
    results = rg.search(coordinates) # default mode = 2
    state = results[0]['admin1']
    country = results[0]['cc']
    location = [state, country]
    # print(location)
    return location

