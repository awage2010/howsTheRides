# howsTheRides
Turbulence forecasting
turbulence_db.py scrapes the NWS GTG database for the last group of turbulence forecasts and saves them in a local folder for processing.

draw_gif.py takes the raw GRIB files, categorizes them by time and altitude, then draws a gif based on input parameters.

route_decode.py will instantiate any point, route, or STAR/SID as an object that can be used to formulate waypoints for a route string via the route_decode function. The instantiation of objects utilizes the FAA NASR files to find the specifications of each category of the route structure.
