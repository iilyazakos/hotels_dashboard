'''
streamlit hotels dashboard
'''

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from bokeh.models.widgets import Div


def open_link(url, new_tab = True):
    if new_tab: js = f"window.open('{url}')"
    else: js = f"window.location.href = '{url}'"
    html = '<img src onerror="{}">'.format(js)
    div = Div(text = html)
    st.bokeh_chart(div)


#[Loading dataset]
_hotels = pd.read_csv('https://github.com/iilyazakos/hotels_dashboard/blob/master/hotel_bookings.csv?raw=true')

hotels = _hotels[['hotel', 'is_canceled', 'arrival_date_month', 'country',
          'reserved_room_type', 'assigned_room_type', 'adr', 'arrival_date_day_of_month',
          'stays_in_weekend_nights', 'stays_in_week_nights', 'market_segment', 'customer_type', 'deposit_type', 'arrival_date_year']]\
        .replace([np.nan, np.inf], 0)



st.set_page_config(layout = "wide")
st.title('Hotels booking dashboard')
st.write('Visualization and analytics of hotel reservations in the Resort and City categories are presented here')


#[Header & Description]
with st.container() as row_description:
    col_github, col_download_ipybn = st.columns(2)

    with col_github:
        github = st.button(label = ' My Github')
         #Open my github
        if github: open_link("https://github.com/iilyazakos")

#[Totals]
with st.container() as row_totals:
    col_avg, col_count_canceled, col_count_success = st.columns(3)

    with col_avg:
        st.metric(label = 'Average price per room', value = '$'+str(round(hotels['adr'].mean(), 2)))

    with col_count_canceled:
        st.metric(label = 'Count of cancellations', value = int(hotels["is_canceled"].sum()))

    with col_count_success:
        st.metric(label = 'Count of success booking', value = int((hotels["is_canceled"] == 0).sum()))



#[Prices]
with st.container() as row_prices_books:
    data_box_guests_pay = hotels[hotels['is_canceled'] == 0]

    st.plotly_chart(px.box(data_box_guests_pay, x = 'reserved_room_type', y = 'adr', color = 'hotel',
             title = 'How much do guests pay per room per day',
             labels = {'adr': 'Average daily rate',
                       'reserved_room_type': 'Code of the booked room type',
                       'hotel': 'Type of hotels'}), use_container_width = True)


#[Bookings]

with st.container() as row_col_slider:
    dynamics_data = hotels[['hotel', 'is_canceled', 'arrival_date_month', 'arrival_date_year', 'adr']]
    dynamics_data[['arrival_date']] = pd.to_datetime(
    dynamics_data['arrival_date_month'].map(str) + '' + dynamics_data['arrival_date_year'].map(str), format = '%B%Y').dt.strftime('%Y-%m')
    select_period_1, select_period_2 = st.select_slider('Choose a period',
                                                          options=dynamics_data['arrival_date'].unique(),
                                                        value = (dynamics_data['arrival_date'].min(), dynamics_data['arrival_date'].max()))
    dynamics_data_selection = dynamics_data[dynamics_data['arrival_date'].between(select_period_1, select_period_2)]

with st.container() as row_price_dynamics_business_month:
    col_price_dynamics, col_busiest_month = st.columns(2)

    with col_price_dynamics:

        data_city = dynamics_data_selection[(dynamics_data_selection['hotel'] == 'Resort Hotel') & (dynamics_data_selection['is_canceled'] == 0)]
        data_resort = dynamics_data_selection[(dynamics_data_selection['hotel'] == 'City Hotel') & (dynamics_data_selection['is_canceled'] == 0)]

        data_city = data_city.groupby(['arrival_date']).agg({'adr': 'mean'}).reset_index()
        data_resort = data_resort.groupby('arrival_date').agg({'adr': 'mean'}).reset_index()

        city_resort_data = pd.merge(data_resort, data_city, how = 'inner', on = 'arrival_date')
        city_resort_data.sort_values(by = ['arrival_date'], inplace = True)
        city_resort_data.columns = ['time period', 'price for resort hotel', 'price for a city hotel']

        # {Line}
        fig_price_dynamics = px.line(city_resort_data, x = 'time period', y = ['price for resort hotel', 'price for a city hotel'],
                   title = 'How does the price of a hotels change throughout the years ')

        fig_price_dynamics.update_layout(legend = dict(orientation = "h",yanchor = "bottom",
            y = 1.02,xanchor = "right",x = 1))

        st.plotly_chart(fig_price_dynamics, use_container_width = True)


        with col_busiest_month:

            resort_raw = dynamics_data_selection[(dynamics_data_selection['hotel'] == 'Resort Hotel') & (dynamics_data_selection['is_canceled'] == 0)]
            resort_hotel_data = resort_raw['arrival_date'].value_counts().reset_index()
            resort_hotel_data.columns = ['time period', 'number of guests']

            city_raw = dynamics_data_selection[(dynamics_data_selection['hotel'] == 'City Hotel') & (dynamics_data_selection['is_canceled'] == 0)]
            city_hotel_data = city_raw['arrival_date'].value_counts().reset_index()
            city_hotel_data.columns = ['time period', 'number of guests']

            final_data = pd.merge(resort_hotel_data, city_hotel_data, how = 'inner', on = 'time period')
            final_data.columns = ['time period', 'Guests of resort hotels', 'Guests of city hotels']
            final_data.sort_values(by = ['time period'], inplace=True)

            # {Line}
            fig_busiest_month = px.line(final_data, x = 'time period', y = ['Guests of resort hotels', 'Guests of city hotels'],
                                     title = 'How did the workload of hotels change by month')

            fig_busiest_month.update_layout(legend = dict(orientation = "h", yanchor = "bottom",
                y = 1.02, xanchor = "right", x = 1))

            st.plotly_chart(fig_busiest_month, use_container_width = True)

#[Where from clients]
with st.container() as row_from:
    data_countries = hotels[hotels['is_canceled'] == 0]['country'].value_counts().reset_index()
    data_countries.columns = ['country', 'number of guests']

    # {choropleth}
    st.plotly_chart(px.choropleth(data_countries, locations = data_countries['country'],
                    color = data_countries['number of guests'],
                    hover_name = data_countries['country'],
                    title = 'Where do the guests come from (map)'), use_container_width = True)

with st.container() as col_from:
    col_from_resort, col_from_city = st.columns(2)

    with col_from_resort:
        # {Resort hotels BAR}
        data_resort_for_bar = hotels[['hotel', 'is_canceled', 'country']]
        data_resort_for_bar = data_resort_for_bar[(data_resort_for_bar['hotel'] == 'Resort Hotel')
                                          & (hotels['is_canceled'] == 0)]
        data_resort_for_bar = data_resort_for_bar['country'].value_counts().reset_index()
        data_resort_for_bar.columns = ['country', 'number of guests']

        st.plotly_chart(px.bar(data_resort_for_bar, x = 'country', y = 'number of guests',
                        title = 'Where do the guests come from: Resort hotels'), use_container_width = True)

    with col_from_city:
        # {City hotels BAR}
        data_city_for_bar = hotels[['hotel', 'is_canceled', 'country']]
        data_city_for_bar = data_city_for_bar[(data_city_for_bar['hotel'] == 'City Hotel')
                                      & (hotels['is_canceled'] == 0)]
        data_city_for_bar = data_city_for_bar['country'].value_counts().reset_index()
        data_city_for_bar.columns = ['country', 'number of guests']

        st.plotly_chart(px.bar(data_city_for_bar, x = 'country', y = 'number of guests',
                      title = 'Where do the guests come from: City hotels'), use_container_width = True)


#[Bookings]
with st.container() as row_top_bookings:
    col_hotel_type, col_market_segment = st.columns(2)

    with col_hotel_type:
        hotel_data_more_booking = hotels['hotel'].value_counts().reset_index()
        hotel_data_more_booking.columns = ['type', 'quantity of booking']

        # {Donut}
        st.plotly_chart(px.pie(hotel_data_more_booking, values = 'quantity of booking', color = 'type',
                          title = 'The type of hotel with the most bookings', names = 'type'), use_container_width = True)

    with col_market_segment:
        data_bookings_by_market_segment = hotels[['stays_in_weekend_nights', 'stays_in_week_nights', 'market_segment']]
        data_bookings_by_market_segment = data_bookings_by_market_segment.groupby(
             ['market_segment']).sum().reset_index()
        data_bookings_by_market_segment['bookings'] = data_bookings_by_market_segment['stays_in_weekend_nights'] \
                                                      + data_bookings_by_market_segment['stays_in_week_nights']
        data_bookings_by_market_segment = data_bookings_by_market_segment[['market_segment', 'bookings']]
        data_bookings_by_market_segment.columns = ['market segment', 'bookings']

        # {Donut}
        st.plotly_chart(px.pie(data_bookings_by_market_segment, values = 'bookings',
                                        color = 'market segment', names = 'market segment',
                                        title = 'Bookings by market segment'), use_container_width = True)


#[Cancellations]
with st.container() as row_cancellations:
    col_clients_types, col_deposit_type = st.columns(2)

    with col_clients_types:
        data_book_cancellation = hotels[['customer_type', 'is_canceled']]
        data_book_cancellation = data_book_cancellation['customer_type'].value_counts().reset_index()

        data_book_cancellation.columns = ['customer type', 'canceled']

        st.plotly_chart(px.bar(data_book_cancellation, x = 'customer type', y = 'canceled',
                               color = 'customer type', log_y = True,
                               title = 'Which type of customer cancels the booking more often'), use_container_width = True)

        with col_deposit_type:
            data_book_cancellation_deposit = hotels[['deposit_type', 'is_canceled']]
            data_book_cancellation_deposit = data_book_cancellation_deposit['deposit_type'].value_counts().reset_index()

            data_book_cancellation_deposit.columns = ['deposit type', 'canceled']

            st.plotly_chart(px.bar(data_book_cancellation_deposit, x = 'deposit type', y = 'canceled',
                                           color = 'deposit type', log_y=True,
                                           title = 'What type of deposit is canceled more often'), use_container_width = True)
with st.container() as predict_price:
    data_city = dynamics_data[(dynamics_data['hotel'] == 'Resort Hotel') & (dynamics_data['is_canceled'] == 0)]
    data_resort = dynamics_data[(dynamics_data['hotel'] == 'City Hotel') & (dynamics_data['is_canceled'] == 0)]
    data_city = data_city.groupby(['arrival_date']).agg({'adr': 'mean'}).reset_index()
    data_resort = data_resort.groupby('arrival_date').agg({'adr': 'mean'}).reset_index()
    a_city = np.array(data_city[['adr']].iloc[6:18])
    b_city = np.array(data_city[['adr']].iloc[[18, 19, 20, 21, 22, 23, 24, 25, 2, 3, 4, 5]])
    model_city = LinearRegression().fit(a_city, b_city.reshape((-1, 1)))
    pred_city = model_city.predict(a_city)
    out_city = pd.DataFrame(pred_city)

    a_resort = np.array(data_resort[['adr']].iloc[6:18])
    b_resort = np.array(data_resort[['adr']].iloc[[18, 19, 20, 21, 22, 23, 24, 25, 2, 3, 4, 5]])
    model_resort = LinearRegression().fit(a_resort, b_resort.reshape((-1, 1)))
    pred_resort = model_resort.predict(a_resort)
    out_resort = pd.DataFrame(pred_resort)

    out_resort_city = np.hstack([out_city, out_resort])
    df = pd.DataFrame(out_resort_city, index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], columns =['city', 'resort'])
    st.plotly_chart(px.line(df, y = ['city', 'resort'],title = 'Prediction of price changes in city and resort hotels over the next year'), use_container_width=True)

with st.container() as predict_workload:

    city_raw = dynamics_data[(dynamics_data['hotel'] == 'City Hotel') & (dynamics_data['is_canceled'] == 0)]
    city_hotel_data = city_raw['arrival_date'].value_counts().reset_index()
    city_hotel_data.columns = ['time period', 'number of guests']

    resort_raw = dynamics_data[(dynamics_data['hotel'] == 'Resort Hotel') & (dynamics_data['is_canceled'] == 0)]
    resort_hotel_data = resort_raw['arrival_date'].value_counts().reset_index()
    resort_hotel_data.columns = ['time period', 'number of guests']

    x_city = np.array(city_hotel_data[['number of guests']].iloc[6:18])
    y_city = np.array(city_hotel_data[['number of guests']].iloc[[18, 19, 20, 21, 22, 23, 24, 25, 2, 3, 4, 5]])
    model_city_workload = LinearRegression().fit(x_city, y_city.reshape((-1, 1)))
    pred_city_workload = model_city_workload.predict(x_city)
    out_city_workload = pd.DataFrame(pred_city_workload)

    x_resort = np.array(resort_hotel_data[['number of guests']].iloc[6:18])
    y_resort = np.array(resort_hotel_data[['number of guests']].iloc[[18, 19, 20, 21, 22, 23, 24, 25, 2, 3, 4, 5]])
    model_resort_workload = LinearRegression().fit(x_resort, y_resort.reshape((-1, 1)))
    pred_resort_workload = model_resort_workload.predict(x_resort)
    out_resort_workload = pd.DataFrame(pred_resort_workload)

    out_city_resort_workload = np.hstack([out_city_workload, out_resort_workload])
    df_workload = pd.DataFrame(out_city_resort_workload, index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], columns=['city', 'resort'])
    st.plotly_chart(px.line(df_workload, y=['city', 'resort'], title='Predicting the workload of city and resort hotels over the next year'), use_container_width=True)
