"""
Custom Permission Classes for Prolean API
"""
from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    """
    Permission class that allows access only to authenticated users with STUDENT role and ACTIVE status.
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role == 'STUDENT' and
            request.user.profile.status == 'ACTIVE'
        )


class IsStaffOrAdmin(permissions.BasePermission):
    """
    Permission class that allows access only to staff (ADMIN or ASSISTANT roles).
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role in ['ADMIN', 'ASSISTANT']
        )


class IsProfessor(permissions.BasePermission):
    """
    Permission class that allows access only to professors.
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role == 'PROFESSOR'
        )


class IsActiveStudent(permissions.BasePermission):
    """
    Permission class for students with ACTIVE status only.
    More lenient than IsStudent for endpoints that need to show pending status info.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'profile'):
            return False
        
        return request.user.profile.role == 'STUDENT'
