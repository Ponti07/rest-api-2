# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import mysql.connector
# from werkzeug.security import generate_password_hash, check_password_hash

# app = Flask(__name__)
# CORS(app)

# db_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "",
#     "database": "restapi"
# }


# def get_db_connection():
#     return mysql.connector.connect(**db_config)


# @app.route("/", methods=["GET"])
# def api_docs():
#     return jsonify({
#         "message": "Välkommen till mitt REST API",
#         "routes": [
#             {"method": "GET", "route": "/", "description": "Dokumentation"},
#             {"method": "GET", "route": "/users", "description": "Hämta alla användare"},
#             {"method": "GET", "route": "/users/<id>", "description": "Hämta en användare"},
#             {"method": "POST", "route": "/users", "description": "Skapa användare"},
#             {"method": "PUT", "route": "/users/<id>", "description": "Uppdatera användare"},
#             {"method": "POST", "route": "/login", "description": "Logga in"}
#         ]
#     }), 200


# @app.route("/users", methods=["GET"])
# def get_users():
#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)

#     cursor.execute("SELECT id, username, name, age FROM users")
#     users = cursor.fetchall()

#     cursor.close()
#     connection.close()

#     return jsonify(users), 200


# @app.route("/users/<int:user_id>", methods=["GET"])
# def get_user(user_id):
#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)

#     cursor.execute(
#         "SELECT id, username, name, age FROM users WHERE id = %s",
#         (user_id,)
#     )
#     user = cursor.fetchone()

#     cursor.close()
#     connection.close()

#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     return jsonify(user), 200


# @app.route("/users", methods=["POST"])
# def create_user():
#     data = request.get_json()

#     if not data:
#         return jsonify({"error": "Du måste skicka med JSON-data"}), 400

#     username = data.get("username")
#     password = data.get("password")
#     name = data.get("name")
#     age = data.get("age")

#     if not username or not password or not name or age is None:
#         return jsonify({
#             "error": "Du måste skicka med username, password, name och age"
#         }), 400

#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)

#     # kolla om username redan finns
#     cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
#     if cursor.fetchone():
#         cursor.close()
#         connection.close()
#         return jsonify({"error": "Användarnamnet finns redan"}), 409

#     hashed_password = generate_password_hash(password)

#     cursor = connection.cursor()
#     sql = """
#         INSERT INTO users (username, password, name, age)
#         VALUES (%s, %s, %s, %s)
#     """
#     cursor.execute(sql, (username, hashed_password, name, age))
#     connection.commit()

#     user_id = cursor.lastrowid

#     cursor.close()
#     connection.close()

#     return jsonify({
#         "id": user_id,
#         "username": username,
#         "name": name,
#         "age": age
#     }), 201


# @app.route("/users/<int:user_id>", methods=["PUT"])
# def update_user(user_id):
#     data = request.get_json()

#     if not data:
#         return jsonify({"error": "Du måste skicka med JSON-data"}), 400

#     username = data.get("username")
#     name = data.get("name")
#     age = data.get("age")

#     if not username or not name or age is None:
#         return jsonify({
#             "error": "Du måste skicka med username, name och age"
#         }), 400

#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)

#     # kolla om användaren finns
#     cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
#     if not cursor.fetchone():
#         cursor.close()
#         connection.close()
#         return jsonify({"error": "User not found"}), 404

#     # kolla duplicate username
#     cursor.execute(
#         "SELECT id FROM users WHERE username = %s AND id != %s",
#         (username, user_id)
#     )
#     if cursor.fetchone():
#         cursor.close()
#         connection.close()
#         return jsonify({"error": "Username already taken"}), 409

#     cursor = connection.cursor()
#     sql = "UPDATE users SET username = %s, name = %s, age = %s WHERE id = %s"
#     cursor.execute(sql, (username, name, age, user_id))
#     connection.commit()

#     cursor.close()
#     connection.close()

#     return jsonify({
#         "message": "User updated",
#         "id": user_id,
#         "username": username,
#         "name": name,
#         "age": age
#     }), 200


# @app.route("/login", methods=["POST"])
# def login():
#     data = request.get_json()

#     if not data:
#         return jsonify({"error": "Du måste skicka med JSON-data"}), 400

#     username = data.get("username")
#     password = data.get("password")

#     if not username or not password:
#         return jsonify({"error": "Du måste skicka med username och password"}), 400

#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)

#     cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
#     user = cursor.fetchone()

#     cursor.close()
#     connection.close()

#     if not user:
#         return jsonify({"error": "Fel användarnamn eller lösenord"}), 401

#     if not check_password_hash(user["password"], password):
#         return jsonify({"error": "Fel användarnamn eller lösenord"}), 401

#     return jsonify({
#         "message": "Login successful",
#         "user": {
#             "id": user["id"],
#             "username": user["username"],
#             "name": user["name"],
#             "age": user["age"]
#         }
#     }), 200


# if __name__ == "__main__":
#     app.run(debug=True, port=3001)


from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import timedelta

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "hemlig-nyckel"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
jwt = JWTManager(app)

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "restapi"
}


def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route("/", methods=["GET"])
def api_docs():
    html = """
    <!DOCTYPE html>
    <html lang="sv">
    <head>
        <meta charset="UTF-8">
        <title>API Dokumentation</title>
        <style>
            body {
                background-color: white;
                color: black;
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
            }

            h1 {
                margin-bottom: 10px;
            }

            h2 {
                margin-top: 30px;
            }

            .route {
                margin-bottom: 20px;
            }

            .top-line {
                font-weight: bold;
            }

            .path {
                font-family: monospace;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>

        <h1>API Dokumentation</h1>
        <p>Välkommen till mitt REST API</p>

        <h2>Routes</h2>

        <div class="route">
            <div class="top-line">GET <span class="path">/</span></div>
            <div>Visar dokumentation</div>
        </div>

        <div class="route">
            <div class="top-line">GET <span class="path">/users</span></div>
            <div>Hämtar alla användare</div>
        </div>

        <div class="route">
            <div class="top-line">GET <span class="path">/users/&lt;id&gt;</span></div>
            <div>Hämtar en användare</div>
        </div>

        <div class="route">
            <div class="top-line">POST <span class="path">/users</span></div>
            <div>Skapar en användare</div>
        </div>

        <div class="route">
            <div class="top-line">PUT <span class="path">/users/&lt;id&gt;</span></div>
            <div>Uppdaterar en användare</div>
        </div>

        <div class="route">
            <div class="top-line">POST <span class="path">/login</span></div>
            <div>Loggar in och får token</div>
        </div>

    </body>
    </html>
    """
    return html, 200


@app.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT id, username, name, age FROM users")
    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(users), 200


@app.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, username, name, age FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user), 200


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Du måste skicka med JSON-data"}), 400

    username = data.get("username")
    password = data.get("password")
    name = data.get("name")
    age = data.get("age")

    if not username or not password or not name or age is None:
        return jsonify({
            "error": "Du måste skicka med username, password, name och age"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({"error": "Användarnamnet finns redan"}), 409

    hashed_password = generate_password_hash(password)

    cursor = connection.cursor()
    sql = """
        INSERT INTO users (username, password, name, age)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (username, hashed_password, name, age))
    connection.commit()

    user_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "id": user_id,
        "username": username,
        "name": name,
        "age": age
    }), 201


@app.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Du måste skicka med JSON-data"}), 400

    username = data.get("username")
    name = data.get("name")
    age = data.get("age")

    if not username or not name or age is None:
        return jsonify({
            "error": "Du måste skicka med username, name och age"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({"error": "User not found"}), 404

    cursor.execute(
        "SELECT id FROM users WHERE username = %s AND id != %s",
        (username, user_id)
    )
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({"error": "Username already taken"}), 409

    cursor = connection.cursor()
    sql = "UPDATE users SET username = %s, name = %s, age = %s WHERE id = %s"
    cursor.execute(sql, (username, name, age, user_id))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "User updated",
        "id": user_id,
        "username": username,
        "name": name,
        "age": age
    }), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Du måste skicka med JSON-data"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Du måste skicka med username och password"}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if not user:
        return jsonify({"error": "Fel användarnamn eller lösenord"}), 401

    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Fel användarnamn eller lösenord"}), 401

    access_token = create_access_token(identity=str(user["id"]))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    }), 200


@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({"error": "Token saknas"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"error": "Ogiltig token"}), 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Token har gått ut"}), 401


if __name__ == "__main__":
    app.run(debug=True, port=3001)