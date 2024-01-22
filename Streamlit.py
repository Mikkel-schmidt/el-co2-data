import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import requests

#from streamlit_folium import st_folium
from streamlit_functions import get_token, test_datahub, eloverblik_IDs, eloverblik_timeseries, check_password
#from streamlit_tree_select import tree_select
from streamlit_extras.app_logo import add_logo

import locale
#for lang in locale.windows_locale.values():
#    st.write(lang)

#locale.setlocale(locale.LC_ALL, "da_DK") 

st.set_page_config(layout="wide", page_title="Forside", page_icon="https://media.licdn.com/dms/image/C4E0BAQEwX9tzA6x8dw/company-logo_200_200/0/1642666749832?e=2147483647&v=beta&t=UiNzcE1RvJD3kHI218Al7omOzPLhHXXeE_svU4DIwEM")
st.sidebar.image('https://via.ritzau.dk/data/images/00181/e7ddd001-aee3-4801-845f-38483b42ba8b.png')

if check_password():
    st.success('Login success')

    cvr = st.number_input('Input cvr', )
    fromdate = st.date_input('Input first data')
    area = st.selectbox('Hvilket prisområde:', ('DK1', 'DK2'))

    access_token = get_token()

    cvr = '10373816'

    

    if st.button('Hent data'):
        my_bar = st.progress(0, text='Henter CO2 data')
        # DeclarationEmissionHour
        response = requests.get(
            url='https://api.energidataservice.dk/dataset/DeclarationGridEmission?start='+str(fromdate)+'T00:00&limit=400000')
        result = response.json()

        my_bar.progress(10, text='Henter CO2 data')
        co2 = pd.json_normalize(result, 'records',
                errors='ignore')

        co2 = co2[co2['FuelAllocationMethod']=='125%']
        co2 = co2[['HourDK', 'PriceArea', 'FuelAllocationMethod', 'CO2PerkWh']]
        co2['HourDK'] = pd.to_datetime(co2['HourDK'])
        co2 = co2[co2['PriceArea']==area]

        my_bar.progress(20, text='Henter data fra eloverblik')
        df = eloverblik_timeseries(cvr, str(fromdate))
        st.dataframe(df)

        samlet = df.merge(co2, how='left', left_on='from', right_on='HourDK')
        samlet = samlet.rename(columns={'from':'datetime', 'amount': 'Mængde [kWh]'})

        samlet['UdledningPrTime [kg]'] = samlet['Mængde [kWh]'] * (samlet['CO2PerkWh']/1000)

        virksomhed = samlet.groupby('datetime').agg({'Mængde [kWh]':'sum', 'CO2PerkWh':'mean', 'UdledningPrTime [kg]':'sum'}).reset_index()

        #samlet.to_excel('virksomhedsdata/' + cvr + ' målerniveau.xlsx', index=False)
        #virksomhed.to_excel('virksomhedsdata/' + cvr + ' hele firmaet.xlsx', index=False)

    else:
        st.write('Goodbye')
    



    

