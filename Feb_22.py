import openpyxl
import pandas as pd
import plotly.graph_objects as go
import matplotlib
import numpy as np
import streamlit as st
from matplotlib.backends.backend_agg import RendererAgg
matplotlib.use('agg')
from st_btn_select import st_btn_select
import streamlit_authenticator as stauth
from wordcloud import WordCloud
_lock = RendererAgg.lock



# -----------------------------------------set page layout-------------------------------------------------------------
st.set_page_config(page_title='iSMM Dashboard',
                    page_icon = ':chart_with_upwards_trend:',
                    layout='wide',
                    initial_sidebar_state='collapsed')

#-----------------------------------------------User Authentication-----------------------------------------------
names = ['wenna', 'Mr.Loh']
usernames = ['wenna0306@gmail.com', 'booninn.loh@surbanajurong.com']
passwords = ['password', 'password']

hashed_passwords = stauth.hasher(passwords).generate()

authenticator = stauth.authenticate(names,usernames,hashed_passwords,
    'some_cookie_name','some_signature_key',cookie_expiry_days=30)

name, authentication_status = authenticator.login('Login','main')

if authentication_status:
    st.write('Welcome *%s*' % (name))


#-----------------------------------------------different pages setup-----------------------------------------------

    page = st_btn_select(('Faults', 'Schedules', 'Inventories'),
                        nav=True,
                        format_func=lambda name: name.capitalize(),
                        )


# =============================================Fault================================================
    if page =='Faults':
        html_card_title="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; padding-top: 5px; width: 600px;
           height: 50px;">
            <h1 class="card-title" style=color:#116a8c; font-family:Georgia; text-align: left; padding: 0px 0;">FAULT DASHBOARD</h1>
          </div>
        </div>
        """

        st.markdown(html_card_title, unsafe_allow_html=True)
        st.markdown('##')
        st.markdown('##')
        st.markdown(
            'Welcome to this Analysis App, get more detail from :point_right: [iSMM](https://ismm.sg/ce/login)')
        st.markdown('##')

        def fetch_file(filename):
            cols = ['Fault Number', 'Trade', 'Trade Category',
                    'Type of Fault', 'Impact', 'Site', 'Building', 'Floor', 'Room', 'Cancel Status', 'Reported Date',
                    'Fault Acknowledged Date', 'Responded on Site Date', 'RA Conducted Date',
                    'Work Started Date', 'Work Completed Date', 'Attended By', 'Action(s) Taken',
                    'Other Trades Required Date', 'Cost Cap Exceed Date',
                    'Assistance Requested Date', 'Fault Reference',
                     'Incident Report', 'Remarks']
            parse_dates = ['Reported Date',
                           'Fault Acknowledged Date', 'Responded on Site Date', 'RA Conducted Date',
                           'Work Started Date', 'Work Completed Date',
                           'Other Trades Required Date', 'Cost Cap Exceed Date',
                           'Assistance Requested Date']
            dtype_cols = {'Site': 'str', 'Building': 'str', 'Floor': 'str', 'Room': 'str'}
            return pd.read_excel(filename, header=1, index_col='Fault Number', usecols=cols, parse_dates=parse_dates, dtype=dtype_cols)


        df2 = fetch_file('Fault_GBB_s.xlsx')

        df2.columns = df2.columns.str.replace(' ', '_')
        df2['Time_Acknowledged_mins'] = (df2.Fault_Acknowledged_Date - df2.Reported_Date)/pd.Timedelta(minutes=1)
        df2['Time_Site_Reached_mins'] = (df2.Responded_on_Site_Date - df2.Reported_Date)/pd.Timedelta(minutes=1)
        df2['Time_Work_Started_mins'] = (df2.Work_Started_Date - df2.Reported_Date)/pd.Timedelta(minutes=1)
        df2['Time_Work_Recovered_mins'] = (df2.Work_Completed_Date - df2.Reported_Date)/pd.Timedelta(minutes=1)



        outstanding_cols = ['Trade', 'Trade_Category', 'Type_of_Fault', 'Impact', 'Site', 'Building', 'Floor', 'Room', 'Cancel_Status', 
        'Reported_Date', 'Other_Trades_Required_Date', 'Cost_Cap_Exceed_Date', 'Assistance_Requested_Date', 'Fault_Reference', 
         'Incident_Report', 'Remarks']

        df_outstanding = df2.loc[(df2['Cancel_Status'].isna()) & (df2['Work_Completed_Date'].isna()), outstanding_cols].copy()

        recovered_cols = ['Site', 'Building', 'Floor', 'Room', 'Trade', 'Trade_Category', 'Type_of_Fault', 'Attended_By', 'Time_Acknowledged_mins',
                   'Time_Site_Reached_mins', 'Time_Work_Started_mins', 'Time_Work_Recovered_mins']

        df3 = df2.loc[(df2['Cancel_Status'].isna()) & (df2['Work_Completed_Date'].notna()), recovered_cols].copy() #recovered faults


        bin_responded = [0, 10, 30, 60, np.inf]
        label_responded = ['0-10mins', '10-30mins', '30-60mins', '60-np.inf']

        bin_recovered = [0, 60, 240, 480, np.inf]
        label_recovered = ['0-1hr', '1-4hrs', '4-8hrs', '8-np.inf']

        df3['KPI_For_Responded'] = pd.cut(df3.Time_Site_Reached_mins, bins=bin_responded, labels=label_responded, include_lowest=True)
        df3['KPI_For_Recovered'] = pd.cut(df3.Time_Work_Recovered_mins, bins=bin_recovered, labels=label_recovered, include_lowest=True)

        df_daily = df2.loc[(df2['Cancel_Status'].isna()) & (df2['Work_Completed_Date'].notna()),:].copy() #some columns is not exist in df3

        # ----------------------------------------Sidebar---------------------------------------------------------------------
        st.sidebar.header('Please Filter Here:')

        Trade = st.sidebar.multiselect(
            'Select the Trade:',
            options=df2['Trade'].unique(),
            default=df2['Trade'].unique()
        )

        Trade_Category = st.sidebar.multiselect(
            'Select the Trade Category:',
            options=df2['Trade_Category'].unique(),
            default=df2['Trade_Category'].unique()
        )

        df2 = df2.query(
            'Trade ==@Trade & Trade_Category==@Trade_Category'
        )


        # ----------------------------------------------Main Page---------------------------------------------------------------
        html_card_subheader_outstanding = """
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 350px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Outstanding Fault</h3>
          </div>
        </div>
        """
        html_card_subheader_daily="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 350px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Daily Fault Cases</h3>
          </div>
        </div>
        """
        html_card_subheader_KPI_Responded="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 450px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">KPI Monitoring-Responded</h3>
          </div>
        </div>
        """
        html_card_subheader_KPI_Recovered="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 450px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">KPI Monitoring-Recovered</h3>
          </div>
        </div>
        """
        html_card_subheader_Tier1="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 400px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Recovered Fault vs Trade</h3>
          </div>
        </div>
        """
        html_card_subheader_Tier2="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 500px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Recovered Fault vs Trade Category</h3>
          </div>
        </div>
        """
        html_card_subheader_Tier3="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 520px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Recovered Fault vs Type of Fault</h3>
          </div>
        </div>
        """
        html_card_subheader_location="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 450px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Recovered Fault vs Location</h3>
          </div>
        </div>
        """
        html_card_subheader_fault_Technician="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #116a8c; padding-top: 5px; width: 550px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#116a8c; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">No. of Recovered Fault vs Technician</h3>
          </div>
        </div>
        """
        # -----------------------------------------------------Fault--------------------------------------------------------
        total_fault = df2.shape[0]
        fault_cancelled = int(df2['Cancel_Status'].notna().sum())
        fault_not_recovered = df2.loc[(df2['Cancel_Status'].isna()) & (df2['Work_Completed_Date'].isna()),:].shape[0]
        fault_recovered = df2.loc[(df2['Cancel_Status'].isna()) & (df2['Work_Completed_Date'].notna()),:].shape[0]
        fault_incident = int(df2['Incident_Report'].sum())

        column01_fault, column02_fault, column03_fault, column04_fault, column05_fault = st.columns(5)
        with column01_fault, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Total</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{total_fault}</h2>", unsafe_allow_html=True)

        with column02_fault, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Cancelled</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{fault_cancelled}</h2>", unsafe_allow_html=True)

        with column03_fault, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Outstanding</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: red;'>{fault_not_recovered}</h2>", unsafe_allow_html=True)

        with column04_fault, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Recovered</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #116a8c;'>{fault_recovered}</h2>", unsafe_allow_html=True)

        with column05_fault, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #116a8c;'>Incident Report</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: red;'>{fault_incident}</h2>", unsafe_allow_html=True)

#--------------------------------------- color & width & opacity----------------------------------------------
            # all chart
            titlefontcolor = '#116a8c'

            # pie chart for outstanding and tier1
            colorpieoutstanding = ['#116a8c', '#4c9085', '#50a747', '#59656d', '#06c2ac', '#137e6d', '#929906', '#ff9408']
            colorpierecoveredtier1 = ['#116a8c', '#4c9085', '#50a747', '#59656d', '#06c2ac', '#137e6d', '#929906', '#ff9408']

            # all barchart include stack bar chart and individual barchart and linechart
            plot_bgcolor = 'rgba(0,0,0,0)'
            gridwidth = 0.1
            gridcolor = '#1f3b4d'

            # stack barchart
            colorstackbarpass = '#048243'
            colorstackbarfail01 = '#116a8c'
            colorstackbarfail02 = '#ffdb58'
            colorstackbarfail03 = '#fa2a55'

            # individual barchart color, barline color& width, bar opacity
            markercolor = '#116a8c'
            markerlinecolor = '#116a8c'
            markerlinewidth = 1
            opacity01 = 1
            opacity02 = 1
            opacity03 = 1

            # x&y axis width and color
            linewidth_xy_axis = 1
            linecolor_xy_axis = '#59656d'

            # linechart
            linecolor = '#96ae8d'
            linewidth = 2

        # -----------------------------------------Outstanding Fault--------------------------------------------------------
        st.markdown('##')
        st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
        st.markdown(html_card_subheader_outstanding, unsafe_allow_html=True)
        st.markdown('##')

        df_outstanding_show = df_outstanding.loc[:, ['Trade', 'Trade_Category', 'Type_of_Fault', 'Site', 'Building', 'Floor', 'Room',
                                                     'Reported_Date', 'Other_Trades_Required_Date', 'Cost_Cap_Exceed_Date', 'Assistance_Requested_Date',
                                                    'Remarks']].sort_values('Trade')

        props = 'font-style: italic; color: #ffffff; font-size:0.8em; font-weight:normal;'  #border: 0.0001px solid #116a8c; background: #116a8c'
        df_outstandingdataframe = df_outstanding_show.style.applymap(lambda x: props)
        st.dataframe(df_outstandingdataframe, 2000, 200)

        ser_outstanding_building = df_outstanding.groupby(['Trade'])['Type_of_Fault'].count().sort_values(ascending=False)
        ser_outstanding_category = df_outstanding.groupby(['Trade_Category'])['Type_of_Fault'].count().sort_values(ascending=False)
    

        x_outstanding_building = ser_outstanding_building.index
        y_outstanding_building = ser_outstanding_building.values
        x_outstanding_category = ser_outstanding_category.index
        y_outstanding_category = ser_outstanding_category.values
        
        fig_outstanding_building, fig_outstanding_category = st.columns([1, 2])
        
        with fig_outstanding_building, _lock:
            fig_outstanding_building = go.Figure(data=[go.Pie(labels=x_outstanding_building, values=y_outstanding_building, hoverinfo='all', textinfo='label+percent+value', textfont_size=15, textfont_color='white', textposition='inside', showlegend=False, hole=.4)])
            fig_outstanding_building.update_layout(title='Number of Fault vs Trade', annotations=[dict(text='Outstanding', x=0.5, y=0.5, font_size=18, showarrow=False)])
            fig_outstanding_building.update_traces(marker=dict(colors=colorpierecoveredtier1))
            st.plotly_chart(fig_outstanding_building, use_container_width=True)
        
        with fig_outstanding_category, _lock:
            fig_outstanding_category = go.Figure(data=[go.Bar(x=x_outstanding_category, y=y_outstanding_category, orientation='v',
                                                              text=y_outstanding_category, textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                                               textposition='auto', textangle=-45)])
            fig_outstanding_category.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_outstanding_category.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_outstanding_category.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth)
            fig_outstanding_category.update_layout(title='Number of Fault vs Trade Category', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig_outstanding_category, use_container_width=True)

        st.markdown('##')
        st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)


        # --------------------------------------Daily Fault----------------------------------------------------
        st.markdown(html_card_subheader_daily, unsafe_allow_html=True)
        x_daily = df_daily['Reported_Date'].dt.day.value_counts().sort_index().index
        y_daily = df_daily['Reported_Date'].dt.day.value_counts().sort_index().values
        y_mean = df_daily['Reported_Date'].dt.day.value_counts().sort_index().mean()

        day_max = df_daily.Reported_Date.dt.day.max()

        fig_daily = go.Figure(data=go.Scatter(x=x_daily, y=y_daily, mode='lines+markers+text', line=dict(color='#116a8c', width=3),
                                              text=y_daily, textfont=dict(family='sana serif', size=14, color='#c4fff7'), textposition='top center'))
        fig_daily.add_hline(y=y_mean, line_dash='dot', line_color=linecolor, line_width=linewidth, annotation_text='Average Line',
                                  annotation_position='bottom right', annotation_font_size=18, annotation_font_color='green')
        fig_daily.update_xaxes(title_text='Date', tickangle=-45, title_font_color=titlefontcolor, tickmode='linear', range=[1, day_max],
                                           showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, zeroline=False)
        fig_daily.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=False,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, zeroline=False)
        fig_daily.update_layout(title='Number of Fault vs Date', plot_bgcolor=plot_bgcolor)
        st.plotly_chart(fig_daily, use_container_width=True)


     #---------------------------------------------KPI Monitoring-------------------------------------------------------

        st.markdown(html_card_subheader_KPI_Responded, unsafe_allow_html=True)
        st.markdown('##')
        st.markdown('Response Time refers to the time the fault or emergency was reported to the time the Contractor arrived on-site with evidence')
        st.markdown('##')

        x_KPI_building_010_Responded = df3.groupby(by='KPI_For_Responded').Trade.value_counts().loc['0-10mins'].index
        x_KPI_building_1030_Responded = df3.groupby(by='KPI_For_Responded').Trade.value_counts().loc['10-30mins'].index
        x_KPI_building_3060_Responded = df3.groupby(by='KPI_For_Responded').Trade.value_counts().loc['30-60mins'].index
        x_KPI_building_60inf_Responded = df3.groupby(by='KPI_For_Responded').Trade.value_counts().loc['60-np.inf'].index

        y_KPI_building_010_Responded = df3.groupby(by='KPI_For_Responded').Trade.value_counts().loc['0-10mins'].values
        y_KPI_building_1030_Responded = df3.groupby(by='KPI_For_Responded').Trade.value_counts().loc['10-30mins'].values
        y_KPI_building_3060_Responded = df3.groupby(by='KPI_For_Responded').Trade.value_counts().loc['30-60mins'].values
        y_KPI_building_60inf_Responded = df3.groupby(by='KPI_For_Responded').Trade.value_counts().loc['60-np.inf'].values

        x_KPI_category_010_Responded = df3.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['0-10mins'].index
        x_KPI_category_1030_Responded = df3.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['10-30mins'].index
        x_KPI_category_3060_Responded = df3.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['30-60mins'].index
        x_KPI_category_60inf_Responded = df3.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['60-np.inf'].index

        y_KPI_category_010_Responded = df3.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['0-10mins'].values
        y_KPI_category_1030_Responded = df3.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['10-30mins'].values
        y_KPI_category_3060_Responded = df3.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['30-60mins'].values
        y_KPI_category_60inf_Responded = df3.groupby(by='KPI_For_Responded').Trade_Category.value_counts().loc['60-np.inf'].values

        fig_responded_building, fig_responded_category = st.columns([1, 2])
        with fig_responded_building, _lock:
            fig_responded_building = go.Figure(data=[
                go.Bar(name='0-10mins', x=x_KPI_building_010_Responded, y=y_KPI_building_010_Responded, marker_color=colorstackbarpass),
                go.Bar(name='10-30mins', x=x_KPI_building_1030_Responded, y=y_KPI_building_1030_Responded, marker_color=colorstackbarfail01),
                go.Bar(name='30-60mins', x=x_KPI_building_3060_Responded, y=y_KPI_building_3060_Responded, marker_color=colorstackbarfail02),
                go.Bar(name='>60mins', x=x_KPI_building_60inf_Responded, y=y_KPI_building_60inf_Responded, marker_color=colorstackbarfail03)
            ])
            fig_responded_building.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolor,
                                                showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True,
                                                linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_building.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth, gridcolor=gridcolor,
                               showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_building.update_layout(barmode='stack', title='KPI Monitoring(Responded) vs Trade', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig_responded_building, use_container_width=True)

        with fig_responded_category, _lock:
            fig_responded_category = go.Figure(data=[
                go.Bar(name='0-10mins', x=x_KPI_category_010_Responded, y=y_KPI_category_010_Responded, marker_color=colorstackbarpass),
                go.Bar(name='10-30mins', x=x_KPI_category_1030_Responded, y=y_KPI_category_1030_Responded, marker_color=colorstackbarfail01),
                go.Bar(name='30-60mins', x=x_KPI_category_3060_Responded, y=y_KPI_category_3060_Responded, marker_color=colorstackbarfail02),
                go.Bar(name='>60mins', x=x_KPI_category_60inf_Responded, y=y_KPI_category_60inf_Responded, marker_color=colorstackbarfail03),
            ])
            fig_responded_category.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor,
                                                showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True,
                                                linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_category.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True,
                                                gridwidth=gridwidth, gridcolor=gridcolor, showline=True,
                                                linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_responded_category.update_layout(barmode='stack', title='KPI Monitoring(Responded) vs Trade Category',
                                                 plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig_responded_category, use_container_width=True)

        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_KPI_Recovered, unsafe_allow_html=True)
        st.markdown('##')
        st.markdown('Recovery Time refers to the time the fault or emergency was reported to the time the Contractor completed the work with evidence')
        st.markdown('##')

        x_KPI_building_010_recovered = df3.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['0-1hr'].index
        x_KPI_building_1030_recovered = df3.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['1-4hrs'].index
        x_KPI_building_3060_recovered = df3.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['4-8hrs'].index
        x_KPI_building_60inf_recovered = df3.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['8-np.inf'].index

        y_KPI_building_010_recovered = df3.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['0-1hr'].values
        y_KPI_building_1030_recovered = df3.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['1-4hrs'].values
        y_KPI_building_3060_recovered = df3.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['4-8hrs'].values
        y_KPI_building_60inf_recovered = df3.groupby(by='KPI_For_Recovered').Trade.value_counts().loc['8-np.inf'].values

        x_KPI_category_010_recovered = df3.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['0-1hr'].index
        x_KPI_category_1030_recovered = df3.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['1-4hrs'].index
        x_KPI_category_3060_recovered = df3.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['4-8hrs'].index
        x_KPI_category_60inf_recovered = df3.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['8-np.inf'].index

        y_KPI_category_010_recovered = df3.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['0-1hr'].values
        y_KPI_category_1030_recovered = df3.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['1-4hrs'].values
        y_KPI_category_3060_recovered = df3.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['4-8hrs'].values
        y_KPI_category_60inf_recovered = df3.groupby(by='KPI_For_Recovered').Trade_Category.value_counts().loc['8-np.inf'].values

        fig_recovered_building, fig_recovered_category = st.columns([1, 2])
        with fig_recovered_building, _lock:
            fig_recovered_building = go.Figure(data=[
                go.Bar(name='0-1hr', x=x_KPI_building_010_recovered, y=y_KPI_building_010_recovered, marker_color=colorstackbarpass),
                go.Bar(name='1-4hrs', x=x_KPI_building_1030_recovered, y=y_KPI_building_1030_recovered, marker_color=colorstackbarfail01),
                go.Bar(name='4-8hrs', x=x_KPI_building_3060_recovered, y=y_KPI_building_3060_recovered, marker_color=colorstackbarfail02),
                go.Bar(name='>8hrs', x=x_KPI_building_60inf_recovered, y=y_KPI_building_60inf_recovered, marker_color=colorstackbarfail03)
            ])
            fig_recovered_building.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolor,
                                                showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True,
                                                linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_building.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True,
                                                gridwidth=gridwidth, gridcolor=gridcolor, showline=True,
                                                linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_building.update_layout(barmode='stack', title='KPI Monitoring(Recovered) vs Trade', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig_recovered_building, use_container_width=True)

        with fig_recovered_category, _lock:
            fig_recovered_category = go.Figure(data=[
                go.Bar(name='0-1hr', x=x_KPI_category_010_recovered, y=y_KPI_category_010_recovered, marker_color=colorstackbarpass),
                go.Bar(name='1-4hrs', x=x_KPI_category_1030_recovered, y=y_KPI_category_1030_recovered, marker_color=colorstackbarfail01),
                go.Bar(name='4-8hrs', x=x_KPI_category_3060_recovered, y=y_KPI_category_3060_recovered, marker_color=colorstackbarfail02),
                go.Bar(name='>8hrs', x=x_KPI_category_60inf_recovered, y=y_KPI_category_60inf_recovered, marker_color=colorstackbarfail03)
            ])
            fig_recovered_category.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor,
                                                showgrid=False, gridwidth=gridwidth, gridcolor=gridcolor, showline=True,
                                                linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_category.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=True,
                                                gridwidth=gridwidth, gridcolor=gridcolor, showline=True,
                                                linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_recovered_category.update_layout(barmode='stack', title='KPI Monitoring(Recovered) vs Trade Category', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig_recovered_category, use_container_width=True)


        # ---------------------------Fault vs Trade & Trade Category & Type of Fault------------------------

        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_Tier1, unsafe_allow_html=True)
        st.markdown('##')

        df3['Time_Acknowledged_hrs'] = df3.Time_Acknowledged_mins/60
        df3['Time_Site_Reached_hrs'] = df3.Time_Site_Reached_mins/60
        df3['Time_Work_Started_hrs'] = df3.Time_Work_Started_mins/60
        df3['Time_Work_Recovered_hrs'] = df3.Time_Work_Recovered_mins/60

        df4 = df3.loc[:, ['Site', 'Building', 'Floor', 'Room', 'Trade', 'Trade_Category', 'Type_of_Fault', 'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 
                    'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']].copy()
        df4 = df4[['Site', 'Building', 'Floor', 'Room', 'Trade', 'Trade_Category', 'Type_of_Fault',
                   'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']]

        grouptrade_usecols = ['Trade', 'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']
        df5 = df4[grouptrade_usecols].groupby(by=['Trade']).agg(['count', 'max', 'min', 'mean', 'sum']).sort_values(
            ('Time_Acknowledged_hrs', 'count'), ascending=False)

        cols_name = ['Fault_Acknowledged_count', 'Fault_Acknowledged_max(hrs)', 'Fault_Acknowledged_min(hrs)',
                     'Fault_Acknowledged_mean(hrs)', 'Fault_Acknowledged_sum(hrs)', 'Fault_Site_Reached_count', 'Fault_Site_Reached_max(hrs)',
                     'Fault_Site_Reached_min(hrs)', 'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)', 'Fault_Work_Started_count',
                     'Fault_Work_Started_max(hrs)', 'Fault_Work_Started_min(hrs)', 'Fault_Work_Started_mean(hrs)', 'Fault_Work_Started_sum(hrs)',
                     'Fault_Recovered_count', 'Fault_Recovered_max(hrs)', 'Fault_Recovered_min(hrs)', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']
        df5.columns = cols_name
        df6 = df5.loc[:, ['Fault_Site_Reached_count', 'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)',
                          'Fault_Recovered_count', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']].copy()
        df6.reset_index(inplace=True)

        x = df6['Trade']
        y4 = df6.Fault_Recovered_count
        y5 = df6['Fault_Recovered_mean(hrs)']
        y6 = df6['Fault_Recovered_sum(hrs)']

        fig04, fig05, fig06 = st.columns(3)
        with fig04, _lock:
            fig04 = go.Figure(data=[go.Pie(values=y4, labels=x, hoverinfo='all', textinfo='label+percent+value',
                                           textfont_size=15, textfont_color='white', textposition='inside',
                                           showlegend=False, hole=.4)])
            fig04.update_layout(title='Proportions of Trade(Recovered)', annotations=[
                dict(text='Recovered', x=0.5, y=0.5, font_color='white', font_size=15, showarrow=False)])
            fig04.update_traces(marker=dict(colors=colorpierecoveredtier1))
            st.plotly_chart(fig04, use_container_width=True)

        with fig05, _lock:
            fig05 = go.Figure(data=[
                go.Bar(x=x, y=y5, orientation='v', text=y5, textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                       textposition='auto', textangle=-45, texttemplate='%{text:.2f}')])
            fig05.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolor, showgrid=False,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis,
                               linecolor=linecolor_xy_axis)
            fig05.update_yaxes(title_text='Mean Time Spent', title_font_color=titlefontcolor, showgrid=True,
                               gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig05.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor,
                                marker_line_width=markerlinewidth, opacity=opacity02)
            fig05.update_layout(title='Mean Time Spent to Recovered(hrs)', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig05, use_container_width=True)

        with fig06, _lock:
            fig06 = go.Figure(data=[go.Bar(x=x, y=y6, orientation='v', text=y6,
                                           textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                           textposition='auto', textangle=-45, texttemplate='%{text:.2f}')
                                    ])
            fig06.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolor, showgrid=False,
                               gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig06.update_yaxes(title_text='Total Time Spent', title_font_color=titlefontcolor, showgrid=True,
                               gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig06.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor,
                                marker_line_width=markerlinewidth, opacity=opacity03)
            fig06.update_layout(title='Total Time Spent to Recovered(hrs)', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig06, use_container_width=True)

        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_Tier2, unsafe_allow_html=True)
        st.markdown('##')

        groupcategory_usecols = ['Trade_Category', 'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']

        df7 = df4[groupcategory_usecols].groupby(by=['Trade_Category']).agg(['count', 'max', 'min', 'mean', 'sum']).sort_values(
            ('Time_Acknowledged_hrs', 'count'), ascending=False)
        cols_name01 = ['Fault_Acknowledged_count', 'Fault_Acknowledged_max(hrs)', 'Fault_Acknowledged_min(hrs)',
                       'Fault_Acknowledged_mean(hrs)','Fault_Acknowledged_sum(hrs)', 'Fault_Site_Reached_count', 'Fault_Site_Reached_max(hrs)',
                       'Fault_Site_Reached_min(hrs)', 'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)', 'Fault_Work_Started_count',
                       'Fault_Work_Started_max(hrs)', 'Fault_Work_Started_min(hrs)', 'Fault_Work_Started_mean(hrs)', 'Fault_Work_Started_sum(hrs)',
                       'Fault_Recovered_count', 'Fault_Recovered_max(hrs)', 'Fault_Recovered_min(hrs)', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']
        df7.columns = cols_name01
        df8 = df7.loc[:, ['Fault_Site_Reached_count', 'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)',
                          'Fault_Recovered_count', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']].copy()
        df8.reset_index(inplace=True)

        df_fig10 = df8.loc[:, ['Trade_Category', 'Fault_Recovered_count']].sort_values('Fault_Recovered_count', ascending=False).head(10)
        df_fig11 = df8.loc[:, ['Trade_Category', 'Fault_Recovered_mean(hrs)']].sort_values('Fault_Recovered_mean(hrs)', ascending=False).head(10)
        df_fig12 = df8.loc[:, ['Trade_Category', 'Fault_Recovered_sum(hrs)']].sort_values('Fault_Recovered_sum(hrs)', ascending=False).head(10)

        x_fig10 = df_fig10.Trade_Category
        y_fig10 = df_fig10['Fault_Recovered_count']
        x_fig11 = df_fig11.Trade_Category
        y_fig11 = df_fig11['Fault_Recovered_mean(hrs)']
        x_fig12 = df_fig12.Trade_Category
        y_fig12 = df_fig12['Fault_Recovered_sum(hrs)']

        fig10, fig11, fig12 = st.columns(3)
        with fig10, _lock:
            fig10 = go.Figure(data=[go.Bar(x=x_fig10, y=y_fig10, orientation='v', text=y_fig10,
                                           textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                           textposition='auto', textangle=-45)])
            fig10.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor, showgrid=False,
                               gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig10.update_yaxes(title_text='Count(Recovered)', title_font_color=titlefontcolor, showgrid=True,
                               gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig10.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor,
                                marker_line_width=markerlinewidth, opacity=opacity01)
            fig10.update_layout(title='Count(Recovered)-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig10, use_container_width=True)

        with fig11, _lock:
            fig11 = go.Figure(data=[go.Bar(x=x_fig11, y=y_fig11, orientation='v', text=y_fig11,
                                           textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                           textposition='auto', textangle=-45, texttemplate='%{text:.2f}')
                                    ])
            fig11.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor, showgrid=False,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig11.update_yaxes(title_text='Mean Time Spent', title_font_color=titlefontcolor, showgrid=True,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig11.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity02)
            fig11.update_layout(title='Mean Time Spent to Recovered(hrs)-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig11, use_container_width=True)

        with fig12, _lock:
            fig12 = go.Figure(data=[go.Bar(x=x_fig12, y=y_fig12, orientation='v', text=y_fig12,
                                           textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                           textposition='auto', textangle=-45, texttemplate='%{text:.2f}')
                                    ])
            fig12.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolor, showgrid=False,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig12.update_yaxes(title_text='Total Time Spent', title_font_color=titlefontcolor, showgrid=True,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig12.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity03)
            fig12.update_layout(title='Total Time Spent to Recovered(hrs)-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig12, use_container_width=True)

        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_Tier3, unsafe_allow_html=True)
        st.markdown('##')

        grouptypeoffault_usecols = ['Type_of_Fault', 'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']

        df9 = df4[grouptypeoffault_usecols].groupby(by=['Type_of_Fault']).agg(['count', 'max', 'min', 'mean', 'sum']).sort_values(('Time_Acknowledged_hrs', 'count'), ascending=False)
        cols_name02 = ['Fault_Acknowledged_count', 'Fault_Acknowledged_max(hrs)', 'Fault_Acknowledged_min(hrs)',
                       'Fault_Acknowledged_mean(hrs)', 'Fault_Acknowledged_sum(hrs)', 'Fault_Site_Reached_count', 'Fault_Site_Reached_max(hrs)',
                       'Fault_Site_Reached_min(hrs)', 'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)', 'Fault_Work_Started_count',
                       'Fault_Work_Started_max(hrs)', 'Fault_Work_Started_min(hrs)', 'Fault_Work_Started_mean(hrs)', 'Fault_Work_Started_sum(hrs)',
                       'Fault_Recovered_count', 'Fault_Recovered_max(hrs)', 'Fault_Recovered_min(hrs)', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']
        df9.columns = cols_name02
        df10 = df9.loc[:, ['Fault_Site_Reached_count', 'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)',
                           'Fault_Recovered_count', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']].copy()
        df10.reset_index(inplace=True)

        df_fig16 = df10.loc[:, ['Type_of_Fault', 'Fault_Recovered_count']].sort_values('Fault_Recovered_count', ascending=False).head(10)
        df_fig17 = df10.loc[:, ['Type_of_Fault', 'Fault_Recovered_mean(hrs)']].sort_values('Fault_Recovered_mean(hrs)', ascending=False).head(10)
        df_fig18 = df10.loc[:, ['Type_of_Fault', 'Fault_Recovered_sum(hrs)']].sort_values('Fault_Recovered_sum(hrs)', ascending=False).head(10)

        x_fig16 = df_fig16.Type_of_Fault
        y_fig16 = df_fig16['Fault_Recovered_count']
        x_fig17 = df_fig17.Type_of_Fault
        y_fig17 = df_fig17['Fault_Recovered_mean(hrs)']
        x_fig18 = df_fig18.Type_of_Fault
        y_fig18 = df_fig18['Fault_Recovered_sum(hrs)']

        fig16, fig17, fig18 = st.columns(3)
        with fig16, _lock:
            fig16 = go.Figure(data=[go.Bar(x=x_fig16, y=y_fig16, orientation='v', text=y_fig16,
                                           textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                           textposition='auto', textangle=-45)])
            fig16.update_xaxes(title_text="Type of Fault", tickangle=-45, title_font_color=titlefontcolor, showgrid=False,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig16.update_yaxes(title_text='Count(Recovered)', title_font_color=titlefontcolor, showgrid=True,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig16.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity01)
            fig16.update_layout(title='Count(Recovered)-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig16, use_container_width=True)

        with fig17, _lock:
            fig17 = go.Figure(data=[go.Bar(x=x_fig17, y=y_fig17, orientation='v', text=y_fig17,
                                           textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                           textposition='auto', textangle=-45, texttemplate='%{text:.2f}')])
            fig17.update_xaxes(title_text="Type of Fault", tickangle=-45, title_font_color=titlefontcolor, showgrid=False,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig17.update_yaxes(title_text='Mean Time Spent', title_font_color=titlefontcolor, showgrid=True,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig17.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity02)
            fig17.update_layout(title='Mean Time Spent to Recovered(hrs)-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig17, use_container_width=True)

        with fig18, _lock:
            fig18 = go.Figure(data=[go.Bar(x=x_fig18, y=y_fig18, orientation='v', text=y_fig18,
                                           textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                           textposition='auto', textangle=-45, texttemplate='%{text:.2f}')
                                    ])
            fig18.update_xaxes(title_text="Type of Fault", tickangle=-45, title_font_color=titlefontcolor, showgrid=False,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig18.update_yaxes(title_text='Total Time Spent', title_font_color=titlefontcolor, showgrid=True,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig18.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity03)
            fig18.update_layout(title='Total Time Spent to Recovered(hrs)-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig18, use_container_width=True)

     #-------------------------------------------Fault vs Location-------------------------------------------------

        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_location, unsafe_allow_html=True)
        st.markdown('##')

        ## groupby building

        groupbuilding_usecols = ['Building', 'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']

        df11 = df4[groupbuilding_usecols].groupby(by=['Building']).agg(['count', 'max', 'min', 'mean', 'sum'])
        cols_name_building = ['Fault_Acknowledged_count', 'Fault_Acknowledged_max(hrs)', 'Fault_Acknowledged_min(hrs)', 'Fault_Acknowledged_mean(hrs)',
                       'Fault_Acknowledged_sum(hrs)', 'Fault_Site_Reached_count', 'Fault_Site_Reached_max(hrs)', 'Fault_Site_Reached_min(hrs)',
                       'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)', 'Fault_Work_Started_count', 'Fault_Work_Started_max(hrs)',
                       'Fault_Work_Started_min(hrs)', 'Fault_Work_Started_mean(hrs)', 'Fault_Work_Started_sum(hrs)', 'Fault_Recovered_count',
                       'Fault_Recovered_max(hrs)', 'Fault_Recovered_min(hrs)', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']
        df11.columns = cols_name_building
        df12 = df11.loc[:, ['Fault_Recovered_count', 'Fault_Recovered_sum(hrs)']]

        x_fig19 = df12['Fault_Recovered_count'].sort_values().index
        y_fig19 = df12['Fault_Recovered_count'].sort_values().values

        x_fig20 = df12['Fault_Recovered_sum(hrs)'].sort_values().index
        y_fig20 = df12['Fault_Recovered_sum(hrs)'].sort_values().values


        fig19, fig20 = st.columns(2)
        with fig19, _lock:
            fig19 = go.Figure(data=[go.Bar(x=y_fig19, y=x_fig19, orientation='h', text=y_fig19,
                                 textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                 textposition='auto', textangle=0)
                                    ])
            fig19.update_xaxes(title_text="Number of Fault", title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig19.update_yaxes(title_text='Building', title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickmode='linear')
            fig19.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity02)
            fig19.update_layout(title='Number of Fault vs Building', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig19, use_container_width=True)

        with fig20, _lock:
            fig20 = go.Figure(data=[go.Bar(x=y_fig20, y=x_fig20, orientation='h', text=y_fig20,
                                   textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                   textposition='auto', textangle=0, texttemplate='%{text:.2f}')
                                    ])
            fig20.update_xaxes(title_text="Total Time Spent", title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig20.update_yaxes(title_text='Building', title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickmode='linear')
            fig20.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity03)
            fig20.update_layout(title='Total Time Spent(hrs) vs Building', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig20, use_container_width=True)

    ## groupby building floor
        df4['buildingfloor'] = df4.Building + '-' + df4.Floor

        groupbuildingfloor_usecols = ['buildingfloor', 'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']
        
        df13 = df4[groupbuildingfloor_usecols].groupby(by=['buildingfloor']).agg(['count', 'max', 'min', 'mean', 'sum'])
        cols_name_buildingfloor = ['Fault_Acknowledged_count', 'Fault_Acknowledged_max(hrs)', 'Fault_Acknowledged_min(hrs)', 'Fault_Acknowledged_mean(hrs)',
                       'Fault_Acknowledged_sum(hrs)', 'Fault_Site_Reached_count', 'Fault_Site_Reached_max(hrs)', 'Fault_Site_Reached_min(hrs)',
                       'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)', 'Fault_Work_Started_count', 'Fault_Work_Started_max(hrs)',
                       'Fault_Work_Started_min(hrs)', 'Fault_Work_Started_mean(hrs)', 'Fault_Work_Started_sum(hrs)', 'Fault_Recovered_count',
                       'Fault_Recovered_max(hrs)', 'Fault_Recovered_min(hrs)', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']
        df13.columns = cols_name_buildingfloor
        df14 = df13.loc[:, ['Fault_Recovered_count', 'Fault_Recovered_sum(hrs)']].sort_values(by=['Fault_Recovered_count'], ascending=False).head(10)
        df15 = df13.loc[:, ['Fault_Recovered_count', 'Fault_Recovered_sum(hrs)']].sort_values(by=['Fault_Recovered_sum(hrs)'], ascending=False).head(10)

        x_fig21 = df14['Fault_Recovered_count'].sort_values().index
        y_fig21 = df14['Fault_Recovered_count'].sort_values().values

        x_fig22 = df15['Fault_Recovered_sum(hrs)'].sort_values().index
        y_fig22 = df15['Fault_Recovered_sum(hrs)'].sort_values().values


        fig21, fig22 = st.columns(2)
        with fig21, _lock:
            fig21 = go.Figure(data=[go.Bar(x=y_fig21, y=x_fig21, orientation='h', text=y_fig21,
                                 textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                 textposition='auto', textangle=0)
                                    ])
            fig21.update_xaxes(title_text="Number of Fault", title_font_color=titlefontcolor, showgrid=True,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig21.update_yaxes(title_text='Floor', title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickmode='linear')
            fig21.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity02)
            fig21.update_layout(title='Number of Fault vs Building& Floor-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig21, use_container_width=True)

        with fig22, _lock:
            fig22 = go.Figure(data=[go.Bar(x=y_fig22, y=x_fig22, orientation='h', text=y_fig22,
                                   textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                   textposition='auto', textangle=0, texttemplate='%{text:.2f}')
                                    ])
            fig22.update_xaxes(title_text="Total Time Spent", title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig22.update_yaxes(title_text='Floor', title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickmode='linear')
            fig22.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity03)
            fig22.update_layout(title='Total Time Spent(hrs) vs Building& Floor-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig22, use_container_width=True)


    ## groupby building floor room
        df4['buildingfloorroom'] = df4.Building + '-' + df4.Floor + '-' + df4.Room

        groupbuildingfloorroom_usecols = ['buildingfloorroom', 'Time_Acknowledged_hrs', 'Time_Site_Reached_hrs', 'Time_Work_Started_hrs', 'Time_Work_Recovered_hrs']

        df16 = df4[groupbuildingfloorroom_usecols].groupby(by=['buildingfloorroom']).agg(['count', 'max', 'min', 'mean', 'sum'])
        cols_name_buildingfloorroom = ['Fault_Acknowledged_count', 'Fault_Acknowledged_max(hrs)', 'Fault_Acknowledged_min(hrs)', 'Fault_Acknowledged_mean(hrs)',
                       'Fault_Acknowledged_sum(hrs)', 'Fault_Site_Reached_count', 'Fault_Site_Reached_max(hrs)', 'Fault_Site_Reached_min(hrs)',
                       'Fault_Site_Reached_mean(hrs)', 'Fault_Site_Reached_sum(hrs)', 'Fault_Work_Started_count', 'Fault_Work_Started_max(hrs)',
                       'Fault_Work_Started_min(hrs)', 'Fault_Work_Started_mean(hrs)', 'Fault_Work_Started_sum(hrs)', 'Fault_Recovered_count',
                       'Fault_Recovered_max(hrs)', 'Fault_Recovered_min(hrs)', 'Fault_Recovered_mean(hrs)', 'Fault_Recovered_sum(hrs)']
        df16.columns = cols_name_buildingfloorroom

        df17 = df16.loc[:, ['Fault_Recovered_count', 'Fault_Recovered_sum(hrs)']].sort_values('Fault_Recovered_count', ascending=False).head(10)
        df18 = df16.loc[:, ['Fault_Recovered_count', 'Fault_Recovered_sum(hrs)']].sort_values('Fault_Recovered_sum(hrs)',ascending=False).head(10)

        x_fig23 = df17['Fault_Recovered_count'].sort_values().index
        y_fig23 = df17['Fault_Recovered_count'].sort_values().values

        x_fig24 = df18['Fault_Recovered_sum(hrs)'].sort_values().index
        y_fig24 = df18['Fault_Recovered_sum(hrs)'].sort_values().values


        fig23, fig24 = st.columns(2)
        with fig23, _lock:
            fig23 = go.Figure(data=[go.Bar(x=y_fig23, y=x_fig23, orientation='h', text=y_fig23,
                                 textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                 textposition='auto', textangle=0)
                                    ])
            fig23.update_xaxes(title_text="Number of Fault", title_font_color=titlefontcolor, showgrid=True,
                               gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig23.update_yaxes(title_text='Room', title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickmode='linear')
            fig23.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity02)
            fig23.update_layout(title='Number of Fault vs Building Floor& Room-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig23, use_container_width=True)

        with fig24, _lock:
            fig24 = go.Figure(data=[go.Bar(x=y_fig24, y=x_fig24, orientation='h', text=y_fig24,
                                   textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                   textposition='auto', textangle=0, texttemplate='%{text:.1f}')
                                    ])
            fig24.update_xaxes(title_text="Total Time Spent", title_font_color=titlefontcolor, showgrid=True, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig24.update_yaxes(title_text='Room', title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                               gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickmode='linear')
            fig24.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity03)
            fig24.update_layout(title='Total Time Spent(hrs) vs Building Floor& Room-Top 10', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig24, use_container_width=True)

#------------------------------------Number of fault vs people & wordcloud--------------------------------------
        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_fault_Technician, unsafe_allow_html=True)
        st.markdown('##')

        x_faultpeople = df3.Attended_By.value_counts().index
        y_faultpeople = df3.Attended_By.value_counts().values

        # y_faultpeople_sum = sum(y_faultpeople)
        # st.markdown(f"Total Fault = {y_faultpeople_sum}")

        fig_faultpeople, wc = st.columns(2)

        with fig_faultpeople, _lock:
            fig_faultpeople = go.Figure(data=[go.Bar(x=x_faultpeople, y=y_faultpeople, orientation='v', text=y_faultpeople,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45)])
            fig_faultpeople.update_xaxes(title_text="Name", title_font_color=titlefontcolor, showgrid=False, gridwidth=gridwidth,
                                gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis, tickangle=-45)
            fig_faultpeople.update_yaxes(title_text='Number of Fault', title_font_color=titlefontcolor, showgrid=False,
                                gridwidth=gridwidth, gridcolor=gridcolor, showline=True, linewidth=linewidth_xy_axis, linecolor=linecolor_xy_axis)
            fig_faultpeople.update_traces(marker_color=markercolor, marker_line_color=markerlinecolor, marker_line_width=markerlinewidth, opacity=opacity03)
            fig_faultpeople.update_layout(title='Number of Fault vs Name', plot_bgcolor=plot_bgcolor)
            st.plotly_chart(fig_faultpeople, use_container_width=True)

        with wc, _lock:
            st.markdown('**Actions Taken**')
            stopwords = ['done', 'Done', 'Found', 'found', 'from', 'have', 'nan' 'Nan', 'NAN',
                         'in', 'on', 'at', 'make', 'it', 'the', 'and', 'to', 'for', 'need', 'NORMAL', 'normal', 'not', 'of', 'with', 
                         'No', 'NO', 'no', 'site', 'Site', 'up', 'now', 'Now']
            wc = WordCloud(background_color='#0e1117', stopwords= stopwords, colormap='Set2', width = 1920, height = 1200).generate(str(df2['Action(s)_Taken'].values))
            st.image(wc.to_array(), width=650)



    # --------------------------------------Schedule----------------------------------------------------------------------
    if page =='Schedules':
        def fetch_file_schedules(filename):
            cols = ['Schedule ID', 'Trade', 'Trade Category', 'Strategic Partner',
               'Frequency', 'Description', 'Type', 'Scope', 'Site', 'Building',
               'Floor', 'Room', 'Start Date',
               'End Date', 'Work Started Date', 'Work Completed Date',
               'Attended By', 'Portal ID', 'Service Report Completed Date',
               'Total Number of Service Reports',
               'Total Number of Quantity in Service Reports', 'Asset Tag Number',
               'Alert Case']
            parse_dates = ['Start Date', 'End Date', 'Work Started Date', 'Work Completed Date',
                           'Service Report Completed Date']
            dtype_cols = {'Site': 'str', 'Building': 'str', 'Floor': 'str', 'Room': 'str'}
            return pd.read_excel(filename, header=0, index_col='Schedule ID', usecols=cols, parse_dates=parse_dates, dtype=dtype_cols)

        dfs = fetch_file_schedules('schedules_GBB_s.xlsx')
        dfs.columns = dfs.columns.str.replace(' ', '_')
        dfs['Time_Work_Completed_hrs'] = (dfs.Work_Completed_Date - dfs.Work_Started_Date) / pd.Timedelta(hours=1)

    # ----------------------------------------Sidebar---------------------------------------------------------------------
        st.sidebar.header('Please Filter Here:')

        Trade = st.sidebar.multiselect(
            'Select the Trade:',
            options=dfs['Trade'].unique(),
            default=dfs['Trade'].unique()
        )

        Trade_Category = st.sidebar.multiselect(
            'Select the Trade Category:',
            options=dfs['Trade_Category'].unique(),
            default=dfs['Trade_Category'].unique()
        )

        dfs = dfs.query(
            'Trade ==@Trade & Trade_Category==@Trade_Category'
        )
     # ----------------------------------------Main page-----------------------------------------------------------
        html_card_title_schedules="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; padding-top: 5px; width: 800px;
           height: 50px;">
            <h1 class="card-title" style=color:#4c9085; font-family:Georgia; text-align: left; padding: 0px 0;">SCHEDULES DASHBOARD</h1>
          </div>
        </div>
        """
        st.markdown(html_card_title_schedules, unsafe_allow_html=True)
        st.markdown('##')
        st.markdown('##')

        total_schedule = dfs.shape[0]
        schedule_outstanding = dfs[dfs['Work_Completed_Date'].isna()].shape[0]
        schedule_completed = dfs[dfs['Work_Completed_Date'].notna()].shape[0]
        total_SR = dfs.Total_Number_of_Service_Reports.sum()
        # total_asset =
        alert_case = int(dfs['Alert_Case'].sum())

        column01_schedule, column02_schedule, column03_schedule, column04_schedule, column05_schedule = st.columns(5)
        with column01_schedule, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #4c9085;'>Total</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #4c9085;'>{total_schedule}</h2>", unsafe_allow_html=True)

        with column02_schedule, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #4c9085;'>Outstanding</h6>",unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #4c9085;'>{schedule_outstanding}</h2>", unsafe_allow_html=True)

        with column03_schedule, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #4c9085;'>Completed</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #4c9085;'>{schedule_completed}</h2>", unsafe_allow_html=True)

        with column04_schedule, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #4c9085;'>Alert</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: red;'>{alert_case}</h2>", unsafe_allow_html=True)

        with column05_schedule, _lock:
            st.markdown(f"<h6 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:bottom; color: #4c9085;'>No.of SR</h6>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='background-color:#0e1117; width:120px; height:20px; text-align: left; vertical-align:top; color: #4c9085;'>{total_SR}</h2>", unsafe_allow_html=True)

        html_card_subheader_outstanding_schedules="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #4c9085; padding-top: 5px; width: 350px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#4c9085; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Outstanding Schedules</h3>
          </div>
        </div>
        """
        html_card_subheader_daily_schedules="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #4c9085; padding-top: 5px; width: 350px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#4c9085; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Daily Schedule Cases</h3>
          </div>
        </div>
        """
        html_card_subheader_schedules_Tier1="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #4c9085; padding-top: 5px; width: 500px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#4c9085; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Completed Schedules vs Trade</h3>
          </div>
        </div>
        """
        html_card_subheader_schedules_Tier2="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #4c9085; padding-top: 5px; width: 600px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#4c9085; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Completed Schedules vs Trade Category</h3>
          </div>
        </div>
        """
        html_card_subheader_schedules_Technician="""
        <div class="card">
          <div class="card-body" style="border-radius: 10px 10px 0px 0px; background: #4c9085; padding-top: 5px; width: 650px;
           height: 50px;">
            <h3 class="card-title" style="background-color:#4c9085; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">No.of Completed Schedules vs Technician</h3>
          </div>
        </div>
        """
#--------------------------------------- color & width & opacity----------------------------------------------
        # Pie chart
        colorpieoutstandings = ['#4c9085', '#1dacd6', '#50a747', '#59656d', '#06c2ac', '#137e6d', '#929906', '#ff9408']
        colorpierecoveredstier1 = ['#4c9085', '#1dacd65', '#50a747', '#59656d', '#06c2ac', '#137e6d', '#929906', '#ff9408']

        # all barchart and linechart
        titlefontcolors = '#4c9085'
        gridwidths = 0.1
        gridcolors = '#1f3b4d'
        plot_bgcolors = 'rgba(0,0,0,0)'

        # x&y axis width and color
        linewidths_xy_axis = 1
        linecolors_xy_axis = '#59656d'

        # all barchart
        markercolors = '#4c9085'
        markerlinecolors = '#4c9085'
        markerlinewidths = 1

        #linechart
        linecolors = '#4c9085'
        linewidths = 2
#------------------------------------------ Outstanding Schedules-------------------------------------------------
        st.markdown('##')
        st.markdown('##')
        st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """,
                    unsafe_allow_html=True)
        st.markdown(html_card_subheader_outstanding_schedules, unsafe_allow_html=True)
        st.markdown('##')

        dfs_outstanding = dfs[dfs['Work_Completed_Date'].isna()]

        props = 'font-style: italic; color: #ffffff; font-size:0.8em; font-weight:normal;'  #border: 0.0001px solid #116a8c; background: #116a8c'
        dfs_outstandingdataframe = dfs_outstanding.style.applymap(lambda x: props)
        st.dataframe(dfs_outstandingdataframe, 2000, 200)
        # sers_outstanding_building = dfs_outstanding.groupby(['Trade'])['Trade_Category'].count().sort_values(ascending=False)
        # sers_outstanding_category = dfs_outstanding.groupby(['Trade_Category'])['Trade'].count().sort_values(ascending=False)

        # xs_outstanding_building = sers_outstanding_building.index
        # ys_outstanding_building = sers_outstanding_building.values
        # xs_outstanding_category = sers_outstanding_category.index
        # ys_outstanding_category = sers_outstanding_category.values

        # figs_outstanding_building, figs_outstanding_category = st.columns([1, 2])

        # with figs_outstanding_building, _lock:
        #     figs_outstanding_building = go.Figure(data=[go.Pie(labels=xs_outstanding_building, values=ys_outstanding_building, hoverinfo='all', textinfo='label+percent+value',
        #                                                        textfont_size=15, textfont_color='white', textposition='inside', showlegend=False, hole=.4)])
        #     figs_outstanding_building.update_layout(title='Number of Schedule vs Trade', annotations=[dict(text='Outstanding', x=0.5, y=0.5, font_size=15, font_color='white', showarrow=False)])
        #     figs_outstanding_building.update_traces(marker=dict(colors=colorpieoutstandings))
        #     st.plotly_chart(figs_outstanding_building, use_container_width=True)

        # with figs_outstanding_category, _lock:
        #     figs_outstanding_category = go.Figure(data=[go.Bar(x=xs_outstanding_category, y=ys_outstanding_category, orientation='v',
        #                                                        text=ys_outstanding_category,textfont=dict(family='sana serif', size=14, color='#c4fff7'),
        #                                                        textposition='auto', textangle=-45)
        #                                                 ])
        #     figs_outstanding_category.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolors, showgrid=False, gridwidth=gridwidths,
        #                        gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
        #     figs_outstanding_category.update_yaxes(title_text='Number of Schedule', title_font_color=titlefontcolors, showgrid=True, gridwidth=gridwidths,
        #                        gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
        #     figs_outstanding_category.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
        #     figs_outstanding_category.update_layout(title='Number of Schedule vs Trade Category', plot_bgcolor=plot_bgcolors)
        #     st.plotly_chart(figs_outstanding_category, use_container_width=True)

# ------------------------------------------ Daily Schedules-------------------------------------------------
        st.markdown("""<hr style="height:5px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
        st.markdown(html_card_subheader_daily_schedules, unsafe_allow_html=True)
        st.markdown('##')

        dfs_completed = dfs[dfs['Work_Completed_Date'].notna()].loc[:, ['Trade', 'Trade_Category', 'Work_Started_Date', 'Time_Work_Completed_hrs', 'Attended_By']]

        xs_daily = dfs_completed['Work_Started_Date'].dt.day.value_counts().sort_index().index
        ys_daily = dfs_completed['Work_Started_Date'].dt.day.value_counts().sort_index().values
        ys_mean = dfs_completed['Work_Started_Date'].dt.day.value_counts().sort_index().mean()

        day_max_s = dfs_completed.Work_Started_Date.dt.day.max()

        figs_daily = go.Figure(data=go.Scatter(x=xs_daily, y=ys_daily, mode='lines+markers+text', line=dict(color=linecolors, width=linewidths),
                                text=ys_daily, textfont=dict(family='sana serif', size=14, color='#c4fff7'), textposition='top center'))
        figs_daily.add_hline(y=ys_mean, line_dash='dot', line_color='#96ae8d', line_width=2, annotation_text='Average Line',
                                annotation_position='bottom right', annotation_font_size=18, annotation_font_color='green')
        figs_daily.update_xaxes(title_text='Date', tickangle=-45, title_font_color=titlefontcolors, tickmode='linear',
                                   range=[1, day_max_s], showgrid=False, gridwidth=gridwidths, gridcolor=gridcolors,
                                showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
        figs_daily.update_yaxes(title_text='Number of Schedule', title_font_color=titlefontcolors, tickmode='linear', showgrid=False,
                                gridwidth=gridwidths, gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
        figs_daily.update_layout(title='Number of Schedule vs Date', plot_bgcolor=plot_bgcolors,
                                 # xaxis=dict(showticklabels=True, ticks='outside', tickfont=dict(family='Arial', size=12, color='rgb(82, 82, 82)')),
                                 # yaxis=dict(showticklabels=True, ticks='outside', tickfont=dict(family='Arial', size=12, color='rgb(82, 82, 82)'))
                                 )
        st.plotly_chart(figs_daily, use_container_width=True)

# ------------------------------------------ Schedules Tier1 & Tier2-------------------------------------------------
        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_schedules_Tier1, unsafe_allow_html=True)
        st.markdown('##')

        groupscheduletrade_usecols = ['Trade', 'Time_Work_Completed_hrs']

        dfs1 = dfs_completed[groupscheduletrade_usecols].groupby(by=['Trade']).agg(['count', 'max', 'min', 'mean', 'sum']).sort_values(('Time_Work_Completed_hrs', 'count'), ascending=False)
        col_name_s1 = ['Schedule_Completed_count', 'Time_Schedule_Completed_max(hrs)', 'Time_Schedule_Completed_min(hrs)',
                       'Time_Schedule_Completed_mean(hrs)', 'Time_Schedule_Completed_sum(hrs)']
        dfs1.columns = col_name_s1

        dfs1.reset_index(inplace=True)

        xs1 = dfs1['Trade']
        ys1 = dfs1['Schedule_Completed_count']
        ys2 = dfs1['Time_Schedule_Completed_mean(hrs)']
        ys3 = dfs1['Time_Schedule_Completed_sum(hrs)']

        figs01, figs02, figs03 = st.columns(3)
        with figs01, _lock:
            figs01 = go.Figure(data=[go.Pie(values=ys1, labels=xs1, hoverinfo='all', textinfo='label+percent+value', textfont_size=15, textfont_color='white', textposition='inside', showlegend=False, hole=.4)])
            figs01.update_layout(title='Proportions of Trade', annotations=[dict(text='Completed', x=0.5, y=0.5, font_size=15, font_color='white', showarrow=False)])
            figs01.update_traces(marker=dict(colors=colorpierecoveredstier1))
            st.plotly_chart(figs01, use_container_width=True)

        with figs02, _lock:
            figs02 = go.Figure(data=[go.Bar(x=xs1, y=ys2, orientation='v', text=ys2,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45, texttemplate='%{text:.2f}')
                                     ])
            figs02.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolors, showgrid=False, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs02.update_yaxes(title_text='Mean Time Spent(hrs)', title_font_color=titlefontcolors, showgrid=True, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs02.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
            figs02.update_layout(title='Mean Time Spent to Complete(hrs)', plot_bgcolor=plot_bgcolors)
            st.plotly_chart(figs02, use_container_width=True)

        with figs03, _lock:
            figs03 = go.Figure(data=[go.Bar(x=xs1, y=ys3, orientation='v', text=ys3,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45, texttemplate='%{text:.2f}')
                                     ])
            figs03.update_xaxes(title_text="Trade", tickangle=-45, title_font_color=titlefontcolors, showgrid=False, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs03.update_yaxes(title_text='Total Time Spent(hrs)', title_font_color=titlefontcolors, showgrid=True, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs03.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
            figs03.update_layout(title='Total Time Spent to Complete(hrs)', plot_bgcolor=plot_bgcolors)
            st.plotly_chart(figs03, use_container_width=True)

        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_schedules_Tier2, unsafe_allow_html=True)
        st.markdown('##')

        groupschedulecategory_usecols = ['Trade_Category', 'Time_Work_Completed_hrs']

        dfs2 = dfs_completed[groupschedulecategory_usecols].groupby(by=['Trade_Category']).agg(['count', 'max', 'min', 'mean', 'sum'])
        col_name_s2 = ['Schedule_Completed_count', 'Time_Schedule_Completed_max(hrs)', 'Time_Schedule_Completed_min(hrs)', 'Time_Schedule_Completed_mean(hrs)', 'Time_Schedule_Completed_sum(hrs)']
        dfs2.columns = col_name_s2
        dfs2.reset_index(inplace=True)

        dfs_fig04 = dfs2.loc[:, ['Trade_Category', 'Schedule_Completed_count']].sort_values('Schedule_Completed_count', ascending=False).head(10)
        dfs_fig05 = dfs2.loc[:, ['Trade_Category', 'Time_Schedule_Completed_mean(hrs)']].sort_values('Time_Schedule_Completed_mean(hrs)', ascending=False).head(10)
        dfs_fig06 = dfs2.loc[:, ['Trade_Category', 'Time_Schedule_Completed_sum(hrs)']].sort_values('Time_Schedule_Completed_sum(hrs)', ascending=False).head(10)

        xs_fig04 = dfs_fig04['Trade_Category']
        ys_fig04 = dfs_fig04['Schedule_Completed_count']

        xs_fig05 = dfs_fig05['Trade_Category']
        ys_fig05 = dfs_fig05['Time_Schedule_Completed_mean(hrs)']

        xs_fig06 = dfs_fig06['Trade_Category']
        ys_fig06 = dfs_fig06['Time_Schedule_Completed_sum(hrs)']

        figs04, figs05, figs06 = st.columns(3)
        with figs04, _lock:
            figs04 = go.Figure(data=[go.Bar(x=xs_fig04, y=ys_fig04, orientation='v', text=ys_fig04,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45)
                                     ])
            figs04.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolors, showgrid=False,
                                gridwidth=gridwidths, gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs04.update_yaxes(title_text='Count', title_font_color=titlefontcolors, showgrid=True, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs04.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
            figs04.update_layout(title='Count-Top 10', plot_bgcolor=plot_bgcolors)
            st.plotly_chart(figs04, use_container_width=True)

        with figs05, _lock:
            figs05 = go.Figure(data=[go.Bar(x=xs_fig05, y=ys_fig05, orientation='v', text=ys_fig05,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45, texttemplate='%{text:.2f}')
                                     ])
            figs05.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolors, showgrid=False, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs05.update_yaxes(title_text='Mean Time Spent(hrs)', title_font_color=titlefontcolors, showgrid=True, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs05.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
            figs05.update_layout(title='Mean Time Spent to Complete(hrs)-Top 10', plot_bgcolor=plot_bgcolors)
            st.plotly_chart(figs05, use_container_width=True)

        with figs06, _lock:
            figs06 = go.Figure(data=[go.Bar(x=xs_fig06, y=ys_fig06, orientation='v', text=ys_fig06,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45, texttemplate='%{text:.2f}')
                                     ])
            figs06.update_xaxes(title_text="Trade Category", tickangle=-45, title_font_color=titlefontcolors, showgrid=False, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs06.update_yaxes(title_text='Total Time Spent(hrs)', title_font_color=titlefontcolors, showgrid=True, gridwidth=gridwidths,
                               gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            figs06.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
            figs06.update_layout(title='Total Time Spent to Complete(hrs)-Top 10', plot_bgcolor=plot_bgcolors)
            st.plotly_chart(figs06, use_container_width=True)


#------------------------------------Number of schedule vs people --------------------------------------
        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_schedules_Technician, unsafe_allow_html=True)
        st.markdown('##')

        x_schedulepeople = dfs_completed.Attended_By.value_counts().index
        y_schedulepeople = dfs_completed.Attended_By.value_counts().values

        # y_faultpeople_sum = sum(y_faultpeople)
        # st.markdown(f"Total Fault = {y_faultpeople_sum}")

        fig_schedulepeople, fig_empty = st.columns(2)

        with fig_schedulepeople, _lock:
            fig_schedulepeople = go.Figure(data=[go.Bar(x=x_schedulepeople, y=y_schedulepeople, orientation='v', text=y_schedulepeople,
                                            textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                            textposition='auto', textangle=-45)])
            fig_schedulepeople.update_xaxes(title_text="Name", title_font_color=titlefontcolors, showgrid=False, gridwidth=gridwidths,
                                gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis, tickangle=-45)
            fig_schedulepeople.update_yaxes(title_text='Number of Schedule', title_font_color=titlefontcolors, showgrid=False,
                                gridwidth=gridwidths, gridcolor=gridcolors, showline=True, linewidth=linewidths_xy_axis, linecolor=linecolors_xy_axis)
            fig_schedulepeople.update_traces(marker_color=markercolors, marker_line_color=markerlinecolors, marker_line_width=markerlinewidths)
            fig_schedulepeople.update_layout(title='Number of Schedule vs Name', plot_bgcolor=plot_bgcolors)
            st.plotly_chart(fig_schedulepeople, use_container_width=True)
        
        with fig_empty, _lock:
            st.empty()






# =======================================================================================Inventories=========================================================================================
    if page =='Inventories':

        html_card_title_inventories="""
            <div class="card">
              <div class="card-body" style="border-radius: 10px 10px 0px 0px; padding-top: 5px; width: 800px;
               height: 50px;">
                <h1 class="card-title" style=color:#ff4f00; font-family:Georgia; text-align: left; padding: 0px 0;">INVENTORIES MOVEMENT</h1>
              </div>
            </div>
            """

        html_card_subheader_inventoriesEC11 = """
            <div class="card">
              <div class="card-body" style="border-radius: 10px 10px 0px 0px; background:#ff4f00; padding-top: 5px; width: 600px;
               height: 50px;">
                <h3 class="card-title" style="background-color:#ff4f00; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Inventory Movement Morning-EC11</h3>
              </div>
            </div>
            """

        html_card_subheader_inventoriesEC18 = """
            <div class="card">
              <div class="card-body" style="border-radius: 10px 10px 0px 0px; background:#ff4f00; padding-top: 5px; width: 600px;
               height: 50px;">
                <h3 class="card-title" style="background-color:#ff4f00; color:#eabd1d; font-family:Georgia; text-align: center; padding: 0px 0;">Inventory Movement Morning-EC18</h3>
              </div>
            </div>
            """

        st.markdown(html_card_title_inventories, unsafe_allow_html=True)
        st.markdown('##')
        st.markdown('##')
        st.markdown(html_card_subheader_inventoriesEC11, unsafe_allow_html=True)
        st.markdown('##')

        trans_cols =['Description', 'Category', 'Subcategory', 'Ref. ID', 'Reference Location', 'Type', 'Quantity', 'Request to draw or add',
               'Reference number', 'Created by', 'Created date']
        date=['Created date']

        df_EC11_t = pd.read_excel('Transaction_EC11.xlsx', header=1, usecols=trans_cols, parse_dates=date)
        df_EC11_t['Created day'] = df_EC11_t['Created date'].dt.day
        df_EC11_t['Reference number'] = df_EC11_t['Reference number'].astype(str)
        df_EC11_t['Ref. ID'] = df_EC11_t['Ref. ID'].astype(str)

        df_EC11_t_draw = df_EC11_t[df_EC11_t['Type'] == 'Withdraw']
        ser_EC11_daily_draw = df_EC11_t_draw.groupby(by=['Created day'])['Request to draw or add'].sum()
        ser_EC11_fast_draw = df_EC11_t_draw.groupby(by=['Description'])['Request to draw or add'].sum().sort_values(ascending=False).head(10)

        inventorylist = ser_EC11_fast_draw.sort_values(ascending=True).index

        df_EC11_fast_drawinfo = df_EC11_t_draw.loc[(df_EC11_t_draw['Description'].isin(inventorylist)), ['Description', 'Request to draw or add', 
                                 'Reference Location', 'Reference number', 'Ref. ID', 'Created by', 'Created date']].sort_values(by=['Request to draw or add', 'Description'], ascending=False)

        balance_cols = ['Description', 'Category', 'Subcategory', 'Ref. ID', 'Expired Date', 'Quantity', 'Location']
        df_EC11_balance = pd.read_excel('Inventories_EC11.xlsx', header=1, usecols=balance_cols)

        total_inventory_balanceEC11 = df_EC11_balance['Quantity'].sum()
        total_inventory_drawedEC11 = df_EC11_t[df_EC11_t.Type=='Withdraw']['Request to draw or add'].sum()
        total_replenishmentEC11 = df_EC11_t[df_EC11_t.Type=='Add Quantity']['Request to draw or add'].sum()
        total_transaction = df_EC11_t['Description'].count()

        column01_inventory, column02_inventory, column03_inventory, column04_inventory= st.columns(4)

        with column01_inventory, _lock:
            st.markdown('**Balance**')
            st.markdown(f"<h2 style='text-align: left; color: #703bef;'>{total_inventory_balanceEC11}</h2>", unsafe_allow_html=True)
        with column02_inventory, _lock:
            st.markdown('**Requested**')
            st.markdown(f"<h2 style='text-align: left; color: #3c9992;'>{total_inventory_drawedEC11}</h2>", unsafe_allow_html=True)
        with column03_inventory, _lock:
            st.markdown('**Replenishment**')
            st.markdown(f"<h2 style='text-align: left; color: #d0c101;'>{total_replenishmentEC11}</h2>", unsafe_allow_html=True)
        with column04_inventory, _lock:
            st.markdown('**Transaction**')
            st.markdown(f"<h2 style='text-align: left; color: #d0c101;'>{total_transaction}</h2>", unsafe_allow_html=True)

        # xinventories_daily = ser_EC11_daily_draw.index
        # yinventories_daily = ser_EC11_daily_draw.values
        # yinventories_mean = ser_EC11_daily_draw.values.mean()

        # figinventories_daily = go.Figure(data=go.Scatter(x=xinventories_daily, y=yinventories_daily, mode='lines+markers+text', line=dict(color='#13bbaf', width=3),
        #                         text=yinventories_daily, textfont=dict(family='sana serif', size=14, color='#c4fff7'), textposition='top center'))
        # figinventories_daily.add_hline(y=yinventories_mean, line_dash='dot', line_color='#96ae8d', line_width=2, annotation_text='Average Line',
        #                         annotation_position='bottom right', annotation_font_size=18, annotation_font_color='green')
        # figinventories_daily.update_xaxes(title_text='Date', tickangle=-45, title_font_color='#74a662', tickmode='linear',
        #                             range=[1, 31], showgrid=False, showline=True, linewidth=1, linecolor='#59656d')
        # figinventories_daily.update_yaxes(title_text='Number of Inventory', title_font_color='#74a662', showgrid=False,
        #                             gridwidth=0.1, gridcolor='#1f3b4d', showline=True, linewidth=1, linecolor='#59656d')
        # figinventories_daily.update_layout(title='Daily Movement', plot_bgcolor='rgba(0, 0, 0, 0)',
        #                             # xaxis=dict(showticklabels=True, ticks='outside', tickfont=dict(family='Arial', size=12, color='rgb(82, 82, 82)')),
        #                             # yaxis=dict(showticklabels=True, ticks='outside', tickfont=dict(family='Arial', size=12, color='rgb(82, 82, 82)'))
        #                             )
        # st.plotly_chart(figinventories_daily, use_container_width=True)



        xinventories_fast = ser_EC11_fast_draw.sort_values(ascending=True).index
        yinventories_fast = ser_EC11_fast_draw.sort_values(ascending=True).values


        figinventories_fast = go.Figure(data=[go.Bar(x=yinventories_fast, y=xinventories_fast, text=yinventories_fast,
                                                        orientation='h', textfont=dict(family='sana serif', size=14, color='#c4fff7'),
                                                    textposition='auto', textangle=0)
                                            ])
        figinventories_fast.update_xaxes(title_text="Number of Inventory", tickangle=-45, title_font_color='#087871', showgrid=True,
                                            gridwidth=0.1, gridcolor='#1f3b4d', showline=True, linewidth=1, linecolor='#59656d')
        figinventories_fast.update_yaxes(title_text='Description', title_font_color='#087871', showgrid=False, gridwidth=0.1,
                            gridcolor='#1f3b4d', showline=True, linewidth=1, linecolor='#59656d')
        figinventories_fast.update_traces(marker_color='#087871', marker_line_color='#087871', marker_line_width=1)
        figinventories_fast.update_layout(title='Fast Moving Inventories-Top 10', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(figinventories_fast, use_container_width=True)

        st.markdown('**Fast Moving Inventories-Top 10 info**')
        st.dataframe(df_EC11_fast_drawinfo, height=300)






elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')



hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)
