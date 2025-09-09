# FastAPI Todo Application

A full-stack todo management system with FastAPI backend and modern frontend.

## 🚀 Features

- **Authentication**: JWT-based login/registration
- **Todo Management**: CRUD operations with priority levels
- **User Profiles**: Password and phone number updates  
- **Admin Panel**: System-wide todo management
- **Responsive UI**: Mobile-friendly design

## 🛠️ Tech Stack

**Backend**: FastAPI, SQLAlchemy, PostgreSQL, Alembic  
**Frontend**: HTML5, CSS3, Vanilla JavaScript  
**Testing**: Pytest with 15 test cases

## ⚙️ Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd "Todo App"

# Install dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run migrations and start server
alembic upgrade head
uvicorn main:app --reload
```

Visit `http://localhost:8000` to use the application.

## 🧪 Testing

```bash
pytest  # Run all 15 tests
```

## 📚 API Documentation

- Interactive docs: `http://localhost:8000/docs`
- Endpoints: `/auth`, `/users`, `/todos`, `/admin`

## 🔧 Configuration

Set environment variables:
```env
DATABASE_URL=postgresql://user:pass@localhost/todoapp
SECRET_KEY=your-secret-key
```

## 📄 License