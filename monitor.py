"""
f.turci@bristol.ac.uk - February 2023

FLOODS VISUALISER

"""

from urllib.request import urlopen
import json
import datetime 
from itertools import groupby
# use Bokeh for interactive plotting
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure,show
from bokeh.models import DatetimeTickFormatter
import numpy as np

root = "http://environment.data.gov.uk/flood-monitoring"
# Read station names 
stations_url = root+"/id/stations"
# store the response of URL
response = urlopen(stations_url)
# from url in data
json_stations = json.loads(response.read())
stations = json_stations['items']
# read the id of every station
station_ids = [s['stationReference'] for s in stations]


class Station:
    def __init__(self,reference):
        """
        Initialise station with reference id.
        """
        self.id = reference
        self.get_data()

    def get_data(self):
        """
        Retrieve data from a specific station.

        INPUT:
            station_id :    station reference

        RETURNS:
            data:           dictionary of measurements from station
        """

        # calculate start date (24 hours before now)
        now = datetime.datetime.now()
        since = now - datetime.timedelta(days=1)
        since_iso = since.strftime('%Y-%m-%dT%H:%M:%SZ')

        station_url = root+"/id/stations/"+self.id+f"/readings?since={since_iso}"
        self.station_url = station_url
        # get data
        response = urlopen(station_url)
        station_json = json.loads(response.read())
        
        # retrieve measurements abd values

        # use groupby to separate measurememnts
        
        self.json = station_json
        # sort the items
        items  = sorted(station_json['items'],key=lambda x:x['measure'])
        # group by measurements
        grouped_items = groupby(items, key=lambda x:x['measure'])
        
        self.measures = [key for key,group in groupby(items, key=lambda x:x['measure'])]
        self.values = {key:[element['value'] for element in list(group)] for key,group in groupby(items, key=lambda x:x['measure'])}
        self.times = {
            key:[
            datetime.datetime.strptime(element['dateTime'][:-1], '%Y-%m-%dT%H:%M:%S') for element in list(group)
            ] 
            for key,group in groupby(items, key=lambda x:x['measure'])
            }
        
        for key,group in groupby(items, key=lambda x:x['measure']):
            print(key,list(group))

        print("groupby",self.values)
        # print(station_json)
        # self.values = [item['value'] for item in station_json['items']]
        # self.times = [datetime.datetime.strptime(item['dateTime'][:-1], '%Y-%m-%dT%H:%M:%S')  for item in station_json['items']]

        # order = np.argsort(self.times)
        # self.values = np.array(self.values)[order]
        # self.times = np.array(self.times)[order]
        # print(self.times)
       
        # 




s = Station(station_ids[15])

print(s.station_url)
measure = s.measures[0]
dsource = ColumnDataSource(dict(x=s.times[measure],y=s.values[measure]))
# print(s.times)


# for k,item in enumerate(s.json['items']):
#     print(k, item['dateTime'])

# create a new plot with a title and axis labels
p = figure(title="Stations", x_axis_label="x", y_axis_label="y",x_axis_type='datetime')

# add a line renderer with legend and line thickness
p.line(x='x',y='y',source=dsource)
# p.xaxis.formatter=DatetimeTickFormatter(days="%m/%d",
# hours="%H",
# minutes="%H:%M")
# show the results
show(p)

