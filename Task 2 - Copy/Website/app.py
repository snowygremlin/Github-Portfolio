from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'  # Example URI, change for your DB
app.secret_key = '029075'  
db = SQLAlchemy(app)

# user model  stores user info

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    phone_number = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    signup_date = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    user_role = db.Column(db.Enum('admin', 'user', name='user_role_enum'), default='user', nullable=False)
    owned_products = db.relationship('OwnedProduct', backref='user', lazy=True)

# Consultation model - tracks bookings

class Consultation(db.Model):
    consultation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    consultation_type = db.Column(db.Enum('Solar Panels', 'HEMS', 'EV Charging', name='consultation_type_enum'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    status = db.Column(db.Enum('Scheduled', 'Completed', 'Pending', name='consultation_status_enum'), nullable=False)

# energy usage to save users energy wastage

class EnergyUsage(db.Model):
    usage_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    solar_panel_energy = db.Column(db.Numeric(10, 2), nullable=True)
    ev_charging_energy = db.Column(db.Numeric(10, 2), nullable=True)
    hems_efficiency = db.Column(db.Numeric(5, 2), nullable=True)
    recorded_date = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

# carbon footprint modal

class CarbonFootprint(db.Model):
    carbon_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    emission_type = db.Column(db.Enum('Home', 'Transportation', 'Lifestyle', name='emission_type_enum'), nullable=False)
    emission_amount = db.Column(db.Numeric(10, 2), nullable=False)  # CO2 emission amount in kg
    calculation_date = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)



class UserHub(db.Model):
    hub_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultation.consultation_id'), nullable=True)
    energy_usage_id = db.Column(db.Integer, db.ForeignKey('energy_usage.usage_id'), nullable=True)

# owned product model  links users to their products

class OwnedProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_type = db.Column(db.String(50), nullable=False)  # e.g., Solar Panels, HEMS
    purchase_date = db.Column(db.Date, nullable=False)  # Date of purchase
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # Link to the user


# Create the tables in the database (only once on initial setup)
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template("home.html") # Serve the homepage

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']

        # Check if email or phone number already exists
        existing_user = User.query.filter((User.email == email) | (User.phone_number == phone_number)).first()
        if existing_user:
            flash("Email or phone number already exists. Please try again.", "danger")
            return redirect('/signup')

        try:
            # Add new user to the database
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                password=password,  # Note: Always hash passwords in production!
                signup_date=datetime.now(timezone.utc),
                user_role="user"  # Ensure `user_role` is correctly set
            )
            db.session.add(new_user)
            db.session.commit()

            # Flash a success message
            flash("Account created successfully! You can now log in.", "success")
            return redirect('/login')

        except Exception as e:
            # Rollback in case of any errors
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect('/signup')

    # Render the signup form
    return render_template("signup.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        user = User.query.filter((User.email == identifier) | (User.phone_number == identifier)).first()
        if user and user.password == password:
            session['user_id'] = user.user_id
            session['user_role'] = user.user_role  # Add user_role to the session
            flash("Login successful!", "success")
            return redirect('/dashboard')  # Redirect to the dashboard
        else:
            flash("Invalid login credentials.", "danger")
            return redirect('/login')

    return render_template('login.html')



@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access your dashboard.", "warning")
        return redirect('/login')

    user = db.session.get(User, session['user_id'])
    if not user:
        flash("User not found. Please log in again.", "danger")
        return redirect('/login')

    # Fetch all owned products for the current user
    owned_products = OwnedProduct.query.filter_by(user_id=user.user_id).all()

    # Fetch all consultations for the current user
    consultations = Consultation.query.filter_by(user_id=user.user_id).all()

    # Handle form submission for adding owned products
    if request.method == 'POST' and 'product_type' in request.form:
        product_type = request.form['product_type']
        purchase_date = request.form['purchase_date']

        new_product = OwnedProduct(
            product_type=product_type,
            purchase_date=datetime.strptime(purchase_date, '%Y-%m-%d'),
            user_id=user.user_id
        )
        db.session.add(new_product)
        db.session.commit()
        flash("Product added successfully!", "success")
        return redirect('/dashboard')

    # Handle GET request for visualization
    time_period = request.args.get('time_period')
    selected_product = request.args.get('product')

    # Default empty values
    labels = []
    generated_energy = []
    used_energy = []
    message = ""

    # Validate that both fields are provided
    if not time_period or not selected_product:
        message = "Please select both a timeframe and a product to view data."
    else:
        # Timeframe settings
        if time_period == 'day':
            hours = 24
            labels = [f"{hour}:00" for hour in range(hours)]
            generated_energy = [random.uniform(0.5, 1.5) for _ in range(hours)]
            used_energy = [random.uniform(0.8, 2.0) for _ in range(hours)]
        elif time_period in ['week', 'month']:
            if time_period == 'week':
                days = 7
            elif time_period == 'month':
                days = 30
            labels = [(datetime.now() - timedelta(days=days-i)).strftime('%Y-%m-%d') for i in range(days)]
            generated_energy = [random.uniform(5, 15) for _ in range(days)]
            used_energy = [random.uniform(8, 20) for _ in range(days)]

    return render_template(
        'dashboard.html',
        user=user,
        owned_products=owned_products,
        consultations=consultations,  # Pass consultations to the template
        labels=labels,
        generated_energy=generated_energy,
        used_energy=used_energy,
        time_period=time_period,
        selected_product=selected_product,
        message=message
    )





@app.route('/owned_products')
def owned_products():
    if 'user_id' not in session:
        flash("Please log in to view your products.", "warning")
        return redirect('/login')

    owned_products = OwnedProduct.query.filter_by(user_id=session['user_id']).all()

    return render_template('owned_products.html', owned_products=owned_products)



@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear user session
    flash("Logged out successfully.", "success")
    return redirect('/')


@app.route('/carboncalculator', methods=['GET', 'POST'])
def carbon_calculator():
    if request.method == 'POST':
        # Retrieve user inputs from the form
        electricity_usage = float(request.form['electricity_usage'])  # kWh per month
        driving_miles = float(request.form['driving_miles'])         # miles per month
        new_products = int(request.form['new_products'])            # items per month

        # Multipliers (arbitrary values for now)
        electricity_multiplier = 0.5   # kg CO2 per kWh
        driving_multiplier = 0.4       # kg CO2 per mile
        product_multiplier = 10.0      # kg CO2 per new product

        # Calculate carbon footprint
        electricity_emissions = electricity_usage * electricity_multiplier
        driving_emissions = driving_miles * driving_multiplier
        product_emissions = new_products * product_multiplier
        total_emissions = electricity_emissions + driving_emissions + product_emissions

        # Flash result to display on the screen
        flash(f"Your estimated monthly carbon footprint is {total_emissions:.2f} kg CO₂!", "success")
        return redirect('/carboncalculator')

    return render_template('carboncalculator.html')

@app.route('/consultation_page')
def consultation_page():
    if 'user_id' not in session:
        flash("Please log in to access the consultation page.", "warning")
        return redirect('/login')
    
    return render_template('consultation.html')


@app.route('/consultation', methods=['GET', 'POST'])
def consultation():
    if 'user_id' not in session:
        flash("Please log in to book a consultation.", "warning")
        return redirect('/login')

    if request.method == 'POST':
        consultation_type = request.form['consultation_type']
        booking_date = request.form['booking_date']

        # Save the consultation to the database
        new_consultation = Consultation(
            user_id=session['user_id'],
            consultation_type=consultation_type,
            booking_date=datetime.strptime(booking_date, '%Y-%m-%d'),
            status="Scheduled"
        )
        db.session.add(new_consultation)
        db.session.commit()
        flash("Consultation booked successfully!", "success")
        return redirect('/dashboard')

    return render_template('consultation.html') # Serve booking page


@app.route('/cancel_consultation/<int:consultation_id>')
def cancel_consultation(consultation_id):
    if 'user_id' not in session:
        flash("Please log in to cancel consultations.", "warning")
        return redirect('/login')

    consultation = db.session.get(Consultation, consultation_id)
    if consultation and consultation.user_id == session['user_id']:
        db.session.delete(consultation) # Remove consultation
        db.session.commit()
        flash("Consultation canceled successfully.", "success")
    else:
        flash("Consultation not found or you don't have permission to cancel it.", "danger")

    return redirect('/dashboard')

@app.route('/admin', methods=['GET'])
def admin_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'admin':  # Correct access control check
        flash("Access denied. Admins only.", "danger")
        return redirect('/')
    
    # Placeholder analytics data
    analytics_data = {
        'total_visitors': 1500,
        'active_users': 25,
        'page_views': 8200,
        'bounce_rate': 32.5,
        'top_pages': [
            {'title': 'Home', 'views': 2500},
            {'title': 'EV Charging', 'views': 1200},
            {'title': 'Solar Panels', 'views': 800},
            {'title': 'HEMS', 'views': 700},
            {'title': 'Carbon Calculator', 'views': 500}
        ]
    }

    return render_template('admin.html', analytics=analytics_data)



# Routes to pages with no functions

@app.route('/ev')
def ev_page():
    return render_template('ev.html')


@app.route('/hems')
def hems_page():
    return render_template('hems.html')


@app.route('/solar')
def solar_page():
    return render_template('solar.html')

@app.route('/greenenergy')
def greeneenergy_page():
    return render_template('greenenergy.html')

@app.route('/faq')
def faq_page():
    return render_template('faq.html')




if __name__ == '__main__':
    app.run(debug=True)
