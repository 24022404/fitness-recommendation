// API Configuration
const API_URL = 'http://localhost:5000/api/recommend';

// Smooth scroll to form
function scrollToForm() {
    document.getElementById('form-section').scrollIntoView({ behavior: 'smooth' });
}

// Form submission handler
document.getElementById('recommendation-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form data
    const formData = {
        age: parseInt(document.getElementById('age').value),
        gender: document.querySelector('input[name="gender"]:checked').value,
        weight: parseFloat(document.getElementById('weight').value),
        height: parseFloat(document.getElementById('height').value),
        experience: document.getElementById('experience').value
    };
    
    // Validation
    if (!validateForm(formData)) {
        return;
    }
    
    // Show loading state
    const submitButton = document.querySelector('.submit-button');
    submitButton.disabled = true;
    document.getElementById('button-text').style.display = 'none';
    document.getElementById('button-loading').style.display = 'inline';
    
    try {
        // Call API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error('API request failed');
        }
        
        const data = await response.json();
        
        // Display results
        displayResults(data);
        
        // Scroll to results
        setTimeout(() => {
            document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });
        }, 300);
        
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to get recommendations. Please make sure the backend server is running.');
    } finally {
        // Reset button
        submitButton.disabled = false;
        document.getElementById('button-text').style.display = 'inline';
        document.getElementById('button-loading').style.display = 'none';
    }
});

// Validation
function validateForm(data) {
    if (data.age < 15 || data.age > 80) {
        alert('Age must be between 15 and 80');
        return false;
    }
    
    if (data.weight < 40 || data.weight > 200) {
        alert('Weight must be between 40 and 200 kg');
        return false;
    }
    
    if (data.height < 1.4 || data.height > 2.2) {
        alert('Height must be between 1.4 and 2.2 meters');
        return false;
    }
    
    return true;
}

// Display results
function displayResults(data) {
    // Show results section
    document.getElementById('results-section').style.display = 'block';
    
    // Main Stats - Success Probability
    const successProb = data.success_probability;
    document.getElementById('success-bar').style.width = successProb + '%';
    document.getElementById('success-value-main').textContent = successProb + '%';
    
    // Main Stats - Goal
    const goalHTML = `<span class="goal-text">${formatGoal(data.goal)}</span>`;
    document.getElementById('goal-info').innerHTML = goalHTML;
    
    // Main Stats - Cluster
    document.getElementById('cluster-display').textContent = data.cluster_info;
    
    // Profile Info - Clean metric cards
    const profileHTML = `
        <div class="metric-row">
            <span class="metric-label">Age</span>
            <span class="metric-value">${data.profile.age} years</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Gender</span>
            <span class="metric-value">${data.profile.gender}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Weight</span>
            <span class="metric-value">${data.profile.weight} kg</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Height</span>
            <span class="metric-value">${data.profile.height} m</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">BMI</span>
            <span class="metric-value">${data.profile.bmi} <span class="metric-tag ${getBMIClass(data.profile.bmi)}">${getBMICategory(data.profile.bmi)}</span></span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Body Fat</span>
            <span class="metric-value">~${data.profile.fat_pct}%</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Experience</span>
            <span class="metric-value">${data.profile.experience}</span>
        </div>
    `;
    document.getElementById('profile-info').innerHTML = profileHTML;
    
    // Recommendations - Clean layout
    const recsHTML = `
        <div class="plan-item primary-item">
            <div class="plan-label">
                <span class="plan-icon">🏋️</span>
                Workout Type
            </div>
            <div class="plan-value">${data.recommendations.workout_type}</div>
        </div>
        <div class="plan-item">
            <div class="plan-label">
                <span class="plan-icon">📅</span>
                Frequency
            </div>
            <div class="plan-value">${data.recommendations.frequency}</div>
        </div>
        <div class="plan-item">
            <div class="plan-label">
                <span class="plan-icon">🥩</span>
                Protein Level
            </div>
            <div class="plan-value">${data.recommendations.protein_level}</div>
        </div>
        <div class="plan-item">
            <div class="plan-label">
                <span class="plan-icon">⏰</span>
                Best Time
            </div>
            <div class="plan-value">${data.recommendations.best_time}</div>
        </div>
        <div class="plan-item success-item">
            <div class="plan-label">
                <span class="plan-icon">🎯</span>
                Expected Success
            </div>
            <div class="plan-value">${data.recommendations.expected_success_rate}%</div>
        </div>
    `;
    document.getElementById('recommendations').innerHTML = recsHTML;
    
    // Nutrition - Metric cards
    const nutritionHTML = `
        <div class="nutrition-item">
            <div class="nutrition-label">Daily Protein</div>
            <div class="nutrition-value">${data.nutrition.protein_grams}g</div>
            <div class="nutrition-sublabel">${data.nutrition.protein_level} Level</div>
        </div>
        <div class="nutrition-item">
            <div class="nutrition-label">Daily Calories</div>
            <div class="nutrition-value">${data.nutrition.calories}</div>
            <div class="nutrition-sublabel">kcal/day</div>
        </div>
        <div class="nutrition-item">
            <div class="nutrition-label">Protein per kg</div>
            <div class="nutrition-value">${(data.nutrition.protein_grams / data.profile.weight).toFixed(1)}g</div>
            <div class="nutrition-sublabel">per kg bodyweight</div>
        </div>
    `;
    document.getElementById('nutrition-info').innerHTML = nutritionHTML;
    
    // Exercises - Grid layout
    const exercisesHTML = data.exercises.map((exercise, index) => 
        `<div class="exercise-card">
            <div class="exercise-number">${index + 1}</div>
            <div class="exercise-name">${exercise}</div>
        </div>`
    ).join('');
    document.getElementById('exercises-list').innerHTML = exercisesHTML;
    
    // Insights - Professional cards
    const insightsHTML = `
        <div class="insight-card">
            <div class="insight-header">
                <svg class="insight-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                </svg>
                <span class="insight-title">Top Success Factor</span>
            </div>
            <div class="insight-content">${data.insights.top_success_factor}</div>
        </div>
        <div class="insight-card">
            <div class="insight-header">
                <svg class="insight-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M12 6v6l4 2"/>
                </svg>
                <span class="insight-title">Protein Importance</span>
            </div>
            <div class="insight-content">${data.insights.protein_importance}</div>
        </div>
        <div class="insight-card">
            <div class="insight-header">
                <svg class="insight-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
                </svg>
                <span class="insight-title">Optimal Timing</span>
            </div>
            <div class="insight-content">${data.insights.timing}</div>
        </div>
    `;
    document.getElementById('insights').innerHTML = insightsHTML;
}

// Helper: Get BMI category
function getBMICategory(bmi) {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
}

// Helper: Get BMI class for styling
function getBMIClass(bmi) {
    if (bmi < 18.5) return 'tag-warning';
    if (bmi < 25) return 'tag-success';
    if (bmi < 30) return 'tag-warning';
    return 'tag-danger';
}

// Helper: Format goal
function formatGoal(goal) {
    const goalMap = {
        'Weight_Loss': 'Weight Loss',
        'Muscle_Gain': 'Muscle Gain',
        'Fat_Loss': 'Fat Loss',
        'Fitness': 'General Fitness'
    };
    return goalMap[goal] || goal;
}

// Reset form
function resetForm() {
    document.getElementById('recommendation-form').reset();
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('form-section').scrollIntoView({ behavior: 'smooth' });
}

// Console welcome message
console.log('%c🏋️ AI Workout Recommender ', 'background: #ff4655; color: white; padding: 10px; font-size: 16px; font-weight: bold;');
console.log('%cPowered by: Association Rules (Apriori) + Random Forest + K-Means', 'color: #8b92a8; font-size: 12px;');
console.log('%cAnalyzed 51,633 workout records from 973 users', 'color: #00d9a3; font-size: 12px;');