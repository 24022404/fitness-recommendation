# Gym Workout Recommendation System

A smart workout recommendation system utilizing Data Mining and Machine Learning techniques.

## Team Members

- Nguyễn Đức Huy
- Dương Lý Khánh Ha
- Nguyễn Đức Minh

## Project Overview

This project builds a personalized gym workout recommendation system by combining multiple data mining approaches:

- **K-Means Clustering**: Customer segmentation based on physical characteristics and fitness levels
- **Apriori Algorithm**: Mining association rules to discover workout patterns and exercise combinations
- **Classification Models**: Predicting suitable workout types for individual users

## Dataset

- `gym_members_exercise_tracking.csv`: 973 gym members with exercise tracking data
- `megaGymDataset.csv`: 2,918 detailed workout exercises

## Technologies

- Python 3.x
- pandas, numpy, scikit-learn
- mlxtend (Apriori algorithm)
- matplotlib, seaborn

## Usage

```bash
jupyter notebook gym_data_mining_detailed_report.ipynb
```

## Key Results

- Successfully segmented 973 gym members into 4 distinct customer groups using K-Means (optimal K=4 via Elbow Method)
- Mined 528 association rules with 275 frequent itemsets using Apriori algorithm
- Top rules achieved Lift values of 3.5-5.3, indicating strong relationships between workout patterns
- Baseline model accuracy: 24.10% (original data)
- Expert-labeled model accuracy: 100.00% (after applying domain knowledge-based labeling)

---

**Course**: Data Mining  
**Assignment**: Seminar 2 - Association Rule Mining
