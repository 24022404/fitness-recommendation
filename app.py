from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Allow frontend to call API

# Load data
df = pd.read_csv('data/gym_workout_sessions.csv')

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
            'success_rate': 80
        },
        'Muscle_Gain': {
            'workout_type': workout_type if workout_type != 'Mixed' else 'Strength Training',
            'frequency': '4-5 days/week',
            'protein': 'High',
            'best_time': 'Morning or Evening',
            'success_rate': 100
        },
        'Fat_Loss': {
            'workout_type': workout_type if workout_type != 'Mixed' else 'HIIT',
            'frequency': '4-5 days/week',
            'protein': 'Medium-High',
            'best_time': 'Morning',
            'success_rate': 75
        },
        'Fitness': {
            'workout_type': workout_type if workout_type != 'Mixed' else 'Mixed (Cardio + Strength)',
            'frequency': '3-4 days/week',
            'protein': 'Medium',
            'best_time': 'Any',
            'success_rate': 65
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