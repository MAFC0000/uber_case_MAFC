import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pandas.api.types import CategoricalDtype
from pmdarima import auto_arima
from matplotlib.ticker import MaxNLocator

# Function to calculate the total of deliveries
def des_kpi_total_function(deliveries):
    total=deliveries.count()
    return total

# Function to calculate the median ATD in minutes
def des_kpi_atd_function(atd):
    median_atd=atd.median()
    return median_atd

# Function to calculate the median velocity in Km/Min
def des_kpi_velocity_function(pick_up_distance, drop_off_distance, atd):
    total_distance=pick_up_distance+drop_off_distance
    velocity=total_distance/atd
    total=round(velocity.median(),3)
    return total

# Function to create a scatterplot visual
def des_visuals_archetype_scatterplot(filtered_df):
    
    #Preparing data for the scatterplot
    filtered_df['total_distance']=filtered_df['pickup_distance']+filtered_df['dropoff_distance']
    grouped_df=filtered_df.groupby('geo_archetype').agg(
            atd_median=('ATD', 'median'),
            distance_median=('total_distance', 'median'),
            total_deliveries=('delivery_trip_uuid', 'count')).reset_index()
    grouped_df=grouped_df.rename(columns={'geo_archetype':'Archetype', 'total_deliveries':'Total deliveries'})
    
    vel_df=grouped_df[['distance_median','atd_median']]
    vel_df['velocity']=round(vel_df['distance_median']/vel_df['atd_median'],4)

    #Creating the scatterplot
    sns.set_theme(style="darkgrid", font_scale=.9)
    graph=sns.relplot(x="atd_median", y="distance_median", hue="Archetype", size="Total deliveries",
                sizes=(75, 1000), alpha=.8, palette=['#3AA76D', '#FFC043', '#D44333', '#99644C','#ED6E33', '#7356BF'],
                height=4, legend="brief", aspect=1, data=grouped_df)
    graph.set(
        xlabel="Median ATD (Minutes)",
        ylabel="Total distance median (Km)")
    
    graph.ax.set_xlabel(graph.ax.get_xlabel(), fontweight='bold')
    graph.ax.set_ylabel(graph.ax.get_ylabel(), fontweight='bold')

    for i, row in vel_df.iterrows():
        graph.ax.text(
            row["atd_median"], row["distance_median"], row["velocity"],
            color="black", fontsize=8, ha="right", fontstyle="italic"
        )
    
    fig=graph.figure
    return fig

# Function to create a scatterplot visual
def des_visuals_territory_scatterplot(filtered_df):
    
    #Preparing data for the scatterplot
    filtered_df['total_distance']=filtered_df['pickup_distance']+filtered_df['dropoff_distance']
    grouped_df=filtered_df.groupby('territory').agg(
            atd_median=('ATD', 'median'),
            distance_median=('total_distance', 'median'),
            total_deliveries=('delivery_trip_uuid', 'count')).reset_index()
    grouped_df=grouped_df.rename(columns={'territory':'Territory','total_deliveries':'Total deliveries'})
    
    vel_df=grouped_df[['distance_median','atd_median']]
    vel_df['velocity']=round(vel_df['distance_median']/vel_df['atd_median'],4)

    #Creating the scatterplot
    sns.set_theme(style="darkgrid", font_scale=.9)
    graph=sns.relplot(x="atd_median", y="distance_median", hue="Territory", size="Total deliveries",
                sizes=(75, 1000), alpha=.8, palette=['#3AA76D', '#FFC043', '#D44333', '#99644C','#ED6E33', '#7356BF'],
                height=4, legend="brief", aspect=1, data=grouped_df)
    graph.set(
        xlabel="Median ATD (Minutes)",
        ylabel="Total distance median (Km)")
    
    graph.ax.set_xlabel(graph.ax.get_xlabel(), fontweight='bold')
    graph.ax.set_ylabel(graph.ax.get_ylabel(), fontweight='bold')
    
    for i, row in vel_df.iterrows():
        graph.ax.text(
            row["atd_median"], row["distance_median"], row["velocity"],
            color="black", fontsize=8, ha="right", fontstyle="italic"
        )

    fig=graph.figure
    return fig

# Function to create a stacked bar visual
def des_visuals_stacked_bar(filtered_df):
    
    #Preparing data for the stacked bar chart
    filtered_df=filtered_df.rename(columns={'territory':'Territory'})
    
    #Creating the stacked bar chart
    fig, ax = plt.subplots(figsize=(5.5, 4.05))
    sns.set_theme(style="darkgrid", font_scale=.8)
    sns.histplot(
        data=filtered_df,
        x='geo_archetype',
        hue='Territory',
        multiple="stack",
        shrink=.7,
        ax=ax,
        palette=['#3AA76D', '#FFC043', '#D44333', '#99644C','#ED6E33', '#7356BF']
    )
    
    ax.set_xlabel("Archetype", fontweight='bold')
    ax.set_ylabel("Total deliveries", fontweight='bold')
    
    
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

# Function to create a pie
def des_visuals_pie(filtered_df):
    
    # Preparing data for the pie charts
    df_flow = filtered_df.groupby('courier_flow').size().reset_index(name='Count')
    df_flow = df_flow.rename(columns={'courier_flow': 'Courier flow'})
    
    # Creating the pie chart
    fig, ax = plt.subplots(figsize=(4.5, 5.6)) 
    sns.set_theme(style="white")
    colors = sns.color_palette(['#3AA76D', '#FFC043', '#D44333', '#99644C','#ED6E33', '#7356BF', '#000000'])
    
    wedges, texts, autotexts = ax.pie(
        df_flow['Count'],
        labels=None,
        colors=colors,
        autopct='',
        startangle=90,
        pctdistance=.85, 
        wedgeprops={'edgecolor': 'white', 'linewidth': 1},
        textprops={'fontsize': 13.5, 'color': 'black'})
    
    ax.axis('equal')
    
    ax.legend(
        wedges,
        df_flow['Courier flow'],
        title="Courier flow",
        loc="lower center",
        bbox_to_anchor=(0.5, -0.1),
        ncol=3)

    plt.tight_layout()
    return fig

# Function to create a bar visual
def des_visuals_day_bars(filtered_df):
    
    # Preparing data for the bars
    filtered_df=filtered_df.rename(columns={'geo_archetype':'Archetype'})
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_cat = CategoricalDtype(categories=day_order, ordered=True)
    filtered_df['weekday'] = filtered_df['weekday'].astype(day_cat)
    
    driver_metrics = filtered_df.groupby('weekday')['driver_uuid'].nunique().reset_index(name='unique_drivers')
    
    daily_order_count = filtered_df.groupby('weekday', observed=True).size().reset_index(name='Total_Deliveries')
    
    # Creating the bars
    sns.set_theme(style="darkgrid", font_scale=.9)
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(8, 5.8)) 
    
    ax1 = axes[0]
    sns.boxplot(
        data=filtered_df, 
        x="weekday", 
        y="ATD", 
        color="gray",
        showfliers=False,
        ax=ax1,
        boxprops={'alpha': 0.7}
    )
    ax1.set_xlabel("", fontweight='bold')
    ax1.set_ylabel("ATD", fontweight='bold')
    ax1.set_xticklabels([])
    ax1.set_title("ATD distribution by Weekday", fontstyle='italic')
    
    ax2 = axes[1]
    sns.barplot(
        data=daily_order_count,
        x="weekday", 
        y="Total_Deliveries",
        color="#276ef1",
        ax=ax2,
        width=.7,
        order=day_order,
        alpha=.7
    )
    ax2.set_xlabel("", fontweight='bold')
    ax2.set_ylabel("Total deliveries", fontweight='bold')
    ax2.set_xticklabels([])
    ax2.set_title("Total deliveries by Weekday", fontstyle='italic')

    ax3 = axes[2]
    sns.barplot(
        data=driver_metrics,
        x="weekday", 
        y="unique_drivers",
        color="#276ef1",
        width=.7,
        ax=ax3,
        alpha=.7
    )
    ax3.set_xlabel("Weekday", fontweight='bold')
    ax3.set_ylabel("Number of drivers", fontweight='bold')
    ax3.set_title("Number of unique drivers by Weekday", fontstyle='italic')

    plt.tight_layout()
    return fig

# Function to create a summary table
def des_visuals_table(filtered_df):
    
    # Preparing data for the table
    filtered_df['total_distance']=filtered_df['pickup_distance']+filtered_df['dropoff_distance']
    
    grouped_df=filtered_df.groupby(['geo_archetype','territory', 'courier_flow']).agg(
            atd_median=('ATD', 'median'),
            distance_median=('total_distance', 'median'),
            total_deliveries=('delivery_trip_uuid', 'count')).reset_index()
    grouped_df=grouped_df.rename(columns={'geo_archetype':'Archetype', 'total_deliveries':'Total deliveries', 'territory':'Territory', 'courier_flow':'Courier flow', 'atd_median':'ATD median', 'distance_median':'Distance median'})
    
    return grouped_df

# Function to create initial graphs with predictions
def des_initial_graph_prediction_function(df):
    
    # Data preparation
    df['eater_request_timestamp_local'] = df['eater_request_timestamp_local'].dt.date

    df = df.groupby('eater_request_timestamp_local').agg(
        total_deliveries=('delivery_trip_uuid', 'count'),
        ATD_median=('ATD', 'median')).reset_index()

    df = df.sort_values(by='eater_request_timestamp_local', ascending=True)

    df.set_index('eater_request_timestamp_local', inplace=True)
    df.index = pd.DatetimeIndex(df.index.values, freq='D')

    model_total_deliveries=auto_arima(df['total_deliveries'], seasonal=True, m=7)    
    forecast_total_deliveries=model_total_deliveries.predict(14)

    model_ATD_median=auto_arima(df['ATD_median'], seasonal=True, m=7)    
    forecast_ATD_median=model_ATD_median.predict(14)
    
    # Creating the graphs
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(17, 3.5)) 

    ax1 = axes[0]
    ax1.plot(df.index, df['total_deliveries'], label="Total Deliveries", color="#276ef1", linestyle="-", marker="o", linewidth=2)
    ax1.plot(forecast_total_deliveries.index, forecast_total_deliveries, label="Total Deliveries prediction", color="#000000", linestyle="--", linewidth=2)

    ax1.set_title("Daily deliveries trend", fontstyle='italic', fontsize=11)
    ax1.set_xlabel('Periods', fontsize=10)
    ax1.set_ylabel('Daily deliveries', fontsize=10)
    ax1.legend(loc="upper left", fontsize=9)
    ax1.xaxis.set_major_locator(MaxNLocator(nbins=8))
    ax1.grid(True, linestyle='--', alpha=0.6)

    ax2 = axes[1]
    ax2.plot(df.index, df['ATD_median'], label="ATD median", color="#453473", linestyle="-", marker="o", linewidth=2)
    ax2.plot(forecast_ATD_median.index, forecast_ATD_median, label="ATD median prediction", color="#000000", linestyle="--", linewidth=2)

    ax2.set_title("Daily ATD median trend", fontstyle='italic', fontsize=11)
    ax2.set_xlabel('Periods', fontsize=10)
    ax2.set_ylabel('Daily ATD median', fontsize=10)
    ax2.legend(loc="upper left", fontsize=9)
    ax2.xaxis.set_major_locator(MaxNLocator(nbins=8))
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    return fig

# Function to create initial graphs without predictions
def des_initial_graph_function(df):
    
    # Data preparation
    df['eater_request_timestamp_local'] = df['eater_request_timestamp_local'].dt.date

    df = df.groupby('eater_request_timestamp_local').agg(
        total_deliveries=('delivery_trip_uuid', 'count'),
        ATD_median=('ATD', 'median')).reset_index()

    df = df.sort_values(by='eater_request_timestamp_local', ascending=True)

    df.set_index('eater_request_timestamp_local', inplace=True)
    df.index = pd.DatetimeIndex(df.index.values, freq='D')
    
    # Creating the graphs
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(17, 3.5)) 

    ax1 = axes[0]
    ax1.plot(df.index, df['total_deliveries'], label="Total Deliveries", color="#276ef1", linestyle="-", marker="o", linewidth=2)
    
    ax1.set_title("Daily deliveries trend", fontstyle='italic', fontsize=11)
    ax1.set_xlabel('Periods', fontsize=10)
    ax1.set_ylabel('Daily deliveries', fontsize=10)
    ax1.legend(loc="upper left", fontsize=9)
    ax1.xaxis.set_major_locator(MaxNLocator(nbins=8))
    ax1.grid(True, linestyle='--', alpha=0.6)

    ax2 = axes[1]
    ax2.plot(df.index, df['ATD_median'], label="ATD median", color="#276ef1", linestyle="-", marker="o", linewidth=2)
    
    ax2.set_title("Daily ATD median trend", fontstyle='italic', fontsize=11)
    ax2.set_xlabel('Periods', fontsize=10)
    ax2.set_ylabel('Daily ATD median', fontsize=10)
    ax2.legend(loc="upper left", fontsize=9)
    ax2.xaxis.set_major_locator(MaxNLocator(nbins=8))
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    return fig

def des_visuals_hour_bars(filtered_df):
    
    # Preparing data for the bars
    daily_order_count = filtered_df.groupby('hour_of_day', observed=True).size().reset_index(name='Total_Deliveries')
    
    # Creating the bars
    sns.set_theme(style="darkgrid", font_scale=.5)
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 2.5)) 
    
    ax1 = axes[0]
    sns.boxplot(
        data=filtered_df, 
        x="hour_of_day", 
        y="ATD", 
        color="gray",
        showfliers=False,
        ax=ax1,
        boxprops={'alpha': 0.7}
    )
    ax1.set_xlabel("", fontweight='bold')
    ax1.set_xticklabels([])
    ax1.set_ylabel("ATD", fontweight='bold')
    ax1.set_title("ATD distribution by hour", fontstyle='italic')
    
    ax2 = axes[1]
    sns.barplot(
        data=daily_order_count,
        x="hour_of_day", 
        y="Total_Deliveries",
        color="#276ef1",
        ax=ax2,
        width=.7,
        alpha=.7
    )
    ax2.set_xlabel("", fontweight='bold')
    ax2.set_ylabel("Total deliveries", fontweight='bold')
    ax2.set_title("Total deliveries by hour", fontstyle='italic')
    ax2.set_xlabel("Hour of day", fontweight='bold')

    plt.tight_layout()
    return fig