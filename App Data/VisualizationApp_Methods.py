import numpy as np
import math
from netCDF4 import Dataset
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
from time import sleep
from plotly.offline import plot
import os
import webbrowser
import math
from geopy.geocoders import Nominatim
from scipy.optimize import curve_fit

#Set path holding necesary files
PATH = "/Users/metaslowly/Desktop/SeaLevelVisualization/"

#Create folder for html figures
folder_name = "templates"

if not os.path.exists(folder_name):
    os.makedirs(folder_name)


#Read sea level data
More_Data = PATH+"csiro_recons_gmsl_yr_2015_csv.csv"
moreDta=[]
with open(More_Data) as fobj:
  lst = [[int(line.split(',')[0][:4]), float(line.split(',')[1])/100] for line in fobj]

#separate data into two lists
years = [d[0] for d in lst]
seaLevels = [d[1] for d in lst]

# Define the function to fit the data
def func(x, a, b, c, d, e):
    return a * x**4 + b * x**3 + c * x**2 + d * x + e

# Perform the curve fitting
popt, pcov = curve_fit(func, years, seaLevels)

#create list with wanted years
yearsList = []
for i in range(1850, 2201):
  yearsList.append(i)
yearsList = np.array(yearsList)

#create year level estimates
yearsLevelList = func(yearsList, *popt)

#Create final 2d Array
SeaLevels = []
i = 0
for year in yearsList:
  new_seaLevel = [yearsList[i],yearsLevelList[i]]
  SeaLevels.append(new_seaLevel)
  i = i + 1

#Adjust array to etopo sea level (level in year 1984)
for i in SeaLevels:
  if i[0]==1984:
    difference=i[1]
    break
for i in lst:
  i[1]= round(i[1]-difference, 3)

dataFile = PATH+"ETOPO1_Ice_g_gdal.grd"
firstRead=True
def Etopo(lon_area, lat_area, resolution):
  ### Input
  # resolution: resolution of topography for both of longitude and latitude [deg]
  # (Original resolution is 0.0167 deg)
  # lon_area and lat_area: the region of the map which you want like [100, 130], [20, 25]
  ###
  ### Output
  # Mesh type longitude, latitude, and topography data
  ###
  global firstRead, lat1, lon1, topo1, spacing
  if firstRead:
    # Read NetCDF data
    data = Dataset(dataFile, "r")
    # Get data
    lon_range = data.variables['x_range'][:]
    lat_range = data.variables['y_range'][:]
    #topo_range = data.variables['z_range'][:]
    spacing = data.variables['spacing'][:]
    dimension = data.variables['dimension'][:]
    z = data.variables['z'][:]

    lon_num = dimension[0]
    lat_num = dimension[1]
    
    # Prepare array
    lon_input = np.zeros(lon_num); lat_input = np.zeros(lat_num)
    for i in range(lon_num):
        lon_input[i] = lon_range[0] + i * spacing[0]
    for i in range(lat_num):
        lat_input[i] = lat_range[0] + i * spacing[1]

    # Create 2D array
    lon1, lat1 = np.meshgrid(lon_input, lat_input)
    
    # Convert 2D array from 1D array for z value
    topo1 = np.reshape(z, (lat_num, lon_num))

    firstRead=False
    
  lon, lat, topo = secondEtopo(lon_area, lat_area, resolution, spacing, lon1, lat1, topo1)

  return lon, lat, topo

#Etopo function has been split for faster running since first function only runned once
def secondEtopo(lon_area, lat_area, resolution, spacing, lon, lat, topo):
  # Skip the data for resolution
  if ((resolution < spacing[0]) | (resolution < spacing[1])):
    print('Set the highest resolution')
  else:
    skip = int(resolution/spacing[0])
    lon = lon[::skip,::skip]
    lat = lat[::skip,::skip]
    topo = topo[::skip,::skip]
  
  topo = topo[::-1]
  
  # Select the range of map
  range1 = np.where((lon>=lon_area[0]) & (lon<=lon_area[1]))
  lon = lon[range1]; lat = lat[range1]; topo = topo[range1]
  range2 = np.where((lat>=lat_area[0]) & (lat<=lat_area[1]))
  lon = lon[range2]; lat = lat[range2]; topo = topo[range2]
  
  # Convert 2D again
  lon_num = len(np.unique(lon))
  lat_num = len(np.unique(lat))
  lon = np.reshape(lon, (lat_num, lon_num))
  lat = np.reshape(lat, (lat_num, lon_num))
  topo = np.reshape(topo, (lat_num, lon_num))

  return lon, lat, topo
   
#Method to change degrees into radians
def degree2radians(degree):
  # convert degrees to radians
  return degree*np.pi/180
  
#To change data from 2d map to 3d coordinates
def mapping_map_to_sphere (lon, lat, radius=1):
  # this function maps the points of coords (lon, lat) to points onto the sphere of radius radius
  lon=np.array(lon, dtype=np.float64)
  lat=np.array(lat, dtype=np.float64)
  lon=degree2radians(lon)
  lat=degree2radians(lat)
  xs=radius*np.cos(lon)*np.cos(lat)
  ys=radius*np.sin(lon)*np.cos(lat)
  zs=radius*np.sin(lat)
  return xs, ys, zs


# Select the area you want
#This might be what we change whith the individual part rendering
resolution = 0.8
lon_area = [-180., 180.]
lat_area = [-90., 90.]

#Create spheric dataset with topography values
def TopoSphere(i, xs, ys, zs, topo):
  
  topo_sphere=dict(type='surface',
    x=xs,
    y=ys,
    z=zs,
    colorscale=Ctopo,
    surfacecolor=topo-i,
    cmin=cmin,
    cmax=cmax)
  return topo_sphere

#generate data with given range and resolution
def regenerateData(resolution, lon_area, lat_area, i):

  lon_topo, lat_topo, topo = Etopo(lon_area, lat_area, resolution)
  xs, ys, zs = mapping_map_to_sphere(lon_topo, lat_topo)  
  topo_sphere=TopoSphere(i, xs, ys, zs, topo)

  return topo_sphere

#Define Topography colour and range
Ctopo = [[0, 'rgb(0, 0, 70)'],[0.2, 'rgb(0,90,150)'], 
          [0.4, 'rgb(150,180,230)'], [0.5, 'rgb(210,230,250)'],
          [0.50001, 'rgb(0,120,0)'], [0.57, 'rgb(220,180,130)'], 
          [0.65, 'rgb(120,100,0)'], [0.75, 'rgb(80,70,0)'], 
          [0.9, 'rgb(200,200,200)'], [1.0, 'rgb(255,255,255)']]
cmin = -8000
cmax = 8000

#get first topographic data
topo_sphere = regenerateData(resolution, lon_area, lat_area, 0)

#define axis
noaxis=dict(showbackground=False,
  showgrid=False,
  showline=False,
  showticklabels=False,
  ticks='',
  title='',
  zeroline=False)

#Define title and bg colour
titlecolor = 'white'
bgcolor = 'black'

#Define layout for data
layout = go.Layout(
  autosize=False, width=1200, height=800,
  title = 'Sea level evolution',
  titlefont = dict(family='Courier New', color=titlecolor),
  showlegend = True,
  scene = dict(
    xaxis = noaxis,
    yaxis = noaxis,
    zaxis = noaxis,
    aspectmode='data',
    aspectratio=go.layout.scene.Aspectratio(
      x=1, y=1, z=1)),
  paper_bgcolor = bgcolor,
  plot_bgcolor = bgcolor,
  dragmode=False
)




#make everything into methods
#list of leasons learned
#fill code with comments
year=1984
x=1
y=0
z=0
zoomCount = 0
zoomArray = [1, 0.8, 0.68, 0.58, 0.5, 0.4]
x=1
y=0
z=0
r = np.sqrt(x**2 + y**2 + z**2)
i=0
res = 0.8
size = 90

#Methods for movement
#Figure will not show until StartVisualization or UpdateView is called
def lat_long_to_cartesian(latitude, longitude):
    # Convert latitude and longitude to radians
    lat_r = math.radians(latitude)
    long_r = math.radians(longitude)

    # Convert to Cartesian coordinates
    x = math.cos(lat_r) * math.cos(long_r)
    y = math.cos(lat_r) * math.sin(long_r)
    z = math.sin(lat_r)

    # Scale to range [-1, 1]
    x = 2 * (x - (-1)) / (1 - (-1)) - 1
    y = 2 * (y - (-1)) / (1 - (-1)) - 1
    z = 2 * (z - (-1)) / (1 - (-1)) - 1

    return x, y, z
def rotPhi(phi, n):
  phi_new  = phi + np.radians(n)
  return phi_new
def rotTheta(theta, n):
  theta_new = theta + np.radians(n)
  return theta_new
def getCoordinates(r, phi, theta):
  x_new = r * np.sin(theta) * np.cos(phi)
  y_new = r * np.sin(theta) * np.sin(phi)
  z_new = r * np.cos(theta)
  return x_new, y_new, z_new
def getPlaceXYZ(place):
    global geolocator
    global theta, phi
    location = geolocator.geocode(place)
    x, y, z = lat_long_to_cartesian(location.latitude, location.longitude)
    theta = np.arctan2(np.sqrt(x**2 + y**2), z)
    phi = np.arctan2(y, x)
    return x, y, z

#Create first figure with default city
fig = go.Figure(data=topo_sphere, layout=layout)
geolocator = Nominatim(user_agent="geoapiExercises")
city = "cadiz"
x, y, z = getPlaceXYZ(city)
#Adjust theta & phi
theta = np.arctan2(np.sqrt(x**2 + y**2), z)
phi = np.arctan2(y, x)

#method to be called from web to start visualization
def startVisualization():
    global fig
    updateView(fig)
    return

#Horizontal methods to be called from web
def rotRight():
    rotHorizontal(1)
def rotLeft():
    rotHorizontal(-1)
    
#Vertical methods to be called from web
def rotUp():
    rotVertical(-1)  
def rotDown():
    rotVertical(1)

#Methods to zoom in and out
def zoomIn():
    #define global variables
    global phi, x, y, z, theta, lat, lon, r, res, size, zoomCount
    
    if zoomCount < 5:
        #Change zoom count and get radius for visualization
        zoomCount = zoomCount + 1
        r = zoomArray[zoomCount]
        x, y, z = getCoordinates(r, phi, theta)

        if zoomCount == 5:
            #change res and size of data in figure
            res = 0.18
            size = 2
            lat, lon = getLatLon()
            #update visualization
            superUpdate(True, lat, lon)
        elif zoomCount == 4:
            #change res and size of data in figure
            res = 0.6
            size = 5
            lat, lon = getLatLon()
            #update visualization
            superUpdate(True,  lat, lon)
        else:
            updateView(fig)    
def zoomOut():
    global phi, x, y, z, theta, lat, lon, r, res, size, zoomCount

    
    if zoomCount > 0:
        #Change zoom count and get radius for visualization
        zoomCount = zoomCount - 1
        r = zoomArray[zoomCount]
        x, y, z = getCoordinates(r, phi, theta)
    
        if zoomCount == 4:
            #change res and size of data in figure
            res = 0.6
            size = 5
            lat, lon = getLatLon()
            #update visualization
            superUpdate(True, lat, lon)
        elif zoomCount == 3:
            #change res and size of data in figure
            res = 0.8
            size = 90
            lat, lon = getLatLon()
            #update visualization
            superUpdate(True, lat, lon)
        else:
            updateView(fig)

#updateSeaLevel will rise sea level of topography by m meters (m can be negative)
def updateSeaLevel(m):
    global fig, lat, lon, lat_area, lon_area, i
    i = m
    lat, lon = getLatLon()
    lon_area = [lon-size*2, lon+size*2]
    lat_area = [lat-size, lat+size]
    plot_data=[regenerateData(res, lon_area, lat_area, i)]
    fig = go.Figure(data=plot_data, layout=layout)
    updateView(fig)
#updateSeaLevelYear will return sea level rise of corresponding year inside estimation
def updateSeaLevelYear(y):
    global year
    if y<2201 and y>1849:
       #if y in range get sea level from corresponding possition
       l=SeaLevels[y-1850][1]
       year = y
       updateSeaLevel(l)

#changes center of the visualization to any given city of country...
def updateCenter(place):
    global x, y, z, fig, lat, lon
    x, y, z = getPlaceXYZ(place)
    if zoomCount > 3:
        lat, lon = getLatLon()
        x, y, z = getCoordinates(zoomArray[zoomCount], phi, theta)
        superUpdate(True, lat, lon)
    else:
        updateView(fig)

def showSeaLevelGraph():
   #Visualize data
    data = {
        'year': (i[0] for i in SeaLevels),
        'level': (i[1] for i in SeaLevels)
        }
    df = pd.DataFrame(data)
    fig = px.line(df, x=df['year'], y=df['level'])
    fig.show()

#methods to run 
def rotHorizontal(p):
    global phi, x, y, z, theta, lat, lon, r
    n=30*(r**3.5)
    phi = rotPhi(phi, n*p)
    x, y, z = getCoordinates(r, phi, theta)
    if(zoomCount>3):
        lat, lon = getLatLon()
        superUpdate(True, lat, lon)
    else:
        updateView(fig)
def rotVertical(p):
    global phi, x, y, z, theta, lat, lon, r
    n=10*(r**3.5)
    theta = rotTheta(theta, n*p)
    x, y, z = getCoordinates(r, phi, theta)

    if(zoomCount>3):
        lat, lon = getLatLon()
        superUpdate(True, lat, lon)
    else:
        updateView(fig)

#methods to update view and data
def superUpdate(updateSection, lat, lon):
    global size, res
    if updateSection:
      if size == 90:
        lon_area = [-180., 180.]
        lat_area = [-90., 90.]    
      else:
        lon_area = [lon-size*2, lon+size*2]
        lat_area = [lat-size, lat+size]
      plot_data=[regenerateData(res, lon_area, lat_area, i)]
      fig = go.Figure(data=plot_data, layout=layout)
      updateView(fig)
    else:
      updateView(fig)
def updateView(fig):
    global year
    fig.update_layout(scene_camera_eye=dict(x=x, y=y, z=z), title='Sea Visualization ({})'.format(year), titlefont = dict(family='Courier New', color=titlecolor))
    fig.write_html(PATH+"/templates/figure.html")
    webbrowser.open('file://' + os.path.realpath(PATH+"/templates/figure.html"))

#get lat and lon using global theta and phi
def getLatLon():
    global phi, theta, size
    xOut, yOut, zOut = getCoordinates(1, phi, theta)
    lat = math.asin(zOut / 1)
    lon = math.atan2(yOut, xOut)
    lat = math.degrees(lat)
    lon = math.degrees(lon)
    return lat, lon

#Demo test calling methods
startVisualization()
sleep(3)
zoomIn()
sleep(3)
zoomIn()
sleep(3)
zoomIn()
sleep(3)
zoomIn()
sleep(3)
updateCenter("puerto rico")
sleep(3)
rotLeft()
sleep(3)
zoomIn()
sleep(3)
updateSeaLevelYear(1850)
sleep(3)
updateSeaLevelYear(2000)
sleep(3)
updateSeaLevelYear(2200)
sleep(3)
