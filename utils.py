# Environment Variables
import requests
import json
import gmplot
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np


# Global Variables
LATITUDE = 33.746026 
LONGITUDE = -84.390658
RADIUS = 32000 # ~20mi radius
NUMSITES = 100   #500

PLOTLY_UN = 'stomy1'
PLOTLY_API_KEY = '2jLklvsASX01PKxb7sLB'
MAPBOX_ACCESS_TOKEN = "pk.eyJ1Ijoic2V0aHRvbXkiLCJhIjoiY2pteHBmeHBmMGJ0dDN3bTl0bDBjOHJhdiJ9.5YY_WBnxgJc3JAAkuuL1wQ"


# NCR API Call Wrappers: [find-nearby, catalog-items, item-availability]
def get_nearby_sites(lat = LATITUDE, lon = LONGITUDE, radius = RADIUS, numSites = NUMSITES):
    """Get numSites amount of sites w/in radius.

    Keyword arguments:
    radius(String) -- radius of search in meters
    numSites(String) -- how many sites you want returned
    
    Returns:
    Dictionary with list of: store-ids, latitudes, longitudes, site-names
    """
    
    # NCR API Call
    url = "https://gateway-staging.ncrcloud.com/site/sites/find-nearby/33.746026%20,-84.390658"

    querystring = {"radius": radius,"numSites": numSites}  

    headers = {
        'Content-Type': "application/json",
        'nep-application-key': "8a00860b6641a0ae0166471356ba000f",
        'Authorization': "Basic YWNjdDpqYW1AamFtc2VydmljZXVzZXI6MTIzNDU2Nzg=",
        'Cache-Control': "no-cache",
        'Postman-Token': "5130f289-eec6-4ae0-9ba6-f4cd3fefcdb0"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    
    # load json into lists
    response_dict = json.loads(response.text)
    
    site_dict = {}
    #hours_open_list = []
    #hours_closed_list = []
    for i in range(0, len(response_dict['sites']) - 1):
        site_dict[response_dict['sites'][i]['id']] = [response_dict['sites'][i]['coordinates']['latitude'],
                                                      response_dict['sites'][i]['coordinates']['longitude'],
                                                      response_dict['sites'][i]['siteName']]
            
    return site_dict

def get_item_availability(store_id, search_item):
    """Return boolean if item is available or not.

    Keyword arguments:
    store_id(String) -- id of store
    search_item(String) -- what we're looking for (i.e. "milk")
    
    Returns:
    True if the item is available, False if not
    """

    # NCR Catalog items that contain search query
    url = "https://gateway-staging.ncrcloud.com/catalog/items"

    querystring = {"pageNumber":"0","pageSize":"200","longDescriptionPattern":("%2A " + search_item)}

    headers = {
        'nep-application-key': "8a00860b6641a0ae0166471356ba000f",
        'accept': "application/json",
        'content-type': "application/json",
        'Authorization': "Basic YWNjdDpqYW1AamFtc2VydmljZXVzZXI6MTIzNDU2Nzg=",
        'Cache-Control': "no-cache",
        'Postman-Token': "d25fe7bb-7340-45ef-ab07-76205c9097f8"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response_dict = json.loads(response.text)
    
    item_code_list = []
    item_name_list = []
    # load item_code's into list
    for i in range(0, len(response_dict['pageContent'])):
        item_name_list.append(response_dict['pageContent'][i]['longDescription']["value"])
        item_code_list.append(response_dict['pageContent'][i]['itemId']['itemCode'])
    
    # NCR API Call - returns UNAVAILABLE items :(
    for item_code in item_code_list:
        url = "https://gateway-staging.ncrcloud.com/ias/item-availability/" + item_code

        headers = {
            'Nep-application-key': "8a00860b6641a0ae0166471356ba000f",
            'Nep-Enterprise-Unit': store_id,
            'Authorization': "Basic YWNjdDpqYW1AamFtc2VydmljZXVzZXI6MTIzNDU2Nzg=",
            'Cache-Control': "no-cache",
            'Postman-Token': "e0f63448-ee53-4028-a4d0-5d2ef9c8ce0c"
            }

        response = requests.request("GET", url, headers=headers)


        response_dict = json.loads(response.text)
        if(response_dict['availableForSale']):
            return True

    return False

def map(lat_list, lon_list):
    """Return boolean if item is available or not.

    Keyword arguments:
    lat_list(floats) -- list of latitudes
    lon_list(floats) -- list of longitudes
    """
    
    plotly.tools.set_credentials_file(username=PLOTLY_UN, api_key=PLOTLY_API_KEY)

    mapbox_access_token = MAPBOX_ACCESS_TOKEN

    data = [
        go.Scattermapbox(
            lat=lat_list,
            lon=lon_list,
            mode='markers',
            marker=dict(
                size=9
            ),
        )
    ]

    layout = go.Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=LATITUDE,
                lon=LONGITUDE
            ),
            pitch=0,
            zoom=10
        ),
    )

    fig = dict(data=data, layout=layout)
    py.iplot(fig, filename='Multiple Mapbox')

def distanceCalculator(lat1, lon1, lat2, lon2):

    R = 3959

    dlon = (lon2 - lon1)*np.pi/180.
    dlat = (lat2 - lat1)*np.pi/180.
    a = (np.sin(dlat/2))**2 + np.cos(lat1) * np.cos(lat2) * (np.sin(dlon/2))**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return round(R * c, 2)

def get_sites(lat, lon, grocery_list):
    
    nearby_sites = get_nearby_sites(lat, lon)
    possible_store_count = 0
    possible_sites_dict = {}
    
    for site in nearby_sites.keys():
        all_items = True
        for item in grocery_list:
            if not(get_item_availability(site, item)):
                all_items = False
                break
        if(all_items):
            possible_sites_dict[site] = nearby_sites[site]
            possible_store_count += 1        
        if(possible_store_count >= 6):
            break

    return possible_sites_dict        
    
    """     
    # format lists for plotly
    lat_list = []
    lon_list = []
    for site in possible_sites_dict.keys():
        lat_list.append(str(possible_sites_dict[site][0]))
        lon_list.append(str(possible_sites_dict[site][1]))
    map(lat_list, lon_list)
    """
