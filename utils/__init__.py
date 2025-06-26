# core/__init__.py
from .agent import UniversalCodeAgent

# generators/__init__.py
from .templates import CodeTemplateGenerator

# analyzers/__init__.py
from .project_analyzer import ProjectAnalyzer

# utils/__init__.py
from .imports import get_availability_status, print_status

# cli/__init__.py
from .main import main

# web/__init__.py
from .streamlit_app import main