"""
f.turci@bristol.ac.uk - February 2023

FLOODS VISUALISER

"""

from urllib.request import urlopen
import json
import datetime 
import pandas as pd
from itertools import groupby
# use Bokeh for interactive plotting
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure,show,curdoc
from bokeh.models import DatetimeTickFormatter, Dropdown ,AutocompleteInput,Div
from bokeh.layouts import column, row


root = "http://environment.data.gov.uk/flood-monitoring"
# Read station names 
stations_url = root+"/id/stations"
print(stations_url)
# store the response of URL
response = urlopen(stations_url)
# from url in data
json_stations = json.loads(response.read())
stations = json_stations['items']
print(list(stations[0].keys()))
# read the id of every station
station_ids = [s['notation'] for s in stations]

class Station:
    def __init__(self,reference):
        """
        Initialise station with reference id.
        """
        self.id = reference
        self.get_data()
        print("Checking station",self.id)
        print("Data from", self.station_url)

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
        
        station_json = json.load(response)
        print(station_url)
        self.times = {}
        self.values = {}

        if len(station_json['items'])==0:
            self.message = f"No measurements available at {self.id}."
            self.measures =['none']
            self.times['none'] = []
            self.values['none'] = []
        else:
            self.message = f"{len(station_json['items'])} measurements found at {self.id}."
                  # retrieve measurements and values
            self.json = station_json
            # construct pandas dataframe
            self.df = pd.json_normalize(station_json['items'])
            self.df.sort_values(by='dateTime', inplace = True) 
    
            # retrieve all measure names
            self.measures = self.df['measure'].unique()
            # store measurements

            for m in self.measures:
                selection = self.df.query(f'measure == @m')
                self.times[m] = pd.to_datetime(selection['dateTime'])
                self.values[m] = selection['value']

s = Station(station_ids[70])

measure = s.measures[0]
dsource = ColumnDataSource(dict(x=s.times[measure],y=s.values[measure]))

# create a new plot with a title and axis labels
# print(measure.split("/")[-1])
p = figure(
    title="Flood monitoring", 
    x_axis_label="time", 
    y_axis_label='level [m]',
    x_axis_type='datetime',
    width=550,
    height=350
    )

def update_selected(wttr,old,new):
    s = Station(new)
    measure = s.measures[0]
    dsource.data = dict(x=s.times[measure],y=s.values[measure])
    log.text =s.message

p.line(x='x',y='y',source=dsource)

autocomplete = AutocompleteInput(title="Enter a station reference (e.g. 0020):", completions=station_ids)
autocomplete.on_change('value',update_selected)
log = Div(text=s.message)
layout = row(p,column(autocomplete,log))
curdoc().title = "Flood Monitor"
curdoc().add_root(layout)

