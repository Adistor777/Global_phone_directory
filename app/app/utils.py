"""
Utility functions for phone number handling and other helpers
"""
import phonenumbers
from phonenumbers import NumberParseException
from django.conf import settings
from fuzzywuzzy import fuzz


def normalize_phone_number(phone_number: str, region: str = None) -> str:
    """
    Normalize phone number to E.164 format (+countrycode + number)
    
    Examples:
        '9876543210' (India) -> '+919876543210'
        '+919876543210' -> '+919876543210'
        '1234567890' (US) -> '+11234567890'
    
    Args:
        phone_number: Raw phone number string
        region: ISO country code (e.g., 'IN', 'US')
    
    Returns:
        Normalized phone number in E.164 format
    
    Raises:
        ValueError: If phone number is invalid
    """
    if not phone_number:
        raise ValueError("Phone number cannot be empty")
    
    # Remove spaces and common separators
    phone_number = phone_number.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Use default region from settings if not provided
    if region is None:
        region = getattr(settings, 'PHONENUMBER_DEFAULT_REGION', 'IN')
    
    try:
        # Parse phone number
        parsed_number = phonenumbers.parse(phone_number, region)
        
        # Validate phone number
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError(f"Invalid phone number: {phone_number}")
        
        # Return in E.164 format
        return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
    
    except NumberParseException as e:
        raise ValueError(f"Could not parse phone number '{phone_number}': {str(e)}")


def format_phone_display(phone_number: str) -> str:
    """
    Format phone number for display
    
    Example: '+919876543210' -> '+91 98765 43210'
    """
    try:
        parsed = phonenumbers.parse(phone_number, None)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except:
        return phone_number


def get_phone_variants(phone_number: str) -> list:
    """
    Get all variants of a phone number for searching
    
    Example: '+919876543210' -> ['+919876543210', '919876543210', '9876543210']
    """
    variants = [phone_number]
    
    if phone_number.startswith('+'):
        variants.append(phone_number[1:])
    
    try:
        parsed = phonenumbers.parse(phone_number, None)
        national = str(parsed.national_number)
        if national not in variants:
            variants.append(national)
    except:
        pass
    
    return variants


def calculate_name_similarity(name1: str, name2: str) -> int:
    """
    Calculate similarity between two names (0-100)
    Uses fuzzy matching for better results
    
    Args:
        name1: First name
        name2: Second name
    
    Returns:
        Similarity score (0-100)
    """
    if not name1 or not name2:
        return 0
    
    # Convert to lowercase for comparison
    name1 = name1.lower().strip()
    name2 = name2.lower().strip()
    
    # Exact match
    if name1 == name2:
        return 100
    
    # Use fuzzywuzzy for partial matching
    return fuzz.ratio(name1, name2)