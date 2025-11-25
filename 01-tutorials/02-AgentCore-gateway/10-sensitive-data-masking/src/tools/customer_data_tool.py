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

    # Generate mock customer data with PII
    # Note: Using placeholder PII data as per security guidelines
    first_names = ['[John]', '[Jane]', '[Michael]', '[Sarah]', '[David]', '[Emily]']
    last_names = ['[Smith]', '[Johnson]', '[Williams]', '[Brown]', '[Jones]', '[Garcia]']
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    # Generate mock SSN (format: XXX-XX-XXXX)
    ssn = f"[{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}]"
    
    # Generate other customer details
    account_types = ['Premium', 'Standard', 'Basic']
    statuses = ['Active', 'Inactive', 'Suspended']
    
    customer_data = {
        "customer_id": customer_id,
        "personal_info": {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}",
            "ssn": ssn,  # PII - Social Security Number
            "date_of_birth": f"[{random.randint(1950, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}]",
            "email": f"[{first_name.lower().strip('[]')}.{last_name.lower().strip('[]')}@example.com]",
            "phone": f"[+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}]"
        },
        "account_info": {
            "account_type": random.choice(account_types),
            "status": random.choice(statuses),
            "member_since": f"[{random.randint(2015, 2023)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}]",
            "account_balance": round(random.uniform(0, 10000), 2),
            "credit_score": random.randint(300, 850)
        },
        "address": {
            "street": f"[{random.randint(100, 9999)} Main Street]",
            "city": "[City Name]",
            "state": "[State]",
            "zip_code": f"[{random.randint(10000, 99999)}]",
            "country": "[USA]"
        },
        "metadata": {
            "retrieved_at": datetime.utcnow().isoformat(),
            "data_classification": "PII - Restricted Access",
            "contains_ssn": True
        }
    }

    response = {
        "statusCode": 200,
        "body": json.dumps({
            "tool": "customer_data_tool",
            "result": customer_data,
            "success": True,
            "warning": "This response contains PII data including SSN. Handle with care."
        })
    }

    print(f"Customer data tool response (PII redacted in logs)")
    return response


# MCP Tool Definition for Gateway registration
TOOL_DEFINITION = {
    "name": "customer_data_tool",
    "description": "Retrieve customer information by Customer ID. WARNING: Returns sensitive PII data including SSN. Restricted access only.",
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
