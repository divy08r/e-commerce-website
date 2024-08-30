from flask import Flask, request, render_template, send_file, jsonify, redirect, url_for, flash
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId
import google.generativeai as palm
import json
from ics import Calendar, Event
from datetime import datetime, timedelta
import io
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)
if mongo.cx:
    print("MongoDB connection successful")
else:
    print("MongoDB connection failed")

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    @staticmethod
    def get(user_id):
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_id=str(user_data["_id"]))
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Registration form
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        if username.data:
            user = mongo.db.users.find_one({"username": username.data})
            if user:
                raise ValidationError("Username already exists.")
        else:
            raise ValidationError("Username is required.")

# Login form
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")
    
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        mongo.db.users.insert_one({"username": form.username.data, "password": hashed_password})
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"username": form.username.data})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            user_obj = User(user_id=str(user["_id"]))
            login_user(user_obj)
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html", form=form)

# Configure the Google Generative AI API
PALM_API = os.getenv('PALM_API_KEY')
palm.configure(api_key=PALM_API)
models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name

def parse_time(time_str):
    """Parse time in 'HH:MM AM/PM' format into a datetime object."""
    return datetime.strptime(time_str, "%I:%M %p").time()

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        city = request.form['city']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        preferences = request.form.get('hidden_preferences', '')
        
        days = (end_date - start_date).days

        preferences_list = [pref.strip() for pref in preferences.split(',') if pref.strip()]

        prompt = f"You are a travel expert. Give me an itinerary for {city}, for {days} days, assuming each day starts at 10am and ends at 8pm with a buffer of 30 minutes between activities. I like to "

        if preferences_list:
            prompt += ", ".join(preferences_list) + "."
        else:
            prompt += " provide a general itinerary."

        prompt += """ Generate a structured JSON representation for the travel itinerary.
        {
        "days": [
            {
            "day": 1,
            "activities": [
                {
                "title": "Activity 1",
                "description": "Description of Activity 1",
                "link": "https://example.com/activity1",
                "start_time": "10:00 AM",
                "end_time": "12:00 PM",
                "location": "https://maps.google.com/?q=location1"
                }
            ]
            }
        ]
        }
        Ensure that each day has a 'day' field and a list of 'activities' with 'title', 'description', 'start_time', 'end_time', and 'location' fields. Keep descriptions concise.
        """        
    
        

        # Call the Generative AI API
        try:
            completion = palm.generate_text(
                model=model,
                prompt=prompt,
                temperature=0,
                max_output_tokens=6000,
            )

            itinerary = completion.result.strip()
            # print("Raw JSON Output:", itinerary) 

            print(prompt)
            print("Preferences", preferences)
            itinerary_json_str = itinerary[7:-3].strip()
            itinerary_json = json.loads(itinerary_json_str)
        except Exception as e:
            return "An error occurred while generating the itinerary. Please try again."

        # Create calendar
        cal = Calendar()
        for day, activities in enumerate(itinerary_json.get("days", []), start=1):
            for activity in activities.get("activities", []):
                try:
                    event = Event()
                    event.name = activity.get("title", "")
                    event.description = activity.get("description", "")
                    event.location = activity.get("location", "")

                    start_time_str = activity.get("start_time", "10:00 AM")
                    end_time_str = activity.get("end_time", "10:00 AM")
                    
                    
                    start_time = parse_time(start_time_str)
                    end_time = parse_time(end_time_str)

                    event_start = datetime.combine(start_date + timedelta(days=day - 1), start_time)
                    event_end = datetime.combine(start_date + timedelta(days=day - 1), end_time)

                    if event_end <= event_start:
                        raise ValueError(f"End time {end_time_str} must be after start time {start_time_str} for activity {activity.get('title')}")

                    event.begin = event_start
                    event.end = event_end

                    cal.events.add(event)
                except ValueError as e:
                    print(f"Error creating event: {e}")
        
        # Generate calendar file
        cal_content = str(cal)
        cal_file = io.BytesIO(cal_content.encode('utf-8'))
        
        return render_template('itenary.html', itinerary=itinerary_json, calendar_file=cal_file)

    return render_template('index.html')

@app.route('/download')
@login_required
def download():
    cal_file = request.args.get('file')
    if not cal_file:
        return "No file provided.", 400

    return send_file(
        io.BytesIO(cal_file.encode('utf-8')),
        as_attachment=True,
        download_name="Itinerary.ics",
        mimetype="text/calendar"
    )

if __name__ == '__main__':
    app.run(debug=True)
