# Routes module for ExamSmith
# Contains all API route handlers organized by role

from routes.auth_routes import router as auth_router
from routes.admin_routes import router as admin_router
from routes.instructor_routes import router as instructor_router
from routes.student_routes import router as student_router
from routes.pdf_routes import router as pdf_router

__all__ = [
    "auth_router",
    "admin_router", 
    "instructor_router",
    "student_router",
    "pdf_router"
]
