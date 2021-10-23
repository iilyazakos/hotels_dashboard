'''
streamlit hotels dashboard
'''

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from bokeh.models.widgets import Div


st.set_page_config(layout = 'wide')

def open_link(url, new_tab=True):
    if new_tab: js = f"window.open('{url}')"
    else: js = f"window.location.href = '{url}'"
    html = '<img src onerror="{}">'.format(js)
    div = Div(text = html)
    st.bokeh_chart(div)


#[Loading dataset]
_hotels = pd.read_csv("C:\dataset\dataset_1\hotel_bookings.csv")

hotels = _hotels[['hotel', 'is_canceled', 'arrival_date_month', 'country',
                  'reserved_room_type', 'assigned_room_type', 'adr', 'arrival_date_day_of_month',
                  'stays_in_weekend_nights', 'stays_in_week_nights', 'market_segment', 'customer_type', 'deposit_type']]\
                .replace([np.nan, np.inf], 0)


#[Header & Description]
with st.container() as row_description:
    st.title('Hotels booking dashboard')

    st.markdown('hello bla bla bla')

    col_github, col_download_ipybn = st.columns([1, 1])

    with col_github:
        github = st.button(label = 'Github')

    #with col_download_ipybn:
    #    st.download_button(label = 'Download .ipynb', data = hotels,
    #                       file_name = 'hotels_dashboard.ipynb', )

#open my github
if github: open_link(f"http://google.com")

#[Totals]
with st.container() as row_totals:
    col_avg, col_count = st.columns([3, 3])

    with col_avg:
        st.metric(label = 'Average price per room', value = '$'+str(round(hotels['adr'].mean(), 2)))

    with col_count:
        st.metric(label = 'Count of cancellations', value = int(hotels["is_canceled"].sum()))

    #TODO: busiest month


#[Prices]
with st.container() as row_prices_books:
    data_box_guests_pay = hotels[hotels['is_canceled'] == 0]
    fig_box = go.Figure()
    fig_box = px.box(data_box_guests_pay, x = 'reserved_room_type', y = 'adr', color = 'hotel',
                     title = 'How much do guests pay per room per day',
                     labels = {'adr': 'Average daily rate',
                               'reserved_room_type': 'Code of the booked room type',
                               'hotel': 'Type of hotels'})

    st.plotly_chart(fig_box)


#[Bookings]
with st.container() as row_price_dynamics_business_month:
    col_price_dynamics, col_business_month = st.columns([3, 3])

    with col_price_dynamics:
        data_city = hotels[(hotels['hotel'] == 'Resort Hotel') & (hotels['is_canceled'] == 0)]
        data_resort = hotels[(hotels['hotel'] == 'City Hotel') & (hotels['is_canceled'] == 0)]

        data_city = data_city.groupby(['arrival_date_month']).agg({'adr': 'mean'}).reset_index()
        data_resort = data_resort.groupby('arrival_date_month').agg({'adr': 'mean'}).reset_index()

        city_resort_data = pd.merge(data_resort, data_city, how='inner', on='arrival_date_month')
        city_resort_data['arrival_date_month'] = pd.to_datetime(city_resort_data['arrival_date_month'],
                                                                format='%B').dt.month
        city_resort_data.sort_values(by=['arrival_date_month'], inplace=True)
        city_resort_data.columns = ['month', 'price for resort hotel', 'price for a city hotel']

        # {Line}
        fig_line = go.Figure()
        fig_line = px.line(city_resort_data, x='month', y=['price for resort hotel', 'price for a city hotel'],
                           title='How does the price of a hotel change throughout the year')

        st.plotly_chart(fig_line)

        with col_business_month:
            resort_raw = hotels[(hotels['hotel'] == 'Resort Hotel') & (hotels['is_canceled'] == 0)]
            resort_hotel_data = resort_raw['arrival_date_month'].value_counts().reset_index()
            resort_hotel_data.columns = ['month', 'number of guests']
            city_raw = hotels[(hotels['hotel'] == 'City Hotel') & (hotels['is_canceled'] == 0)]
            city_hotel_data = city_raw.arrival_date_month.value_counts().reset_index()
            city_hotel_data.columns = ['month', 'number of guests']
            final_data = pd.merge(resort_hotel_data, city_hotel_data, how='inner', on='month')
            final_data.columns = ['month', 'Guests of resort hotels', 'Guests of city hotels']
            final_data['month'] = pd.to_datetime(final_data['month'], format='%B').dt.month
            final_data.sort_values(by=['month'], inplace=True)

            # {Line}
            fig_busy_month = go.Figure()
            fig_busy_month = px.line(final_data, x='month', y=['Guests of resort hotels', 'Guests of city hotels'],
                                     title='The busiest month')

            st.plotly_chart(fig_busy_month)

#[Where from clients]
with st.container() as row_from:
    data_countries = hotels[hotels['is_canceled'] == 0]['country'].value_counts().reset_index()
    data_countries.columns = ['country', 'number of guests']

    # {choropleth}
    fig_map = px.choropleth(data_countries, locations=data_countries['country'],
                            color=data_countries['number of guests'],
                            hover_name=data_countries['country'],
                            title='Where do the guests come from (map)')

    st.plotly_chart(fig_map)

    col_from_resort, col_from_city = st.columns([3, 3])

    with col_from_resort:
        # {Resort hotels BAR}
        data_resort_for_bar = hotels[['hotel', 'is_canceled', 'country']]
        data_resort_for_bar = data_resort_for_bar[(data_resort_for_bar['hotel'] == 'Resort Hotel')
                                                  & (hotels['is_canceled'] == 0)]
        data_resort_for_bar = data_resort_for_bar['country'].value_counts().reset_index()
        data_resort_for_bar.columns = ['country', 'number of guests']

        fig_resort_bar = go.Figure()
        fig_resort_bar = px.bar(data_resort_for_bar, x='country', y='number of guests',
                                title='Where do the guests come from: Resort hotels')

        st.plotly_chart(fig_resort_bar)

    with col_from_city:
        # {City hotels BAR}
        data_city_for_bar = hotels[['hotel', 'is_canceled', 'country']]
        data_city_for_bar = data_city_for_bar[(data_city_for_bar['hotel'] == 'City Hotel')
                                              & (hotels['is_canceled'] == 0)]
        data_city_for_bar = data_city_for_bar['country'].value_counts().reset_index()
        data_city_for_bar.columns = ['country', 'number of guests']

        fig_city_bar = go.Figure()
        fig_city_bar = px.bar(data_city_for_bar, x='country', y='number of guests',
                              title='Where do the guests come from: City hotels')

        st.plotly_chart(fig_city_bar)


#[Bookings]
with st.container() as row_top_bookings:
    col_hotel_type, col_market_segment = st.columns([1, 1])

    with col_hotel_type:
        hotel_data_more_booking = hotels['hotel'].value_counts().reset_index()
        hotel_data_more_booking.columns = ['type', 'quantity of booking']

        # {Donut}
        fig_more_booking = px.pie(hotel_data_more_booking, values='quantity of booking', color='type',
                                  title='The type of hotel with the most bookings', names='type')

        st.plotly_chart(fig_more_booking)

    with col_market_segment:
        data_bookings_by_market_segment = hotels[['stays_in_weekend_nights', 'stays_in_week_nights', 'market_segment']]
        data_bookings_by_market_segment = data_bookings_by_market_segment.groupby(
            ['market_segment']).sum().reset_index()
        data_bookings_by_market_segment['bookings'] = data_bookings_by_market_segment['stays_in_weekend_nights'] \
                                                      + data_bookings_by_market_segment['stays_in_week_nights']
        data_bookings_by_market_segment = data_bookings_by_market_segment[['market_segment', 'bookings']]
        data_bookings_by_market_segment.columns = ['market segment', 'bookings']

        # {Donut}
        fig_bookings_by_market_segment = px.pie(data_bookings_by_market_segment, values='bookings',
                                                color='market segment', names='market segment',
                                                title='Bookings by market segment')

        st.plotly_chart(fig_bookings_by_market_segment)


#[Cancellations]
with st.container() as row_cancellations:
    col_clients_types, col_deposit_type = st.columns([1, 1])

    with col_clients_types:
        data_book_cancellation = hotels[['customer_type', 'is_canceled']]
        data_book_cancellation = data_book_cancellation['customer_type'].value_counts().reset_index()

        data_book_cancellation.columns = ['customer type', 'canceled']
        fig_book_cancellation = px.bar(data_book_cancellation, x='customer type', y='canceled',
                                       color='customer type', log_y=True,
                                       title='Which type of customer cancels the booking more often')

        st.plotly_chart(fig_book_cancellation)

        with col_deposit_type:
            data_book_cancellation_deposit = hotels[['deposit_type', 'is_canceled']]
            data_book_cancellation_deposit = data_book_cancellation_deposit['deposit_type'].value_counts().reset_index()

            data_book_cancellation_deposit.columns = ['deposit type', 'canceled']
            fig_book_cancellation_deposit = px.bar(data_book_cancellation_deposit, x='deposit type', y='canceled',
                                                   color='deposit type', log_y=True,
                                                   title='What type of deposit is canceled more often')

            st.plotly_chart(fig_book_cancellation_deposit)