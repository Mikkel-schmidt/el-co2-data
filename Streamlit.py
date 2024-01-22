import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import requests
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb


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

    # Initialize session state variables
    if 'data_fetched' not in st.session_state:
        st.session_state.data_fetched = False
        st.session_state.samlet = pd.DataFrame()
        st.session_state.virksomhed = pd.DataFrame()

    cvr = st.number_input('Input cvr', value=10373816)  
    fromdate = st.date_input('Input first data')
    area = st.selectbox('Hvilket prisområde:', ('DK1', 'DK2'))

    if st.button('Hent data'):
        st.session_state.samlet, st.session_state.virksomhed = eloverblik_timeseries(str(cvr), str(fromdate), area)
        st.session_state.data_fetched = True

    if st.session_state.data_fetched:
        st.write(st.session_state.samlet.head())

        if not st.session_state.virksomhed.empty:
            df_xlsx_v = to_excell(st.session_state.virksomhed)
            st.download_button(label='📥 Virksomhedsniveau',
                               data=df_xlsx_v,
                               file_name=f'{cvr} virksomhed.xlsx')

        if not st.session_state.samlet.empty:
            df_xlsx_s = to_excell(st.session_state.samlet)
            st.download_button(label='📥 Måler niveau',
                               data=df_xlsx_s,
                               file_name=f'{cvr} samlet.xlsx')