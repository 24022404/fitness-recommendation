from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import pickle

app = Flask(__name__)
CORS(app)  # Allow frontend to call API

# Load data
df = pd.read_csv('data/gym_workout_sessions.csv')

# ═══════════════════════════════════════════════════════
# 🆕 LOAD RANDOM FOREST MODEL & LABEL ENCODERS
# ═══════════════════════════════════════════════════════
try:
    # Load trained Random Forest model
    with open('models/rf_model.pkl', 'rb') as f:
        rf_model = pickle.load(f)
    
    # Load label encoders
    with open('models/label_encoders.pkl', 'rb') as f:
        label_encoders = pickle.load(f)
    
    print("✅ Random Forest model loaded successfully")
except:
    print("⚠️ Random Forest model not found. Success rate prediction disabled.")
    rf_model = None
    label_encoders = None

# Helper functions
def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 1)

def estimate_fat_pct(bmi, gender, age):
    """Estimate body fat % from BMI"""
    if gender == 'Male':
        fat = (1.20 * bmi) + (0.23 * age) - 16.2
    else:
        fat = (1.20 * bmi) + (0.23 * age) - 5.4
    return round(max(10, min(45, fat)), 1)

def calculate_nutrition(goal, weight):
    """Calculate nutrition based on user's CHOSEN goal"""
    if goal == 'Muscle_Gain':
        protein = weight * 2.0
        protein_level = 'High'
        calories = weight * 35
    elif goal in ['Weight_Loss', 'Fat_Loss']:
        protein = weight * 1.6
        protein_level = 'Medium'
        calories = weight * 25
    else:  # Fitness
        protein = weight * 1.2
        protein_level = 'Low'
        calories = weight * 30
    
    return {
        'protein_grams': round(protein, 0),
        'protein_level': protein_level,
        'calories': round(calories, 0)
    }

def get_success_patterns(goal, workout_type):
    """Get recommendations based on user's CHOSEN goal and workout type"""
    patterns = {
        'Weight_Loss': {
            'workout_type': workout_type if workout_type != 'Mixed' else 'Cardio or HIIT',
            'frequency': '4-5 days/week',
            'protein': 'Medium',
            'best_time': 'Morning',
            'apriori_success_rate': 80  # From Apriori rules
        },
        'Muscle_Gain': {
            'workout_type': workout_type if workout_type != 'Mixed' else 'Strength Training',
            'frequency': '4-5 days/week',
            'protein': 'High',
            'best_time': 'Morning or Evening',
            'apriori_success_rate': 100  # From Apriori rules
        },
        'Fat_Loss': {
            'workout_type': workout_type if workout_type != 'Mixed' else 'HIIT',
            'frequency': '4-5 days/week',
            'protein': 'Medium-High',
            'best_time': 'Morning',
            'apriori_success_rate': 75
        },
        'Fitness': {
            'workout_type': workout_type if workout_type != 'Mixed' else 'Mixed (Cardio + Strength)',
            'frequency': '3-4 days/week',
            'protein': 'Medium',
            'best_time': 'Any',
            'apriori_success_rate': 65
        }
    }
    return patterns.get(goal, patterns['Fitness'])

def get_exercises(workout_type, experience):
    """Get suggested exercises based on user's CHOSEN workout type"""
    
    # Use user's preferred workout type directly
    if workout_type == 'Mixed':
        # For mixed, get variety
        exercises = []
        for wtype in ['Strength', 'Cardio']:
            ex = df[
                (df['Workout_Type'] == wtype) & 
                (df['Experience_Level'] == experience)
            ]['Exercise_Name'].value_counts().head(3).index.tolist()
            exercises.extend(ex)
    else:
        # Filter exercises based on user's choice
        exercises = df[
            (df['Workout_Type'] == workout_type) & 
            (df['Experience_Level'] == experience)
        ]['Exercise_Name'].value_counts().head(5).index.tolist()
    
    # If not enough, relax experience constraint
    if len(exercises) < 4:
        if workout_type == 'Mixed':
            exercises = df[df['Workout_Type'].isin(['Strength', 'Cardio'])]['Exercise_Name'].value_counts().head(5).index.tolist()
        else:
            exercises = df[df['Workout_Type'] == workout_type]['Exercise_Name'].value_counts().head(5).index.tolist()
    
    return exercises[:5] if exercises else ['Push-ups', 'Squats', 'Planks', 'Jumping Jacks', 'Burpees']

def predict_cluster(age, bmi, fat_pct):
    """Simple rule-based cluster assignment"""
    if age < 30 and bmi < 25:
        return 1
    elif bmi >= 30:
        return 0
    elif age >= 45:
        return 2
    else:
        return 3

# ═══════════════════════════════════════════════════════
# 🆕 PREDICT SUCCESS RATE using Random Forest
# ═══════════════════════════════════════════════════════
def predict_success_rate(user_profile):
    """
    Predict success rate using Random Forest
    
    Input:
        user_profile: dict with all user info
    
    Output:
        success_rate: float (0-100) or None if model unavailable
    """
    if rf_model is None or label_encoders is None:
        return None
    
    try:
        # Extract frequency from pattern (e.g., "4-5 days/week" -> 4)
        freq_str = user_profile['frequency']
        frequency = int(freq_str.split('-')[0]) if '-' in freq_str else 4
        
        # Map workout type
        workout_mapping = {
            'Cardio or HIIT': 'Cardio',
            'Strength Training': 'Strength',
            'Mixed (Cardio + Strength)': 'Strength',
            'HIIT': 'HIIT',
            'Yoga': 'Yoga',
            'Cardio': 'Cardio',
            'Strength': 'Strength',
            'Mixed': 'Strength'
        }
        workout_for_rf = workout_mapping.get(user_profile['workout_type_raw'], 'Strength')
        
        # Encode categorical variables
        goal_enc = label_encoders['Goal'].transform([user_profile['goal']])[0]
        workout_enc = label_encoders['Workout_Type'].transform([workout_for_rf])[0]
        protein_enc = label_encoders['Protein_Level'].transform([user_profile['protein_level']])[0]
        
        # Map best_time to Time
        time_mapping = {
            'Morning': 'Morning',
            'Evening': 'Evening',
            'Morning or Evening': 'Morning',
            'Any': 'Morning',
            'Afternoon': 'Afternoon'
        }
        workout_time = time_mapping.get(user_profile['best_time'], 'Morning')
        time_enc = label_encoders['Workout_Time'].transform([workout_time])[0]
        
        exp_enc = label_encoders['Experience_Level'].transform([user_profile['experience']])[0]
        gender_enc = label_encoders['Gender'].transform([user_profile['gender']])[0]
        
        # Create feature vector (12 features - MUST match training order!)
        # ['Goal', 'Workout_Type', 'Frequency_per_week', 'Protein_Level', 
        #  'Workout_Time', 'Duration_Minutes', 'BMI', 'Fat_pct', 'Age', 
        #  'Gender', 'Experience_Level', 'Num_Exercises']
        
        features = [
            goal_enc,                      # Goal
            workout_enc,                   # Workout_Type
            frequency,                     # Frequency_per_week
            protein_enc,                   # Protein_Level
            time_enc,                      # Workout_Time
            55,                           # Duration_Minutes (average)
            user_profile['bmi'],          # BMI
            user_profile['fat_pct'],      # Fat_pct
            user_profile['age'],          # Age
            gender_enc,                    # Gender
            exp_enc,                       # Experience_Level
            5                             # Num_Exercises (average)
        ]
        
        # Predict probability
        proba = rf_model.predict_proba([features])[0]
        success_rate = round(proba[1] * 100, 1)  # % of Success=1
        
        return success_rate
        
    except Exception as e:
        print(f"Error in RF prediction: {e}")
        return None

# API Routes
@app.route('/')
def home():
    return jsonify({
        'message': 'Gym Workout Recommendation API',
        'endpoints': {
            '/api/recommend': 'POST - Get workout recommendations'
        }
    })

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        
        # Extract input - NOW INCLUDING user's choices
        age = int(data.get('age'))
        gender = data.get('gender')
        weight = float(data.get('weight'))
        height = float(data.get('height'))
        experience = data.get('experience', 'Beginner')
        
        # 🆕 GET USER'S CHOICES
        goal = data.get('goal', 'Fitness')  # User chooses their goal
        workout_type = data.get('workout_type', 'Mixed')  # User chooses workout type
        
        # Calculate derived values
        bmi = calculate_bmi(weight, height)
        fat_pct = estimate_fat_pct(bmi, gender, age)
        
        # Use user's CHOSEN goal and workout type
        nutrition = calculate_nutrition(goal, weight)
        cluster = predict_cluster(age, bmi, fat_pct)
        patterns = get_success_patterns(goal, workout_type)
        exercises = get_exercises(workout_type, experience)
        
        # ═══════════════════════════════════════════════════════
        # 🆕 PREDICT SUCCESS RATE using Random Forest
        # ═══════════════════════════════════════════════════════
        user_profile_for_rf = {
            'age': age,
            'gender': gender,
            'bmi': bmi,
            'fat_pct': fat_pct,
            'goal': goal,
            'experience': experience,
            'frequency': patterns['frequency'],
            'protein_level': nutrition['protein_level'],
            'best_time': patterns['best_time'],
            'workout_type_raw': workout_type
        }
        
        ai_success_rate = predict_success_rate(user_profile_for_rf)
        
        # Build response
        response = {
            'profile': {
                'age': age,
                'gender': gender,
                'weight': weight,
                'height': height,
                'bmi': bmi,
                'fat_pct': fat_pct,
                'experience': experience
            },
            'goal': goal,  # Echo back user's choice
            'cluster': cluster,
            'cluster_info': {
                0: 'Overweight, Moderate Activity',
                1: 'Young, Low Commitment',
                2: 'Middle-aged, Moderate',
                3: 'High Performance'
            }[cluster],
            'nutrition': nutrition,
            'recommendations': {
                'workout_type': patterns['workout_type'],
                'frequency': patterns['frequency'],
                'protein_level': patterns['protein'],
                'best_time': patterns['best_time']
            },
            'exercises': exercises,
            # 🆕 SUCCESS RATE INFO
            'success_rate': {
                'apriori': patterns['apriori_success_rate'],  # From association rules
                'ai_prediction': ai_success_rate,  # From Random Forest
                'available': ai_success_rate is not None
            },
            'insights': {
                'top_success_factor': 'Frequency (4-5 days/week is optimal)',
                'protein_importance': f"{nutrition['protein_level']} protein intake recommended for {goal.replace('_', ' ')}",
                'timing': f"{patterns['best_time']} workouts are ideal for your schedule"
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)