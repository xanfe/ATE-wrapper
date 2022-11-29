import requests
import os
import json

import configparser
config = configparser.ConfigParser()
config.read('settings\config.ini')

api_url = config["urls"]["kemx_plant1_ws"]

def backcheck(serial, station):
    obj = {
    "serialNumber": serial,
    "stationName": station,
    "application": "wsconnector",
    "pcName": os.environ['COMPUTERNAME'],
    "dllVersion": "1.1.0"
    }

    return requests.post(api_url + "Traceability_GetMacAddress_BySerNum", data = obj).text.split("|")[1][:-1]



def get_mac (serial, pnumber, station):

    obj = {
    "serialNumber": serial,
    "partNumber": pnumber,
    "stationName": station,
    "application": "wsconnector",
    "pcName": os.environ['COMPUTERNAME'],
    "dllVersion": "1.1.0"
    }
    return requests.post(api_url + "Traceability_GetMacAddress_BySerNum", data = obj).text.split("|")[1][:-1]

def get_pnumber(serial):
    obj = {
    "SerialNumber": serial,
    "PartNumber": ""
    }

    return json.loads(requests.post(api_url + "Traceability_FindPartNumberBySerialNumber", data = obj).text)["PartNumber"][:-1]


