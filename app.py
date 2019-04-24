from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import sqlalchemy
import datetime as dt 
from sqlalchemy import create_engine, func, inspect


####################CREATE THE DATABASE CONNECTION#############
engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)
#Reflect the existing database
Base=automap_base()
#reflect the tables in the DB
Base.prepare(engine,reflect=True)
#table references
Measurement = Base.classes.measurement
Station=Base.classes.station

#add the Session link to the DB
session = Session(engine)
#Fire up Flask
app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"<head><b>welcome to the best vacation ever API<br/></head></b>"
        
        f"<br/>"
        f"These are your available Routes:<br/>"
        f"<br>"
        f"A. / -- Thats this directory"
                f"<br>"
        f"B. /api/v1.0/precipitation -- Precipitation Data"
                        f"<br>"
        f"C. /api/v1.0/stations -- Directory of stations"
                        f"<br>"
        f"D. /api/v1.0/tobs -- Directory of Temperature Observations (TOBS)"
                                f"<br>"

        f"E. /api/v1.0/<start> -- Date range search with only start date. <b>Enter Dates in this format 2012-02-28</b>"
                                f"<br>"

        f"F. /api/v1.0/<start>/<end> -- Date range search: <b>Enter Dates in this format 2012-02-28/2012-02-28"
        
    )

@app.route("/api/v1.0/stations")
def stations():
        #Query and Pull all the stations
        station_list = []
        station_count = session.query(Station)
        for station in station_count:
            station_list.append(station.station)
        return jsonify(station_list)

@app.route("/api/v1.0/precipitation")
def precipitation():
        #gather precipitation data from 1 year back and extract the first date
        first = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
        first = first[0]
        #Calculate the date one year behind
        year_ago = dt.datetime.strptime(first,"%Y-%M-%d") -dt.timedelta(days=365)
        #Hit the database with a query
        one_yr_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > year_ago).\
        order_by(Measurement.date)
        #convert to a List
        pprcp_list = dict(one_yr_data)
        #Jsonify
        return jsonify(pprcp_list)

@app.route("/api/v1.0/tobs")
def tobs():
        #this is essnetiall the same as precipitation Route
        #gather precipitation data from 1 year back and extract the first date
        first = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
        #get the first value in of first for reference
        first = first[0]
        #Calculate the date one year behind
        year_ago = dt.datetime.strptime(first,"%Y-%M-%d") -dt.timedelta(days=365)
        #Hit the database with a query
        one_yr_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > year_ago).\
        order_by(Measurement.date)
        #convert to a List
        pprcp_list = list(one_yr_data)
        #Jsonify
        return jsonify(pprcp_list)

@app.route("/api/v1.0/<start>")
def start(start=None):
    start_date = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), 
    func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    start_date=list(start_date)
    return jsonify(start_date)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    
    date_range = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    date_range=list(date_range)
    return jsonify(date_range)

if __name__=="__main__":
    app.run(debug=True)

