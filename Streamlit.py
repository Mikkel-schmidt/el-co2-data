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

    cvr = st.number_input('Input cvr', )
    fromdate = st.date_input('Input first data')
    area = st.selectbox('Hvilket prisområde:', ('DK1', 'DK2'))

    access_token = get_token()

    cvr = '10373816'

    

    if st.button('Hent data'):
        
        samlet, virksomhed = eloverblik_timeseries(cvr, str(fromdate), area)


        st.write(samlet.head())

        #samlet.to_excel('virksomhedsdata/' + cvr + ' målerniveau.xlsx', index=False)
        #virksomhed.to_excel('virksomhedsdata/' + cvr + ' hele firmaet.xlsx', index=False)

        def to_excell(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            format1 = workbook.add_format({'num_format': '0.00'}) 
            worksheet.set_column('A:A', None, format1)  
            writer.save()
            processed_data = output.getvalue()
            return processed_data
        
        df_xlsx = to_excell(samlet)
        st.download_button(label='📥 Måler niveau',
                                        data=df_xlsx ,
                                        file_name= 'samlet.xlsx')

        df_xlsx = to_excell(virksomhed)
        st.download_button(label='📥 Virksomhedsniveau',
                                        data=df_xlsx ,
                                        file_name= 'virksomhed.xlsx')
        

    else:
        st.write('Goodbye')
    



    

