# InteractiveSeaLevel_Group_62
## Description
This website displays sea level data in a visually appealing and interactive way using Python.
The application allows users to enter a location and date, and the 3D world visualization will move to that location, and display the sea level changes for the given date. The application uses an ETOPO database and multiple sea level databases to provide accurate visualizations.

## Using the Application
When you access the website, you will be presented with a form that allows you to enter a location and select a time range. After submitting the form, the website will show the sea level data for the selected location and time range on the 3D visualitation.

You can interact with the graph by hovering over data points to see more information, zooming in and out, and panning to different areas of the graph.

## Additional Features
In addition to visualizing sea level changes, this web application also includes the following features:

Multiple Sea Level Databases: The application uses multiple sea level databases to provide more accurate and comprehensive visualizations.
Data Sources: The ETOPO database provides the topography data, while the sea level databases provide the sea level rise data.
Adjustable Sea Level Rise: The application allows users to adjust the sea level rise value to see how it affects sea levels at different locations.

## Etopo Data

https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/ice_surface/grid_registered/netcdf/

## Kanban board

https://zube.io/group-project-4/interactive-sea-level-group-62/w/must/kanban

## Coding

The Sea Level Rise visualisation web page runs on the server using the Flask implementation. Flask is a framework written in Python, which can create web pages with a small number of code lines due to its minimalist style. Flask allows us to run Python inside the HTML and CSS files. These files and the main.py file's interconnection is the one that forms this web page. Main.py is the main file which contains all flask functionalities. Html contains the code which forms the web age, and CSS is in charge of the style and design.  

The files in charge of running the visualization and all functionalities are written in Python. All this coding is divided into two main parts. 

The first one is in charge of accessing the data saved on the ETOPO 1 database, which is the one that contains all the coordinates and topography data. These values are stored in three different arrays in a 2D format. The values from the arrays are then converted into 3D to create the globe. Then a cartographic representation technique is used to distinguish different altitudes and sea levels. Due to the limited amount of RAM lower resolution of the globe will skip coordinates data. 

The second one keeps all the functionalities working. Different functionalities are available in this visualization. For example, the programme allows the user to move around the globe and test out different sea levels. These sea levels are obtained by storing data from different sources in different arrays, and by combining all of them we can get the sea level rise values from 1850 till nowadays. Moreover, using mathematical precautions, we can predict the sea level rise values and add them to the array created before.

To sum up, the code is divided into three parts. The first one is the files in charge of creating the web page and running the programme. The second one is the one in charge of creating the visualization. And the last one implements all the functionalities of the visualisation created.

## Usage of the server

In order to use the server, copy the server folder into the server host machine. Create a virtual enviroment and use the following code

```
source venv/bin/activate
python main.py
```

This will use all the code in world.py in order to create the visualizations. Please do have a look at the world.py.

## Limitations 

1 - Resolution of the data: The resolution of the 3D visualitation is limited. Even at it's maximun resolution, etopo data set makes it dificult to differentiate where then coastline starts. 
2 - Performance: The webside go slowlier than expected.  
3 - Database: Etopo and sea level database are use. Extra database could be add to develop futher fitures.
4 - Webside: We had develop the code for interacting with the 3D visualitation, creating the fetures to make that possible on the website has been a limitation. Futhermore, each time that the user ask for a place or date, the 3D visualitation is open into another window, being a limitation. 
5 - Animation of the historic values: The fact that an animation during years can be done is a limitation. A timelaps tool could be create.

