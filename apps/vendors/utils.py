"""Utility functions for vendor module"""
import os
from django.core.exceptions import ValidationError


def validate_file_size(file, max_size_mb=5):
    """
    Validate file size
    Args:
        file: UploadedFile object
        max_size_mb: Maximum file size in MB (default: 5)
    Returns:
        bool: True if valid
    Raises:
        ValidationError if file is too large
    """
    if file and file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'File size must not exceed {max_size_mb}MB.')
    return True


def validate_file_extension(file, allowed_extensions=None):
    """
    Validate file extension
    Args:
        file: UploadedFile object
        allowed_extensions: List of allowed extensions (default: PDF, images, docs)
    Returns:
        bool: True if valid
    Raises:
        ValidationError if extension not allowed
    """
    if allowed_extensions is None:
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
    
    if file:
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}')
    return True


def validate_id_format(id_type, id_number):
    """
    Validate ID number format based on ID type
    Args:
        id_type: Type of ID (PAN, Aadhaar, GST, Udyam)
        id_number: ID number string
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    id_number = id_number.strip().upper()
    
    if id_type == 'PAN Card':
        if len(id_number) != 10:
            return False, 'PAN Card must be 10 characters long.'
        if not id_number.isalnum():
            return False, 'PAN Card must be alphanumeric.'
        return True, ''
    
    elif id_type == 'Aadhaar':
        if len(id_number) != 12:
            return False, 'Aadhaar must be 12 digits long.'
        if not id_number.isdigit():
            return False, 'Aadhaar must contain only digits.'
        return True, ''
    
    elif id_type == 'GST':
        if len(id_number) != 15:
            return False, 'GST number must be 15 characters long.'
        if not id_number.isalnum():
            return False, 'GST number must be alphanumeric.'
        return True, ''
    
    elif id_type == 'Udyam':
        if len(id_number) != 19:
            return False, 'Udyam number must be 19 characters long.'
        return True, ''
    
    return True, ''


def format_payment_schedule(value, unit):
    """
    Format payment schedule for display
    Args:
        value: Number value (e.g., 7, 15, 30)
        unit: Unit (Days, Weeks, Months)
    Returns:
        str: Formatted string (e.g., "7 Days", "2 Weeks")
    """
    return f"{value} {unit}"
