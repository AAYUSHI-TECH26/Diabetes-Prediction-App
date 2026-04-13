# 🩺 Diabetes Prediction System

A full-stack web application that predicts diabetes risk using Machine Learning, built with Flask and trained on the **Pima Indian Diabetes Dataset**.

---

## ✨ Features

- 🔐 **Role-based Authentication** — Separate login for Patients and Doctors
- 🤖 **ML-Powered Prediction** — Ensemble model trained on real clinical data
- 📊 **Risk Assessment** — Detailed risk score with 4 levels (Low / Moderate / High / Very High)
- 📄 **PDF Report Generation** — Professional downloadable reports via ReportLab
- ✅ **Doctor Verification System** — Doctors can review, verify, and add notes to reports
- 📈 **Model Info Dashboard** — View accuracy, AUC score, and feature importance

---

## 🖥️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| ML Model | Scikit-learn (Ensemble) |
| Database | SQLite |
| PDF Reports | ReportLab |
| Frontend | HTML, CSS, Jinja2 Templates |
| Dataset | Pima Indian Diabetes Dataset |

---

## 📁 Project Structure

```
diabetes_project/
├── app.py                   ← Main Flask app (all routes)
├── report_generator.py      ← PDF generation with ReportLab
├── requirements.txt
├── model/
│   └── predictor.py         ← ML model (Pima dataset embedded)
└── templates/
    ├── base.html             ← Nav, layout, alerts
    ├── index.html            ← Landing page
    ├── login.html
    ├── signup.html
    ├── patient_dashboard.html
    ├── doctor_dashboard.html
    ├── predict.html          ← 8-field prediction form
    ├── result.html           ← Risk score + insights
    ├── verify.html           ← Doctor verification form
    └── model_info.html       ← Accuracy, AUC, feature importance
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/AAYUSHI-TECH26/Diabetes-Prediction-App.git
cd diabetes-prediction-system
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

---

## 👤 Demo Credentials

| Role | Email | Password |
|---|---|---|
| 🩺 Doctor | doctor@demo.com | doctor123 |
| 🧑 Patient | patient@demo.com | patient123 |

---

## 🔬 Input Parameters

The model uses **8 clinical features** from the Pima dataset:

| Parameter | Description |
|---|---|
| Pregnancies | Number of times pregnant |
| Glucose | Plasma glucose concentration (mg/dL) |
| Blood Pressure | Diastolic blood pressure (mmHg) |
| Skin Thickness | Triceps skin fold thickness (mm) |
| Insulin | 2-Hour serum insulin (μU/mL) |
| BMI | Body mass index (kg/m²) |
| Diabetes Pedigree | Diabetes pedigree function score |
| Age | Age in years |

---

## 📊 Risk Levels

| Risk Level | Meaning |
|---|---|
| 🟢 Low Risk | Low probability of diabetes |
| 🟡 Moderate Risk | Borderline — lifestyle changes recommended |
| 🔴 High Risk | High probability — consult doctor |
| 🟣 Very High Risk | Immediate medical attention advised |

---

## 📄 PDF Reports

Each prediction generates a downloadable PDF report containing:
- Patient information & report ID
- Diagnosis result and risk score
- Clinical measurements with normal ranges
- Doctor's verification status and notes
- General health recommendations

---

## ⚠️ Disclaimer

> This application is a **decision-support tool** built for educational purposes.
> It is **not a substitute** for professional medical diagnosis.
> Always consult a qualified physician for medical advice.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋‍♂️ Author
AAYUSHI

Made with ❤️ for learning ML + Flask integration.
Feel free to fork, star ⭐, and contribute!
