from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, People, Planet, Favorite
from admin import setup_admin
from utils import APIException
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def index():
    return jsonify({"message": "Bienvenido a la API de Star Wars"}), 200

# --- People ---


@app.route("/people", methods=["GET"])
def get_people():
    people = People.query.all()
    return jsonify([p.serialize() for p in people]), 200


@app.route("/people/<int:people_id>", methods=["GET"])
def get_one_person(people_id):
    person = People.query.get(people_id)
    if person:
        return jsonify(person.serialize()), 200
    return jsonify({"error": "Person not found"}), 404


@app.route("/people", methods=["POST"])
def create_person():
    data = request.get_json()
    name = data.get("name")
    birth_year = data.get("birth_year")
    gender = data.get("gender")

    if not name or not birth_year or not gender:
        return jsonify({"error": "Missing required fields"}), 400

    new_person = People(name=name, birth_year=birth_year, gender=gender)
    db.session.add(new_person)
    db.session.commit()
    return jsonify(new_person.serialize()), 201

# --- Planets ---


@app.route("/planets", methods=["GET"])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200


@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize()), 200
    return jsonify({"error": "Planet not found"}), 404


@app.route("/planets", methods=["POST"])
def create_planet():
    data = request.get_json()
    name = data.get("name")
    climate = data.get("climate")
    population = data.get("population")

    if not name or not climate or not population:
        return jsonify({"error": "Missing required fields"}), 400

    new_planet = Planet(name=name, climate=climate, population=population)
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201

# --- Users ---


@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200

# --- Favorites ---


@app.route("/users/favorites", methods=["GET"])
def get_favorites():
    favorites = Favorite.query.all()
    return jsonify([f.serialize() for f in favorites]), 200


@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_fav_planet(planet_id):
    user_id = request.json.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201


@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_fav_people(people_id):
    user_id = request.json.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201


@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_fav_planet(planet_id):
    fav = Favorite.query.filter_by(planet_id=planet_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({"done": True}), 200
    return jsonify({"error": "Favorite not found"}), 404


@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_fav_people(people_id):
    fav = Favorite.query.filter_by(people_id=people_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({"done": True}), 200
    return jsonify({"error": "Favorite not found"}), 404


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
