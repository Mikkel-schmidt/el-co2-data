import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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

st.set_page_config(page_title="Forside", page_icon="https://media.licdn.com/dms/image/C4E0BAQEwX9tzA6x8dw/company-logo_200_200/0/1642666749832?e=2147483647&v=beta&t=UiNzcE1RvJD3kHI218Al7omOzPLhHXXeE_svU4DIwEM")
col1, col2 = st.columns([1,2])
col1.image('https://via.ritzau.dk/data/images/00181/e7ddd001-aee3-4801-845f-38483b42ba8b.png')

def to_excell(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')

        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Table format options
        table_format = {
            'columns': [{'header': column} for column in df.columns],
            'style': 'Table Style Medium 9',  # You can choose different styles
        }

        # Add the DataFrame as an Excel table
        (max_row, max_col) = df.shape
        column_settings = [{'header': column} for column in df.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings, 'style': 'Table Style Medium 9'})

        # Auto-adjust columns' width
        for i, col in enumerate(df.columns):
            # Find the maximum length of the data in the column
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 1
            worksheet.set_column(i, i, column_len)

    processed_data = output.getvalue()
    return processed_data

if check_password():
    st.success('Login success')

    st.write('Hvis du skal give kunden et link til at give adgang til tredjepartsdata skal du bruge følgende link: [Eloverblik fuldmagt](https://eloverblik.dk/authorization/authorization?thirdPartyId=3AB602AD-78B1-4E02-8E16-E326420403D8&fromDate=2020-01-23&toDate=2027-01-23&customerKey=El-co2&returnUrl=nrgi.dk%2Ferhverv)')

    # Initialize session state variables
    if 'data_fetched' not in st.session_state:
        st.session_state.data_fetched = False
        st.session_state.samlet = pd.DataFrame()
        st.session_state.virksomhed = pd.DataFrame()

    cvr = st.number_input('Input cvr', value=1000000)  #10373816
    fromdate = st.date_input('Input first data', value=datetime.today() - timedelta(days=14), min_value=datetime.date(2022, 1, 1), max_value=datetime.today() - timedelta(days=13))
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