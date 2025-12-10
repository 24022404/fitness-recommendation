# Khai Phá Mẫu Tập Luyện Gym
**Khai Phá Dữ Liệu - Bài Tập Seminar**

## Thành Viên Nhóm
- Nguyễn Đức Huy
- Dương Lý Khánh Ha
- Nguyễn Đức Minh

---

## Tổng Quan
Khai phá mẫu tập luyện thành công và xây dựng hệ thống gợi ý workout thông minh.

**Phương pháp:**
- Khai phá luật kết hợp (Apriori) - Bắt buộc
- Phân loại (Random Forest)
- Phân cụm (K-Means)
- Hệ thống gợi ý

---

## Bộ Dữ Liệu
**Đầu vào:**
- `gym_members_exercise_tracking.csv` - 973 người dùng
- `megaGymDataset.csv` - 2,918 bài tập

**Đầu ra:**
- `gym_workout_sessions.csv` - 51,633 bản ghi (sau khi tăng cường)

**Các Đặc Trưng Chính Được Thêm Vào:**
- Mục tiêu (Giảm_Cân/Tăng_Cơ/Đốt_Mỡ/Thể_Lực)
- Dinh dưỡng (Lượng protein, Mức protein, Calories)
- Thời gian (Sáng/Chiều/Tối)
- Nhãn thành công (0/1)

---

## Cấu Trúc Dự Án
```
├── data/
│   ├── gym_members_exercise_tracking.csv
│   ├── megaGymDataset.csv
│   └── gym_workout_sessions.csv
├── 01_data_merge_clean.ipynb        # Tăng cường dữ liệu
├── 02_main_analysis.ipynb           # Phân tích chính
└── README.md
```

---

## Các Notebook
### 1. Tăng Cường Dữ Liệu (`01_data_merge_augmentation.ipynb`)
- Hợp nhất 2 bộ dữ liệu
- Thêm dinh dưỡng, thời gian, mục tiêu
- Tạo 51,633 bản ghi tập luyện
- Tính toán nhãn thành công

### 2. Phân Tích Chính (`02_main_analysis.ipynb`)
**Luật Kết Hợp:**
- Tìm thấy 140 mẫu thành công
- Tốt nhất: `{Tần_suất_4, Protein_Cao} → Thành_Công` (Lift: 9.21)

**Phân Loại:**
- Random Forest: 99.85% độ chính xác
- Đặc trưng quan trọng nhất: Tần_suất_mỗi_tuần (19.3%)

**Phân Cụm:**
- 4 nhóm người dùng (K-Means)
- Cụm 3: 97% tỷ lệ thành công (tần suất cao)

**Gợi Ý:**
- Đầu vào: Hồ sơ người dùng → Đầu ra: Kế hoạch tập luyện
- Dựa trên phân cụm + luật kết hợp

---

## Kết Quả Chính
- Tần suất cao (4-5 ngày/tuần) = yếu tố thành công mạnh nhất
- Mức protein quan trọng: Protein cao → 100% thành công cho tăng cơ
- Tập buổi sáng tốt hơn một chút so với buổi tối
- Xác định được 4 nhóm người dùng khác biệt

---

## Cài Đặt
```bash
pip install pandas numpy matplotlib seaborn mlxtend scikit-learn
```

Chạy các notebook theo thứ tự:
1. `01_data_merge_clean.ipynb` → Tạo bộ dữ liệu
2. `02_main_analysis.ipynb` → Chạy phân tích

---

## Tài Liệu Tham Khảo
**Bộ dữ liệu:**
- [Kaggle: Gym Members](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset)
- [Kaggle: MegaGym](https://www.kaggle.com/datasets/niharika41298/gym-exercise-data)
