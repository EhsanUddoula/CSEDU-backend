from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from sqlalchemy import Date, Time, Float, Enum as SQLEnum, JSON

Base = declarative_base()

# ----------------- ENUM for User Role -----------------
class RoleEnum(str, enum.Enum):
    student = "Student"
    teacher = "Teacher"
    admin = "Admin"

# ----------------- USER -----------------
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)

    # Relationships
    student = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    teacher = relationship("Teacher", back_populates="user", uselist=False, cascade="all, delete-orphan")
    admin = relationship("Admin", back_populates="user", uselist=False, cascade="all, delete-orphan")

# ----------------- STUDENT -----------------
class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), unique=True)
    
    registration_number = Column(String(100), unique=True, nullable=False)
    name = Column(String(100))
    father_name = Column(String(100))
    mother_name = Column(String(100))
    session = Column(String(50))
    phone = Column(String(20))
    hall = Column(String(100))
    email = Column(String(100))
    address = Column(String(255))
    profile_pic = Column(String(255))
    semester = Column(String(20))
    degree = Column(String(100))

    user = relationship("User", back_populates="student")
    results = relationship("Result", back_populates="student", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="student", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="student", cascade="all, delete-orphan")
    equipment_bookings = relationship("EquipmentBooking", back_populates="student", cascade="all, delete-orphan")

# ----------------- RESULT -----------------
class Result(Base):
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True)
    semester = Column(String(50))
    courses = Column(Text)  # you may normalize later
    grade = Column(String(10))
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE", onupdate="CASCADE"))

    student = relationship("Student", back_populates="results")

# ----------------- COURSE -----------------
class CourseTypeEnum(str, enum.Enum):
    general = "General"
    core = "Core"
    elective = "Elective"

class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    title = Column(String(255))
    credit = Column(Integer)
    type = Column(Enum(CourseTypeEnum))
    year = Column(String(10))
    semester = Column(String(20))
    active = Column(Boolean, default=True)
    content = Column(Text)
    degree = Column(String(100))
    teacher = Column(String(100))  # FK to Teacher table later if needed

# ----------------- ASSIGNMENT -----------------
class Assignment(Base):
    __tablename__ = 'assignments'

    id = Column(Integer, primary_key=True)
    course_code = Column(String(50))  # Optional FK to Course
    teacher = Column(String(100))     # Optional FK to Teacher table
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE", onupdate="CASCADE"))

    title = Column(String(255))
    instructions = Column(Text)
    points = Column(Integer)
    due_date = Column(DateTime)
    published_date = Column(DateTime)
    attachment = Column(String(255))

    student = relationship("Student", back_populates="assignments")

# ----------------- PAYMENT -----------------
class Payment(Base):
    __tablename__ = 'payments'

    payment_no = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE", onupdate="CASCADE"))
    fee = Column(String(100))
    cause = Column(String(255))

    student = relationship("Student", back_populates="payments")

# ----------------- EQUIPMENT LIST -----------------
class EquipmentList(Base):
    __tablename__ = 'equipment_list'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    availability = Column(Boolean, default=True)

# ----------------- EQUIPMENT BOOKING -----------------
class EquipmentBooking(Base):
    __tablename__ = 'equipment_bookings'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE", onupdate="CASCADE"))
    booking_time = Column(DateTime)
    return_date = Column(DateTime)

    student = relationship("Student", back_populates="equipment_bookings")

# ----------------- TEACHER -----------------
class Teacher(Base):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), unique=True)

    name = Column(String(100))
    bio = Column(Text)
    profile_pic = Column(String(255))
    title = Column(String(100))  # Designation
    email = Column(String(100))
    phone = Column(String(20))
    research_profile = Column(String(255))
    department = Column(String(100))

    socials_linkedin = Column(String(255))
    socials_github = Column(String(255))
    socials_twitter = Column(String(255))

    user = relationship("User", backref="teacher", cascade="all, delete-orphan", uselist=False)

    # Relationships
    education = relationship("Education", back_populates="teacher", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="teacher", cascade="all, delete-orphan")
    awards = relationship("Award", back_populates="teacher", cascade="all, delete-orphan")
    publications = relationship("Publication", back_populates="teacher", cascade="all, delete-orphan")
    routines = relationship("Routine", back_populates="teacher", cascade="all, delete-orphan")

# ----------------- EDUCATION -----------------
class Education(Base):
    __tablename__ = 'education'

    id = Column(Integer, primary_key=True)
    degree_name = Column(String(100))
    major = Column(String(100))
    institution = Column(String(100))
    year = Column(String(10))
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE", onupdate="CASCADE"))

    teacher = relationship("Teacher", back_populates="education")

# ----------------- EXPERIENCE -----------------
class Experience(Base):
    __tablename__ = 'experience'

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    organization = Column(String(100))
    duration = Column(String(50))
    year = Column(String(10))
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE", onupdate="CASCADE"))

    teacher = relationship("Teacher", back_populates="experience")

# ----------------- AWARD -----------------
class Award(Base):
    __tablename__ = 'awards'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    type = Column(String(100))
    description = Column(Text)
    year = Column(String(10))
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE", onupdate="CASCADE"))

    teacher = relationship("Teacher", back_populates="awards")

# ----------------- PUBLICATION -----------------
class Publication(Base):
    __tablename__ = 'publications'

    id = Column(Integer, primary_key=True)
    type = Column(String(100))
    title = Column(String(255))
    url = Column(String(255))
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE", onupdate="CASCADE"))

    teacher = relationship("Teacher", back_populates="publications")

# ----------------- ROUTINE -----------------
class Routine(Base):
    __tablename__ = 'routines'

    id = Column(Integer, primary_key=True)
    batch = Column(String(50))
    semester = Column(String(50))
    day = Column(String(20))  # e.g., Monday
    time_interval = Column(String(50))  # e.g., 9:00-10:30
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    room_no = Column(String(50))
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE", onupdate="CASCADE"))

    teacher = relationship("Teacher", back_populates="routines")

# ----------------- CONTACT -----------------
class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(100))
    subject = Column(String(255))
    message = Column(Text)

# ----------------- ADMIN -----------------
class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), unique=True)
    name = Column(String(100))
    email = Column(String(100))
    password = Column(String(255))
    phone = Column(String(20))

    user = relationship("User", backref="admin", cascade="all, delete-orphan", uselist=False)

# ----------------- NOTICE -----------------
class NoticeCategory(str, enum.Enum):
    academic = "academic"
    general = "general"
    administrative = "administrative"

class Notice(Base):
    __tablename__ = 'notices'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text)
    detailed_description = Column(Text)
    pdf_file = Column(String(255))  # File path or URL
    category = Column(SQLEnum(NoticeCategory))
    date = Column(String(20))
    expiry_date = Column(String(20))
    author = Column(String(100))
    location = Column(String(255))
    time = Column(String(50))
    is_archived = Column(Boolean, default=False)

# ----------------- EVENT -----------------
class EventCategory(str, enum.Enum):
    workshop = "workshop"
    hackathon = "hackathon"
    seminar = "seminar"
    career = "career"
    bootcamp = "bootcamp"
    competition = "competition"

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    date = Column(String(20))
    start_time = Column(String(20))
    end_time = Column(String(20))
    location = Column(String(255))
    description = Column(Text)
    detailed_description = Column(Text)
    image = Column(String(255))  # File path or URL
    tags = Column(JSON)
    registration_open = Column(Boolean, default=True)
    registration_closed = Column(Boolean, default=False)
    max_attendees = Column(Integer)
    current_attendees = Column(Integer)
    category = Column(SQLEnum(EventCategory))
    organizer = Column(String(100))
    registration_deadline = Column(String(20))
    contact_email = Column(String(100))

# ----------------- FORM DATA -----------------
class FormData(Base):
    __tablename__ = 'form_data'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    roll = Column(String(50))
    registration_id = Column(String(50))
    batch_no = Column(String(50))
    phone = Column(String(20))
    registration_fee = Column(String(100))

# ----------------- ROOM AVAILABILITY -----------------
class RoomAvailabilityStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    available = "available"
    unavailable = "unavailable"

class RoomAvailability(Base):
    __tablename__ = 'room_availability'

    room_id = Column(Integer, primary_key=True)
    location = Column(String(255))
    capacity = Column(Integer)
    available = Column(SQLEnum(RoomAvailabilityStatus))
    date = Column(String(20))
    start_time = Column(String(20))
    end_time = Column(String(20))

# ----------------- ROOM BOOKING -----------------
class RoomBookingStatus(str, enum.Enum):
    approved = "approved"
    rejected = "rejected"
    pending = "pending"

class RoomBooking(Base):
    __tablename__ = 'room_bookings'

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("room_availability.room_id", ondelete="CASCADE", onupdate="CASCADE"))
    booking_date = Column(String(20))
    start_time = Column(String(20))
    end_time = Column(String(20))
    booking_purpose = Column(String(255))
    status = Column(SQLEnum(RoomBookingStatus))

    room = relationship("RoomAvailability", backref="bookings")

# ----------------- EXAM SCHEDULE -----------------
class ExamSchedule(Base):
    __tablename__ = 'exam_schedules'

    id = Column(Integer, primary_key=True)
    date = Column(String(20))
    start_time = Column(String(20))
    end_time = Column(String(20))
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    room_no = Column(String(50))
    invigilator = Column(String(100))
    semester = Column(String(20))

    course = relationship("Course", backref="exam_schedules")

# ----------------- MEETING -----------------
class MeetingStatus(str, enum.Enum):
    approved = "approved"
    rejected = "rejected"
    pending = "pending"

class Meeting(Base):
    __tablename__ = 'meetings'

    id = Column(Integer, primary_key=True)
    date = Column(String(20))
    time = Column(String(20))
    topic = Column(String(255))
    host_name = Column(String(100))
    location = Column(String(255))
    status = Column(SQLEnum(MeetingStatus))

# ----------------- APPLICATION -----------------
class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100))
    student_id = Column(String(50))
    email = Column(String(100))
    phone = Column(String(20))
    passing_program = Column(String(100))
    cgpa = Column(String(10))
    transcript = Column(String(255))  # path or URL to file
    apply_for = Column(String(100))
    recommender1_email = Column(String(100))
    recommender2_email = Column(String(100))
