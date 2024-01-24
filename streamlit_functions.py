import streamlit as st
import pandas as pd
from datetime import datetime
from datetime import timedelta
import requests
import time
from tqdm import tqdm
from stqdm import stqdm


def get_token():
    refresh_token = st.secrets["refresh_token"]    
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
        st.write('Datahub Down, waiting 1 minute')
        time.sleep(60)
        i += 1
        if i > 10:
            st.write('Datahub Down for 10 min')
            break
    return 'Ok'

def eloverblik_IDs(CVR):
    access_token = get_token()
    url = 'https://api.eloverblik.dk/thirdpartyapi/api/authorization/authorization/meteringpointids/customerCVR/' + CVR

    headers = {'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json'}

    response = requests.get(url, headers=headers)
    return response.json()['result']

def authorizations():
    access_token = get_token()
    url = 'https://api.eloverblik.dk/thirdpartyapi/api/authorization/authorizations'

    headers = {'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json'}
    
    response = requests.get(url, headers=headers)

    try:
        df = pd.json_normalize(response.json(), 'result',
            errors='ignore')
    except:
        print('Error')

    return df


def eloverblik_timeseries(CVR, fromdate, todate, area):
    my_bar = st.progress(0.05, text='Henter CO2 data')
    # DeclarationEmissionHour
    response = requests.get(
        url='https://api.energidataservice.dk/dataset/DeclarationGridEmission?start='+str(fromdate)+'T00:00&end='+str(todate)+'T00:00&limit=400000')
    result = response.json()

    my_bar.progress(0.10, text='Henter CO2 data')
    co2 = pd.json_normalize(result, 'records',
            errors='ignore')

    co2 = co2[co2['FuelAllocationMethod']=='125%']
    co2 = co2[['HourDK', 'PriceArea', 'FuelAllocationMethod', 'CO2PerkWh']]
    co2['HourDK'] = pd.to_datetime(co2['HourDK'])
    co2 = co2[co2['PriceArea']==area]

    my_bar.progress(0.20, text='Henter målere fra eloverblik')


    access_token = get_token()
    test = test_datahub()
    if test != 'Ok':
        return print('Datahub down')
    meters = eloverblik_IDs(CVR)
    my_bar.progress(0.30, text='Henter data fra målere')
    #meters = IDs
    df = pd.DataFrame(columns=['meter', 'amount',  'from', 'hour'])   
    url = 'https://api.eloverblik.dk/thirdpartyapi/api/meterdata/gettimeseries/' + str(fromdate) + '/'+str(todate)+'/Hour'
    headers = {'Authorization': 'Bearer ' + access_token,
    'Accept': 'application/json',
    'Content-Type': 'application/json'}
    print('hejsa')
    i=0
    for meter in stqdm(meters):
        i+=0.5/len(meters)
        my_bar.progress(0.30+i, text='Henter timedata fra målerne')
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

    my_bar.progress(0.80, text='Samler data')
    samlet = df.merge(co2, how='left', left_on='from', right_on='HourDK')
    samlet = samlet.rename(columns={'amount': 'Mængde [kWh]'})

    samlet['UdledningPrTime [kg]'] = samlet['Mængde [kWh]'] * (samlet['CO2PerkWh']/1000)
    my_bar.progress(0.90, text='Laver filer')
    st.write(samlet)
    virksomhed = samlet.groupby('HourDK').agg({'Mængde [kWh]':'sum', 'CO2PerkWh':'mean', 'UdledningPrTime [kg]':'sum'}).reset_index()

    # maler_excel = samlet.to_excel(CVR + ' målerniveau.xlsx', index=False)
    # virksomhed_excel = virksomhed.to_excel(CVR + ' hele firmaet.xlsx', index=False)

    my_bar.progress(1.00, text='Download filer er klar om 2 sek.')

    return samlet, virksomhed

def el_production(df, fromdate, todate, area):
    # DeclarationGridMix
    response = requests.get(
        url='https://api.energidataservice.dk/dataset/DeclarationGridmix?start='+str(fromdate)+'T00:00&end='+str(todate)+'T00:00&&limit=400000')

    result = response.json()

    prod = pd.json_normalize(result, 'records',
                errors='ignore')
    prod['HourDK'] = pd.to_datetime(prod['HourDK'])
    prod['percent'] =  prod['SharePPM'] / 1000000 * 100
    prod = prod[['HourDK', 'PriceArea', 'ReportGrp', 'percent']]
    prod = prod[prod['PriceArea']==area]

    piv = prod.pivot_table(index=['HourDK', 'PriceArea'], columns='ReportGrp', values='percent').reset_index().fillna(0)
    st.write(piv)
    st.write(df)
    dff = df.merge(piv, how='left', on='HourDK')


    return dff





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
