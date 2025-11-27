"""
Customer Data Tool - Mock customer information API for Gateway

This tool provides mock customer information including PII data like SSN.
WARNING: This tool handles sensitive PII data and should have restricted access.
"""

import json
import random
from datetime import datetime


def lambda_handler(event, context):
    """
    Lambda handler for customer data tool.

    Expected input:
    {
        "customer_id": "CUST-12345"
    }

    Returns mock customer data including PII (SSN).
    """
    print(f"Customer data tool received event: {json.dumps(event)}")

    # Parse input
    body = event if isinstance(event, dict) else json.loads(event)
    customer_id = body.get('customer_id', None)

    if not customer_id:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "tool": "customer_data_tool",
                "error": "customer_id is required",
                "success": False
            })
        }

    # Generate mock customer data with various PII types
    # These will be detected and masked by Bedrock Guardrails
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    # Generate various PII types that Bedrock Guardrails will detect
    customer_data = {
        "customer_id": customer_id,
        "personal_info": {
            # NAME - Will be detected by Guardrails
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}",
            
            # AGE - Will be detected by Guardrails
            "age": random.randint(25, 65),
            
            # EMAIL - Will be detected by Guardrails
            "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
            
            # PHONE - Will be detected by Guardrails
            "phone": f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "mobile": f"({random.randint(200, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
            
            # US_SOCIAL_SECURITY_NUMBER - Will be detected by Guardrails
            "ssn": f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}",
            
            # DRIVER_ID - Will be detected by Guardrails
            "drivers_license": f"D{random.randint(1000000, 9999999)}",
            
            # US_PASSPORT_NUMBER - Will be detected by Guardrails
            "passport_number": f"{random.randint(100000000, 999999999)}",
            
            # DATE OF BIRTH
            "date_of_birth": f"{random.randint(1950, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            
            # USERNAME - Will be detected by Guardrails
            "username": f"{first_name.lower()}{random.randint(100, 999)}",
            
            # PASSWORD - Will be detected by Guardrails (simulated)
            "temporary_password": f"TempPass{random.randint(1000, 9999)}!"
        },
        "financial_info": {
            # SENSITIVE - Will be masked by Guardrails
            # US_BANK_ACCOUNT_NUMBER - Will be detected by Guardrails
            "bank_account": f"{random.randint(100000000, 999999999)}",
            
            # US_BANK_ROUTING_NUMBER - Will be detected by Guardrails
            "routing_number": f"{random.randint(100000000, 999999999)}",
            
            # CREDIT_DEBIT_CARD_NUMBER - Will be detected by Guardrails
            "credit_card": f"{random.randint(4000, 4999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            
            # CREDIT_DEBIT_CARD_CVV - Will be detected by Guardrails
            "cvv": f"{random.randint(100, 999)}",
            
            # CREDIT_DEBIT_CARD_EXPIRY - Will be detected by Guardrails
            "card_expiry": f"{random.randint(1, 12):02d}/{random.randint(25, 30)}",
            
            # PIN - Will be detected by Guardrails
            "pin": f"{random.randint(1000, 9999)}",
            
            # US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER - Will be detected by Guardrails
            "tax_id": f"{random.randint(900, 999)}-{random.randint(70, 99)}-{random.randint(1000, 9999)}",
            
            # NON-SENSITIVE - These will NOT be masked
            "account_balance": round(random.uniform(1000, 50000), 2),
            "credit_score": random.randint(600, 850),
            "currency": "USD",
            "payment_terms": random.choice(['Net 30', 'Net 60', 'Immediate']),
            "credit_limit": round(random.uniform(5000, 50000), 2),
            "available_credit": round(random.uniform(1000, 25000), 2)
        },
        "address": {
            # ADDRESS - Will be detected by Guardrails
            "street": f"{random.randint(100, 9999)} Main Street",
            "city": "Springfield",
            "state": "California",
            "zip_code": f"{random.randint(90000, 96999)}",
            "country": "USA",
            "full_address": f"{random.randint(100, 9999)} Main Street, Springfield, CA {random.randint(90000, 96999)}"
        },
        "technical_info": {
            # SENSITIVE - Will be masked by Guardrails
            # IP_ADDRESS - Will be detected by Guardrails
            "last_login_ip": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            
            # MAC_ADDRESS - Will be detected by Guardrails
            "device_mac": f"{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}",
            
            # URL - Will be detected by Guardrails
            "profile_url": f"https://customer-portal.example.com/profile/{customer_id}",
            
            # NON-SENSITIVE - These will NOT be masked
            "last_login_timestamp": datetime.utcnow().isoformat(),
            "device_type": random.choice(['Desktop', 'Mobile', 'Tablet']),
            "browser": random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
            "operating_system": random.choice(['Windows', 'macOS', 'iOS', 'Android', 'Linux']),
            "session_count": random.randint(1, 1000),
            "two_factor_enabled": random.choice([True, False])
        },
        "vehicle_info": {
            # SENSITIVE - Will be masked by Guardrails
            # VEHICLE_IDENTIFICATION_NUMBER - Will be detected by Guardrails
            "vin": f"1HGBH41JXMN{random.randint(100000, 999999)}",
            
            # LICENSE_PLATE - Will be detected by Guardrails
            "license_plate": f"{random.randint(1, 9)}{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}{random.randint(100, 999)}",
            
            # NON-SENSITIVE - These will NOT be masked
            "make": random.choice(['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Tesla']),
            "model": random.choice(['Camry', 'Accord', 'F-150', 'Silverado', 'Model 3']),
            "year": random.randint(2015, 2024),
            "color": random.choice(['Black', 'White', 'Silver', 'Blue', 'Red']),
            "mileage": random.randint(5000, 150000)
        },
        "account_info": {
            # NON-SENSITIVE - These fields will NOT be masked
            "account_type": random.choice(['Premium', 'Standard', 'Basic']),
            "status": random.choice(['Active', 'Inactive', 'Suspended']),
            "member_since": f"{random.randint(2015, 2023)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "loyalty_tier": random.choice(['Bronze', 'Silver', 'Gold', 'Platinum']),
            "total_orders": random.randint(5, 500),
            "last_order_date": f"{random.randint(2023, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "preferred_language": random.choice(['English', 'Spanish', 'French']),
            "notification_preferences": {
                "email_notifications": random.choice([True, False]),
                "sms_notifications": random.choice([True, False]),
                "push_notifications": random.choice([True, False])
            }
        },
        "preferences": {
            # NON-SENSITIVE - Customer preferences will NOT be masked
            "favorite_categories": random.sample(['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys'], k=3),
            "preferred_payment_method": random.choice(['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer']),
            "newsletter_subscribed": random.choice([True, False]),
            "marketing_consent": random.choice([True, False]),
            "theme_preference": random.choice(['Light', 'Dark', 'Auto'])
        },
        "statistics": {
            # NON-SENSITIVE - Aggregated statistics will NOT be masked
            "lifetime_value": round(random.uniform(500, 25000), 2),
            "average_order_value": round(random.uniform(50, 500), 2),
            "total_spent": round(random.uniform(1000, 50000), 2),
            "return_rate": round(random.uniform(0, 15), 2),
            "satisfaction_score": round(random.uniform(3.5, 5.0), 1),
            "referrals_made": random.randint(0, 20)
        },
        "metadata": {
            "retrieved_at": datetime.utcnow().isoformat(),
            "data_classification": "PII - Highly Sensitive",
            "contains_pii": True,
            "pii_types": [
                "NAME", "AGE", "EMAIL", "PHONE", "SSN", "DRIVER_ID", "PASSPORT",
                "USERNAME", "PASSWORD", "BANK_ACCOUNT", "ROUTING_NUMBER", 
                "CREDIT_CARD", "CVV", "CARD_EXPIRY", "PIN", "TAX_ID",
                "ADDRESS", "IP_ADDRESS", "MAC_ADDRESS", "URL", "VIN", "LICENSE_PLATE"
            ]
        }
    }

    response = {
        "statusCode": 200,
        "body": json.dumps({
            "tool": "customer_data_tool",
            "result": customer_data,
            "success": True,
            "warning": "This response contains multiple types of PII data. All sensitive fields will be masked by Bedrock Guardrails."
        })
    }

    print(f"Customer data tool response (PII redacted in logs)")
    return response


# MCP Tool Definition for Gateway registration
TOOL_DEFINITION = {
    "name": "customer_data_tool",
    "description": "Retrieve comprehensive customer information by Customer ID. WARNING: Returns highly sensitive PII data including SSN, credit card, bank account, passport, driver's license, and other personal information. All PII will be automatically masked by Bedrock Guardrails before being returned to clients.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The unique customer identifier (e.g., 'CUST-12345')"
            }
        },
        "required": ["customer_id"]
    }
}


if __name__ == "__main__":
    # Test the tool locally
    test_events = [
        {"customer_id": "CUST-12345"},
        {"customer_id": "CUST-67890"},
        {}  # Test missing customer_id
    ]

    for test_event in test_events:
        print(f"\n{'='*60}")
        print(f"Testing with: {test_event}")
        print(f"{'='*60}")
        result = lambda_handler(test_event, None)
        print(f"\nTest result:\n{json.dumps(result, indent=2)}")
