import uuid

def generate_referral_code():
    """
    Generate a unique reference code for an affiliate.
    """
    return uuid.uuid4().hex[:8].upper()