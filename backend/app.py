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


        # IMPORTANT: येथे फक्त users चे 10 values आहेत

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

        data = request.get_json()

        print("Login request received")

        if not data:

            return jsonify({
                "success": False,
                "message": "No login data received"
            }), 400


        username = data.get("username")
        user_password = data.get("password")


        # ================= VALIDATION =================

        if not username or not user_password:

            return jsonify({
                "success": False,
                "message": "Please enter mobile/email and password"
            }), 400


        # ================= MYSQL =================

        db = get_db_connection()

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

            return jsonify({
                "success": False,
                "message": "Invalid mobile number/email or password"
            }), 401


        # ================= PASSWORD CHECK =================

        if user["password"] != user_password:

            return jsonify({
                "success": False,
                "message": "Invalid mobile number/email or password"
            }), 401


        # Remove password

        user.pop("password", None)


        # ================= LOGIN SUCCESS =================

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


# ==================================================
# ================= APPLICATION =====================
# ==================================================

@app.route("/application", methods=["POST"])
def application():

    print("\n========== APPLICATION REQUEST ==========")

    db = None
    cursor = None

    try:

        data = request.get_json()

        print("Received application data:")
        print(data)


        if not data:

            return jsonify({
                "success": False,
                "message": "No application data received"
            }), 400


        # ================= GET APPLICATION VALUES =================

        service = data.get("service")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        dob = data.get("dob")
        gender = data.get("gender")
        mobile = data.get("mobile")
        email = data.get("email")
        address = data.get("address")
        state = data.get("state")
        city = data.get("city")
        purpose = data.get("purpose")
        details = data.get("details")


        # ================= VALIDATION =================

        if (
            not service or
            not first_name or
            not last_name or
            not dob or
            not gender or
            not mobile or
            not address or
            not state or
            not city or
            not purpose
        ):

            return jsonify({
                "success": False,
                "message": "Please fill all required fields"
            }), 400


        # ================= DATABASE =================

        print("Connecting to MySQL...")

        db = get_db_connection()

        print("MySQL connected successfully!")

        cursor = db.cursor()


        # ================= INSERT APPLICATION =================

        query = """
        INSERT INTO applications
        (
            service,
            first_name,
            last_name,
            dob,
            gender,
            mobile,
            email,
            address,
            state,
            city,
            purpose,
            details
        )
        VALUES
        (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        """


        values = (
            service,
            first_name,
            last_name,
            dob,
            gender,
            mobile,
            email,
            address,
            state,
            city,
            purpose,
            details
        )


        # ================= EXECUTE QUERY =================

        print("Submitting application...")

        cursor.execute(query, values)

        db.commit()


        # Get automatically generated ID

        application_id = cursor.lastrowid

        application_id = f"ID2026{application_id:06d}"


        print("Application submitted successfully!")
        print("Application ID:", application_id)


        # ================= SUCCESS RESPONSE =================

        return jsonify({
            "success": True,
            "message": "Application submitted successfully!",
            "application_id": application_id
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

# ================= TRACK APPLICATION =================

@app.route("/track/<application_id>", methods=["GET"])
def track_application(application_id):

    db = None
    cursor = None

    try:

        print("\n========== TRACK APPLICATION ==========")
        print("Received ID:", application_id)

        # ID2026000002 → 2
        db_id = int(application_id[-6:])

        # Connect to MySQL
        db = get_db_connection()

        print("MySQL connected successfully!")

        cursor = db.cursor(dictionary=True)

        # Find application
        query = """
        SELECT
            id,
            service,
            first_name,
            last_name,
            status,
            created_at
        FROM applications
        WHERE id = %s
        """

        cursor.execute(query, (db_id,))

        application_data = cursor.fetchone()

        # Application not found
        if not application_data:

            return jsonify({
                "success": False,
                "message": "Application not found."
            }), 404

        # Convert database ID to display ID
        application_data["application_id"] = (
            f"ID2026{application_data['id']:06d}"
        )

        print("Application found!")
        print(application_data)

        return jsonify({
            "success": True,
            "application": application_data
        }), 200

    except ValueError:

        return jsonify({
            "success": False,
            "message": "Invalid Application ID."
        }), 400

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