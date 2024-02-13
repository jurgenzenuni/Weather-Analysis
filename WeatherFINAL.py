import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

path_to_folder = 'D:/coding/Python/WeatherAnalysis/'
file_name = '3308704.csv'
df_weather = pd.read_csv(path_to_folder + file_name)

path_to_folder2 = 'D:/coding/Python/WeatherAnalysis/'
file_name2 = 'collisions.csv'
df_crashes = pd.read_csv(path_to_folder2 + file_name2)

df_weather['TAVG'] = df_weather[['TMIN','TMAX']].mean(axis=1)#rows (axis=0) or columns (axis=1). In this case, setting axis=1 in the mean function tells pandas to calculate the mean across columns.
df_weather = df_weather[df_weather["DATE"].astype(str).str.startswith(('2019', '2020', '2021', '2022'))][["DATE", "TAVG", "AWND", "SNOW", "PRCP", "WT01"]]
df_weather = df_weather.rename(columns={'WT01': 'FOG'})

df_crashes = df_crashes.rename(columns={'CRASH DATE': 'DATE'})
df_crashes['DATE'] = pd.to_datetime(df_crashes['DATE'], format='%m/%d/%Y')
df_crashes['DATE'] = df_crashes['DATE'].dt.strftime('%Y-%m-%d')

df_crashes = df_crashes[(df_crashes['DATE'].astype(str).str.startswith(('2019', '2020', '2021', '2022')))
                         & (df_crashes['BOROUGH'] == 'MANHATTAN')][['DATE', 'BOROUGH', 'COLLISION_ID' ,'NUMBER OF PERSONS INJURED', 'NUMBER OF PERSONS KILLED', 'VEHICLE TYPE CODE 1', 'VEHICLE TYPE CODE 2']]

df_numacc = df_crashes.groupby('DATE')['BOROUGH'].count().reset_index(name='# OF ACCIDENTS')

merged_df = pd.merge(df_weather, df_numacc, on='DATE')
#print(merged_df)

# Simple crash plots showing trends of # of accidents over the last 4 years
plt.plot(df_numacc['DATE'], df_numacc['# OF ACCIDENTS'])
plt.title('Number of Accidents in Manhattan (2019-2022)')
plt.xlabel('Date')
plt.ylabel('Number of Accidents')
plt.show()

# Pie chart showing whether more accidents happen on warmer or colder days, based on the avg temp of the top 50 days in terms of # of accidents
daily_stats = merged_df.groupby('DATE').agg({'# OF ACCIDENTS': 'sum', 'TAVG': 'mean'})
top_50 = daily_stats.sort_values('# OF ACCIDENTS', ascending=False).head(50)
top_50 = top_50.reset_index()
top_50 = top_50.rename(columns={'DATE': 'Date', '# OF ACCIDENTS': 'Num of Accidents', 'TAVG': 'Avg Temp'})
avg_temp = top_50['Avg Temp'].mean()
warmer = top_50[top_50['Avg Temp'] >= avg_temp]['Num of Accidents'].sum()
colder = top_50[top_50['Avg Temp'] < avg_temp]['Num of Accidents'].sum()
labels = ['Warmer', 'Colder']
values = [warmer, colder]
plt.pie(values, labels=labels, autopct='%1.1f%%')
plt.title('Accidents on Warmer vs. Colder Days, for the top 50 days(# of accidents)')
plt.axis('equal')
plt.text(1.2, 0, f'Avg Temp: {avg_temp:.1f}°F', fontsize=12)
plt.show()

# bar chart showing number of accidents for different types of weather conditions
weather_types = ['Clear', 'Rainy', 'Snowy', 'Foggy']
num_accidents_by_weather = []
for weather in weather_types:
    if weather == 'Clear':
        num_accidents_by_weather.append(merged_df[(merged_df['PRCP'] == 0) & (merged_df['SNOW'] == 0) & (merged_df['FOG'].isnull())]['# OF ACCIDENTS'].sum())
    elif weather == 'Rainy':
        num_accidents_by_weather.append(merged_df[(merged_df['PRCP'] > 0) & (merged_df['SNOW'] == 0)]['# OF ACCIDENTS'].sum())
    elif weather == 'Snowy':
        num_accidents_by_weather.append(merged_df[merged_df['SNOW'] > 0]['# OF ACCIDENTS'].sum())
    elif weather == 'Foggy':
        num_accidents_by_weather.append(merged_df[merged_df['FOG'] > 0]['# OF ACCIDENTS'].sum())
        
plt.bar(weather_types, num_accidents_by_weather, color=['yellowgreen', 'lightskyblue', 'blue', 'grey'], edgecolor='black')
plt.title('Number of Accidents by Weather Condition')
plt.xlabel('Weather Condition')
plt.ylabel('Number of Accidents')
plt.show()


#Foggy or not and avg num of accidents 
fog_days = merged_df.loc[merged_df['FOG'] > 0]
fog_days_accidents = fog_days['# OF ACCIDENTS'].mean()
no_fog_days = merged_df.loc[(merged_df['FOG'] == '') | (merged_df['FOG'].isnull())]
no_fog_days_accidents = no_fog_days['# OF ACCIDENTS'].mean()
plt.bar(['fog days','No Fog Days'], [fog_days_accidents, no_fog_days_accidents])
plt.title('Average Number of Accidents by fog Conditions')
plt.xlabel('fog Conditions')
plt.ylabel('Average Number of Accidents')
for i, v in enumerate([fog_days_accidents, no_fog_days_accidents]):
    plt.text(i, v + 0.5, '{:.2f}'.format(v), ha='center')
plt.show()

# Bar graph showing avg number of accidents for days where it snows, doesnt snow and snows more than 5 inches
feb_1 = merged_df.loc[merged_df['DATE'] == '2021-02-01']
feb_1_avg_accidents = feb_1['# OF ACCIDENTS'].mean()
snow_days2 = merged_df.loc[merged_df['SNOW'] > 5.0]
snow2_avg_accidents = snow_days2['# OF ACCIDENTS'].mean()
snow_days = merged_df.loc[merged_df['SNOW'] > 0]
snow_avg_accidents = snow_days['# OF ACCIDENTS'].mean()
no_snow_days = merged_df.loc[merged_df['SNOW'] == 0]
no_snow_avg_accidents = no_snow_days['# OF ACCIDENTS'].mean()
plt.bar(['> 5.0 inches','Snowy Days', 'Non-Snowy Days', ' highest snow day, 2/1/21 (14.8inches)'], [snow2_avg_accidents ,snow_avg_accidents, no_snow_avg_accidents, feb_1_avg_accidents])
plt.title('Average Number of Accidents by Snow Conditions')
plt.xlabel('Snow Conditions')
plt.ylabel('Average Number of Accidents')
for i, v in enumerate([snow2_avg_accidents ,snow_avg_accidents, no_snow_avg_accidents, feb_1_avg_accidents]):
    plt.text(i, v + 0.5, '{:.2f}'.format(v), ha='center')
plt.show()

# bar graph showing avg num of accidents for days when its raining and not.
sept_1 = merged_df.loc[merged_df['DATE'] == '2021-09-01']
sept_1_avg_accidents = sept_1['# OF ACCIDENTS'].mean()
rain_days2 = merged_df.loc[merged_df['PRCP'] > 1.50]
rain2_avg_accidents = rain_days2['# OF ACCIDENTS'].mean()
rain_days = merged_df.loc[merged_df['PRCP'] > 0]
rain_avg_accidents = rain_days['# OF ACCIDENTS'].mean()
no_rain_days = merged_df.loc[merged_df['PRCP'] == 0]
no_rain_avg_accidents = no_rain_days['# OF ACCIDENTS'].mean()
plt.bar(['rain > 1.5 inches','rainy days', 'Not rainy days', 'Rainiest day, 9/1/21 (7.13 inches)'], [rain2_avg_accidents,rain_avg_accidents, no_rain_avg_accidents, sept_1_avg_accidents])
plt.title('Average number of accidents by rain conditions')
plt.xlabel('Rain conditions')
plt.ylabel('Average number of accidents')
for i, v in enumerate([rain2_avg_accidents,rain_avg_accidents, no_rain_avg_accidents, sept_1_avg_accidents]):
    plt.text(i, v + 0.5, '{:.2f}'.format(v), ha='center')
plt.show()

#top 75 days in terms of accidents and what types of conditions were going on in those days
top_75 = merged_df.nlargest(75, '# OF ACCIDENTS')
snow_days = top_75[top_75['SNOW']>0]['DATE'].count()
rain_days = top_75[top_75['PRCP']>0]['DATE'].count()
fog_days = top_75[top_75['FOG']>0]['DATE'].count()
warmer_days = top_75[top_75['TAVG']> 60]['DATE'].count()
colder_days = top_75[top_75['TAVG']< 60]['DATE'].count()
clear_days = top_75[(top_75['PRCP']==0) & (top_75['FOG'].isnull()) & (top_75['SNOW']==0)]['DATE'].count()
labels = ['Snow', 'Rain', 'Fog', 'Warmer days(TAVG>60)', 'Colder days(TAVG<60)' ,'Clear']
counts = [snow_days, rain_days, fog_days, warmer_days, colder_days, clear_days]
colors = ['lightblue', 'lightgreen', 'gray', 'red','blue', 'lightyellow']
counts = [0 if x < 0 else x for x in counts]
plt.bar(labels, counts, color=colors)
plt.title('Weather conditions on top 75 accident days')
plt.xlabel('Weather conditions')
plt.ylabel('Count')
for i, v in enumerate(counts):
    plt.text(i, v + 0.5, str(v), ha='center')
plt.show()

