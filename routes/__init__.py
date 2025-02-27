"""
Routes package initialization
"""
from .document_routes import bp as document_routes_bp
from .matching_routes import bp as matching_routes_bp
from .health_routes import bp as health_routes_bp

__all__ = ['document_routes_bp', 'matching_routes_bp', 'health_routes_bp']