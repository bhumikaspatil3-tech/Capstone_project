from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)

# Allow frontend to connect
CORS(app)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="Bhumika@6322",
        database="eseva_db",
        connection_timeout=5,
        use_pure=True
    )


# ============================================================
# HOME
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "message": "e-Seva Backend is Running!"
    })


# ============================================================
# REGISTER
# ============================================================

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

        if not first_name or not last_name or not mobile or not password:

            return jsonify({
                "success": False,
                "message": "Please fill all required fields"
            }), 400

        db = get_db_connection()

        print("MySQL connected successfully!")

        cursor = db.cursor()

        # ---------------- CHECK MOBILE ----------------

        cursor.execute("""
            SELECT id
            FROM users
            WHERE mobile = %s
            LIMIT 1
        """, (mobile,))

        existing_mobile = cursor.fetchone()

        if existing_mobile:

            return jsonify({
                "success": False,
                "message": "Mobile number already registered"
            }), 409

        # ---------------- CHECK EMAIL ----------------

        if email:

            cursor.execute("""
                SELECT id
                FROM users
                WHERE email = %s
                LIMIT 1
            """, (email,))

            existing_email = cursor.fetchone()

            if existing_email:

                return jsonify({
                    "success": False,
                    "message": "Email address already registered"
                }), 409

        # ---------------- INSERT USER ----------------

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


# ============================================================
# CITIZEN LOGIN
# ============================================================

@app.route("/login", methods=["POST"])
def login():

    print("\n========== LOGIN REQUEST ==========")

    db = None
    cursor = None

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No login data received"
            }), 400

        username = data.get("username")
        user_password = data.get("password")

        if not username or not user_password:

            return jsonify({
                "success": False,
                "message": "Please enter mobile/email and password"
            }), 400

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)

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

        if not user:

            return jsonify({
                "success": False,
                "message": "Invalid mobile number/email or password"
            }), 401

        if user["password"] != user_password:

            return jsonify({
                "success": False,
                "message": "Invalid mobile number/email or password"
            }), 401

        user.pop("password", None)

        return jsonify({
            "success": True,
            "message": "Login successful!",
            "user": user
        }), 200

    except mysql.connector.Error as e:

        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Server error: " + str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()

@app.route("/my-applications/<int:user_id>", methods=["GET"])
def my_applications(user_id):

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        query = """
        SELECT
            id,
            application_number,
            service_type,
            applicant_name,
            mobile,
            email,
            application_date,
            status,
            officer_name,
            remarks,
            current_stage,
            next_stage
        FROM applications
        WHERE user_id = %s
        ORDER BY application_date DESC
        """

        cursor.execute(query, (user_id,))
        applications = cursor.fetchall()

        return jsonify({
            "success": True,
            "applications": applications
        }), 200

    except mysql.connector.Error as e:

        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Server error: " + str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ============================================================
# APPLICATION SUBMIT
# ============================================================

@app.route("/applications", methods=["POST"])
def submit_application():

    db = None
    cursor = None

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No application data received"
            }), 400

        service_type = data.get("service_type")
        applicant_name = data.get("applicant_name")
        mobile = data.get("mobile")
        email = data.get("email")
        user_id = data.get("user_id")

        if not service_type or not applicant_name:

            return jsonify({
                "success": False,
                "message": "Service and applicant name are required"
            }), 400

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)

        # ====================================================
        # APPLICATION NUMBER
        # ====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM applications
        """)

        count = cursor.fetchone()["total"]

        application_number = "ESEVA" + str(1001 + count)

        # ====================================================
        # GET FIRST WORKFLOW STAGE
        # Usually:
        # 1 = Application Submitted
        # ====================================================

        cursor.execute("""
            SELECT
                stage_order,
                stage_name
            FROM service_workflows
            WHERE service_name = %s
            ORDER BY stage_order ASC
            LIMIT 1
        """, (service_type,))

        submission_stage = cursor.fetchone()

        if not submission_stage:

            return jsonify({
                "success": False,
                "message": "Workflow not configured for this service"
            }), 400

        # ====================================================
        # GET FIRST OFFICER STAGE
        # Skip Application Submitted
        # ====================================================

        cursor.execute("""
            SELECT
                stage_order,
                stage_name
            FROM service_workflows
            WHERE service_name = %s
            AND stage_order > %s
            ORDER BY stage_order ASC
            LIMIT 1
        """, (
            service_type,
            submission_stage["stage_order"]
        ))

        first_officer_stage = cursor.fetchone()

        if not first_officer_stage:

            return jsonify({
                "success": False,
                "message": "First officer stage not configured"
            }), 400

        # ====================================================
        # FIND FIRST OFFICER
        # ====================================================

        cursor.execute("""
            SELECT
                id,
                officer_id,
                name,
                department,
                stage_name
            FROM officers
            WHERE stage_name = %s
            AND status = 'Active'
            LIMIT 1
        """, (
            first_officer_stage["stage_name"],
        ))

        first_officer = cursor.fetchone()

        if not first_officer:

            return jsonify({
                "success": False,
                "message":
                    "No officer available for stage: "
                    + first_officer_stage["stage_name"]
            }), 400

        # ====================================================
        # FIND NEXT STAGE
        # ====================================================

        cursor.execute("""
            SELECT
                stage_name
            FROM service_workflows
            WHERE service_name = %s
            AND stage_order = %s
            LIMIT 1
        """, (
            service_type,
            first_officer_stage["stage_order"] + 1
        ))

        next_stage_data = cursor.fetchone()

        if next_stage_data:

            next_stage = next_stage_data["stage_name"]

        else:

            next_stage = None

        # ====================================================
        # INSERT APPLICATION
        # ====================================================

        query = """
        INSERT INTO applications
        (
            application_number,
            user_id,
            service_type,
            applicant_name,
            mobile,
            email,
            status,
            current_stage,
            current_officer_id,
            officer_name,
            next_stage
        )
        VALUES
        (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        """

        cursor.execute(
            query,
            (
                application_number,
                user_id,
                service_type,
                applicant_name,
                mobile,
                email,
                "Pending",
                first_officer_stage["stage_name"],
                first_officer["id"],
                first_officer["name"],
                next_stage
            )
        )

        application_id = cursor.lastrowid

        # ====================================================
        # SAVE APPLICATION SUBMITTED HISTORY
        # ====================================================

        cursor.execute("""
            INSERT INTO application_stages
            (
                application_id,
                stage_name,
                officer_name,
                status,
                completed_at
            )
            VALUES
            (
                %s,
                %s,
                %s,
                'Completed',
                NOW()
            )
        """, (
            application_id,
            submission_stage["stage_name"],
            "System"
        ))

        # ====================================================
        # SAVE CURRENT OFFICER STAGE
        # ====================================================

        cursor.execute("""
            INSERT INTO application_stages
            (
                application_id,
                stage_name,
                officer_name,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                'Pending'
            )
        """, (
            application_id,
            first_officer_stage["stage_name"],
            first_officer["name"]
        ))

        db.commit()

        print(
            "Application submitted:",
            application_number,
            "Assigned to:",
            first_officer["name"]
        )

        return jsonify({
            "success": True,
            "message": "Application submitted successfully!",
            "application_number": application_number,
            "current_stage": first_officer_stage["stage_name"],
            "officer_name": first_officer["name"],
            "next_stage": next_stage
        }), 201

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


# ============================================================
# ADMIN APPLICATIONS
# ============================================================

@app.route("/admin/applications", methods=["GET"])
def get_admin_applications():

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                application_number,
                service_type,
                applicant_name,
                mobile,
                email,
                application_date,
                status,
                officer_name,
                remarks,
                current_stage,
                next_stage
            FROM applications
            ORDER BY id DESC
        """)

        applications = cursor.fetchall()

        return jsonify({
            "success": True,
            "applications": applications
        }), 200

    except mysql.connector.Error as e:

        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Server error: " + str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ============================================================
# APPLICATION DETAILS
# ============================================================

@app.route("/admin/application/<int:application_id>", methods=["GET"])
def get_application_details(application_id):

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM applications
            WHERE id = %s
        """, (application_id,))

        application = cursor.fetchone()

        if not application:

            return jsonify({
                "success": False,
                "message": "Application not found"
            }), 404

        return jsonify({
            "success": True,
            "application": application
        }), 200

    except mysql.connector.Error as e:

        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Server error: " + str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route("/admin/login", methods=["POST"])
def admin_login():

    db = None
    cursor = None

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No login data received"
            }), 400

        username = data.get("username")
        admin_password = data.get("password")

        if not username or not admin_password:

            return jsonify({
                "success": False,
                "message": "Please enter username and password"
            }), 400

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                username,
                name,
                password
            FROM admin
            WHERE username = %s
            LIMIT 1
        """, (username,))

        admin = cursor.fetchone()

        if not admin:

            return jsonify({
                "success": False,
                "message": "Invalid admin username or password"
            }), 401

        if admin["password"] != admin_password:

            return jsonify({
                "success": False,
                "message": "Invalid admin username or password"
            }), 401

        admin.pop("password", None)

        return jsonify({
            "success": True,
            "message": "Admin login successful!",
            "admin": admin
        }), 200

    except mysql.connector.Error as e:

        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Server error: " + str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ============================================================
# OFFICER LOGIN
# ============================================================

@app.route("/officer/login", methods=["POST"])
def officer_login():

    db = None
    cursor = None

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No login data received"
            }), 400

        officer_id = data.get("officer_id")
        password = data.get("password")

        if not officer_id or not password:

            return jsonify({
                "success": False,
                "message": "Officer ID and password are required"
            }), 400

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                officer_id,
                name,
                department,
                stage_name,
                email,
                mobile,
                status
            FROM officers
            WHERE officer_id = %s
            AND password = %s
            AND status = 'Active'
            LIMIT 1
        """, (
            officer_id,
            password
        ))

        officer = cursor.fetchone()

        if not officer:

            return jsonify({
                "success": False,
                "message": "Invalid Officer ID or password"
            }), 401

        return jsonify({
            "success": True,
            "message": "Officer login successful",
            "officer": officer
        }), 200

    except mysql.connector.Error as e:

        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Server error: " + str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ============================================================
# OFFICER APPLICATIONS
# ============================================================

@app.route("/officer/applications/<int:officer_id>", methods=["GET"])
def officer_applications(officer_id):

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                application_number,
                service_type,
                applicant_name,
                mobile,
                email,
                application_date,
                status,
                officer_name,
                remarks,
                current_stage,
                next_stage
            FROM applications
            WHERE current_officer_id = %s
            AND status = 'Pending'
            ORDER BY application_date DESC
        """, (officer_id,))

        applications = cursor.fetchall()

        return jsonify({
            "success": True,
            "applications": applications
        }), 200

    except mysql.connector.Error as e:

        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Server error: " + str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ============================================================
# OFFICER APPROVE & FORWARD
# ============================================================

@app.route(
    "/officer/application/<int:application_id>/approve",
    methods=["POST"]
)
def approve_application(application_id):

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)

        # ====================================================
        # GET APPLICATION
        # ====================================================

        cursor.execute("""
            SELECT
                id,
                application_number,
                service_type,
                current_stage,
                current_officer_id,
                officer_name,
                status
            FROM applications
            WHERE id = %s
            LIMIT 1
        """, (application_id,))

        application = cursor.fetchone()

        if not application:

            return jsonify({
                "success": False,
                "message": "Application not found"
            }), 404

        if application["status"] != "Pending":

            return jsonify({
                "success": False,
                "message": "Application is not pending"
            }), 400

        # ====================================================
        # GET CURRENT WORKFLOW ORDER
        # ====================================================

        cursor.execute("""
            SELECT
                stage_order,
                stage_name
            FROM service_workflows
            WHERE service_name = %s
            AND stage_name = %s
            LIMIT 1
        """, (
            application["service_type"],
            application["current_stage"]
        ))

        current_workflow = cursor.fetchone()

        if not current_workflow:

            return jsonify({
                "success": False,
                "message": "Current workflow stage not found"
            }), 400

        current_order = current_workflow["stage_order"]

        # ====================================================
        # MARK CURRENT STAGE COMPLETED
        # ====================================================

        cursor.execute("""
            UPDATE application_stages
            SET
                status = 'Completed',
                completed_at = NOW()
            WHERE application_id = %s
            AND stage_name = %s
            AND status = 'Pending'
        """, (
            application_id,
            application["current_stage"]
        ))

        # ====================================================
        # FIND NEXT WORKFLOW STAGE
        # ====================================================

        cursor.execute("""
            SELECT
                stage_order,
                stage_name
            FROM service_workflows
            WHERE service_name = %s
            AND stage_order = %s
            LIMIT 1
        """, (
            application["service_type"],
            current_order + 1
        ))

        next_workflow = cursor.fetchone()

        # ====================================================
        # FINAL APPROVAL CASE
        #
        # Example:
        # Tahsildar Verification = 4
        # Final Approval = 5
        #
        # Final Approval does not need separate officer.
        # ====================================================

        if next_workflow and next_workflow["stage_name"] == "Final Approval":

            cursor.execute("""
                UPDATE applications
                SET
                    status = 'Approved',
                    current_stage = 'Final Approval',
                    current_officer_id = NULL,
                    officer_name = NULL,
                    next_stage = NULL
                WHERE id = %s
            """, (application_id,))

            db.commit()

            return jsonify({
                "success": True,
                "message": "Application finally approved!",
                "application_number":
                    application["application_number"],
                "status": "Approved"
            }), 200

        # ====================================================
        # NO NEXT STAGE
        # ====================================================

        if not next_workflow:

            cursor.execute("""
                UPDATE applications
                SET
                    status = 'Approved',
                    current_stage = 'Final Approval',
                    current_officer_id = NULL,
                    officer_name = NULL,
                    next_stage = NULL
                WHERE id = %s
            """, (application_id,))

            db.commit()

            return jsonify({
                "success": True,
                "message": "Application finally approved!",
                "status": "Approved"
            }), 200

        next_stage = next_workflow["stage_name"]

        # ====================================================
        # FIND NEXT OFFICER
        # ====================================================

        cursor.execute("""
            SELECT
                id,
                officer_id,
                name,
                department,
                stage_name
            FROM officers
            WHERE stage_name = %s
            AND status = 'Active'
            LIMIT 1
        """, (next_stage,))

        next_officer = cursor.fetchone()

        if not next_officer:

            db.rollback()

            return jsonify({
                "success": False,
                "message":
                    "No officer available for stage: "
                    + next_stage
            }), 400

        # ====================================================
        # FIND STAGE AFTER NEXT OFFICER
        # ====================================================

        cursor.execute("""
            SELECT
                stage_name
            FROM service_workflows
            WHERE service_name = %s
            AND stage_order = %s
            LIMIT 1
        """, (
            application["service_type"],
            next_workflow["stage_order"] + 1
        ))

        following_stage = cursor.fetchone()

        if following_stage:

            following_stage_name = following_stage["stage_name"]

        else:

            following_stage_name = None

        # ====================================================
        # UPDATE APPLICATION
        # ====================================================

        cursor.execute("""
            UPDATE applications
            SET
                current_stage = %s,
                current_officer_id = %s,
                officer_name = %s,
                status = 'Pending',
                next_stage = %s
            WHERE id = %s
        """, (
            next_stage,
            next_officer["id"],
            next_officer["name"],
            following_stage_name,
            application_id
        ))

        # ====================================================
        # ADD NEXT STAGE HISTORY
        # ====================================================

        cursor.execute("""
            INSERT INTO application_stages
            (
                application_id,
                stage_name,
                officer_name,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                'Pending'
            )
        """, (
            application_id,
            next_stage,
            next_officer["name"]
        ))

        db.commit()

        # ====================================================
        # SUCCESS
        # ====================================================

        return jsonify({
            "success": True,
            "message": "Application forwarded successfully",
            "application_number":
                application["application_number"],
            "next_stage": next_stage,
            "next_officer": next_officer["name"],
            "following_stage": following_stage_name
        }), 200

    except mysql.connector.Error as e:

        if db:
            db.rollback()

        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500

    except Exception as e:

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

@app.route("/track/<application_number>", methods=["GET"])
def track_application(application_number):

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Get application details
        cursor.execute("""
            SELECT
                id,
                application_number,
                service_type,
                applicant_name,
                mobile,
                email,
                application_date,
                status,
                officer_name,
                current_stage,
                next_stage
            FROM applications
            WHERE application_number = %s
            LIMIT 1
        """, (application_number,))

        application = cursor.fetchone()

        if not application:
            return jsonify({
                "success": False,
                "message": "Application not found"
            }), 404

        # Get application history
        cursor.execute("""
            SELECT
                stage_name,
                officer_name,
                status
            FROM application_stages
            WHERE application_id = %s
            ORDER BY id ASC
        """, (application["id"],))

        history = cursor.fetchall()

        return jsonify({
            "success": True,
            "application": application,
            "history": history
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

# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
@app.route("/track/<application_number>", methods=["GET"])
def track_application(application_number):
    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                application_number,
                service_type,
                applicant_name,
                mobile,
                email,
                application_date,
                status,
                officer_name,
                current_stage,
                next_stage
            FROM applications
            WHERE application_number = %s
            LIMIT 1
        """, (application_number,))

        application = cursor.fetchone()

        if not application:
            return jsonify({
                "success": False,
                "message": "Application not found"
            }), 404

        cursor.execute("""
            SELECT
                stage_name,
                officer_name,
                status,
                action_date
            FROM application_stages
            WHERE application_id = %s
            ORDER BY id ASC
        """, (application["id"],))

        history = cursor.fetchall()

        return jsonify({
            "success": True,
            "application": application,
            "history": history
        }), 200

    except mysql.connector.Error as e:
        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Server error: " + str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()