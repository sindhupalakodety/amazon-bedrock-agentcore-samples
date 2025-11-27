"""
Request Interceptor for Inventory Tool

Translates client-friendly schema (snake_case) to inventory tool schema (camelCase)
"""

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def extract_tool_name(body):
    """Extract tool name from MCP tools/call request body"""
    try:
        if isinstance(body, dict):
            params = body.get("params", {})
            tool_name = params.get("name", "")
            # Tool names are of the form: <target>___<toolName>
            if "___" in tool_name:
                return tool_name.split("___")[-1]
            return tool_name
    except Exception:
        pass
    return None

def build_pass_through_response(auth_header, body):
    """Return a pass-through response to let the request reach the target"""
    return {
        "interceptorOutputVersion": "1.0",
        "mcp": {
            "transformedGatewayRequest": {
                "headers": {
                    "Authorization": auth_header,
                    "Content-Type": "application/json"
                },
                "body": body
            }
        }
    }

def build_error_response(message, body, status_code=403):
    """Return an MCP-style error response"""
    return {
        "interceptorOutputVersion": "1.0",
        "mcp": {
            "transformedGatewayResponse": {
                "statusCode": status_code,
                "body": {
                    "jsonrpc": "2.0",
                    "id": body.get("id", "unknown") if isinstance(body, dict) else "unknown",
                    "error": {
                        "code": -32600,
                        "message": message
                    }
                }
            }
        }
    }

def lambda_handler(event, context):
    """
    Lambda handler for request interceptor
    """

    print(f"Received event: {json.dumps(event)}")
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Extract the gateway request from the correct structure
    mcp_data = event.get("mcp", {})
    gateway_request = mcp_data.get("gatewayRequest", {})
    headers = gateway_request.get("headers", {})
    body = gateway_request.get("body", {})
    
    # Extract Authorization header
    auth_header = headers.get("Authorization", "")
    
    # Enforce presence of a Bearer token for ALL requests
    if not auth_header.startswith("Bearer "):
        response = build_error_response("No authorization token provided", body)
        print(f"Returning error response (no token): {json.dumps(response)}")
        return response

    try:

        method = body.get("method", "")
        tool_name = extract_tool_name(body)

        print(f"MCP method: {method}")
        print(f"Requested tool: {tool_name}")
     
        # Only process inventory tool calls

        if method == "tools/call" and tool_name == "inventory_tool":

            print("Processing inventory tool request")
            
            # Get inputs from params
            inputs = body.get('params', {}).get('arguments', {})
            print(inputs)
            
            # Simple replacement of item_id with itemId if it exists
            if 'item_id' in inputs:
                inputs['itemId'] = inputs.pop('item_id')
                print("Replaced item_id with itemId")
                
            # Add location as "East Warehouse" only if it's not already provided
            if 'location' not in inputs:
                inputs['location'] = "East Warehouse"
                print("Added default location: East Warehouse")

            print("request_body after transformation:", body)
            response = build_pass_through_response(auth_header, body)
            print(f"returning response after transformation: {json.dumps(response)}")
            return response

    except Exception as e:
        print(f"Error during schema translation: {e}")
        response = build_error_response(f"Invalid token - {e}", body)
        print(f"Returning error response (exception): {json.dumps(response)}")
        return response
    
    # Authorized → pass through
    response = build_pass_through_response(auth_header, body)
    print(f"Returning pass-through response (authorized): {json.dumps(response)}")
    return response