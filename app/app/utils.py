import phonenumbers
from phonenumbers import NumberParseException
from rest_framework.exceptions import ValidationError


def normalize_phone_number(phone_number, default_region='IN'):
    """
    Normalize phone number to E.164 format (+919876543210)
    Handles formats: 9876543210, +919876543210, 919876543210
    """
    if not phone_number:
        raise ValidationError("Phone number is required")
    
    # Clean the input - remove spaces, dashes, parentheses
    phone_number = str(phone_number).strip()
    phone_number = phone_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    try:
        # Parse the number with default region
        parsed_number = phonenumbers.parse(phone_number, default_region)
        
        # Validate it's a valid number
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError(f"'{phone_number}' is not a valid phone number")
        
        # Format to E.164 standard (+919876543210)
        return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
    
    except NumberParseException as e:
        # User-friendly error messages
        error_msg = str(e)
        if "TOO_SHORT" in error_msg or "too short" in error_msg:
            raise ValidationError(f"Phone number '{phone_number}' is too short. Please enter a valid 10-digit number.")
        elif "TOO_LONG" in error_msg or "too long" in error_msg:
            raise ValidationError(f"Phone number '{phone_number}' is too long. Please enter a valid 10-digit number.")
        elif "INVALID_COUNTRY_CODE" in error_msg:
            raise ValidationError(f"Invalid country code in '{phone_number}'. For India, use +91 or just the 10-digit number.")
        else:
            raise ValidationError(f"Invalid phone number format: '{phone_number}'. Please enter a valid 10-digit number.")
    
    except Exception as e:
        raise ValidationError(f"Phone number error: {str(e)}")