from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)

# Allow frontend to connect
CORS(app)


# ================= DATABASE CONNECTION =================

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="root",
        database="eseva_db",
        connection_timeout=5,
        use_pure=True
    )


# ================= HOME =================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "message": "e-Seva Backend is Running!"
    })


# ================= REGISTER =================

@app.route("/register", methods=["POST"])
def register():

    print("\n========== REGISTER REQUEST ==========")

    db = None
    cursor = None

    try:

        # Get JSON data
        data = request.get_json()

        print("Received data:")
        print(data)

        if not data:

            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400


        # Get values
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        dob = data.get("dob")
        gender = data.get("gender")
        mobile = data.get("mobile")
        email = data.get("email")
        address = data.get("address")
        state = data.get("state")
        city = data.get("city")
        password = data.get("password")


        # Required fields
        if not first_name or not last_name or not mobile or not password:

            return jsonify({
                "success": False,
                "message": "Please fill all required fields"
            }), 400


        # ================= MYSQL =================

        print("Connecting to MySQL...")

        db = get_db_connection()

        print("MySQL connected successfully!")

        cursor = db.cursor()


        # ================= CHECK MOBILE =================

        check_mobile = """
        SELECT id
        FROM users
        WHERE mobile = %s
        LIMIT 1
        """

        cursor.execute(
            check_mobile,
            (mobile,)
        )

        existing_mobile = cursor.fetchone()


        if existing_mobile:

            print("Mobile number already registered!")

            return jsonify({
                "success": False,
                "message": "Mobile number already registered"
            }), 409


        # ================= CHECK EMAIL =================

        if email:

            check_email = """
            SELECT id
            FROM users
            WHERE email = %s
            LIMIT 1
            """

            cursor.execute(
                check_email,
                (email,)
            )

            existing_email = cursor.fetchone()

            if existing_email:

                print("Email already registered!")

                return jsonify({
                    "success": False,
                    "message": "Email address already registered"
                }), 409


        # ================= INSERT USER =================

        query = """
        INSERT INTO users
        (
            first_name,
            last_name,
            dob,
            gender,
            mobile,
            email,
            address,
            state,
            city,
            password
        )
        VALUES
        (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        """


        values = (
            first_name,
            last_name,
            dob,
            gender,
            mobile,
            email,
            address,
            state,
            city,
            password
        )


        print("Inserting user...")

        cursor.execute(query, values)

        db.commit()


        print("User inserted successfully!")


        return jsonify({
            "success": True,
            "message": "Registration successful!"
        }), 200


    except mysql.connector.Error as e:

        print("MYSQL ERROR:")
        print(e)

        if db:
            db.rollback()

        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500


    except Exception as e:

        print("GENERAL ERROR:")
        print(e)

        if db:
            db.rollback()

        return jsonify({
            "success": False,
            "message": "Server error: " + str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ================= LOGIN =================

@app.route("/login", methods=["POST"])
def login():

    print("\n========== LOGIN REQUEST ==========")

    db = None
    cursor = None

    try:

        # Get JSON data
        data = request.get_json()

        print("Login request received")

        if not data:

            return jsonify({
                "success": False,
                "message": "No login data received"
            }), 400


        # Get login values
        username = data.get("username")
        user_password = data.get("password")


        # ================= VALIDATION =================

        if not username or not user_password:

            return jsonify({
                "success": False,
                "message": "Please enter mobile/email and password"
            }), 400


        # ================= MYSQL =================

        print("Connecting to MySQL...")

        db = get_db_connection()

        print("MySQL connected successfully!")

        cursor = db.cursor(dictionary=True)


        # ================= FIND USER =================

        query = """
        SELECT
            id,
            first_name,
            last_name,
            dob,
            gender,
            mobile,
            email,
            address,
            state,
            city,
            password
        FROM users
        WHERE mobile = %s OR email = %s
        LIMIT 1
        """


        cursor.execute(
            query,
            (username, username)
        )


        user = cursor.fetchone()


        # ================= USER NOT FOUND =================

        if not user:

            print("User not found!")

            return jsonify({
                "success": False,
                "message": "Invalid mobile number/email or password"
            }), 401


        # ================= PASSWORD CHECK =================

        if user["password"] != user_password:

            print("Wrong password!")

            return jsonify({
                "success": False,
                "message": "Invalid mobile number/email or password"
            }), 401


        # ================= REMOVE PASSWORD =================

        user.pop("password", None)


        # ================= LOGIN SUCCESS =================

        print("Login successful!")

        return jsonify({
            "success": True,
            "message": "Login successful!",
            "user": user
        }), 200


    except mysql.connector.Error as e:

        print("MYSQL ERROR:")
        print(e)

        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500


    except Exception as e:

        print("GENERAL ERROR:")
        print(e)

        return jsonify({
            "success": False,
            "message": "Server error: " + str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ================= RUN SERVER =================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )