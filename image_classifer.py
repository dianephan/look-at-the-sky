from clarifai.rest import ClarifaiApp
from pprint import pprint   #makes payload look nicer to read
app = ClarifaiApp()

def get_tags(image_url):
    response_data = app.tag_urls([image_url])
    sky_tags = {}   #dictionary data structure for faster lookup time 
    for concept in response_data['outputs'][0]['data']['concepts']:
        sky_tags[concept['name']] = 1
    return sky_tags
# pprint("image_classifer.py compiled")

