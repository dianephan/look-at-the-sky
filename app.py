import os
from dotenv import load_dotenv
from flask import Flask, request, render_template
from twilio.twiml.messaging_response import MessagingResponse
from pprint import pprint   # makes payload look nicer to read
from twilio.rest import Client
from image_classifer import get_tags
from geocoder import get_location
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

load_dotenv()
 
app = Flask(__name__)
client = Client()
 
sky_pics = {}
markers = []
 
def respond(message):
    response = MessagingResponse()
    response.message(message)
    return str(response)
 
@app.route('/webhook', methods=['POST'])
def reply():
    sender = request.form.get('From')
    media_msg = request.form.get('NumMedia')    # 1 if its a picture 
    message_latitude = request.values.get('Latitude')
    message_longitude = request.values.get('Longitude')
    # check if the user already sent in a pic. if they send something new, then update it
    if media_msg == '1' and sender in sky_pics:
        pic_url = request.form.get('MediaUrl0')  # URL of the person's media
        relevant_tags = get_tags(pic_url)
        print("The tags for your picture are : ", relevant_tags)
        if 'sky' or 'weather' in relevant_tags and sky_pics.get(sender)[4] is None:
            sky_pics.get(sender)[4] = pic_url
            return respond(f'Thanks for sending in a picture.')
        if 'sky' or 'weather' in relevant_tags and sky_pics.get(sender)[4] is not None:
            # replace the picture URL in sky_pics dictionary
            sky_pics.get(sender)[4] = pic_url
            return respond(f'Your picture has been updated.')
        else:
            return respond(f'Please send in a picture of the sky.')
    elif message_latitude is not None and message_longitude is not None:
        location = get_location(message_latitude, message_longitude)
        sky_pics[sender] = [None] * 5
        sky_pics.get(sender)[0] = message_latitude
        sky_pics.get(sender)[1] = message_longitude
        sky_pics.get(sender)[2] = location[0]
        sky_pics.get(sender)[3] = location[1]
        return respond(f'Your location has been set to : {location}')
    else:
        return respond(f'Please send your current location, then send a picture of the sky.')

@app.route("/")
def mapview():
    for entry in sky_pics:
        if sky_pics.get(entry)[4] is None:
            url_entry_pic = 'https://s3-external-1.amazonaws.com/media.twiliocdn.com/ACa2dea70cb125daf20c4ac433be77eda4/d7a07ccac2cf9321e82559c82beff7ed'       #rando pics
            sky_pics.get(entry)[4] = url_entry_pic
        markers.append({
            'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
            'lat': sky_pics.get(entry)[0], 
            'lng': sky_pics.get(entry)[1],
            'infobox': '<div id="bodyContent">' +
                '<img src="' +
                sky_pics.get(entry)[4] + 
                '" alt = "sky" style="width:175px;height:220px;"></img>' +
                '</div>' 
        })
    mymap = Map(
        identifier="sndmap",
        style=(
            "height:100%;"
            "width:100%;"
            "top:0;"
            "position:absolute;"
            "z-index:200;"
            "zoom: -9999999;"
        ),
        # these coordinates re-center the map 
        lat=37.805355,
        lng=-122.322618,
        markers = markers,
    )
    
    return render_template('index.html', mymap=mymap)

def start_ngrok():
    from twilio.rest import Client
    from pyngrok import ngrok
    url = ngrok.connect(5000)
    print(' * Tunnel URL:', url)
    client = Client()
 
if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        start_ngrok()
    app.run(debug=True)
