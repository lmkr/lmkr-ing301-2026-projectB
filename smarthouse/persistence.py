import sqlite3
from typing import Optional
from smarthouse.domain import *

class SmartHouseRepository:
    """
    Provides the functionality to persist and load a _SmartHouse_ object 
    in a SQLite database.
    """

    def __init__(self, file: str) -> None:
        self.file = file 
        self.conn = sqlite3.connect(file, check_same_thread=False)

    def __del__(self):
        self.conn.close()

    def cursor(self) -> sqlite3.Cursor:
        """
        Provides a _raw_ SQLite cursor to interact with the database.
        When calling this method to obtain a cursors, you have to 
        rememeber calling `commit/rollback` and `close` yourself when
        you are done with issuing SQL commands.
        """
        return self.conn.cursor()

    def reconnect(self):
        self.conn.close()
        self.conn = sqlite3.connect(self.file)

    
    def load_smarthouse_deep(self):
        """
        This method retrives the complete single instance of the _SmartHouse_ 
        object stored in this database. The retrieval yields a _deep_ copy, i.e.
        all referenced objects within the object structure (e.g. floors, rooms, devices) 
        are retrieved as well. 
        """
        # TODO: START here! remove the following stub implementation and implement this function 
        #       by retrieving the data from the database via SQL `SELECT` statements.
        cur = self.cursor()

        res = cur.execute ('SELECT * FROM rooms')

        rooms = res.fetchall()

        # create SmartHouse object
        smarthouse = SmartHouse()

        # create floors
        levels = set()  # for storing discovered levels
        for room in rooms:
            floor = room[1]
            levels.add(floor)

        for l in levels:
            smarthouse.register_floor(l)

        # register rooms
        floors = smarthouse.get_floors()

        ids_room = dict()

        for room in rooms:

            id = room[0]
            level = room[1]
            area = room[2]
            name = room[3]

            for f in floors:
                if f.level == level:
                    r = smarthouse.register_room(f,area,name)
                    ids_room.update({id:r})

        # print(ids_room)
        # create and register devices

        res = cur.execute('SELECT * FROM devices')

        devices = res.fetchall()

        # print(devices)

        for device in devices:
            id = device[0]
            room_number = device[1]
            kind = device[2]
            category = device[3]
            supplier = device[4]
            product = device[5]

            d = None
            if category == 'sensor':
                d = Sensor(id,product,supplier,kind) # why no unit here?
            elif category == 'actuator':
                d = Actuator(id,product,supplier,kind) # TODO: Fix in case of value

                res = cur.execute(f'SELECT * FROM actuators where device = "{id}"')
                a = res.fetchone()

                print(a)
                # set persisted state of actuator if it exists
                if a is not None:
                    state = a[1]
                    value = a[2] # TODO

                    if state == "ON":
                       d.turn_on()
                    else:
                       d.turn_off()

            r = ids_room.get(room_number)

            smarthouse.register_device(r,d)

        return smarthouse

    def get_latest_reading(self, sensor) -> Optional[Measurement]:
        """
        Retrieves the most recent sensor reading for the given sensor if available.
        Returns None if the given object has no sensor readings.
        """
        # TODO: After loading the smarthouse, continue here

        did = sensor.id

        cur = self.cursor()

        res = cur.execute(f'SELECT * FROM measurements m where m.device = "{did}" ORDER BY m.ts DESC')

        m = res.fetchone()

        if m is not None:

            ts = m[1]
            value = m[2]
            unit = m[3]

            return Measurement(ts,value,unit)

        return None

    def update_actuator_state(self, actuator):
        """
        Saves the state of the given actuator in the database. 
        """
        # TODO: Implement this method. You will probably need to extend the existing database structure: e.g.
        #       by creating a new table (`CREATE`), adding some data to it (`INSERT`) first, and then issue
        #       and SQL `UPDATE` statement. Remember also that you will have to call `commit()` on the `Connection`
        #       stored in the `self.conn` instance variable.
        # CREATE TABLE actuators(
        #    device TEXT NOT NULL,
        #    state TEXT,
        #    value TEXT
        # )
        cur = self.cursor()

        state = "OFF"
        if actuator.is_active():
            state = "ON"

        id = actuator.id
        res = cur.execute(f'SELECT * FROM actuators where device = "{id}"')
        a = res.fetchone()

        if a is not None:
            cur.execute(f'UPDATE actuators SET state = "{state}" WHERE actuators.device = "{id}"')
        else:
            cur.execute(f'INSERT INTO actuators VALUES ("{id}","{state}","")')

        self.conn.commit()
        # TODO: insert actuators with state as part of deep method

        #res = cur.execute('SELECT * FROM actuators')

        # states = res.fetchall()
        #print('X')
        #print(states)

    # statistics
    def calc_avg_temperatures_in_room(self, room, from_date: Optional[str] = None, until_date: Optional[str] = None) -> dict:
        """Calculates the average temperatures in the given room for the given time range by
        fetching all available temperature sensor data (either from a dedicated temperature sensor 
        or from an actuator, which includes a temperature sensor like a heat pump) from the devices 
        located in that room, filtering the measurement by given time range.
        The latter is provided by two strings, each containing a date in the ISO 8601 format.
        If one argument is empty, it means that the upper and/or lower bound of the time range are unbounded.
        The result should be a dictionary where the keys are strings representing dates (iso format) and 
        the values are floating point numbers containing the average temperature that day.
        """
        # TODO: This and the following statistic method are a bit more challenging. Try to design the respective 
        #       SQL statements first in a SQL editor like Dbeaver and then copy it over here.  
        return NotImplemented

    
    def calc_hours_with_humidity_above(self, room, date: str) -> list:
        """
        This function determines during which hours of the given day
        there were more than three measurements in that hour having a humidity measurement that is above
        the average recorded humidity in that room at that particular time.
        The result is a (possibly empty) list of number representing hours [0-23].
        """
        # TODO: implement
        return NotImplemented

