# CSEDU-backend

# CSEDU Backend API

This is the backend system for the CSEDU university department website built with **FastAPI** and **MySQL**. It supports user roles like **Student**, **Teacher**, and **Admin** to manage data like students, results, room bookings, equipment, events, notices, and more.

---

## 🔧 Features

- Role-based access (Student, Teacher, Admin)
- CRUD operations for:
  - Students, Courses, Teachers
  - Results, Assignments, Meetings
  - Room & Equipment Booking
  - Events, Notices, Applications
- Filtering and sorting support
- Token-based authentication

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/EhsanUddoula/csedu-backend.git
cd CSEDU-backend
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up .env File
```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=csedu
```

### 5. Run The App
```bash
uvicorn main:app --reload
```


