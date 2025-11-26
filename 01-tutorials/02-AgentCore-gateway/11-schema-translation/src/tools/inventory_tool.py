"""
Inventory Tool - Mock inventory information API for Gateway

This tool provides mock inventory information in camelCase format.
It will be transformed by the schema translator interceptor.
"""

import json
import random
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """
    Lambda handler for inventory tool.

    Expected input:
    {
        "itemId": "ITEM-12345",
        "location": "East Warehouse" (optional)
    }

    Returns mock inventory data in camelCase format.
    """
    print(f"Inventory tool received event: {json.dumps(event)}")

    # Parse input
    body = event if isinstance(event, dict) else json.loads(event)
    itemId = body.get('itemId', None)
    location = body.get('location', None)

    if not itemId:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "tool": "inventory_tool",
                "error": "itemId is required",
                "success": False
            })
        }

    # Generate mock inventory data in camelCase format
    # This will be translated by the interceptor
    product_names = ['Premium Laptop', 'Wireless Headphones', 'Smart Watch', 
                    'Bluetooth Speaker', 'Gaming Console', 'Smartphone']
    
    locations = ['East Warehouse', 'West Warehouse', 'North Warehouse', 
                'South Warehouse', 'Central Distribution']
    
    # Use provided location if available, otherwise randomly select one
    warehouse_location = location if location else random.choice(locations)
    
    # Generate random date in the last 30 days
    days_ago = random.randint(0, 30)
    update_date = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
    
    inventory_data = {
        "itemId": itemId,  # camelCase format
        "productName": random.choice(product_names),
        "quantityAvailable": random.randint(0, 1000),
        "warehouseLocation": warehouse_location,
        "lastUpdated": update_date,
        "isInStock": random.choice([True, False]),
        "reorderLevel": random.randint(10, 100),
        "supplierInfo": {
            "supplierId": f"SUP-{random.randint(1000, 9999)}",
            "supplierName": f"Supplier {random.choice(['A', 'B', 'C', 'D', 'E'])}",
            "leadTimeInDays": random.randint(3, 30)
        },
        "productDetails": {
            "weightInKg": round(random.uniform(0.1, 20.0), 2),
            "dimensionsInCm": {
                "length": round(random.uniform(5, 100), 1),
                "width": round(random.uniform(5, 100), 1),
                "height": round(random.uniform(5, 100), 1)
            }
        }
    }

    response = {
        "statusCode": 200,
        "body": json.dumps({
            "tool": "inventory_tool",
            "result": inventory_data,
            "success": True
        })
    }

    print(f"Inventory tool response generated")
    return response

# MCP Tool Definition for Gateway registration
TOOL_DEFINITION = {
    "name": "inventory_tool",
    "description": "Retrieve inventory information by Item ID. Returns data in camelCase format.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "itemId": {
                "type": "string",
                "description": "The unique item identifier (e.g., 'ITEM-12345')"
            },
            "location": {
                "type": "string",
                "description": "The warehouse location (e.g., 'East Warehouse'). If not provided, a random location will be selected."
            }
        },
        "required": ["itemId"]
    }
}

if __name__ == "__main__":
    # Test the tool locally
    test_events = [
        {"itemId": "ITEM-12345"},
        {"itemId": "ITEM-67890", "location": "East Warehouse"},
        {"itemId": "ITEM-54321", "location": "Central Distribution"},
        {}  # Test missing itemId
    ]

    for test_event in test_events:
        print(f"\n{'='*60}")
        print(f"Testing with: {test_event}")
        print(f"{'='*60}")
        result = lambda_handler(test_event, None)
        print(f"\nTest result:\n{json.dumps(result, indent=2)}")
