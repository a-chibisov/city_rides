from flask.cli import FlaskGroup
from project import app, db, Duplicate_Log, Deployment, Pickup, Ride
import os


cli = FlaskGroup(app)


def Load_Data(file_name):
    with open(file_name, 'r') as data:
        return [i.replace('\n', '').split(',') for i in data.readlines()[1:]]


@cli.command("create_db")
def create_db():
    # Create DB and tables
    db.drop_all()
    db.create_all()
    db.session.commit()
    engine = db.create_engine(os.getenv('DATABASE_URL'), {})

    # Create functions
    sql_scripts_dir = os.path.abspath(os.path.dirname(__file__)) + '/sql_scripts'

    with open(os.path.join(sql_scripts_dir, 'fn_calculate_distance.sql'), 'r') as file:
        escaped_sql = db.text(file.read())
        engine.execute(escaped_sql)

    with open(os.path.join(sql_scripts_dir, 'fn_get_vehicle_analysis.sql'), 'r') as file:
        escaped_sql = db.text(file.read())
        engine.execute(escaped_sql)

    with open(os.path.join(sql_scripts_dir, 'fn_get_duplicates.sql'), 'r') as file:
        escaped_sql = db.text(file.read())
        engine.execute(escaped_sql)


@cli.command("init_load_db")
def init_load_db():
    data_dir = os.path.abspath(os.path.dirname(__file__)) + '/data'
    data_dir_deployments = os.path.join(data_dir, 'deployments')
    data_dir_pickups = os.path.join(data_dir, 'pickups')
    data_dir_rides = os.path.join(data_dir, 'rides')

    # Load Deployments
    data_deployments = []
    for filename in os.listdir(data_dir_deployments):
        data_deployments.extend(Load_Data(os.path.join(data_dir_deployments, filename)))

    duplicate_check = {}
    for i in data_deployments:
        if i[0] in duplicate_check:
            db.session.add(Duplicate_Log(table_name='deployments',
                                         data_row=str(i),
                                         data_key=i[0]))
            continue
        else:
            try:
                duplicate_check[i[0]] = 1
                db.session.add(Deployment(task_id=i[0],
                                          vehicle_id=i[1],
                                          time_task_created=i[2],
                                          time_task_resolved=i[3]))
            except Exception as e:
                db.session.rollback()

    db.session.commit()

    # Load Pickups
    data_pickups = []
    for filename in os.listdir(data_dir_pickups):
        data_pickups.extend(Load_Data(os.path.join(data_dir_pickups, filename)))

    duplicate_check = {}
    for i in data_pickups:
        if i[0] in duplicate_check:
            db.session.add(Duplicate_Log(table_name='pickups',
                                         data_row=str(i),
                                         data_key=i[0]))
            continue
        else:
            try:
                duplicate_check[i[0]] = 1
                db.session.add(Pickup(task_id=i[0],
                                      vehicle_id=i[1],
                                      qr_code=i[2],
                                      time_task_created=i[3],
                                      time_task_resolved=i[4]))
            except Exception as e:
                db.session.rollback()

    db.session.commit()

    # Load Rides
    data_rides = []
    for filename in os.listdir(data_dir_rides):
        data_rides.extend(Load_Data(os.path.join(data_dir_rides, filename)))

    duplicate_check = {}
    for i in data_rides:
        if i[0] in duplicate_check:
            db.session.add(Duplicate_Log(table_name='rides',
                                         data_row=str(i),
                                         data_key=i[0]))
            continue
        else:
            try:
                duplicate_check[i[0]] = 1
                db.session.add(Ride(ride_id=i[0],
                                    vehicle_id=i[1],
                                    time_ride_start=i[2],
                                    time_ride_end=i[3],
                                    start_lat=i[4],
                                    start_lng=i[5],
                                    end_lat=i[6],
                                    end_lng=i[7],
                                    gross_amount=i[8]))
            except Exception as e:
                db.session.rollback()

    db.session.commit()

    # Run analysis data calculation
    engine = db.create_engine(os.getenv('DATABASE_URL'), {})
    sql_scripts_dir = os.path.abspath(os.path.dirname(__file__)) + '/sql_scripts'

    with open(os.path.join(sql_scripts_dir, 'load_rides_analysis.sql'), 'r') as file:
        escaped_sql = db.text(file.read())
        engine.execute(escaped_sql)


if __name__ == "__main__":
    cli()