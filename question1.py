# 1. Managing a Fitness Center Database
# Objective: The aim of this assignment is to develop a Flask application to manage a fitness center's database, 
# focusing on interacting with the Members and WorkoutSessionstables. This will enhance your skills in building 
# RESTful APIs using Flask, handling database operations, and implementing CRUD functionalities.

# Task 1: Setting Up the Flask Environment and Database Connection - 
# Create a new Flask project and set up a virtual environment. - 
# Install necessary packages like Flask, Flask-Marshmallow, and MySQL connector. - 
# Establish a connection to your MySQL database. - 
# Use the Members and WorkoutSessions tables used on previous Lessons

# Expected Outcome: A Flask project with a connected database and the required tables created.


#--------------------------------------------------------------------------------------------------
#Open a terminal and type the following (less the #):

# python -m venv myenv
# myenv\Scripts\activate
# pip install flask flask-marshmallow mysql-connector-python
    # That will install flask, flask-marshmallow, and mysql-connector
#---------------------------------------------------------------------------------------------------


# Task 2: Implementing CRUD Operations for Members - Create Flask routes to add, retrieve, update, and delete 
# members from the Members table. - Use appropriate HTTP methods: POST for adding, GET for retrieving, PUT for updating, 
# and DELETE for deleting members. - Ensure to handle any errors and return appropriate responses.

# Expected Outcome: Functional endpoints for managing members in the database with proper error handling.

from flask import Flask, jsonify, request   # request is used in adding data
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, ValidationError
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):  # Schemas substantiate how we want data to be
    name = fields.String(required=True)
    age = fields.Int(required=True)

    class Meta:
        fields = ("name", "age", "id")


member_schema = MemberSchema()
members_schema = MemberSchema(many=True)


def get_db_connection():
    db_name = "fitness_center_db"
    user = "CodingTemple"
    password = "C0dingT3mple!"
    host = "127.0.0.1"

    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
        )
        return conn

    except Error as e: 
        print(f"Error: {e}")
        return None

@app.route('/')
def home():
    return 'Welome to the Fitness Center Management System'


@app.route("/members", methods=["GET"])
def get_members():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Members"
        cursor.execute(query)

        members = cursor.fetchall()

        return members_schema.jsonify(members)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/members/<int:id>', methods=['GET']) 
def get_member(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM Members WHERE id = %s", (id, ))
        member = cursor.fetchone() # TODO maybe fetchall()? or add a ;?

        return member_schema.jsonify(member)

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        
        new_member = (member_data['name'], member_data['age'])

        query = ("INSERT INTO Members (name, age) VALUES (%s, %s)")

        cursor.execute(query, new_member)
        conn.commit()

        return jsonify({"message": "New member added successfully"}), 201

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/members/<int:id>", methods=["PUT"]) 
def update_customer(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        
        updated_member = (member_data['name'], member_data['age'],  id)

        query = "UPDATE Members SET name = %s, age = %s WHERE id= %s"

        cursor.execute(query, updated_member)
        conn.commit()

        return jsonify({"message": "Member updated successfully"}), 201

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        
        member_to_remove = (id, )

        cursor.execute("SELECT * FROM Members WHERE id = %s", member_to_remove)

        member = cursor.fetchone()

        if not member:
            return jsonify({"error": "Customer not found"}), 404

        query = "DELETE FROM Members WHERE id = %s" 

        cursor.execute(query, member_to_remove)
        conn.commit()

        return jsonify({"message": "Member removed successfully"}), 200

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# NOTE: Make sure you have ALL of the CRUD operations implemented, not just the two above.


# Task 3: Managing Workout Sessions - Develop routes to schedule, update, and view workout sessions. - 
# Implement a route to retrieve all workout sessions for a specific member.


class WorkoutSchema(ma.Schema):
    member_id = fields.Int(required=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True)
    calories_burned = fields.Int(required=True)

    class Meta:
        fields = ("member_id", "date", "duration_minutes", "calories_burned", "session_id")


workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

@app.route("/workoutsessions", methods=["GET"])
def get_all_workouts():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Workoutsessions"
        cursor.execute(query)

        workouts = cursor.fetchall()

        return workouts_schema.jsonify(workouts)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/workoutsessions/<int:id>', methods=['GET']) 
def get_workouts(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM Workoutsessions WHERE member_id = %s", (id, ))
        workouts = cursor.fetchall() 

        return workouts_schema.jsonify(workouts)

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/workoutsessions', methods=['POST'])
def add_workout():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        
        new_workout = (workout_data['member_id'], workout_data['date'], workout_data['duration_minutes'], workout_data['calories_burned'])

        query = ("INSERT INTO Workoutsessions (member_id, date, duration_minutes, calories_burned) VALUES (%s, %s, %s, %s)")

        cursor.execute(query, new_workout)
        conn.commit()

        return jsonify({"message": "New workout added successfully"}), 201

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/workoutsessions/<int:session_id>", methods=["PUT"]) 
def update_workout(session_id):
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        
        updated_workout = (workout_data['member_id'], workout_data['date'], workout_data['duration_minutes'], workout_data['calories_burned'], session_id)

        query = "UPDATE Workoutsessions SET member_id = %s, date = %s, duration_minutes = %s, calories_burned = %s WHERE session_id= %s"

        cursor.execute(query, updated_workout)
        conn.commit()

        return jsonify({"message": "Workout updated successfully"}), 201

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/workoutsessions/<int:session_id>", methods=["DELETE"])
def delete_workout(session_id):    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        
        workout_to_remove = (session_id, )

        cursor.execute("SELECT * FROM Workoutsessions WHERE session_id = %s", workout_to_remove)

        member = cursor.fetchone()

        if not member:
            return jsonify({"error": "Workout not found"}), 404

        query = "DELETE FROM Workoutsessions WHERE session_id = %s" 

        cursor.execute(query, workout_to_remove)
        conn.commit()

        return jsonify({"message": "Workout removed successfully"}), 200

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)