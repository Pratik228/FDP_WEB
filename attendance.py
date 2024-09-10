import streamlit as st
import cv2
import os
import firebase_admin
import base64
import pickle
import datetime
import subprocess
import pandas as pd
import face_recognition
import numpy as np
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from firebase_config import initialize_firebase
from utils import load_known_encodings_and_ids
from webcam_capture import webcam_capture
import pytz
from PIL import Image
from constants import DEPARTMENTS, SECTIONS, SEMESTERS, JOINING_YEARS
import re

st.set_page_config(
    page_title="Student Attendance System",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.big-font {
    font-size:30px !important;
    font-weight: bold;
}
.stButton>button {
    width: 100%;
}
.stSelectbox {
    margin-bottom: 10px;
}
.stDataFrame {
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Rest of your imports and global variables
bucket, ref, encodings_ref = initialize_firebase()
local_tz = pytz.timezone('Asia/Kolkata')

# Load your logo image
logo = Image.open("cmr.png")

def main():
    # Remove the set_page_config() call from here
    st.sidebar.image(logo, width=150)
    st.sidebar.markdown("<p class='big-font'>Menu</p>", unsafe_allow_html=True)
    
    menu = ["Home", "Store Student Details", "Store Student Image", "Take Attendance", "Check Attendance", "Manage Students"]
    choice = st.sidebar.radio("", menu)

    if choice == "Home":
        show_home()
    elif choice == "Store Student Details":
        store_student_details()
    elif choice == "Store Student Image":
        store_image()
    elif choice == "Take Attendance":
        take_attendance()
    elif choice == "Check Attendance":
        check_attendance()
    elif choice == "Manage Students":
        manage_students()

def show_home():
    st.markdown("<h1 style='text-align: center;'>Welcome to the Student Attendance System</h1>", unsafe_allow_html=True)
    
    st.write("")
    col1, col2, col3 = st.columns([1,2,1])
    
    st.write("")
    st.markdown("""
    This attendance system uses facial recognition to mark attendance for students.
    It allows you to:
    - Register new students
    - Take attendance using live video or uploaded images
    - Store images for each student
    - View and manage attendance records
    """)

def store_student_details():
    st.markdown("<h2 style='text-align: center; color: #4a4a4a;'>Store Student Details</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    .student-form {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .form-header {
        color: #4a4a4a;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.form("student_details_form"):
        st.markdown('<p class="form-header">Enter Student Information</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.text_input("Student ID (USN)", max_chars=10).upper()
            name = st.text_input("Name")
            department = st.selectbox("Department", options=DEPARTMENTS)
        
        with col2:
            joined = st.selectbox("Year of Joining", options=JOINING_YEARS)
            semester = st.selectbox("Semester", options=SEMESTERS)
            section = st.selectbox("Section", options=SECTIONS)

        submit_button = st.form_submit_button("Submit")

    if submit_button:
        with st.spinner("Processing..."):
            # Validate USN
            if not re.match(r'^[A-Z0-9]{10}$', student_id):
                st.error("Invalid USN. It should be 10 characters long and contain only uppercase letters and numbers.")
                return

            # Check if USN already exists
            if db.reference(f'Students/{student_id}').get() is not None:
                st.error(f"A student with USN {student_id} already exists.")
                return

            # Validate Name
            if not name or not re.match(r'^[A-Za-z\s]+$', name):
                st.error("Please enter a valid name (only letters and spaces allowed).")
                return

            # All validations passed, store the data in Firebase
            now = datetime.datetime.now(local_tz)
            data = {
                'name': name,
                'department': department,
                'joined': joined,
                'total_attendance': 0,
                'semester': semester,
                'section': section,
                'last_attendance': str(now.strftime("%Y-%m-%d %H:%M:%S"))
            }
            ref.child(student_id).set(data)

            st.success(f'Success! Data submitted for {name} with USN {student_id}')
            
            # Display submitted data
            st.markdown("### Submitted Data")
            st.json(data)

    st.markdown('<div class="student-form">', unsafe_allow_html=True)
    st.markdown("#### Instructions:")
    st.markdown("1. Fill in all the fields with accurate information.")
    st.markdown("2. USN should be 10 characters long, containing only uppercase letters and numbers.")
    st.markdown("3. Name should only contain letters and spaces.")
    st.markdown("4. Make sure to select the correct Department, Year of Joining, Semester, and Section.")
    st.markdown("5. Click 'Submit' when you're done.")
    st.markdown('</div>', unsafe_allow_html=True)

def manage_students():
    st.markdown("<h2 style='text-align: center; color: #4a4a4a;'>Manage Students</h2>", unsafe_allow_html=True)

    # Use session state to keep track of changes
    if 'refresh_trigger' not in st.session_state:
        st.session_state.refresh_trigger = False

    # Fetch all students
    students_ref = db.reference('Students')
    students_data = students_ref.get()

    if not students_data:
        st.warning("No students found in the database.")
        return

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(students_data, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'USN'}, inplace=True)

    # Display students in an expandable section
    with st.expander("View All Students", expanded=True):
        st.dataframe(df.style.set_properties(**{'background-color': '#f0f2f6', 'color': '#1e1e1e'}))

    # Edit and Delete options
    st.markdown("<h3 style='color: #4a4a4a;'>Edit or Delete Student</h3>", unsafe_allow_html=True)
    selected_usn = st.selectbox("Select a student", df['USN'].tolist())

    if selected_usn:
        student = students_data[selected_usn]
        
        with st.form(key=f"edit_student_form_{selected_usn}"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name", value=student.get('name', ''))
                department = st.selectbox("Department", options=DEPARTMENTS, index=DEPARTMENTS.index(student.get('department', DEPARTMENTS[0])))
                joined = st.selectbox("Year of Joining", options=JOINING_YEARS, index=JOINING_YEARS.index(int(student.get('joined', JOINING_YEARS[0]))))
            with col2:
                semester = st.selectbox("Semester", options=SEMESTERS, index=SEMESTERS.index(int(student.get('semester', SEMESTERS[0]))))
                section = st.selectbox("Section", options=SECTIONS, index=SECTIONS.index(student.get('section', SECTIONS[0])))

            col1, col2 = st.columns(2)
            with col1:
                update_button = st.form_submit_button("Update Student")
            with col2:
                delete_button = st.form_submit_button("Delete Student")

        if update_button:
            with st.spinner("Updating student information..."):
                updated_data = {
                    'name': name,
                    'department': department,
                    'joined': joined,
                    'semester': semester,
                    'section': section,
                    'total_attendance': student.get('total_attendance', 0),
                    'last_attendance': student.get('last_attendance', '')
                }
                students_ref.child(selected_usn).update(updated_data)
                st.success(f"Student {selected_usn} updated successfully!")
                st.session_state.refresh_trigger = True

        if delete_button:
            with st.spinner("Deleting student..."):
                students_ref.child(selected_usn).delete()
                st.success(f"Student {selected_usn} deleted successfully!")
                st.session_state.refresh_trigger = True

    


def store_image():
    st.markdown("<h2 style='text-align: center; color: #4a4a4a;'>Store Student Image</h2>", unsafe_allow_html=True)

    # Custom CSS
    st.markdown("""
    <style>
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .upload-section, .capture-section {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    usn = st.text_input("Enter the USN of the student:")
    
    if not usn:
        st.warning("Please enter a USN before proceeding.")
        return

    option = st.radio("Select Option", ("Upload Image", "Take Photo"))

    def get_encoding(image_path):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(img)
        if len(face_locations) > 0:
            encode = face_recognition.face_encodings(img, face_locations)[0]
            return encode
        return None

    def process_and_store_image(image):
        with st.spinner("Processing image..."):
            file_name = f"Images/{usn}.jpg"
            cv2.imwrite(file_name, image)
            st.success(f"Saved photo as {file_name}")
            
            # Upload the image to Firebase Storage
            blob = bucket.blob("Images/" + f"{usn}.jpg")
            blob.upload_from_filename(file_name)
            st.success("Saved photo to Firebase Storage")

            # Calculate and store the encoding of the new student's image
            new_encoding = get_encoding(file_name)
            if new_encoding is not None:
                encodeKnown.append(new_encoding)
                studId.append(usn)

                # Update the pickle file
                with open("EncodeFile.p", "wb") as f:
                    pickle.dump([encodeKnown, studId], f)
                st.success("Encodings updated successfully.")
            else:
                st.error("Could not detect a face in the image.")

    if option == "Upload Image":
        st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            # Show a preview of the uploaded image
            st.image(img, caption="Preview of the uploaded image", width=300)

            # Add an "Upload" button
            if st.button("Upload and Process"):
                process_and_store_image(img)
        st.markdown("</div>", unsafe_allow_html=True)

    elif option == "Take Photo":
        st.markdown("<div class='capture-section'>", unsafe_allow_html=True)
        # Create the "Images" folder if it does not exist
        if not os.path.exists("Images"):
            os.makedirs("Images")
        
        st.write("Please look at the camera and come a little closer. Click 'Capture Photo' when ready.")
        
        if st.button("Capture Photo"):
            # Initialize the webcam
            cap = cv2.VideoCapture(0)
            
            # Capture a single frame
            ret, frame = cap.read()
            
            if ret:
                st.image(frame, caption="Captured photo", width=300)
                
                if st.button("Upload and Process Captured Photo"):
                    process_and_store_image(frame)
            else:
                st.error("Failed to capture photo. Please try again.")
            
            # Release the webcam
            cap.release()
        st.markdown("</div>", unsafe_allow_html=True)


def store_encodings():
    st.subheader("Store Encodings")
    if st.button("Click to store encodings"):
        subprocess.run(["python", "encoding.py"])
        st.success('Success! Encodings stored.')  

#  Old one changing it completely
# def take_attendance():
#     st.subheader("Take Attendance")
#     if st.button("Take Attendance"):
#         subprocess.run(["python", "main.py"])
#     # Add code to take attendance using saved images
#         st.success('Success! Attendance marked')

# New one with enhanced options
import dlib
def _css_to_rect(css):
    return dlib.rectangle(css.left(), css.top(), css.right(), css.bottom())

def take_attendance():
    st.subheader("Take Attendance")
    semester = st.selectbox("Select Semester", options=[1, 2, 3, 4, 5, 6, 7, 8])
    section = st.selectbox("Select Section", options=["A", "B", "C", "D"])
    department = st.selectbox("Select department", options = ["CSE", "ISE", "ECE", "EEE", "AI&ML", "DS", "Mech", "Civil"])
    option = st.radio("Select Option", ("Live Video", "Upload Image"))
    if option == "Live Video":
        if st.button("Take Attendance"):
            subprocess.run(["python", "main.py"])
            st.success('Success! Attendance marked')
    elif option == "Upload Image":
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            # Read in the uploaded image
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            # Resize image for faster processing
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            


            # Detect faces in the image
            face_locations = face_recognition.face_locations(img) # model="cnn"

            face_encodings = face_recognition.face_encodings(img, face_locations)

            # Load known encodings and student IDs
            encodeKnown, studId = load_known_encodings_and_ids()

            # Loop through each face encoding detected in the uploaded image
            marked_students = 0
            for face_encoding in face_encodings:
                # Find the closest matching known encoding
                distances = face_recognition.face_distance(encodeKnown, face_encoding)
                min_distance_index = np.argmin(distances)
                min_distance = distances[min_distance_index]

                # Set a threshold for the minimum distance to consider a match
                threshold = 0.7

                # If the minimum distance is below the threshold, mark attendance
                if min_distance < threshold:
                    id = studId[min_distance_index]
                    studentInfo = db.reference(f'Students/{id}').get()
                    if studentInfo is not None:
                        datetimeObject = datetime.datetime.strptime(studentInfo['last_attendance'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=local_tz)
                        secondsElapsed = (datetime.datetime.now(local_tz) - datetimeObject).total_seconds()

                        if secondsElapsed > 30:
                            ref = db.reference(f'Students/{id}')
                            studentInfo['total_attendance'] += 1
                            ref.child('total_attendance').set(studentInfo['total_attendance'])
                            ref.child('last_attendance').set(datetime.datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S"))
                            marked_students += 1
                        else:
                            st.warning(f"{studentInfo['name']}'s attendance was already marked within the last 30 seconds.")
                    else:
                        st.warning(f"No student found with ID {id}.")

            if marked_students == 0:
                st.warning("No matching faces found in the uploaded image.")
            else:
                st.success(f"Attendance marked for {marked_students} students.")
    st.subheader("Manual Attendance")
    st.write("Mark attendance for students who were not detected:")

    if "load_unmarked_students" not in st.session_state:
        st.session_state.load_unmarked_students = False

    if st.button("Load Unmarked Students"):
        st.session_state.load_unmarked_students = True

    if st.session_state.load_unmarked_students:
        # Get the attendance data from the "Students" node in the Firebase database
        attendance_ref = db.reference('Students')
        attendance_data = attendance_ref.get()
        attendance_df = pd.DataFrame.from_dict(attendance_data, orient='index')
        attendance_df = attendance_df[(attendance_df['semester'] == str(semester)) & (attendance_df['section'] == section) & (attendance_df['department'] == department)]

        # Get the last attendance date and time from the "last_attendance" column
        last_attendance = attendance_df["last_attendance"]

        # Check if the last attendance date matches today's date
        today = datetime.datetime.now(local_tz).strftime("%Y-%m-%d")
        absent_students = []
        for i, date_time in last_attendance.items():
            date = date_time.split(" ")[0]
            if date != today:
                absent_students.append(i)

        # Show the list of students who were not marked present today and use checkboxes
        students_to_mark = {}
        if len(absent_students) > 0:
            st.write("Students not marked present today:")
            for usn in absent_students:
                students_to_mark[usn] = st.checkbox(f"{usn}: {attendance_data[usn]['name']}")

            # Provide an option to mark attendance manually
            if st.button("Mark Attendance"):
                for usn, mark_attendance in students_to_mark.items():
                    if mark_attendance:
                        studentInfo = db.reference(f'Students/{usn}').get()
                        if studentInfo is not None:
                            ref = db.reference(f'Students/{usn}')
                            studentInfo['total_attendance'] += 1
                            ref.child('total_attendance').set(studentInfo['total_attendance'])
                            ref.child('last_attendance').set(datetime.datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S"))
                            st.success(f"Attendance marked for {studentInfo['name']}")
                        else:
                            st.warning(f"No student found with USN {usn}.")
        else:
            st.success("All students are marked present today.")


 
def check_attendance():
    st.subheader("Check Attendance")
    # Get the attendance data from the "Students" node in the Firebase database
    semester = st.selectbox("Select Semester", options=[1, 2, 3, 4, 5, 6, 7, 8])
    section = st.selectbox("Select Section", options=["A", "B", "C", "D"])
    department = st.selectbox("Select department", options = ["CSE", "ISE", "ECE", "EEE", "AI&ML", "DS", "Mech", "Civil"])

    attendance_ref = db.reference('Students')
    attendance_data = attendance_ref.get()

    # Create a pandas dataframe from the attendance data
    # attendance_df = pd.DataFrame.from_dict(attendance_data, orient='index')
    attendance_df = pd.DataFrame.from_dict(attendance_data, orient='index')
    attendance_df = attendance_df[(attendance_df['semester'] == str(semester)) & (attendance_df['section'] == section) & (attendance_df['department']==department)]


    # Get the last attendance date and time from the "last_attendance" column
    last_attendance = attendance_df["last_attendance"]
    present_today = 0

    # Check if the last attendance date matches today's date
    today = datetime.datetime.now(local_tz).strftime("%Y-%m-%d")
    for i, date_time in last_attendance.items():
        date = date_time.split(" ")[0]
        if date == today:
            present_today += 1

    # Display the attendance data in a table
    st.dataframe(attendance_df)

    # Display a message indicating the number of students present today
    if present_today == 0:
        st.warning("No students are present today.")
    else:
        # st.success(f"{present_today} students are present today!")
        st.success(f"{present_today} students are present in section {section} today!")

    # Create a button to download the CSV file
    csv = attendance_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="attendance.csv">Download CSV file</a>'
    # st.markdown(href, unsafe_allow_html=True)
    st.download_button(label="Download CSV file", data=csv, file_name=f"attendance_{today}.csv", mime="text/csv")


if __name__ == '__main__':
    main()
