import streamlit as st
import pandas as pd
from datetime import datetime
from datetime import timedelta
import requests
from time import time
from tqdm import tqdm
from stqdm import stqdm


def get_token():
    refresh_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlblR5cGUiOiJUSElSRFBBUlRZQVBJX1JlZnJlc2giLCJ0b2tlbmlkIjoiYzNlYTg1YmItOTczMS00N2M5LTg5ZmMtZTk3NmFjMDE5NTYwIiwid2ViQXBwIjoiVGhpcmRQYXJ0eUFwcCIsInZlcnNpb24iOiIyIiwiaWRlbnRpdHlUb2tlbiI6IkhiZ25SMzJiOVQwbUFpblpnMDdidVJIek1pTTJpWjkrbWtJSlZkK1pudEt2S1Eyck9yT1AwM3J2cldMRmUrWElEWGtBUjYvVnpaeUNqTE5vbDBQZWpKRzhJM0RRdm9QTmhlVWd3bGJKOERFMVMrQVZiODc1R2JMOVozK29kaklxSU1sWTFEUkFxdkxnTU1wM0tZb09IcnlzQUVTZ0FXbHJyNklIUkJIeEl3TVRHcElvNjQzdld6THJOMFM4WkZaZngwdk1qNC8vSENnYXBlclpzeUNSR2VLM3FjdVlMOGdmbzlyNWhsNjUxWTFxcEF0Qlh6MFRCNzNJZmJBTk5tZ2txZ1h1K0lqQnMwckN0TXdCeW5HaUJ1azVDVGtrV2VwTEZDckJSRkRCWFVIME0wYXlGTDhISWY3b255RXFtbnNqaXZnQkwvcFBIZUlWZTZ3MDhLNmN5QmYzR0JUNGdQb2NCT04yYjRkS0dxQmJyQnh2KzF1cWxmZmZzUlplTEFDNFhlU1BBOGRRcHdRSnA5YXMxdUozbndZcVJSWlFTM0IwTDM0L1N1VE9ScnRUZXF5NksybEFKSEUrZUp5RDZtYkEyUFRZZGp5SnlTdTdqS2ZvQkJ6ZE9WNVpkL2xiOWEwbHVOV2hQWGpua3pidERLeS96aCtKbzFYeE9nOHUwazF1UWR3endoQ3ZFanZMbkNSb0k2MVV5bTZ6V2VzcTdQOWoyMU5xZ2FuM2VnbVFXdTF5dHdKZHc5ekwvSjhqZ3JEd1NDZlRTR2NLcjgvalhSN1VtcEJqaEJvNTJFVk5QczIyRzg2d2lvUFNPMnhrTUpOVUdGZEYvcWozazAvdmFYRTMzaDVYcXlsNnZEODNyME8wcDJxcUh5bEtFZEVRMm5xQyt1N2YvZStuRVBhdTMwZ2pDTUFZZzdRdUsxREhuRnYrTmpmU0VKang5cy9zRWQraForSDBWcDlzUS9qd1hJNXY4SkU4UUI2VmdwbjJYbnRhV1lzNnhrRi9hZVR0d1AwYVZrZ0pGUkNHWEVpN1hnekY2RXFwYzc2bitLZUpPOHlxeG82SUJKM2dMOURNQkZLczhwYkViMmtTd1crN2pYejFLb0IxUEt1VVNpYkY0d09XWUNBK2R5OTI2eks0MXFSS1Qxd1ZPR2ZWNnYyd2t4RGJqdjdXVzc4UnZCYmVDU3dzTDY4ckNYclhUOFJuYjloMHZuVU5taXJ4aXZqYWpnak5aQTVNNHExQ0JwRVk5MjNvU3ZOdkNodFhLcHZqQnlITTg0bVptN2dwdk5wQkdnSm1zZ0oweVNOaHExNy8zczNMaFl6N25TcEljUXQ2Q04wYndCMDhQWENHempTenA4aUxmdXMvMHFmZnBEdjNCbXVEV2Z1cUROcTA4bmhhY0VyRCtaNjBscnc2cWlBSytSOTJIbmJpNnpqMFFJTUViSndlUFpCajVFRG1kY2todHBsaW9IQ0xrM2RxWW1qaHh0YTdhMlE5UlBlaWxXYkFud01hNWNVUlRnTThsNWhMSHJlcDBpSVIxVkgxakNDMWJpWE9WNWcrVndZL1V0TDZyNlI2N0V6MVVvd3p4b25OTzQzOWZMUVhYMVBaTm5qOFc1bDNjM0VJMDdyQWpJdk5jMTRtSy9aYmprempsVk1RV2V6SW9pWVRoYTVxKzZMY2lXK2JhUWV3SUNtL0xFTW83bk9BcDA0TCsvNWRYb2VsZGJRdzgxb2JyejBnU1J2eUFHbmltNjdZcUduNGxMcFJxK3R3VVRjWFVtSE5kSERDYittdm9RN2M5STRuNSszS3J5ekJsY3B2QlF6YytVL3I5dHduUXI1RkMrWTBBM29LbzlXMzNTVytUVzZLRmRZbjdSbWxUVUcrYlJ0RmJ4U20zWENlaGZ2RjRmMDNPa0JRKzN0SjIzeDdHMkRUYmxKQzNyVUFDQzVlR0pEajdMZWxxclNheVEwcmRMSEhyaDV6OHk4K0VKLzNsY2V5aUlOek1oQnk2VzNubjFaTTNOS0ZwRlk2T3BScFN5UDRtNktCU2lDT2xuUjhpMXZpcmdPNE1Cem0wd1NzNmNKOU42WEZVNlhzZk9XZFFVS2picEpsTDNGUU5iaUlFNXphY01rZXRiK1hkV0dpM3g3Um95WGFub0lZZVk0cm11c0JoTzdIQlVDUG81dVRHbzRJT05CWUlldWpFOUJxRUw3YUQzMjlOZXNiNFIxZlB4T3JENXhwbHMwQ3Q4dzlYbVFLTXdKK1Q3RzV4aTloL0JhWklSZkdDV2hkRXhaUkMvSVk3MENhYnhEN1UrWFJCRWRuQ2VKRFh0elphSkxVM1E9PSIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL2dpdmVubmFtZSI6Ik1pa2tlbCBFcmlrIFJhc211cyBTY2htaWR0IiwibG9naW5UeXBlIjoiQ2VydGlmaWNhdGUiLCJjdnIiOiIzMzA3NzgzMSIsImNvbXBhbnkiOiJOUkdpIFLDpWRnaXZuaW5nIEEvUyIsInJpZCI6IkNWUjozMzA3NzgzMS1SSUQ6NjQ5MjkzMzEiLCJ1c2VySWQiOiI2OTg5MDEiLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6IkNWUjozMzA3NzgzMS1SSUQ6NjQ5MjkzMzEiLCJ0cGlkIjoiM0FCNjAyQUQtNzhCMS00RTAyLThFMTYtRTMyNjQyMDQwM0Q4IiwiZXhwIjoxNzM3MTk3MzI1LCJpc3MiOiJFbmVyZ2luZXQiLCJqdGkiOiJjM2VhODViYi05NzMxLTQ3YzktODlmYy1lOTc2YWMwMTk1NjAiLCJ0b2tlbk5hbWUiOiJNaWtrZWwiLCJyb2xlcyI6IlJlYWRQcml2YXRlLCBSZWFkQnVzaW5lc3MiLCJhdWQiOiJFbmVyZ2luZXQifQ.AkiBDKHHMSKRD7OMQYtPU0R7RD00dkUvX2S_b879fpA'    
    try:
        access_token
    except NameError:
        url = "https://api.eloverblik.dk/ThirdPartyApi" + '/api/Token'
        headers = {'Authorization': 'Bearer ' + refresh_token}
        token_response = requests.get(url, headers=headers, timeout=5)
        token_response.raise_for_status()
        token_json = token_response.json()
        access_token = token_json['result']
        timelog = datetime.now() - timedelta(days=1)
    else:
        time_between_insertion = datetime.now() - timelog
        if  time_between_insertion.days > 1:
            url = "https://api.eloverblik.dk/ThirdPartyApi" + '/api/Token'
            headers = {'Authorization': 'Bearer ' + refresh_token}
            token_response = requests.get(url, headers=headers, timeout=5)
            token_response.raise_for_status()
            token_json = token_response.json()
            access_token = token_json['result']
            
            timelog = datetime.now()
    return access_token

def test_datahub():
    url = 'https://api.eloverblik.dk/thirdpartyapi/api/isalive'
    response = requests.get(url)
    i = 0
    while response.status_code != 200:
        print('Datahub Down')
        time.sleep(60)
        i += 1
        if i > 10:
            print('Datahub Down for 10 min')
            break
    return 'Ok'

def eloverblik_IDs(CVR):
    access_token = get_token()
    url = 'https://api.eloverblik.dk/thirdpartyapi/api/authorization/authorization/meteringpointids/customerCVR/' + CVR

    headers = {'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json'}

    response = requests.get(url, headers=headers)
    return response.json()['result']


def eloverblik_timeseries(CVR, fromdate, area):
    my_bar = st.progress(0, text='Henter CO2 data')
    # DeclarationEmissionHour
    response = requests.get(
        url='https://api.energidataservice.dk/dataset/DeclarationGridEmission?start='+str(fromdate)+'T00:00&limit=400000')
    result = response.json()

    my_bar.progress(0.10, text='Henter CO2 data')
    co2 = pd.json_normalize(result, 'records',
            errors='ignore')

    co2 = co2[co2['FuelAllocationMethod']=='125%']
    co2 = co2[['HourDK', 'PriceArea', 'FuelAllocationMethod', 'CO2PerkWh']]
    co2['HourDK'] = pd.to_datetime(co2['HourDK'])
    co2 = co2[co2['PriceArea']==area]

    my_bar.progress(0.20, text='Henter data fra eloverblik')


    access_token = get_token()
    test = test_datahub()
    if test != 'Ok':
        return print('Datahub down')
    meters = eloverblik_IDs(CVR)
    #meters = IDs
    df = pd.DataFrame(columns=['meter', 'amount',  'from', 'hour'])   
    url = 'https://api.eloverblik.dk/thirdpartyapi/api/meterdata/gettimeseries/' + str(fromdate) + '/2023-10-31/Hour'
    headers = {'Authorization': 'Bearer ' + access_token,
    'Accept': 'application/json',
    'Content-Type': 'application/json'}
    for meter in stqdm(meters):
        my_bar.progress(0.20+(len(meters)/0.50), text='Henter data fra eloverblik')
        body = """{{"meteringPoints": {{
            "meteringPoint": ["{0}"]
        }}
        }}""".format(str(meter))
        

        test = test_datahub()
        if test != 'Ok':
            continue

        response = requests.post(url, data=body, headers=headers)
        data = response.json()

        try:
            data['result'][0]['MyEnergyData_MarketDocument']['TimeSeries'][0]
        except:
            print('Error on ' + str(meter))
            continue
        
        time_series_data = data['result'][0]['MyEnergyData_MarketDocument']['TimeSeries'][0]

        # Extract the mRID.
        mrid = time_series_data['mRID']

        # Normalize the 'Point' data.
        df_meter = pd.json_normalize(
            time_series_data['Period'], 'Point',
            meta=[['timeInterval', 'start'],['timeInterval', 'end']],
            errors='ignore')
        
        df_meter['meter'] = mrid
        df_meter['To_date']= pd.to_datetime(df_meter['timeInterval.end']).dt.date
        df_meter['amount'] = pd.to_numeric(df_meter['out_Quantity.quantity'])
        df_meter['hour'] = pd.to_numeric(df_meter['position'])
        df_meter['from'] = pd.to_datetime(df_meter.To_date) + pd.to_timedelta(df_meter.hour-1, unit='h')
        df_meter = df_meter[['meter', 'amount',  'from', 'hour']]
        df = pd.concat([df, df_meter], ignore_index=True)

    my_bar.progress(0.70, text='Samler data')
    samlet = df.merge(co2, how='left', left_on='from', right_on='HourDK')
    samlet = samlet.rename(columns={'from':'datetime', 'amount': 'Mængde [kWh]'})

    samlet['UdledningPrTime [kg]'] = samlet['Mængde [kWh]'] * (samlet['CO2PerkWh']/1000)
    my_bar.progress(0.90, text='Laver filer')

    virksomhed = samlet.groupby('datetime').agg({'Mængde [kWh]':'sum', 'CO2PerkWh':'mean', 'UdledningPrTime [kg]':'sum'}).reset_index()

    maler_excel = samlet.to_excel('virksomhedsdata/' + CVR + ' målerniveau.xlsx', index=False)
    virksomhed_excel = virksomhed.to_excel('virksomhedsdata/' + CVR + ' hele firmaet.xlsx', index=False)

    my_bar.progress(1.00, text='Download filer er klar')

    return samlet, maler_excel, virksomhed_excel






def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True