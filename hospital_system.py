import streamlit as st
import cv2
import face_recognition
import os
import pandas as pd
import numpy as np
from datetime import datetime

#theme
import base64

def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_image = get_base64("bg.png")

st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="MediCore", layout="centered")
st.markdown("""
    <h1 style="
        color: white;
        font-size: 48px;
        text-align: center;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.7);
    ">
        🩺 MediCore — AI-Powered Patient Registration & Visits
    </h1>
""", unsafe_allow_html=True)

st.markdown("<i>Secure patient identity, registration, and visit management powered by AI.</i>", unsafe_allow_html=True)

# ---------------- FILES ----------------
ADMIN_USER = "adheethi"
ADMIN_PASS = "1234"

PATIENT_FILE = "patients.csv"
VISIT_FILE = "visits.csv"
FACE_DIR = "patient_faces"
os.makedirs(FACE_DIR, exist_ok=True)

if not os.path.exists(PATIENT_FILE):
    pd.DataFrame(columns=["patient_id","name","age","gender","phone","blood","face_path"]).to_csv(PATIENT_FILE,index=False)

if not os.path.exists(VISIT_FILE):
    pd.DataFrame(columns=["patient_id","name","visit_type","visit_time","floor"]).to_csv(VISIT_FILE,index=False)

# ---------------- SESSION STATE ----------------
defaults = {
    "page": None,
    "camera_on": False,
    "captured_face": None,
    "new_patient": None,
    "patient_saved": False,
    "current_pid": None,
    "current_name": None,
    "old_patient_loaded": False,
    "admin":False
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

query_params = st.query_params
if "admin" in query_params:
    st.session_state.page = "admin"

# ---------------- HELPERS ----------------
def generate_patient_id():
    df = pd.read_csv(PATIENT_FILE)
    return f"P{1000 + len(df) + 1}"

def get_floor(v):
    if v in ["Emergency","Casualty"]:
        return "Ground Floor"
    if v == "OPD Appointment":
        return "2nd Floor"
    return "1st Floor"

# ---------------- HOME ----------------
c1,c2= st.columns(2)
if c1.button("🆕 New Patient"):
    st.session_state.page = "new"
if c2.button("👤 Existing Patient"):
    st.session_state.page = "old"
# ================= NEW PATIENT =================
if st.session_state.page == "new":
    st.subheader("🆕 New Patient Registration")
    with st.expander("Fill New Patient Details", expanded=True):

     name = st.text_input("Full Name")
     age = st.number_input("Age",1,120)
     gender = st.selectbox("Gender",["Male","Female","Other"])
     phone = st.text_input("Phone")
     blood = st.selectbox("Blood Group",["O+","O-","A+","A-","B+","B-","AB+","AB-"])
     consent = st.checkbox("I consent to secure storage of my medical data")
     if st.button("Back"):
        st.session_state.page = "home"

    if st.button("Submit & Verify Face"):
        if name and phone:
            st.session_state.new_patient = {"name":name,"age":age,"gender":gender,"phone":phone,"blood":blood}
            st.session_state.current_name = name
            st.session_state.camera_on = True
            st.session_state.captured_face = None
            st.session_state.patient_saved = False
        else:
            st.warning("Enter Name and Phone")

    # -------- STREAMLIT CAMERA --------
    if st.session_state.camera_on:
        st.subheader("📷 Face Capture")
        img = st.camera_input("Take a photo")

        if img is not None:
            bytes_data = img.getvalue()
            np_arr = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            faces = face_recognition.face_locations(rgb)

            if len(faces) == 1:
                st.session_state.captured_face = rgb
                st.session_state.camera_on = False
                st.success("Face captured successfully")
            else:
                st.error("Please show exactly ONE face")

    # -------- SAVE PATIENT --------
    if st.session_state.captured_face is not None and not st.session_state.patient_saved:
        pid = generate_patient_id()
        path = f"{FACE_DIR}/{pid}.jpg"
        cv2.imwrite(path, cv2.cvtColor(st.session_state.captured_face, cv2.COLOR_RGB2BGR))

        df = pd.read_csv(PATIENT_FILE)
        d = st.session_state.new_patient
        df.loc[len(df)] = [pid,d["name"],d["age"],d["gender"],d["phone"],d["blood"],path]
        df.to_csv(PATIENT_FILE,index=False)

        st.session_state.current_pid = pid
        st.session_state.patient_saved = True

    # -------- VISIT --------
    if st.session_state.patient_saved:
        st.success("Patient Registered")
        st.write("Patient ID:", st.session_state.current_pid)

        visit_type = st.selectbox("Visit Type",["Casualty","Emergency","OPD Appointment","Follow-up"])
        if st.button("Submit Visit"):
            if visit_type != "Emergency":
                time = datetime.now().strftime("%Y-%m-%d , %H:%M")
            else:
                time = datetime.now().strftime("%Y-%m-%d , %H:%M")
            floor = get_floor(visit_type)


            visit_df = pd.read_csv(VISIT_FILE)
            visit_df.loc[len(visit_df)] = [st.session_state.current_pid, st.session_state.current_name, visit_type, time, floor]
            visit_df.to_csv(VISIT_FILE,index=False)

            st.success("Visit Booked Successfully")
            if visit_type == "Emergency":
                st.write("🚨 Emergency Visit!","| Floor:", floor)
            else:
                st.write("Floor:", floor, "| Date & Time:", time)


# ================= EXISTING PATIENT =================
if st.session_state.page == "old":
    st.subheader("👤 Existing Patient")

    option = st.segmented_control(
        "Choose Identification Method:",
        ["🔍 Face Recognition", "✍ Manual Search"]
    )

    # ================= FACE RECOGNITION OPTION =================
    if option == "🔍 Face Recognition":

        if not st.session_state.old_patient_loaded:

            st.write("Scan your face to identify patient")

            img = st.camera_input("Capture Face")

            if img is not None:

                bytes_data = img.getvalue()
                np_arr = np.frombuffer(bytes_data, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                faces = face_recognition.face_locations(rgb)

                if len(faces) == 1:

                    new_encoding = face_recognition.face_encodings(rgb)[0]
                    df = pd.read_csv(PATIENT_FILE)

                    matched = False

                    for index, row in df.iterrows():

                        stored_image_path = row["face_path"]

                        if os.path.exists(stored_image_path):

                            stored_image = face_recognition.load_image_file(stored_image_path)
                            stored_encodings = face_recognition.face_encodings(stored_image)

                            if len(stored_encodings) > 0:

                                stored_encoding = stored_encodings[0]

                                match = face_recognition.compare_faces(
                                    [stored_encoding], new_encoding, tolerance=0.5
                                )

                                if match[0]:
                                    st.session_state.current_pid = row["patient_id"]
                                    st.session_state.current_name = row["name"]
                                    st.session_state.old_patient_loaded = True
                                    st.success("Patient Recognized Successfully ✅")
                                    matched = True
                                    break

                    if not matched:
                        st.error("No matching patient found ❌")

                else:
                    st.error("Please show exactly ONE face")

    # ================= MANUAL SEARCH OPTION =================
    if option == "✍ Manual Search":

        if not st.session_state.old_patient_loaded:

            search = st.text_input("Enter Patient ID or Name")

            if st.button("Fetch Patient"):

                df = pd.read_csv(PATIENT_FILE)
                df["name"] = df["name"].astype(str)

                result = df[
                    (df["patient_id"].str.upper() == search.upper()) |
                    (df["name"].str.lower().str.contains(search.lower()))
                ]

                if not result.empty:
                    p = result.iloc[-1]
                    st.session_state.current_pid = p["patient_id"]
                    st.session_state.current_name = p["name"]
                    st.session_state.old_patient_loaded = True
                    st.success("Patient Found ✅")
                else:
                    st.error("Patient Not Found ❌")

    # ================= VISIT FORM (COMMON FOR BOTH) =================
    if st.session_state.old_patient_loaded:

        st.write("Patient ID:", st.session_state.current_pid)
        st.write("Name:", st.session_state.current_name)

        visit_type = st.selectbox(
            "Visit Type",
            ["Follow-up", "OPD Appointment", "Emergency", "Casualty"]
        )

        if st.button("Submit Visit"):

            time = datetime.now().strftime("%Y-%m-%d , %H:%M")
            floor = get_floor(visit_type)

            visit_df = pd.read_csv(VISIT_FILE)
            visit_df.loc[len(visit_df)] = [
                st.session_state.current_pid,
                st.session_state.current_name,
                visit_type,
                time,
                floor,
            ]
            visit_df.to_csv(VISIT_FILE, index=False)

            st.success("Visit Booked Successfully 🎉")

            if visit_type == "Emergency":
                st.write("🚨 Emergency!", "| Floor:", floor)
            else:
                st.write("Floor:", floor, "| Date & Time:", time)

            st.session_state.old_patient_loaded = False

    # ================= ADMIN LOGIN =================
if st.session_state.page=="admin":
    st.subheader("🔐 Admin Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u==ADMIN_USER and p==ADMIN_PASS:
            st.session_state.admin=True
            st.success("Admin authenticated")
        else:
            st.error("Invalid credentials")

# ================= ADMIN DASHBOARD =================
if st.session_state.admin:
    st.markdown("---")
    st.subheader("📊 Admin Insights")

    vdf = pd.read_csv(VISIT_FILE)
    st.metric("Total Visits", len(vdf))
    st.bar_chart(vdf["visit_type"].value_counts())
    st.bar_chart(vdf["floor"].value_counts())

    if st.button("Logout Admin"):
        st.session_state.clear()
        st.query_params.clear()
        
        st.rerun()
     

if not st.session_state.admin:
    st.markdown(
        """
        <hr>
        <div style="text-align:center; font-size:14px; color:#ddd;">
            © MediCore Hospital System &nbsp;|&nbsp;
            <a href="?admin=true" style="color:#aad;">🔐 Admin Login</a>
        </div>
        """,
        unsafe_allow_html=True
    )

