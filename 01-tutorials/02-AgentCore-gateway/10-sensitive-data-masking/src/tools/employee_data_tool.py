"""
Employee Data Tool - Mock employee information API for Gateway

This tool provides mock employee information including contact and location PII.
WARNING: This tool handles sensitive PII data and should have restricted access.
"""

import json
import random
from datetime import datetime


def lambda_handler(event, context):
    """
    Lambda handler for employee data tool.

    Expected input:
    {
        "employee_id": "EMP-98765"
    }

    Returns mock employee data including PII (email, address).
    """
    print(f"Employee data tool received event: {json.dumps(event)}")

    # Parse input
    body = event if isinstance(event, dict) else json.loads(event)
    employee_id = body.get('employee_id', None)

    if not employee_id:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "tool": "employee_data_tool",
                "error": "employee_id is required",
                "success": False
            })
        }

    # Generate mock employee data
    # Field names don't indicate sensitivity, but content contains PII
    first_names = ['Alice', 'Bob', 'Carol', 'David', 'Emma', 'Frank', 'Grace', 'Henry']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
    departments = ['Engineering', 'Marketing', 'Sales', 'Operations', 'Finance', 'Human Resources']
    cities = ['Boston', 'Seattle', 'Austin', 'Denver', 'Portland', 'Chicago']
    streets = ['Oak Avenue', 'Maple Street', 'Pine Road', 'Elm Drive', 'Cedar Lane', 'Birch Way']
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    department = random.choice(departments)
    city = random.choice(cities)
    street = random.choice(streets)
    
    # Generate employee data with 5 fields: 2 sensitive, 3 non-sensitive
    employee_data = {
        # NON-SENSITIVE: Business identifier
        "employee_id": employee_id,
        
        # NON-SENSITIVE: Organizational information
        "department": department,
        
        # SENSITIVE: Contains email (but field name doesn't indicate it)
        # EMAIL - Will be detected and anonymized by Guardrails
        "contact_info": f"{first_name.lower()}.{last_name.lower()}@company.com",
        
        # SENSITIVE: Contains address (but field name doesn't directly indicate it)
        # ADDRESS - Will be detected and anonymized by Guardrails based on CONTENT, not field name
        "mailing_info": f"{random.randint(100, 9999)} {street}, {city}, MA {random.randint(10000, 99999)}",
        
        # NON-SENSITIVE: Employment status
        "status": random.choice(['Active', 'On Leave', 'Remote'])
    }

    response = {
        "statusCode": 200,
        "body": json.dumps({
            "tool": "employee_data_tool",
            "result": employee_data,
            "success": True,
            "note": "Sensitive fields (contact_info, mailing_info) will be anonymized by Bedrock Guardrails based on content, not field names."
        })
    }

    print(f"Employee data tool response generated")
    return response


# MCP Tool Definition for Gateway registration
TOOL_DEFINITION = {
    "name": "employee_data_tool",
    "description": "Retrieve employee information by Employee ID. Returns employee record with contact and location information. Sensitive data will be automatically anonymized by Bedrock Guardrails.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "employee_id": {
                "type": "string",
                "description": "The unique employee identifier (e.g., 'EMP-98765')"
            }
        },
        "required": ["employee_id"]
    }
}


if __name__ == "__main__":
    # Test the tool locally
    test_events = [
        {"employee_id": "EMP-98765"},
        {"employee_id": "EMP-12345"},
        {}  # Test missing employee_id
    ]

    for test_event in test_events:
        print(f"\n{'='*60}")
        print(f"Testing with: {test_event}")
        print(f"{'='*60}")
        result = lambda_handler(test_event, None)
        print(f"\nTest result:\n{json.dumps(result, indent=2)}")
