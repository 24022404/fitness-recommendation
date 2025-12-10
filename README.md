# Gym Workout Pattern Mining

**Data Mining - Seminar Assignment**

## Team Members
- Nguyễn Đức Huy
- Dương Lý Khánh Ha
- Nguyễn Đức Minh

---

## Overview

Khai phá mẫu tập luyện thành công và xây dựng hệ thống gợi ý workout thông minh.

**Methods:**
- Association Rules Mining (Apriori) - Required
- Classification (Random Forest)
- Clustering (K-Means)
- Recommendation System

---

## Dataset

**Input:**
- `gym_members_exercise_tracking.csv` - 973 users
- `megaGymDataset.csv` - 2,918 exercises

**Output:**
- `gym_workout_sessions.csv` - 51,633 records (augmented)

**Key Features Added:**
- Goal (Weight_Loss/Muscle_Gain/Fat_Loss/Fitness)
- Nutrition (Protein intake, Protein level, Calories)
- Timing (Morning/Afternoon/Evening)
- Success label (0/1)

---

## Project Structure

```
├── data/
│   ├── gym_members_exercise_tracking.csv
│   ├── megaGymDataset.csv
│   └── gym_workout_sessions.csv
├── 01_data_merge_clean.ipynb        # Data augmentation
├── 02_main_analysis.ipynb           # Main analysis
└── README.md
```

---

## Notebooks

### 1. Data Augmentation (`01_data_merge_clean.ipynb`)
- Merge 2 datasets
- Add nutrition, timing, goals
- Generate 51,633 workout records
- Calculate success labels

### 2. Main Analysis (`02_main_analysis.ipynb`)

**Association Rules:**
- Found 140 success patterns
- Best: `{Freq_4, Protein_High} → Success` (Lift: 9.21)

**Classification:**
- Random Forest: 99.85% accuracy
- Top feature: Frequency_per_week (19.3%)

**Clustering:**
- 4 user segments (K-Means)
- Cluster 3: 97% success rate (high frequency)

**Recommendation:**
- Input: User profile → Output: Workout plan
- Based on clustering + association rules

---

## Key Results

- High frequency (4-5 days/week) = strongest success factor
- Protein level matters: High protein → 100% success for muscle gain
- Morning workouts slightly better than evening
- 4 distinct user types identified

---

## Installation

```bash
pip install pandas numpy matplotlib seaborn mlxtend scikit-learn
```

Run notebooks in order:
1. `01_data_merge_clean.ipynb` → Generate dataset
2. `02_main_analysis.ipynb` → Run analysis

---

## References

**Datasets:**
- [Kaggle: Gym Members](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset)
- [Kaggle: MegaGym](https://www.kaggle.com/datasets/niharika41298/gym-exercise-data)
