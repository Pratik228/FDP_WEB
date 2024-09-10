# 😎 Face Detection Attendance Web System 😎

Welcome to our cutting-edge Face Detection Attendance System! This project combines facial recognition technology with cloud services to provide a seamless attendance management solution.

## 🌟 Features

- 🔍 Facial recognition-based attendance marking
- 🖼️ Support for live video feeds and image uploads
- ⚡ Real-time attendance tracking and updates
- ✍️ Manual attendance adjustments
- 🔥 Firebase integration for data management
- 📊 Attendance reports and analytics
- 📁 CSV export functionality

## 🛠️ Technologies Used

- 🐍 Python
- 👀 OpenCV
- 🔥 Firebase
- 🚀 Streamlit
- 🐳 Docker (for deployment)

## 📋 Local Installation and Setup

1. Clone the repository:

   ```
   git clone https://github.com/Pratik228/FDP.git
   cd FDP
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up Firebase:

   - Create a new Firebase project in the Firebase Console
   - Enable Authentication and Realtime Database
   - Download the Firebase service account key
   - Create a `.env` file in the project root and add:
     ```
     FIREBASE_SERVICE_ACCOUNT_KEY_PATH=path/to/your/serviceAccountKey.json
     ```

5. Run the application:
   ```
   streamlit run attendance.py
   ```

## 🚀 Usage

1. Access the application through localhost
2. Use the side menu to navigate through different modules
3. Store student details and images
4. Take attendance using live video or uploaded images
5. View and export attendance reports

## 🎥 Demo Video

[Coming Soon] A comprehensive demonstration of the system's features and functionality.

## 🌐 Deployed Version

For a live demo of core features (excluding live camera functionality), visit: [Deployed App URL]

Key differences from the local version:

- Uses uploaded images instead of live camera feed
- Showcases core functionality without camera dependencies

## 🔒 Handling Sensitive Information

- Use environment variables for sensitive data in local development
- For the deployed version, use the platform's secure environment variable storage (e.g., Heroku Config Vars)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Contact

For any queries or feedback, please contact:

- 🙋‍♂️ Name: Pratik Kumar Mishra
- 📧 Email: pratikmishra79@gmail.com
- 🐙 GitHub: [your-github-username]

## 📸 Screenshots

[Add screenshots of key features here]

Get ready to revolutionize attendance management with our Face Detection Attendance System! 🎉🚀

```

```
