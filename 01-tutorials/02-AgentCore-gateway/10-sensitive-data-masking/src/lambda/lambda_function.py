"""
PII Masking Interceptor for Gateway MCP RESPONSES

This Lambda function intercepts Gateway MCP tools/call RESPONSES and masks
sensitive PII data (like SSN) from customer_data_tool responses.
It is configured as a RESPONSE interceptor that transforms the tool response.
"""

import json
from typing import Any, Dict

def mask_ssn(data: Any) -> Any:
    """
    Recursively traverse data structure and mask SSN fields.
    Replaces SSN values with 'XXX-XX-XXXX'.
    
    Args:
        data: Data structure to mask (dict, list, or primitive)
    
    Returns:
        Data structure with masked SSN values
    """
    if isinstance(data, dict):
        masked_data = {}
        for key, value in data.items():      
            # Check if this is an SSN field
            if key.lower() == 'ssn':
                # Mask the SSN value
                masked_data[key] = 'XXX-XX-XXXX'
            else:
                # Recursively mask nested structures
                masked_data[key] = mask_ssn(value)
        return masked_data
    
    elif isinstance(data, list):
        return [mask_ssn(item) for item in data]
    
    else:
        # Primitive value, return as-is
        return data

def mask_customer_data_response(response_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask PII in customer_data_tool response.
    
    Args:
        response_body: MCP JSON-RPC response body
    
    Returns:
        Response body with masked PII
    """
    # Create a deep copy to avoid modifying the original
    masked_response = json.loads(json.dumps(response_body))
    
    # Check if this is a valid response with content
    if ('result' not in masked_response or 
        'content' not in masked_response['result'] or 
        not isinstance(masked_response['result']['content'], list)):
        return masked_response
    
    # Process each content item
    for i, item in enumerate(masked_response['result']['content']):
        if item.get('type') == 'text':
            text = item.get('text', '')
            
            try:
                # Parse the outer JSON (statusCode and body)
                outer_json = json.loads(text)
                
                if 'body' in outer_json and isinstance(outer_json['body'], str):
                    # Parse the inner JSON (the actual body content)
                    body_json = json.loads(outer_json['body'])
                    
                    # Check if this is from customer_data_tool
                    if body_json.get('tool') == 'customer_data_tool' and 'result' in body_json:
                        # Apply masking to the result
                        body_json['result'] = mask_ssn(body_json['result'])
                        
                        # Update the body with masked data
                        outer_json['body'] = json.dumps(body_json)
                        
                        # Update the text with the updated outer JSON
                        masked_response['result']['content'][i]['text'] = json.dumps(outer_json)
                        
                        print("PII masking completed")
            
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                # Not valid JSON or unexpected structure, pass through unchanged
    
    return masked_response

def lambda_handler(event, context):
    """
    Main Lambda handler for Gateway RESPONSE interceptor.
    
    Expected event structure (from Gateway RESPONSE for tools/call):
    {
        "interceptorInputVersion": "1.0",
        "mcp": {
            "gatewayResponse": {
                "headers": {...},
                "body": {
                    "jsonrpc": "2.0",
                    "id": "invoke-tool-request",
                    "result": {
                        "isError": false,
                        "content": [
                            {
                                "type": "text",
                                "text": "{...customer data with SSN...}"
                            }
                        ]
                    }
                },
                "statusCode": 200
            },
            "gatewayRequest": {...}
        }
    }
    
    Returns transformed response with masked PII.
    """
    print(f"PII Masking Interceptor - Received event: {json.dumps(event, default=str)}")
    
    try:
        # Extract MCP data
        mcp_data = event.get('mcp', {})
        gateway_response = mcp_data.get('gatewayResponse', {})
        gateway_request = mcp_data.get('gatewayRequest', {})
        
        # Get response data
        response_headers = gateway_response.get('headers', {})
        response_body = gateway_response.get('body', {})
        status_code = gateway_response.get('statusCode', 200)
        
        # Get request data to check which tool was called
        request_body = gateway_request.get('body', {})
        method = request_body.get('method', '')
        
        print(f"Method: {method}")
        
        # Only process tools/call responses
        if method == 'tools/call':
            params = request_body.get('params', {})
            tool_name = params.get('name', '')
            
            print(f"Tool called: {tool_name}")
            
            # Check if this is customer_data_tool
            if 'customer_data_tool' in tool_name:
                print("Customer data tool detected, applying PII masking...")
                
                # Mask PII in the response
                masked_body = mask_customer_data_response(response_body)
                
                print(f"Masked response body: {json.dumps(masked_body, default=str)}")
                
                # Return transformed response
                return {
                    "interceptorOutputVersion": "1.0",
                    "mcp": {
                        "transformedGatewayResponse": {
                            "headers": response_headers,
                            "body": masked_body,
                            "statusCode": status_code
                        }
                    }
                }
        
        # Pass through unchanged for non-customer-data responses
        return {
            "interceptorOutputVersion": "1.0",
            "mcp": {
                "transformedGatewayResponse": {
                    "headers": response_headers,
                    "body": response_body,
                    "statusCode": status_code
                }
            }
        }
    
    except Exception as e:
        print(f"ERROR in lambda_handler: {e}")
        
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        # On error, pass through unchanged (safer than blocking)
        return {
            "interceptorOutputVersion": "1.0",
            "mcp": {
                "transformedGatewayResponse": {
                    "headers": gateway_response.get('headers', {}),
                    "body": gateway_response.get('body', {}),
                    "statusCode": gateway_response.get('statusCode', 500)
                }
            }
        }