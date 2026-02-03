# 🏥 MediBridge – Hospital Management & ML-Based Self-Diagnosis System

MediBridge is a web-based hospital management system that integrates appointment management, doctor availability handling, and a machine-learning based self-diagnosis and recommendation module into a single platform.

The system helps patients identify possible conditions, recommends suitable doctors based on specialization, and enables seamless appointment booking.

---

## ✨ Features

- Secure patient and doctor authentication with role-based dashboards
- Online appointment booking and status tracking
- Doctor availability and appointment management
- ML-based self-diagnosis using symptom selection
- Condition prediction and specialization mapping
- Automatic doctor recommendation
- Diagnosis history and medical record tracking
- Database-backed record management using SQLite

---

## 🧩 Core Modules

- **Patient Module** – Registration, login, dashboard access and self-diagnosis  
- **Doctor Module** – Dashboard, appointment handling and availability management  
- **Appointment Module** – Doctor selection, booking and status tracking  
- **Diagnosis (ML) Module** – Symptom input, condition prediction, specialization mapping and confidence scoring  
- **Database Management Module** – Stores patient, doctor, appointment and diagnosis records using SQLite  

---

## 🛠️ Technology Stack

- **Backend:** Python, Django  
- **Frontend:** HTML, CSS, Bootstrap, JavaScript  
- **Machine Learning:** Scikit-learn, Joblib  
- **Database:** SQLite3  
- **Tools:** VS Code, Git, Django ORM  

---

## ⚙️ Installation & Setup

```bash
git clone <your-repository-url>
cd hospital
```

Create and activate virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Start the server:

```bash
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000
```

---

## 🤖 ML Model Training

The diagnosis module supports training using an external dataset.

```bash
python manage.py train_diagnosis_model --data <path_to_dataset>
```

The trained model is stored using Joblib and used during prediction.

---

## 🔐 Security

- Django authentication system
- Role-based access (patient / doctor)
- Session-based login
- CSRF protection for all forms
- Server-side validation and access control
- No direct database exposure

---

## 📁 Project Structure (Main Apps)

```
appointments/
doctors/
patients/
diagnosis/
payments/
analytics/
hospital_project/
```

---

## 🚀 Future Enhancements

- Integration of real medical datasets
- Advanced ML and deep learning models
- Mobile application support
- Multi-language interface
- Video consultation and real-time scheduling
- Online payments and digital prescriptions
- Hospital information system (HIS) integration

---

## 📄 License

This project is developed for academic and learning purposes.
