from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from urllib import request
import unittest
import os


app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


class Deployment(db.Model):
    __tablename__ = "deployments"

    task_id = db.Column(db.String(20), primary_key=True)
    vehicle_id = db.Column(db.String(20), nullable=False)
    time_task_created = db.Column(db.DateTime)
    time_task_resolved = db.Column(db.DateTime)

    def __init__(self, task_id, vehicle_id, time_task_created, time_task_resolved):
        self.task_id = task_id
        self.vehicle_id = vehicle_id
        self.time_task_created = time_task_created
        self.time_task_resolved = time_task_resolved


class Pickup(db.Model):
    __tablename__ = "pickups"

    task_id = db.Column(db.String(20), primary_key=True)
    vehicle_id = db.Column(db.String(20), nullable=False)
    qr_code = db.Column(db.String(6), nullable=False)
    time_task_created = db.Column(db.DateTime)
    time_task_resolved = db.Column(db.DateTime)

    def __init__(self, task_id, vehicle_id, qr_code, time_task_created, time_task_resolved):
        self.task_id = task_id
        self.vehicle_id = vehicle_id
        self.qr_code = qr_code
        self.time_task_created = time_task_created
        self.time_task_resolved = time_task_resolved


class Ride(db.Model):
    __tablename__ = "rides"

    ride_id = db.Column(db.String(20), primary_key=True)
    vehicle_id = db.Column(db.String(20), nullable=False)
    time_ride_start = db.Column(db.DateTime)
    time_ride_end = db.Column(db.DateTime)
    start_lat = db.Column(db.Numeric)
    start_lng = db.Column(db.Numeric)
    end_lat = db.Column(db.Numeric)
    end_lng = db.Column(db.Numeric)
    gross_amount = db.Column(db.Numeric, nullable=True)

    def __init__(self, ride_id, vehicle_id, time_ride_start, time_ride_end, start_lat, start_lng, end_lat, end_lng, gross_amount):
        self.ride_id = ride_id
        self.vehicle_id = vehicle_id
        self.time_ride_start = time_ride_start
        self.time_ride_end = time_ride_end
        self.start_lat = start_lat
        self.start_lng = start_lng
        self.end_lat = end_lat
        self.end_lng = end_lng
        self.gross_amount = (gross_amount if gross_amount != '' else None)


class Duplicate_Log(db.Model):
    __tablename__ = "duplicate_log"

    record_id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String)
    data_row = db.Column(db.String)
    data_key = db.Column(db.String)
    record_timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, table_name, data_row, data_key):
        self.table_name = table_name
        self.data_row = data_row
        self.data_key = data_key


class Rides_Analysis(db.Model):
    __tablename__ = "rides_analysis"

    vehicle_id = db.Column(db.String(20), primary_key=True, index=True)
    qr_code = db.Column(db.String(6), primary_key=True, index=True)
    result_to_render = db.Column(db.JSON)

    def __init__(self, vehicle_id, qr_code, result_to_render):
        self.vehicle_id = vehicle_id
        self.qr_code = qr_code
        self.result_to_render = result_to_render


class TestFunctions(unittest.TestCase):

    def test_all_lines_loaded(self):
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'data'))
        data_tables = ['deployments', 'pickups', 'rides']
        csv_non_blank_lines_count = 0

        for data_table in data_tables:
            data_table_dir = os.path.join(data_dir, data_table)
            for filename in os.listdir(data_table_dir):
                with open(os.path.join(data_table_dir, filename), 'r') as file:
                    for line_num, line in enumerate(file):
                        if line_num == 0:
                            continue
                        if line.strip():
                            csv_non_blank_lines_count += 1

        db_non_blank_lines_count = db.session.query(Deployment).count() + \
                                   db.session.query(Pickup).count() + \
                                   db.session.query(Ride).count() + \
                                   db.session.query(Duplicate_Log).count()

        self.assertEqual(csv_non_blank_lines_count, db_non_blank_lines_count)


@app.route("/")
def start_screen():
    result = """/api/vehicle_analysis/[vehicle_id or qr_code] to get a json with vehicle analysis. Deployment number
    and ride number fields represent the respective numbers in descending order ordered by the deployment/ride start time.
    <br><br>/api/duplicates to get a json with duplicates logged.
    <br><br>/api/stress_test to run a test with 5000 subsequent requests and get the time it took to process.
    <br><br>/api/test_all_lines_loaded to run a test comparing the number of lines in source csv files with the number
    of database records (including duplicates logged)."""
    return result


@app.route('/api/vehicle_analysis/<search_parameter>')
def get_vehicle_analysis(search_parameter):
    return jsonify(db.session.query(db.func.public.fn_get_vehicle_analysis(search_parameter)).all())


@app.route('/api/duplicates')
def get_duplicates():
    return jsonify(db.session.query(db.func.public.fn_get_duplicates()).all())


@app.route('/api/stress_test')
def get_stress_test_result():
    start_ts = datetime.datetime.now().timestamp()

    for i in range(5000):
        request.urlopen('http://localhost:5000/api/vehicle_analysis/F444GC').read()

    end_ts = datetime.datetime.now().timestamp()
    result = end_ts - start_ts
    return str(result) + " seconds it took to run 5000 requests."


@app.route('/api/test_all_lines_loaded')
def run_functional_tests():
    run_test = TestFunctions()
    run_test.test_all_lines_loaded()
    return "Test has passed successfully."


