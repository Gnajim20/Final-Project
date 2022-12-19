import streamlit as st #streamlit package
from streamlit_folium import folium_static
import pandas as pd #package for plots and importing xlsx
import geopandas as gpd
import matplotlib.pyplot as plt
import folium #mapping package

#the shapefile is from https://koordinates.com/layer/96163-boston-massachusetts-police-districts/
SHAPEFILE = 'C:/CS230/Police_districts/boston-massachusetts-police-districts.shp'
CRIME_XLSX = 'BostonCrime2021_7000_sample.xlsx'

# --------------------------------------------
# Reading in the files and creating dataframes
# --------------------------------------------
districts_df = gpd.read_file(SHAPEFILE)
df = pd.read_excel(
    io=CRIME_XLSX,
    engine='openpyxl',
    usecols='A,B,D:L,N:Q'
)

# --------------------------------------------
# Creating the Streamlit Page and settings
# Adding in the sidebar with data filters
# --------------------------------------------
st.set_page_config(page_title='Boston Crime Report',
                   layout = 'wide')

st.sidebar.header("Filters")
st.title("Boston Crime Report")

districts = st.sidebar.multiselect(
    label="Select Districs",
    options= df["DISTRICT"].unique(),
    default= df["DISTRICT"].unique()
)
day = st.sidebar.multiselect(
    label="Select Day",
    options= df["DAY_OF_WEEK"].unique(),
    default= df["DAY_OF_WEEK"].unique()
)
shooting = st.sidebar.checkbox(
    label='Show Shootings Only',
    value=False
)
month_range = st.sidebar.slider(
    label="Select Month Range",
    min_value=1,
    max_value=6,
    value=(1,6),
    step = 1
)

# Use the Pandas query function to sort data based on our filters
filtered_df = df.query(
        "DISTRICT in @districts & DAY_OF_WEEK in @day & SHOOTING == @shooting & MONTH >= @month_range[0] & MONTH <= @month_range[1]"
    )
# goes into datafram and applying the filters to the datafram and saves it as a filter to the datafram

# ----------------------------------------------------------------------------------------
# This section is where I make the map
# @boston_map is a blank folium map of boston
# The for loop goes through each of the police districts from the .shp file and adds them
# to the boston map. It also counts how many crimes were committed in that district
# ----------------------------------------------------------------------------------------
boston_map = folium.Map(location=[42.306, -71.095], zoom_start=12) #creating a map of boston in folium

for i, r in districts_df.iterrows():
    count = 0
    for i, x in filtered_df.iterrows():
        if x['DISTRICT'] == r[5]:
            count += 1
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    # takes point of each shape and simplifies each value to three decimals to loop efficiently
    geo_j = sim_geo.to_json()
    # takes points and converts to geo json file, which folium is able to read
    geo_j = folium.GeoJson(data=geo_j)
    # folium reads json file
    geo_j.add_to(boston_map)
    # takes the shapes and plots them on the map
    folium.Popup('District: ' + r[5] + '\nCrimes Committed: ' + str(count)).add_to(geo_j)
    # adds the pop up and allows user to hover and see data for each shape of the district

    # understanding how to read the shape file and put in the map to plot, converting to json which folium can read

# ------------------------------------------------------------------
# This next section is the chart creation.
# @filtered_df_no_null drops all the rows with a null district name
# it is only used in the pie chart
# ------------------------------------------------------------------

def pie_chart():
    filtered_df_no_null = filtered_df.dropna()
    data = filtered_df_no_null.groupby(['DISTRICT']).size()
    names = filtered_df_no_null["DISTRICT"].unique()
    fig = plt.figure(figsize=(10, 5))
    plt.pie(data, labels=names, autopct='%1.1f%%')
    plt.title("Percentage of Crimes Committed per District")
    st.pyplot(fig)

def bar_chart(x,y):

    fig = plt.figure(figsize=(10, 5))
    plt.bar(x,y)
    plt.xlabel("Month")
    plt.ylabel("Crimes Committed")
    plt.title("Crimes Committed Per Month")
    return(fig)

def scatter_plot():
    shooting = True
    only_shootings = df.query("SHOOTING == @shooting")
    xs = only_shootings["DAY_OF_WEEK"]
    ys = only_shootings["HOUR"]
    fig = plt.figure(figsize=(10, 5))
    plt.scatter(xs, ys)
    plt.xlabel("Hour of Day")
    plt.ylabel("Day of the Week")
    plt.title("Crimes Throughout Each Day")
    st.pyplot(fig)

# ----------------------------------------------------------
# In this section I add the maps and charts to the streamlit
# page as well as their decriptions
# ----------------------------------------------------------

folium_static(boston_map)
st.subheader("Reading the Map")
st.write("""
        The above map outlines each of the 12 Police Districts of Boston. View the number of crimes committed
        in each district by clicking on the district.
        """)
pie_chart()
#DESCRIPTION FOR THE PIE CHART HERE. FOLLOW WHAT I DID ABOVE FOR THE MAP
st.subheader("Pie Chart Description")
st.write("The Pie Chart analyzes and displays the percentages of crimes committed per each district. The pie chart is color coded by district. If you click on the filter on the left of the page you can see an updated chart of the percentages of crimes committed per district that involved shootings. You can also filter to only see the data by district, day, and month.")


xs = filtered_df["MONTH"].unique()
ys = filtered_df.groupby(["MONTH"]).size()
st.pyplot(bar_chart(xs,ys))
#DESCRIPTION FOR THE BAR CHART HERE
st.subheader("Bar Chart Description")
st.write("The bar chart takes the data and shows the crimes committed through the 6 month period of the data. If you click on the filters on the left side of the page there are 4 filters that will update the data on the bar chart, crime by shooting, day, week, and month.")

scatter_plot()
#DESCRIPTION FOR THE SCATTER CHART HERE (The chart sucks but better when you filter data)
st.subheader("Scatter Plot Analysis")
st.write("The Scatter Plot presents the day and hours of the crimes committed.This shows what shooting related crimes are most popular and at what time of the day residents of boston should be aware of during the week.")
