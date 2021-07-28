import requests
import pandas as pd
import numpy as np
import time
import os
from secret import API

# activate virtualenv if necessary

api_key = API # Make your own api key using Google Cloud Console make it specific for places
url = "https://maps.googleapis.com/maps/api/place/textsearch/json?" # to get list of places
urldetails = "https://maps.googleapis.com/maps/api/place/details/json?" # to get place details
main_info = [] # main info
additional_info = [] # additional info
place_ids = [] # place id to get additional info
change_file = "" # what filename it should export should end with .xlsx
fields = "formatted_phone_number,website" # additional info you want on business

# simple get query from user and handle potential errors

def check_valid_request(query, next_page=None):
    # What if no responses handle that 
    if next_page == None:
        full_call = url + "query=" + query + "&key=" + api_key
    else:
        full_call = url + "pagetoken=" + next_page + "&key=" + api_key
    
    time.sleep(2) # needs to sleep in order for pagetoken to work takes a second to load
    try:
        response = requests.get(full_call)
    except:
        print("Invalid API KEY") # only reason call wouldn't work is if api_key is wrong
    data = response.json()

    # if status is fine get business info
    if data["status"] == "OK":
        get_businesses(data, query)
    else:
        print("Bad call! Try a different Keyword!")  



def get_businesses(data, query):
    if len(data["results"]) == 0:
        print("No Results! Try different Keywords!") # need query to be different

    else:

        for business in data["results"]:
             # append maininfo
            main_info.append({"name": business["name"], "address": business["formatted_address"], 
            "rating": business["rating"]})
            # append place id to get additional info
            place_ids.append(business["place_id"])
           
        # once all businesses are looked get additional info
        try:
            check_valid_request(query, next_page=data["next_page_token"])
        except:
            print("No new page found!")
            # process only get's started when there is not another page to be found
            # process get's additional info and exports to excel
            start_process()
            


def export_to_excel(): 
    # creates two dataframes using list of dicts
    print("Done!")
    df = pd.DataFrame(main_info)
    df2 = pd.DataFrame(additional_info)
    # combines dataframes by index
    result = pd.concat([df, df2.reindex(df.index)], axis=1)
    print(result)
    # exports to excel without the index
    result.to_excel("Businesses.xlsx", index=False)


def start_process():
    # gets additional info and once done exports to excel
    for id in place_ids:
        get_details(id)
    export_to_excel()
    


def get_details(id):
    # What if info isn't there handle that
    full_call = urldetails + "place_id=" + id + "&fields=website,formatted_phone_number" + "&key=" + api_key
    response = requests.get(full_call)
    data = response.json()
    # make sure call staus is fine
    if data["status"] == "OK":
        # try to add each additional info if not give default values
        try:
            website = data["result"]["website"]
            phone = data["result"]["formatted_phone_number"]
            additional_info.append({"website": website, "phone": phone})
            print("It went well")
        except:
            print("Fields Don't Exist! Adding Null Values!")
            additional_info.append({"website": "NA", "phone": "NA"})
    # if it isn't adds error to data
    else:
        print("Error")
        additional_info.append({"website": "Error", "phone": "Error"})


check_valid_request("waste+hauling+atlanta") # example call for waste management atlanta

