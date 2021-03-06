import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

import os
import seaborn as sns
from scipy import stats
import urllib.request
import math
import statistics

def df_cleanup(df_raw):
    df_clean = pd.DataFrame()
    for region in df_raw['Country/Region'].unique():
        # df_tmp = df_raw_confirmed.loc[df_raw_confirmed['Country/Region'] == region].sum().drop(['Province/State', 'Country/Region', 'Lat', 'Long'])
        df_tmp = df_raw.loc[df_raw['Country/Region'] == region].sum()
        df_clean[region] = pd.Series(df_tmp)
    df_clean = df_clean.drop(['Province/State', 'Country/Region', 'Lat', 'Long'], axis = 0)
    return df_clean

def find_highest(df):
    highest = df.iloc[-1].sort_values(ascending=False)[:10].index
    return highest

def diff_div(df):
    df_diff = df.diff(periods = 1)
    df_div = df.div(df.shift(1).replace(0,0.01)).fillna(value=0)
    return df_diff, df_div

def diff_div_it_be(df):
    df_diff_belgium, df_div_belgium = diff_div(df['Belgium'])
    df_diff_italy, df_div_italy = diff_div(df['Italy'])
    df_diff_it_be = pd.DataFrame([df_diff_belgium, df_diff_italy]).T
    df_div_it_be = pd.DataFrame([df_div_belgium, df_div_italy]).T
    return df_diff_it_be, df_div_it_be

def diff_div_jp_sk(df):
    df_diff_belgium, df_div_belgium = diff_div(df['Japan'])
    df_diff_italy, df_div_italy = diff_div(df['Korea, South'])
    df_diff_it_be = pd.DataFrame([df_diff_belgium, df_diff_italy]).T
    df_div_it_be = pd.DataFrame([df_div_belgium, df_div_italy]).T
    return df_diff_it_be, df_div_it_be

def plot(df, regions, xlabel, ylabel, title, x_size=25, y_size=10, log_scale='off', ymax='off'):
    plt.figure(figsize=(x_size, y_size))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if 'on' in ymax:
        plt.ylim((1, 1.75))
    plt.xticks(rotation=45)
    plt.grid()
    # plt.gca().set_yticks(np.arange(0, df.max().max(), df.max().max()/25))
    plt.rc('grid', linestyle=":", color='grey')
    for region in regions:
        x = df.index
        y = df[region]
        legend = df.iloc[0].index
        plt.plot(x, y, marker='o', label=region)
    if 'on' in log_scale:
        plt.yscale("log")
    plt.legend(loc="upper left", ncol=2, title="Legend", fancybox=True)
    pic_name = title+".jpg"
    plt.annotate('[Data source: https://github.com/CSSEGISandData/COVID-19]', (0, 0), (-140, -20), fontsize=6,
                 xycoords='axes fraction', textcoords='offset points', va='top')
    plt.savefig(pic_name)
    plt.show()

def yesterday_date():
    from datetime import datetime
    now = datetime.now()
    current_time_m = str(int(now.strftime("%m")))
    current_time_d = str(int(now.strftime("%d"))-1)
    current_time_y = now.strftime("%y")
    current_time = current_time_m + str('/') + current_time_d + str('/') + current_time_y
    return current_time

### MAPS ###

def df_cumulative(csv_name):
    df = pd.read_csv(csv_name)
    df = df.rename(columns={"Country/Region": "Country", "Province/State": "Province"})
    current_time = yesterday_date()
    total_list = df.groupby('Country')[current_time].sum().tolist()
    country_list = df["Country"].tolist()
    country_set = set(country_list)
    country_list = list(country_set)
    country_list.sort()
    new_df = pd.DataFrame(list(zip(country_list, total_list)), columns=['Country', 'Total_Cases'])
    return new_df

def plotly_world_map(df, locations='Country', z='Total_Cases', title='Reported Covid-19 Cases', col_bar_title='Reported Covid-19 Cases', figname='world_positive_map.html'):
    colors = ["#F9F9F5", "#FAFAE6", "#FCFCCB", "#FCFCAE",  "#FCF1AE", "#FCEA7D", "#FCD97D",
              "#FCCE7D", "#FCC07D", "#FEB562", "#F9A648",  "#F98E48", "#FD8739", "#FE7519",
              "#FE5E19", "#FA520A", "#FA2B0A", "#9B1803",  "#861604", "#651104", "#570303",]


    fig = go.Figure(data=go.Choropleth(
        locationmode = "country names",
        locations = df[locations],
        z = df[z],
        text = df[z],
        colorscale = colors,
        autocolorscale=False,
        reversescale=False,
        colorbar_title = col_bar_title,
    ))

    fig.update_layout(
        title_text=title,
        geo=dict(
            showcoastlines=True,
        ),
    )

    fig.write_html(figname, auto_open=True)
    return

# Data import
confirmed_name = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
death_name = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
recovered_name = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"

# DataFrame cleanup
df_confirmed = df_cleanup(pd.read_csv(confirmed_name))
df_death = df_cleanup(pd.read_csv(death_name))
df_recovered = df_cleanup(pd.read_csv(recovered_name))

# Top countries are selected
top_countries_confirmed = find_highest(df_confirmed)

# Plot of top countries
title = ["Confirmed", "Death", "Recovered"]
x_label = ["Date", "Date", "Date"]
y_label = ["People", "People", "People"]
df = [df_confirmed, df_death, df_recovered]

for i in range(len(title)):
    plot(df[i], top_countries_confirmed, x_label[i], y_label[i], title[i])

# Plots of diff and div on top countries
df_diff_confirmed, df_div_confirmed = diff_div(df_confirmed)
top_countries_diff_confirmed = find_highest(df_diff_confirmed)

# Plot of top countries
title = ["Diff. Confirmed", "Div. Confirmed"]
x_label = ["Date", "Date"]
y_label = ["People", "People"]
ymax = ['off', 'on']
df = [df_diff_confirmed, df_div_confirmed]

for i in range(len(title)):
    plot(df[i], top_countries_diff_confirmed, x_label[i], y_label[i], title[i], ymax=ymax[i])

# Plot of diff and div for top countries w/ moving average 3 days
title = ["Diff. Confirmed (Moving Avg. 3 days)", "Div. Confirmed"]
df_moving_avg = [df_diff_confirmed, df_div_confirmed.rolling(3).sum()]
for i in range(len(title)):
    plot(df[i], top_countries_diff_confirmed, x_label[i], y_label[i], title[i], ymax=ymax[i])

#-----------Top countries per milion
# Population of top countries
US_population = 327.2
Spain_population = 46.94
Italy_population = 60.36
France_population = 66.99
Germany_population = 83.02
China_population = 1386
UK_population = 66.65
Iran_population = 81.16
Turkey_population = 82
Belgium_population = 11.46

top_countries_population = [US_population,
                            Spain_population,
                            Italy_population,
                            France_population,
                            Germany_population,
                            China_population,
                            UK_population,
                            Iran_population,
                            Turkey_population,
                            Belgium_population]


df_top_10_per_mil = pd.DataFrame()
for i in range(len(top_countries_confirmed)):
    df_top_10_per_mil[top_countries_confirmed[i]] = df_confirmed[top_countries_confirmed[i]] / top_countries_population[i]

plot(df_top_10_per_mil, top_countries_confirmed, 'Date', 'People per milion citizens', 'Confirmed positives per milion citizens of the country')

#-----------

# Plot of Belgium and italy
df_diff_it_be, df_div_it_be = diff_div_it_be(df_confirmed)
regions = ["Belgium", "Italy" ]
title = ["Diff. Confirmed IT & BE", "Div. Confirmed IT & BE"]
x_label = ["Date", "Date"]
y_label = ["People", "People"]
ymax = ['off', 'on']
df = [df_diff_it_be, df_div_it_be]

for i in range(len(title)):
    plot(df[i], regions, x_label[i], y_label[i], title[i], ymax=ymax[i])

# Plot of Japan and South Korea
df_diff_jp_sk, df_div_jp_sk = diff_div_jp_sk(df_confirmed)
regions = ["Japan", "Korea, South" ]
title = ["Diff. Confirmed JP & SK", "Div. Confirmed JP & SK"]
x_label = ["Date", "Date"]
y_label = ["People", "People"]
ymax = ['off', 'on']
df = [df_diff_jp_sk, df_div_jp_sk]

for i in range(len(title)):
    plot(df[i], regions, x_label[i], y_label[i], title[i], ymax=ymax[i])


# US vs. EU
EU_countries = [
    'Austria',
    'Belgium',
    'Bulgaria',
    'Croatia',
    'Cyprus',
    'Czechia',
    'Denmark',
    'Estonia',
    'Finland',
    'France',
    'Germany',
    'Greece',
    'Hungary',
    'Ireland',
    'Italy',
    'Latvia',
    'Lithuania',
    'Luxembourg',
    'Malta',
    'Netherlands',
    'Poland',
    'Portugal',
    'Romania',
    'Slovakia',
    'Slovenia',
    'Spain',
    'Sweden'
]

df_confirmed_EU = df_confirmed[EU_countries].sum(axis=1)
df_confirmed_US = df_confirmed['US']

df = pd.concat([df_confirmed_EU, df_confirmed_US], axis=1, sort=False, ignore_index=True)
df.columns = ['EU', 'US']

plot(df, ['EU', 'US'], xlabel='Dates', ylabel='Positives', title='EU vs. US positive people')

# US vs. EU per milion people
US_population = 327.2
EU_population = 446
df_confirmes_EU_per_mil = df_confirmed_EU / EU_population
df_confirmes_US_per_mil = df_confirmed_US / US_population

df_per_mil = pd.concat([df_confirmes_EU_per_mil, df_confirmes_US_per_mil], axis=1, sort=False, ignore_index=True)
df_per_mil.columns = ['EU', 'US']

plot(df_per_mil, ['EU', 'US'], xlabel='Dates', ylabel='Positives per milion people', title='EU vs. US positives per milion people')

# in dev
def linear_regression(df):
    from sklearn.linear_model import LinearRegression
    x = np.array(range(66,len(df)+66)).reshape(-1,1)
    y = np.array(pd.Series(df)).reshape(-1,1)
    model = LinearRegression().fit(x, y)
    r_sq = model.score(x, y)
    x_pred_y0 = - model.intercept_ / model.coef_ - (x[-1] - x[0])
    x_pred = pd.Series(np.array(range(66, int(x_pred_y0) + 66)))
    y_pred = int(model.coef_) * x_pred + int(model.intercept_)
    return x_pred, y_pred, x_pred_y0

df = df_confirmed.Belgium.diff()[66:]
np.array(df_confirmed.Belgium[66:])
x_pred, y_pred, x_pred_y0 = linear_regression(df)


#### MAPS ###

cumulative_positive = df_cumulative(confirmed_name)
cumulative_death = df_cumulative(death_name)
cumulative_recovered = df_cumulative(recovered_name)

plotly_world_map(cumulative_positive, locations='Country', z='Total_Cases', title='Reported Covid-19 Cases', col_bar_title='Reported Covid-19 Cases', figname='docs/world_positive_map.html')
plotly_world_map(cumulative_death, locations='Country', z='Total_Cases', title='Reported Covid-19 Death', col_bar_title='Reported Covid-19 Death', figname='docs/world_death_map.html')
plotly_world_map(cumulative_recovered, locations='Country', z='Total_Cases', title='Reported Covid-19 Recovered', col_bar_title='Reported Covid-19 Recovered', figname='docs/world_recovered_map.html')