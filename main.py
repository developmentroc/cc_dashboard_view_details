import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
def load_data():
    data = pd.read_csv("Agent Time On Status Template_Jul 10 2025 11_38,Jun 29 2025-Jul 5 2025_MIN15.csv")
    data['Start Time'] = pd.to_datetime(data['Start Time'].str[:-6])
    data['End Time'] = pd.to_datetime(data['End Time'].str[:-6])

    time_cols = ['Available Time', 'Handling Time', 'Wrap Up Time', 'Working Offline Time',
                 'On Break Time', 'Busy Time', 'Logged In Time', 'Offering Time']
    for col in time_cols:
        data[col] = pd.to_timedelta(data[col])

    return data

# Load appointments created data
def load_appointments():
    appointments = pd.read_excel("viewDetails.xlsx", skiprows=3)
    # appointments.columns = appointments.iloc[0]
    # appointments = appointments[1:]
    appointments = appointments[['Representative', 'Created On Date']]
    appointments['Created On Date'] = pd.to_datetime(appointments['Created On Date'], errors='coerce')

    start_date, end_date = '2025-06-29', '2025-07-05'
    appointments = appointments[(appointments['Created On Date'] >= start_date) &
                                (appointments['Created On Date'] <= end_date)]

    appointments_count = appointments.groupby('Representative').size().reset_index(name='Appointments Created')
    return appointments_count

# Data aggregation
def aggregate_data(data, appointments):
    summary = data.groupby('Agent').agg({
        'Available Time': 'sum', 'Handling Time': 'sum', 'Wrap Up Time': 'sum',
        'Working Offline Time': 'sum', 'On Break Time': 'sum', 'Busy Time': 'sum',
        'Logged In Time': 'sum'
    }).reset_index()

    summary['Break Hours'] = round(summary['On Break Time'].dt.total_seconds() / 3600, 2)
    summary['Offline Hours'] = round(summary['Working Offline Time'].dt.total_seconds() / 3600,2)

    merged_summary = summary.merge(appointments, left_on='Agent', right_on='Representative', how='left').fillna(0)
    return merged_summary

# Dashboard creation
st.title('📊 Call Center Agent Dashboard')

# Load and process data
data = load_data()
appointments = load_appointments()
summary = aggregate_data(data, appointments)

# Break, Offline, and Productivity Analysis
st.header('Break, Offline, and Productivity Analysis')
scatter_chart = px.scatter(summary, x='Break Hours', y='Offline Hours',
                           size='Appointments Created', color='Appointments Created', hover_name='Agent',
                           labels={'Break Hours':'Break Time (hrs)', 'Offline Hours':'Offline Time (hrs)', 'Appointments Created':'Appointments Created'},
                           title='Break & Offline Time vs Appointments Created', height=600)
st.plotly_chart(scatter_chart)