# 🩺 MediCore — AI-Powered Hospital Patient Management System

A smart hospital reception system built with **Python**, **Streamlit**, and **Face Recognition AI** that automates patient registration, identity verification, and visit management.

---

## 📌 Overview

MediCore replaces traditional paper-based hospital reception with a digital, AI-powered system. It allows hospital staff to register new patients with facial biometrics, identify returning patients instantly via face scan, and manage visit records — all through a clean web interface.

---

## ✨ Features

- 🆕 **New Patient Registration** — Collects patient details (name, age, gender, blood group, phone) with data consent
- 📷 **Face Capture & Encoding** — Uses `face_recognition` to capture and store unique facial embeddings per patient
- 👤 **Existing Patient Identification** — Recognizes returning patients via live face scan or manual ID/name search
- 🏥 **Visit Management** — Records visit type, timestamp, and directs patients to the correct floor
- 🚨 **Emergency Handling** — Flags emergency visits with special alerts and floor routing
- 📊 **Admin Dashboard** — Password-protected dashboard with visit analytics and charts
- 🎨 **Custom Themed UI** — Background image theming with styled HTML components via Streamlit

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / UI | Streamlit |
| Face Detection | `face_recognition`, `OpenCV (cv2)` |
| Data Storage | CSV files (`pandas`) |
| Language | Python 3 |
| Image Processing | NumPy, OpenCV |

---

## 📁 Project Structure

```
hospital_project/
│
├── hospital_system.py       # Main application file
├── patients.csv             # Patient records database
├── visits.csv               # Visit history log
├── patient_faces/           # Stored patient face images
│   ├── P1001.jpg
│   └── ...
├── bg.png                   # Background theme image
└── requirements.txt         # Python dependencies
```

---

## 🏥 Visit Types & Floor Routing

| Visit Type | Floor |
|---|---|
| Emergency | Ground Floor |
| Casualty | Ground Floor |
| OPD Appointment | 2nd Floor |
| Follow-up | 1st Floor |

---

## 📸 How Face Recognition Works

1. New patient takes a photo via webcam during registration
2. `face_recognition` extracts a 128-dimension facial encoding
3. The encoding is saved as a `.jpg` in the `patient_faces/` directory
4. On return visit, the live face is compared against all stored encodings
5. A match is declared if the distance is within a `tolerance of 0.5`

---

## ⚠️ Important Notes

- Patient face images and CSV data are **not included** in this repository for privacy reasons
- This system is intended as a **prototype / educational project**
- For production use, replace CSV storage with a proper database (e.g., PostgreSQL) and secure the admin credentials using environment variables

---

## 🙋‍♀️ Author

**Adheethi**  
BSc Mathematics | AI/ML Enthusiast  
Kerala, India

---

## 📄 License

This project is for educational and portfolio purposes.
