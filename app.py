from flask import Flask, render_template, request, send_from_directory
import logging
import traceback
import sys
import os

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_bmi(weight, height):
    if weight <= 0 or height <= 0:
        raise ValueError("Weight and height must be positive values")
    return weight / (height ** 2)

def calculate_bmr(gender, age, weight, height):
    """
    Calculate BMR using the Mifflin-St Jeor Equation
    For this formula, weight should be in kg and height in cm
    """
    if gender == 'female':
        return (10 * weight) + (6.25 * height) - (5 * age) - 161
    elif gender == 'male':
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        raise ValueError("Gender must be 'male' or 'female'")

def calculate_tdee(bmr, activity_level):
    """Calculate Total Daily Energy Expenditure based on activity level"""
    activity_multipliers = {
        'sedentary': 1.2,      # Little or no exercise
        'light': 1.375,        # Light exercise 1-3 days/week
        'moderate': 1.55,      # Moderate exercise 3-5 days/week
        'active': 1.725,       # Active exercise 6-7 days/week
        'very_active': 1.9     # Very active exercise, physical job or training twice a day
    }
    
    if activity_level not in activity_multipliers:
        raise ValueError(f"Unsupported activity level: {activity_level}")
        
    return bmr * activity_multipliers[activity_level]

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25.0:
        return "Normal weight"
    elif 25.0 <= bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"

def get_age_specific_bmi_note(age, bmi, gender):
    """Provide age-specific notes for BMI interpretation"""
    
    if age < 18:
        return "For children and teens, BMI is age- and gender-specific. This adult BMI calculator may not be accurate. Consider consulting a healthcare professional for a proper assessment using pediatric growth charts."
    
    elif age >= 65:
        if bmi < 23:
            return "For older adults over 65, a slightly higher BMI (23-30) may be beneficial. Your BMI is below this range, which could indicate undernutrition."
        elif 23 <= bmi <= 30:
            return "For older adults over 65, a BMI between 23-30 is often considered ideal, which you fall within."
        else:
            return "For older adults, very high BMI values over 30 are still associated with health risks, though the threshold may be slightly higher than for younger adults."
    
    elif age >= 18 and age < 25:
        if bmi < 19:
            return "Young adults with BMI below 19 may still be completing their growth. Consider discussing with a healthcare provider."
    
    # Pregnancy note for women of childbearing age
    if gender == 'female' and 18 <= age <= 45:
        return "For women who are pregnant or breastfeeding, BMI calculations are not applicable. Please consult your healthcare provider for appropriate weight guidelines."
    
    return None  # No specific note needed

def convert_weight(weight, unit):
    """Convert weight to kg from different units"""
    if unit == 'kg':
        return weight
    elif unit == 'lb':
        return weight * 0.45359237  # 1 lb = 0.45359237 kg
    else:
        raise ValueError(f"Unsupported weight unit: {unit}")

def convert_height(height, unit, inches=0):
    """Convert height to meters from different units"""
    if unit == 'm':
        return height
    elif unit == 'cm':
        return height / 100  # 1 cm = 0.01 m
    elif unit == 'ft':
        feet_in_meters = height * 0.3048  # 1 ft = 0.3048 m
        inches_in_meters = inches * 0.0254  # 1 inch = 0.0254 m
        return feet_in_meters + inches_in_meters
    else:
        raise ValueError(f"Unsupported height unit: {unit}")

@app.route('/')
def home():
    try:
        logger.info("Accessing home route")
        try:
            # Check if template exists
            open(os.path.join(app.root_path, 'templates', 'home.html'), 'r')
            logger.info("home.html template found")
        except Exception as e:
            logger.error(f"Template check error: {str(e)}")
            
        # Log all available templates
        try:
            template_files = os.listdir(os.path.join(app.root_path, 'templates'))
            logger.info(f"Available templates: {template_files}")
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
            
        return render_template('home.html', title="Understanding BMI and BMR")
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        logger.error(traceback.format_exc())
        return f"An error occurred: {str(e)}", 500

@app.route('/bmi', methods=['GET', 'POST'])
def bmi_calculator():
    try:
        bmi = None
        category = None
        age_note = None
        error = None
        if request.method == 'POST':
            try:
                # Get form values
                weight = float(request.form['weight'])
                weight_unit = request.form['weight_unit']
                height = float(request.form['height'])
                height_unit = request.form['height_unit']
                
                # Get age and gender if provided
                age = None
                gender = None
                if 'age' in request.form:
                    age = int(request.form['age'])
                if 'gender' in request.form:
                    gender = request.form['gender']
                
                # Get inches if height unit is feet
                inches = 0
                if height_unit == 'ft' and 'inches' in request.form:
                    inches = float(request.form['inches'])
                
                # Convert to kg and meters
                weight_kg = convert_weight(weight, weight_unit)
                height_m = convert_height(height, height_unit, inches)
                
                # Validate input values
                if weight <= 0:
                    raise ValueError("Weight must be a positive number")
                if height <= 0:
                    raise ValueError("Height must be a positive number")
                if age is not None and (age < 2 or age > 120):
                    raise ValueError("Age must be between 2 and 120 years")
                    
                # Check for unrealistic values based on units
                if weight_unit == 'kg' and weight_kg > 500:
                    raise ValueError("Please enter a realistic weight (max 500 kg)")
                elif weight_unit == 'lb' and weight > 1100:
                    raise ValueError("Please enter a realistic weight (max 1100 lb)")
                    
                if height_unit == 'm' and height > 3:
                    raise ValueError("Please enter a realistic height (max 3 m)")
                elif height_unit == 'cm' and height > 300:
                    raise ValueError("Please enter a realistic height (max 300 cm)")
                elif height_unit == 'ft' and height > 9:
                    raise ValueError("Please enter a realistic height (max 9 ft)")
                    
                bmi = round(calculate_bmi(weight_kg, height_m), 2)
                category = get_bmi_category(bmi)
                
                # Get age-specific notes if age is provided
                if age is not None and gender is not None:
                    age_note = get_age_specific_bmi_note(age, bmi, gender)
                    
            except ValueError as e:
                error_msg = str(e)
                if "could not convert" in error_msg.lower():
                    error = "Please enter valid numbers."
                else:
                    error = error_msg
                bmi = None
                category = None
                age_note = None
        logger.info("Rendering BMI calculator page")
        return render_template('index.html', bmi=bmi, category=category, age_note=age_note, error=error, title="BMI Calculator")
    except Exception as e:
        logger.error(f"Error in bmi_calculator route: {str(e)}")
        logger.error(traceback.format_exc())
        return f"An error occurred: {str(e)}", 500

@app.route('/home')
def redirect_home():
    try:
        logger.info("Redirecting to home")
        return render_template('home.html', title="Understanding BMI and BMR")
    except Exception as e:
        logger.error(f"Error in redirect_home route: {str(e)}")
        logger.error(traceback.format_exc())
        return f"An error occurred: {str(e)}", 500

@app.route('/sustainable-engineering')
def sustainable_engineering():
    try:
        logger.info("Accessing sustainable engineering page")
        return render_template('sustainable_engineering.html', title="Sustainable Engineering")
    except Exception as e:
        logger.error(f"Error in sustainable_engineering route: {str(e)}")
        logger.error(traceback.format_exc())
        return f"An error occurred: {str(e)}", 500

@app.route('/pros-cons')
def pros_cons():
    try:
        logger.info("Accessing pros and cons page")
        return render_template('pros_cons.html', title="Pros & Cons of BMI")
    except Exception as e:
        logger.error(f"Error in pros_cons route: {str(e)}")
        logger.error(traceback.format_exc())
        return f"An error occurred: {str(e)}", 500

@app.route('/bmr', methods=['GET', 'POST'])
def bmr():
    try:
        bmr_result = None
        tdee_result = None
        error = None
        if request.method == 'POST':
            try:
                # Get form values
                weight = float(request.form['weight'])
                weight_unit = request.form['weight_unit']
                height = float(request.form['height'])
                height_unit = request.form['height_unit']
                age = int(request.form['age'])
                gender = request.form['gender']
                
                # Get activity level if provided
                activity_level = request.form.get('activity_level', 'sedentary')
                
                # Get inches if height unit is feet
                inches = 0
                if height_unit == 'ft' and 'inches' in request.form:
                    inches = float(request.form['inches'])
                
                # Convert to kg and cm
                weight_kg = convert_weight(weight, weight_unit)
                
                # For BMR calculation, height should be in cm
                if height_unit == 'm':
                    height_cm = height * 100
                elif height_unit == 'cm':
                    height_cm = height
                elif height_unit == 'ft':
                    # Convert feet and inches to cm
                    feet_in_cm = height * 30.48  # 1 ft = 30.48 cm
                    inches_in_cm = inches * 2.54  # 1 inch = 2.54 cm
                    height_cm = feet_in_cm + inches_in_cm
                
                # Validate input values
                if weight <= 0:
                    raise ValueError("Weight must be a positive number")
                if height <= 0:
                    raise ValueError("Height must be a positive number")
                if age <= 0 or age > 120:
                    raise ValueError("Age must be between 0 and 120 years")
                    
                # Check for unrealistic values based on units
                if weight_unit == 'kg' and weight_kg > 500:
                    raise ValueError("Please enter a realistic weight (max 500 kg)")
                elif weight_unit == 'lb' and weight > 1100:
                    raise ValueError("Please enter a realistic weight (max 1100 lb)")
                    
                if height_unit == 'm' and height > 3:
                    raise ValueError("Please enter a realistic height (max 3 m)")
                elif height_unit == 'cm' and height > 300:
                    raise ValueError("Please enter a realistic height (max 300 cm)")
                elif height_unit == 'ft' and height > 9:
                    raise ValueError("Please enter a realistic height (max 9 ft)")
                
                # Calculate BMR using the Mifflin-St Jeor Equation
                bmr_result = round(calculate_bmr(gender, age, weight_kg, height_cm), 0)
                
                # Calculate TDEE if activity level is provided
                if activity_level:
                    tdee_result = round(calculate_tdee(bmr_result, activity_level), 0)
                    
            except ValueError as e:
                error_msg = str(e)
                if "could not convert" in error_msg.lower():
                    error = "Please enter valid numbers."
                else:
                    error = error_msg
        logger.info("Rendering BMR calculator page")
        return render_template('bmr.html', bmr_result=bmr_result, tdee_result=tdee_result, error=error, title="BMR Calculator")
    except Exception as e:
        logger.error(f"Error in bmr route: {str(e)}")
        logger.error(traceback.format_exc())
        return f"An error occurred: {str(e)}", 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

# Add a catch-all error handler for Vercel deployment
@app.errorhandler(404)
def not_found(e):
    logger.error(f"404 error: {str(e)}")
    return "Page not found", 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 error: {str(e)}")
    return "Internal server error", 500

if __name__ == '__main__':
    app.run(debug=True)
