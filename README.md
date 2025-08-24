<div align="center">
  
  <h1><strong>EVENTIFY</strong></h1>
  <p>University Event Management Portal - Connecting Students and Club Admins</p>

## 📚 Table of Contents

 [📋 Project Description](#-project-description)
 [🎯 Key Features](#-key-features)
 [🛠️ Technologies Used](#️-technologies-used)
 [🗎️ System Architecture](#️-system-architecture)
 [🗃️ Database Schema](#️-database-schema)
 [🚀 Getting Started](#-getting-started)
 [🎥 Live Demo](#-live-demo)
 [👨‍💻 Team](#-team)
 [💬 Feedback](#-feedback)

## 📋 Project Description

**Eventify** is a comprehensive full-stack web application designed specifically for university clubs to manage events seamlessly. The platform bridges the gap between club administrators and students by providing an intuitive interface for event creation, registration, and management.

With advanced features including ML-powered event recommendations, automated certificate generation, intelligent FAQ chatbot, and email notifications, Eventify transforms the traditional event management experience into a modern, efficient, and engaging platform for the entire university community.

## 🎯 Key Features

### Core Features (MVP)
 **Role-Based Authentication** - Secure signup/login system with Student and Club Admin roles
 **Event Management** - Complete CRUD operations for events by club admins
 **Event Registration** - Students can browse, register, and unregister from events
 **Personal Dashboards** - Customized interfaces for both students and admins
 **Event Discovery** - Browse upcoming events with detailed information

### Advanced Features
 **🤖 AI-Powered Chatbot** - Intelligent FAQ system for common user queries
 **📜 Certificate Generator** - Automatic PDF certificate generation for event participants
 **🎯 ML Recommendation System** - Personalized event suggestions based on user behavior
 **📧 Email Notifications** - Automated registration confirmations and event reminders
 **🔍 Advanced Search & Filtering** - Filter events by category, date, location, and keywords
 **📱 Responsive Design** - Mobile-first approach with full responsiveness
 **🌙 Dark Mode** - Theme switching capability for enhanced user experience
 **📊 Analytics Dashboard** - Comprehensive event statistics and insights for admins
 **⏰ Smart Scheduling** - Prevent location conflicts and manage event deadlines

## 🛠️ Technologies Used

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
  <img src="https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
</div>

### Backend Dependencies
 **Flask 2.3.3** - Web framework
 **Flask-SQLAlchemy 3.0.5** - ORM for database operations
 **Flask-Login 0.6.3** - User session management
 **Flask-WTF 1.2.1** - Form handling and validation
 **Flask-Mail 0.10.0** - Email functionality
 **ReportLab 4.0.4** - PDF certificate generation
 **Pillow** - Image processing
 **Gunicorn** - Production WSGI server

## 🗎️ System Architecture

Our platform follows a modular MVC architecture to ensure scalability and maintainability:

 **Presentation Layer**
    HTML5, CSS3, Bootstrap for responsive UI
    JavaScript for dynamic interactions
    Jinja2 templating engine

 **Application Layer**
    Flask framework with Blueprint structure
    WTForms for form validation
    Flask-Login for authentication

 **Business Logic Layer**
    Event management services
    User authentication and authorization
    ML recommendation engine
    Certificate generation service
    Email notification system

 **Data Layer**
    SQLAlchemy ORM
    SQLite database (development)
    Database migrations and seeding

 **External Integrations**
    Email service integration
    PDF generation library
    Machine learning libraries

## 🗃️ Database Schema

The database design supports the complete event management workflow:

### Core Tables
 **Users** - Student and admin user information
 **Events** - Event details, dates, locations, and metadata
 **Registrations** - Event registration tracking
 **Categories** - Event categorization system
 **Certificates** - Generated certificate records

### Advanced Features Tables
 **UserInteractions** - ML recommendation data
 **EmailLogs** - Email notification tracking
 **FAQResponses** - Chatbot interaction logs
 **EventAnalytics** - Event performance metrics

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

* Python >= 3.8
* pip (Python package manager)
* Virtual environment tool (venv or virtualenv)
* Git

### Installation

 **Clone the repository:**
```bash
git clone https://github.com/DittoOne/Eventify.git
cd Eventify
```

 **Create and activate virtual environment:**
```bash
# Create virtual environment
python -m venv eventify_env

# Activate virtual environment
# On Windows:
eventify_env\Scripts\activate
# On macOS/Linux:
source eventify_env/bin/activate
```

 **Install dependencies:**
```bash
pip install -r requirements.txt
```
 **Run the application:**
```bash
# Development mode
python app.py

# Production mode
gunicorn "app:create_app()"
```

 **Access the application:**
   - Open your browser and navigate to `http://localhost:5000`

## 🎥 Live Demo

* 🌐 [Live Website](https://eventify-4.onrender.com/)
* 🎦 [Demo Video]


## 🌟 Feature Highlights

### 🤖 AI-Powered Recommendation System
 Content-based filtering using event categories and user preferences
 Collaborative filtering based on registration patterns
 Real-time suggestions on student dashboard

### 📜 Automated Certificate Generation
 Custom PDF certificates with event branding
 Automatic generation post-event completion
 Digital signature and verification system

### 💬 Intelligent FAQ Chatbot
 Rule-based response system
 Common query handling
 Integration with user support system

### 📊 Advanced Analytics
 Event performance metrics
 Registration trends analysis
 User engagement insights

## 👨‍💻 Team

| Name                | Git Link          | LinkedIn                                    |
| ------------------- | ----------------- | ------------------------------------------- |
| [Md Shahriar Rahman]| [GitHub](https://github.com/DittoOne)| [LinkedIn](https://www.linkedin.com/in/md-shahriar-rahman-bhuiyan-3893012a8)  |
| [Nur Mohammed Kazi] | [GitHub](https://github.com/NurMohammadkazi)| [LinkedIn](https://www.linkedin.com/in/nur-mohammad-kazi-73632a268/) |
| [Ali Faruk Shihab]  | [GitHub](https://github.com/farukShihab)    | [LinkedIn](https://www.linkedin.com/in/faruk-shihab-608793343) |

## 🤝 Contributing

We welcome contributions! Please follow these steps:

 Fork the repository
 Create a feature branch (`git checkout -b feature/AmazingFeature`)
 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
 Push to the branch (`git push origin feature/AmazingFeature`)
 Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- University IT Department for infrastructure support
- Open source community for amazing libraries
- Beta testers for valuable feedback

## 💬 Feedback

If you have any feedback, suggestions, or want to collaborate — feel free to [open an issue](https://github.com/DittoOne/Eventify.git) or reach out via LinkedIn.

---

<div align="center">
  <p>Made with ❤️ for the University Community</p>
  <p>© 2024 Eventify Team. All rights reserved.</p>
</div>