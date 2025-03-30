import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from metpy.plots import ctables
import metpy.calc as mpcalc
from metpy.units import units
from matplotlib.colors import LinearSegmentedColormap

import Postgresoperator as pg
import os





def stream_data():
    df = pd.read_csv('./data/weather.csv')
    df.drop_duplicates(inplace=True)
    
    df['time'] = pd.to_datetime(df['time'])



    st.title('Weather Forecast')
    st.write('This is a simple weather forecast dashboard.')


    # Date range filter
    min_date = pd.to_datetime(df['time']).min().date()
    max_date = pd.to_datetime(df['time']).max().date()

    start_date, end_date = st.sidebar.date_input(
        'Select date range',
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    # Filter data
    df = df[(pd.to_datetime(df['time']).dt.date >= start_date) & 
                            (pd.to_datetime(df['time']).dt.date <= end_date)]

    

# dùng tabs để chia ra 3 cột để hiển thị dữ liệu
    tab1, tab2, tab3, tab4 = st.tabs(["Temperature", "Weather Conditions", "Himidity Level", "Wind Speed"])

    with tab1:
        
        fig, ax = plt.subplots(3, 2, figsize=(16, 12))
        positions = [(0, 0), (1, 0), (1, 1), (0, 1), (2, 0), (2, 1)]

        for idx, city_name in enumerate(df['city'].unique()):

            city_data = df[df['city'] == city_name].copy()
            city_data['datetime'] = pd.to_datetime(city_data['time'])
            
            # Extract date 
            city_data['date'] = city_data['datetime'].dt.date
            
            # Group by date to get average temperature by day
            daily_temp = city_data.groupby('date').agg(
                avg_temp=('temperature', 'mean'),
                min_temp=('temperature', 'min'),
                max_temp=('temperature', 'max')
            ).reset_index()
            
            i,j = positions[idx]
        # Plot the average temperature by day as a line
            ax[i, j].plot(daily_temp['date'], daily_temp['avg_temp'], 
                'r-', linewidth=3, label='Average Temperature')
            
            # Add min-max range as a shaded area
            ax[i, j].fill_between(daily_temp['date'], 
                        daily_temp['min_temp'], 
                        daily_temp['max_temp'], 
                        alpha=0.3, color='#FF9F9F', 
                        label='Min-Max Range')
            
            # thêm khoảng cách giữa các subplot theo chiều dọc
            plt.subplots_adjust(hspace=0.5)

            # Styling
            ax[i, j].set_title(f'Daily Temperature Range for {city_name}', fontsize=16)
            ax[i, j].set_xlabel('Date', fontsize=12)
            ax[i, j].set_ylabel('Temperature (°C)', fontsize=12)
            ax[i, j].grid(True, linestyle='--', alpha=0.7)
            ax[i, j].legend(loc='best')
            
            
        st.pyplot(fig)





    with tab2:

        # Assuming df contains your weather data
        # Group by time to create individual frames (similar to animation)

        min_temp = df['temperature'].min()
        max_temp = df['temperature'].max()
        time_groups = df.groupby('time')
        times = sorted(df['time'].unique())

        # Example for a single time frame
        sample_time = times[-1]
        sample_data = df[df['time'] == sample_time]

        # Create a map with MetPy
        fig2 = plt.figure(figsize=(12, 8))
        ax = fig2.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.coastlines()
        ax.add_feature(ccrs.cartopy.feature.BORDERS)
        ax.add_feature(ccrs.cartopy.feature.STATES)

        # Use MetPy colortable for meteorological visualization
        cmap = plt.cm.coolwarm  # Using matplotlib's coolwarm colormap instead
        norm = plt.Normalize(min_temp, max_temp)



        point_sizes = (sample_data['temperature']-min_temp+20) * 4

        sc = ax.scatter(sample_data['lon'], sample_data['lat'], 
                    c=sample_data['temperature'], 
                    s=point_sizes,  # Increased size here
                    cmap=cmap, norm=norm,
                    transform=ccrs.PlateCarree(),
                    zorder=10,
                    marker='o', 
                    edgecolor='k', 
                    linewidth=0.7, 
                    alpha=0.8,     
        )

        # Add city labels
        for idx, row in sample_data.iterrows():
            # Add city labels with weather description
            ax.text(row['lon'], row['lat']+0.15, 
                    f"{row['city']}\n{row['weather_des']}", 
                    fontsize=8,
                    ha='center',
                    va='bottom',
                    transform=ccrs.PlateCarree(),
                    bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'),
                    zorder=11
                    )
                        # thêm trạng thái  weather_des vài biểu đồ

        plt.colorbar(sc, ax=ax, orientation='horizontal', pad=0.05, label='Temperature (°C)')
        plt.title(f"Weather Forecast - {sample_time}", fontsize=16)
        plt.tight_layout()

        plt.figure(figsize=(12, 6))
        st.pyplot(fig2)

    with tab3: 


        st.write('### Temperature')
        fig3 = plt.figure(figsize=(12, 6)) 
        for city in df['city'].unique():
            city_data = df[df['city'] == city]

            plt.plot(pd.to_datetime(city_data['time']), city_data['humidity'], label=city, alpha=0.7)
            

        plt.title('Humidity Trends')
        plt.xlabel('Date')
        plt.ylabel('Himidity Level (%)')
        plt.legend()
        plt.grid(True)
        st.pyplot(fig3)


        
        
        
        fig4 = plt.figure(figsize=(14, 10))

        # Pivot the data
        pivot_data = df.pivot_table(
            index='city', 
            columns='time', 
            values='humidity',
            aggfunc='mean'
        )

        # Create custom colormap

        #đổi thành các màu liên quan đến thời tiết 
        color = [
            (0, 'lightblue'),
            (0.5, 'skyblue'),
            (1, 'darkblue')
        ]
        custom_cmap = LinearSegmentedColormap.from_list("humidity_cmap", color)

        # Create the heatmap
        ax = sns.heatmap(
            pivot_data, 
            cmap=custom_cmap,
            linewidths=0.1,
            linecolor='white',
            annot=False,
            fmt=".0f",
            cbar_kws={'label': 'Humidity (%)'},

            
        )

        # Customize appearance
        plt.title('Humidity Levels by City over Time', fontsize=16, pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)

        # Enhance the colorbar
        cbar = ax.collections[0].colorbar
        cbar.ax.tick_params(labelsize=10)

        st.pyplot(fig4)

    with tab4:
        df['direction_bin'] = (df['wind_deg'] // 30) * 30
        wind_stats = df.groupby('direction_bin')['wind_speed'].agg(['mean', 'count']).reset_index()

        # Convert to radians for polar plot
        wind_stats['rad'] = np.radians(wind_stats['direction_bin'])

        # Create polar plot
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='polar')

        # Create bars for wind direction frequency
        bars = ax.bar(
            wind_stats['rad'], 
            wind_stats['count'],
            width=np.radians(30),
            alpha=0.8,
            edgecolor='white',
            linewidth=1
        )

        # Color bars by wind speed
        norm = plt.Normalize(wind_stats['mean'].min(), wind_stats['mean'].max())
        for bar, speed in zip(bars, wind_stats['mean']):
            bar.set_facecolor(plt.cm.viridis(norm(speed)))

        # dùng directions tiếng việt
        directions = ['B', 'ĐB', 'Đ', 'ĐN', 'N', 'TB', 'T', 'TN'] 
        ax.set_xticks(np.radians(np.arange(0, 360, 45)))
        ax.set_xticklabels(directions, fontsize=12)



        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, pad=0.1, shrink=0.75)
        cbar.set_label('Average Wind Speed (m/s)', fontsize=12)

        st.pyplot(fig)

if __name__ == '__main__':
    stream_data()