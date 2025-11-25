"""
Request Interceptor for Inventory Tool

Translates client-friendly schema (snake_case) to inventory tool schema (camelCase)
"""

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Schema mapping: client format → tool format
REQUEST_SCHEMA_MAP = {
    "item_id": "itemId"
    # "product_name": "productName",
    # "quantity": "quantityAvailable",
    # "location": "warehouseLocation",
    # "update_timestamp": "lastUpdated"
}

def translate_request_schema(client_data):
    """
    Translate from client schema to tool schema
    """
    if not isinstance(client_data, dict):
        return client_data
        
    tool_data = {}
    for client_key, client_value in client_data.items():
        # Get the tool key from the mapping, or keep original if not in mapping
        tool_key = REQUEST_SCHEMA_MAP.get(client_key, client_key)
        
        # Handle nested dictionaries or lists recursively
        if isinstance(client_value, dict):
            tool_data[tool_key] = translate_request_schema(client_value)
        elif isinstance(client_value, list):
            tool_data[tool_key] = [translate_request_schema(item) if isinstance(item, dict) else item 
                                  for item in client_value]
        else:
            tool_data[tool_key] = client_value
            
    return tool_data

def lambda_handler(event, context):
    """
    Lambda handler for request interceptor
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract request body
        mcp_data = event.get('mcp', {})
        gateway_request = mcp_data.get('gatewayRequest', {})
        request_body = gateway_request.get('body', {})

        print("statement1")
        
        # Only process inventory_tool calls
        if (request_body.get('method') == 'tools/call' and 
            'params' in request_body and
            request_body['params'].get('tool') == 'inventory-tool-target___inventory_tool'):

            print("statement2")
            
            # Extract tool arguments
            params = request_body['params']
            print(params)
            if 'inputs' in params:
                try:
                    # Parse arguments JSON
                    args_dict = params['inputs']
                    print("original",args_dict)
                    
                    # Translate schema
                    translated_args = translate_request_schema(args_dict)
                    print("translation",translated_args)
                    
                    # Update arguments with translated schema
                    request_body['params']['inputs'] = translated_args
                    # request_body['params']['inputs'] = json.dumps(translated_args)
                    print("updated", request_body['params']['inputs'])
                    
                    logger.info(f"Translated request: {json.dumps(request_body)}")
                except json.JSONDecodeError:
                    logger.warning("Failed to parse inputs JSON")
        
        # Return transformed request
        return {
            "interceptorOutputVersion": "1.0",
            "mcp": {
                "transformedGatewayRequest": gateway_request
            }
        }
        
    except Exception as e:
        logger.error(f"Error in request interceptor: {str(e)}")
        # On error, return original request unchanged
        return {
            "interceptorOutputVersion": "1.0",
            "mcp": {
                "transformedGatewayRequest": gateway_request
            }
        }
