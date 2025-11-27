"""
PII Masking Interceptor for Gateway MCP RESPONSES using Bedrock Guardrails

This Lambda function intercepts Gateway MCP tools/call RESPONSES and masks
sensitive PII data using Amazon Bedrock Guardrails API for ALL tool responses.
It is configured as a RESPONSE interceptor that transforms any tool response.
"""

import json
import os
import boto3
from typing import Any, Dict

# Initialize Bedrock Runtime client
bedrock_runtime = boto3.client('bedrock-runtime')

# Get Guardrail configuration from environment variables
GUARDRAIL_ID = os.environ.get('GUARDRAIL_ID')
GUARDRAIL_VERSION = os.environ.get('GUARDRAIL_VERSION', 'DRAFT')

def mask_pii_with_guardrails(text: str) -> str:
    """
    Use Bedrock Guardrails to mask PII in text.
    
    Args:
        text: Text content that may contain PII
    
    Returns:
        Text with PII masked/anonymized by Guardrails
    """
    if not GUARDRAIL_ID:
        print("WARNING: GUARDRAIL_ID not configured, skipping PII masking")
        return text
    
    try:
        # Apply guardrail to the text
        response = bedrock_runtime.apply_guardrail(
            guardrailIdentifier=GUARDRAIL_ID,
            guardrailVersion=GUARDRAIL_VERSION,
            source='OUTPUT',  # We're filtering output from tools
            content=[{
                'text': {
                    'text': text
                }
            }]
        )
        
        # Extract the masked text from the response
        outputs = response.get('outputs', [])
        if outputs and len(outputs) > 0:
            masked_text = outputs[0].get('text', text)
            
            # Log PII detection details
            usage = response.get('usage', {})
            assessments = response.get('assessments', [])
            
            if usage.get('contentPolicyUnits', 0) > 0:
                print(f"PII detected and anonymized by Guardrails")
                
                # Log what types of PII were detected
                if assessments:
                    for assessment in assessments:
                        sensitive_info = assessment.get('sensitiveInformationPolicy', {})
                        pii_entities = sensitive_info.get('piiEntities', [])
                        if pii_entities:
                            detected_types = [entity.get('type') for entity in pii_entities]
                            print(f"  Detected PII types: {', '.join(detected_types)}")
            
            return masked_text
        
        return text
        
    except Exception as e:
        error_message = str(e)
        print(f"Error applying Guardrails: {error_message}")
        print(f"  Guardrail ID: {GUARDRAIL_ID}")
        print(f"  Guardrail Version: {GUARDRAIL_VERSION}")
        
        # Check if it's a validation error about guardrail not existing
        if 'does not exist' in error_message or 'ValidationException' in error_message:
            print("  ⚠ The Guardrail ID or version is invalid or doesn't exist")
            print("  ⚠ Make sure Step 1.3 was run successfully to create the Guardrail")
            print("  ⚠ Verify the Lambda environment variables are set correctly")
        
        # On error, return original text (fail open to avoid blocking)
        return text

def mask_tool_response(response_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask PII in any tool response using Bedrock Guardrails.
    
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
                    
                    # Apply masking to any tool response that has a 'result' field
                    if 'result' in body_json:
                        tool_name = body_json.get('tool', 'unknown')
                        print(f"Applying PII masking to tool: {tool_name}")
                        
                        # Convert result to string for Guardrails processing
                        result_text = json.dumps(body_json['result'])
                        
                        # Apply Bedrock Guardrails to mask PII
                        masked_text = mask_pii_with_guardrails(result_text)
                        
                        # Parse the masked text back to JSON
                        try:
                            body_json['result'] = json.loads(masked_text)
                        except json.JSONDecodeError:
                            # If Guardrails returns non-JSON text, wrap it
                            body_json['result'] = {'masked_data': masked_text}
                        
                        # Update the body with masked data
                        outer_json['body'] = json.dumps(body_json)
                        
                        # Update the text with the updated outer JSON
                        masked_response['result']['content'][i]['text'] = json.dumps(outer_json)
                        
                        print(f"PII masking completed for tool: {tool_name}")
            
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                # Not valid JSON or unexpected structure, pass through unchanged
    
    return masked_response

def lambda_handler(event, context):
    """
    Main Lambda handler for Gateway RESPONSE interceptor.
    
    This handler applies PII masking to ALL tool responses using Bedrock Guardrails.
    
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
                                "text": "{...tool data with potential PII...}"
                            }
                        ]
                    }
                },
                "statusCode": 200
            },
            "gatewayRequest": {...}
        }
    }
    
    Returns transformed response with masked PII for any tool.
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
            print("Applying PII masking to tool response...")
            
            # Mask PII in the response for any tool
            masked_body = mask_tool_response(response_body)
            
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