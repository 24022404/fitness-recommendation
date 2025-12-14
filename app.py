from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Allow frontend to call API

# Load data
df = pd.read_csv(r'C:\Users\ducmi\OneDrive\Desktop\(19-01)KhaiPhaVaPhanTichDuLieu\Bài tập lập trình 2\fitness-recommendation\data\gym_workout_sessions.csv')

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

def determine_goal(bmi, fat_pct, gender):
    if bmi >= 30:
        return 'Weight_Loss'
    if bmi < 18.5:
        return 'Muscle_Gain'
    if (gender == 'Male' and fat_pct > 25) or (gender == 'Female' and fat_pct > 32):
        return 'Fat_Loss'
    return 'Fitness'

def calculate_nutrition(goal, weight):
    if goal == 'Muscle_Gain':
        protein = weight * 2.0
        protein_level = 'High'
        calories = weight * 35
    elif goal in ['Weight_Loss', 'Fat_Loss']:
        protein = weight * 1.6
        protein_level = 'Medium'
        calories = weight * 25
    else:
        protein = weight * 1.2
        protein_level = 'Low'
        calories = weight * 30
    
    return {
        'protein_grams': round(protein, 0),
        'protein_level': protein_level,
        'calories': round(calories, 0)
    }

def get_success_patterns(goal):
    """Get top success patterns for a goal"""
    patterns = {
        'Weight_Loss': {
            'workout_type': 'Cardio or HIIT',
            'frequency': '4-5 days/week',
            'protein': 'Medium',
            'best_time': 'Morning',
            'success_rate': 80
        },
        'Muscle_Gain': {
            'workout_type': 'Strength Training',
            'frequency': '4-5 days/week',
            'protein': 'High',
            'best_time': 'Morning or Evening',
            'success_rate': 100
        },
        'Fat_Loss': {
            'workout_type': 'HIIT',
            'frequency': '4-5 days/week',
            'protein': 'Medium-High',
            'best_time': 'Morning',
            'success_rate': 75
        },
        'Fitness': {
            'workout_type': 'Mixed (Cardio + Strength)',
            'frequency': '3-4 days/week',
            'protein': 'Medium',
            'best_time': 'Any',
            'success_rate': 65
        }
    }
    return patterns.get(goal, patterns['Fitness'])

def get_exercises(goal, experience):
    """Get suggested exercises based on goal and experience"""
    
    # Map goal to workout type
    goal_to_type = {
        'Weight_Loss': 'Cardio',
        'Muscle_Gain': 'Strength',
        'Fat_Loss': 'HIIT',
        'Fitness': 'Yoga'
    }
    
    workout_type = goal_to_type.get(goal, 'Cardio')
    
    # Filter exercises
    exercises = df[
        (df['Workout_Type'] == workout_type) & 
        (df['Experience_Level'] == experience)
    ]['Exercise_Name'].value_counts().head(5).index.tolist()
    
    # If not enough, relax experience constraint
    if len(exercises) < 4:
        exercises = df[df['Workout_Type'] == workout_type]['Exercise_Name'].value_counts().head(5).index.tolist()
    
    return exercises[:5]

def predict_cluster(age, bmi, fat_pct):
    """Simple rule-based cluster assignment"""
    # Based on analysis results:
    # Cluster 0: Overweight, low freq (50% success)
    # Cluster 1: Young, low commitment (25% success)
    # Cluster 2: Middle-aged, moderate (38% success)
    # Cluster 3: High freq, best results (97% success)
    
    if age < 30 and bmi < 25:
        return 1
    elif bmi >= 30:
        return 0
    elif age >= 45:
        return 2
    else:
        return 3

def calculate_success_probability(goal, bmi, fat_pct, age, gender):
    """Estimate success probability based on profile"""
    score = 50  # Base score
    
    # Goal-body alignment
    if goal == 'Weight_Loss' and bmi >= 30:
        score += 20
    elif goal == 'Muscle_Gain' and bmi < 20:
        score += 20
    elif goal == 'Fat_Loss' and fat_pct > 25:
        score += 15
    
    # Age factor
    if 25 <= age <= 45:
        score += 10
    
    # Gender factor for specific goals
    if goal == 'Muscle_Gain' and gender == 'Male':
        score += 5
    
    return min(95, max(30, score))

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
        
        # Extract input
        age = int(data.get('age'))
        gender = data.get('gender')
        weight = float(data.get('weight'))
        height = float(data.get('height'))
        experience = data.get('experience', 'Beginner')
        
        # Calculate derived values
        bmi = calculate_bmi(weight, height)
        fat_pct = estimate_fat_pct(bmi, gender, age)
        goal = determine_goal(bmi, fat_pct, gender)
        nutrition = calculate_nutrition(goal, weight)
        cluster = predict_cluster(age, bmi, fat_pct)
        success_prob = calculate_success_probability(goal, bmi, fat_pct, age, gender)
        patterns = get_success_patterns(goal)
        exercises = get_exercises(goal, experience)
        
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
            'goal': goal,
            'cluster': cluster,
            'cluster_info': {
                0: 'Overweight, Moderate Activity',
                1: 'Young, Low Commitment',
                2: 'Middle-aged, Moderate',
                3: 'High Performance'
            }[cluster],
            'success_probability': success_prob,
            'nutrition': nutrition,
            'recommendations': {
                'workout_type': patterns['workout_type'],
                'frequency': patterns['frequency'],
                'protein_level': patterns['protein'],
                'best_time': patterns['best_time'],
                'expected_success_rate': patterns['success_rate']
            },
            'exercises': exercises,
            'insights': {
                'top_success_factor': 'Frequency (4-5 days/week is optimal)',
                'protein_importance': f"{nutrition['protein_level']} protein intake recommended for {goal}",
                'timing': f"{patterns['best_time']} workouts show {patterns['success_rate']}% success rate"
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
