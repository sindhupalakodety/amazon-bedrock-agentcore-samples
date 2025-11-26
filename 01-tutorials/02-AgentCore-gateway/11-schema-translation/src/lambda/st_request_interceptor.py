"""
Request Interceptor for Inventory Tool

Translates client-friendly schema (snake_case) to inventory tool schema (camelCase)
"""

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda handler for request interceptor
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract request body
        request_body = event.get('mcp', {}).get('gatewayRequest', {}).get('body', {})
        auth_header = event.get('mcp', {}).get('gatewayRequest', {}).get('headers', {}).get('Authorization', '')
        
        # Only process inventory tool calls
        if (request_body.get('method') == 'tools/call' and 
            request_body.get('params', {}).get('tool') == 'inventory-tool-target___inventory_tool'):

            logger.info("Processing inventory tool request")
            
            # Get inputs from params
            inputs = request_body.get('params', {}).get('inputs', {})
            
            # Simple replacement of item_id with itemId if it exists
            if 'item_id' in inputs:
                inputs['itemId'] = inputs.pop('item_id')
                logger.info("Replaced item_id with itemId")

            print("request_body after transformation:", request_body)
        
        # Create the transformed request
        transformed_request = {
            "interceptorOutputVersion": "1.0",
            "mcp": {
                "transformedGatewayRequest": {
                    "headers": {
                        "Authorization": auth_header,
                        "Content-Type": "application/json"
                    },
                    "body": request_body
                }
            }
        }
        # Print the transformed request
        print("Complete transformed request:")
        print(transformed_request)
        
        return transformed_request
        
    except Exception as e:
        logger.error(f"Error in request interceptor: {str(e)}")
        return {
            "interceptorOutputVersion": "1.0",
            "mcp": {
                "transformedGatewayResponse": {
                    "statusCode": 500,
                    "body": {
                        "jsonrpc": "2.0",
                        "id": "unknown",
                        "error": {
                            "code": -32600,
                            "message": f"Interceptor error: {str(e)}"
                        }
                    }
                }
            }
        }