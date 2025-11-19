"""
Utility functions for processing payload templates with namespace support
"""
import json
import re
from typing import Dict, Any, Optional


def process_payload_template(
    template: str,
    comparison: Optional[Dict[str, Any]] = None,
    difference: Optional[Dict[str, Any]] = None,
    project: Optional[Dict[str, Any]] = None,
    json_raw: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a payload template with namespace placeholders
    
    Supported namespaces:
    - {{comparison.id}} - Comparison ID
    - {{comparison.project_id}} - Project ID
    - {{comparison.executed_at}} - Execution timestamp
    - {{comparison.status}} - Status (pending, running, completed, failed)
    - {{comparison.total_differences}} - Total number of differences
    - {{difference.id}} - Difference/Result ID
    - {{difference.record_id}} - Record identifier
    - {{difference.field_name}} - Field name
    - {{difference.source_value}} - Source value
    - {{difference.target_value}} - Target value
    - {{difference.change_type}} - Change type (added, modified, deleted)
    - {{difference.detected_at}} - Detection timestamp
    - {{json_raw.campo}} - Access any field from complete target record (e.g., {{json_raw.email}}, {{json_raw.id}})
    - {{project.id}} - Project ID
    - {{project.name}} - Project name
    
    Args:
        template: JSON string template with placeholders
        comparison: Dictionary with comparison data
        difference: Dictionary with difference/result data
        project: Dictionary with project data
    
    Returns:
        Processed dictionary with placeholders replaced
    """
    if not template:
        return {}
    
    # Store original template for error handling
    original_template = template
    
    # First, try to parse template as JSON
    # This is important because JSON templates need to be processed as structured objects
    # to properly handle string values (they need quotes)
    try:
        # Parse template as JSON
        payload = json.loads(template)
        payload_str = json.dumps(payload)  # For fallback string processing
        print(f"[PAYLOAD_TEMPLATE] Template parsed as JSON successfully")
    except json.JSONDecodeError as e:
        # If not valid JSON, check if it looks like JSON with placeholders
        template_stripped = template.strip()
        if template_stripped.startswith('{') or template_stripped.startswith('['):
            # It looks like JSON but has placeholders - try to parse as JSON anyway
            # by temporarily replacing placeholders with null values
            print(f"[PAYLOAD_TEMPLATE] Template looks like JSON but failed to parse: {e}")
            print(f"[PAYLOAD_TEMPLATE] Template preview: {template_stripped[:200]}")
            # We'll process it as string template, but need to ensure proper JSON formatting
            payload = None
            payload_str = template_stripped
        else:
            # Not JSON-like, treat as plain string template
            payload = None
            payload_str = template_stripped
    
    # Build namespace dictionary
    namespaces = {}
    
    if comparison:
        namespaces['comparison'] = {
            'id': comparison.get('id', ''),
            'project_id': comparison.get('project_id', ''),
            'executed_at': comparison.get('executed_at', ''),
            'status': comparison.get('status', ''),
            'total_differences': comparison.get('total_differences', 0),
            'metadata': comparison.get('metadata', {})
        }
    
    if difference:
        namespaces['difference'] = {
            'id': difference.get('id', ''),
            'comparison_id': difference.get('comparison_id', ''),
            'record_id': difference.get('record_id', ''),
            'field_name': difference.get('field_name', ''),
            'source_value': difference.get('source_value', ''),
            'target_value': difference.get('target_value', ''),
            'change_type': difference.get('change_type', ''),
            'detected_at': difference.get('detected_at', '')
        }
        # Also support 'result' namespace as alias
        namespaces['result'] = namespaces['difference']
    
    # Add json_raw namespace with complete target record data
    # Can come from difference.target_record_json or as separate parameter
    if json_raw:
        namespaces['json_raw'] = json_raw
    elif difference and difference.get('target_record_json'):
        namespaces['json_raw'] = difference.get('target_record_json')
    else:
        namespaces['json_raw'] = {}
    
    if project:
        namespaces['project'] = {
            'id': project.get('id', ''),
            'name': project.get('name', ''),
            'description': project.get('description', ''),
            'source_table': project.get('source_table', ''),
            'target_table': project.get('target_table', '')
        }
    
    # Replace placeholders - we'll do this in two passes:
    # 1. First pass: replace simple values (strings, numbers, etc.)
    # 2. Second pass: replace complex values (dicts, lists) by modifying the parsed JSON directly
    
    # First, try to parse the template as JSON to work with structured data
    try:
        # Parse template as JSON structure
        if isinstance(payload, dict):
            payload_obj = payload
        else:
            try:
                payload_obj = json.loads(payload_str)
            except json.JSONDecodeError:
                # If payload_str is not valid JSON, raise to fallback to string processing
                raise ValueError("Template is not valid JSON")
        
        # Function to recursively replace placeholders in the JSON object
        def replace_in_object(obj):
            """Recursively replace placeholders in JSON object"""
            if isinstance(obj, dict):
                result = {}
                for k, v in obj.items():
                    result[k] = replace_in_object(v)
                return result
            elif isinstance(obj, list):
                return [replace_in_object(item) for item in obj]
            elif isinstance(obj, str):
                # Check if it's a placeholder
                placeholder_pattern = r'\{\{([^}]+)\}\}'
                matches = list(re.finditer(placeholder_pattern, obj))
                
                if not matches:
                    return obj  # Not a placeholder, return as-is
                
                # If the entire string is a single placeholder, return the value directly
                if len(matches) == 1 and matches[0].group(0) == obj:
                    placeholder = matches[0].group(1)
                    parts = placeholder.split('.')
                    
                    if len(parts) < 2:
                        return obj  # Invalid format
                    
                    namespace = parts[0]
                    key = '.'.join(parts[1:])
                    
                    if namespace in namespaces:
                        namespace_data = namespaces[namespace]
                        value = namespace_data
                        
                        # Handle nested keys
                        for part in key.split('.'):
                            if isinstance(value, dict) and part in value:
                                value = value[part]
                            else:
                                return obj  # Key not found, return original
                        
                        # Return value directly (not as JSON string)
                        return value
                
                # Multiple placeholders or placeholder within string - do string replacement
                def replace_placeholder_str(match):
                    placeholder = match.group(1).strip()
                    parts = placeholder.split('.')
                    
                    if len(parts) < 2:
                        return match.group(0)
                    
                    namespace = parts[0]
                    key = '.'.join(parts[1:])
                    
                    if namespace in namespaces:
                        namespace_data = namespaces[namespace]
                        value = namespace_data
                        
                        for part in key.split('.'):
                            if isinstance(value, dict) and part in value:
                                value = value[part]
                            else:
                                return match.group(0)
                        
                # Convert to string for string interpolation
                # IMPORTANT: When replacing in a JSON string context, we need to properly format values
                # Strings must be wrapped in quotes, numbers and booleans should not be
                if isinstance(value, (dict, list)):
                    return json.dumps(value, ensure_ascii=False)
                elif value is None:
                    return 'null'
                elif isinstance(value, bool):
                    return 'true' if value else 'false'
                elif isinstance(value, (int, float)):
                    return str(value)
                else:
                    # String value - must be wrapped in quotes and escaped
                    # Escape quotes and backslashes in the string
                    escaped_value = str(value).replace('\\', '\\\\').replace('"', '\\"')
                    return f'"{escaped_value}"'
                    
                    return match.group(0)
                
                # Replace placeholders in string
                replaced_str = re.sub(placeholder_pattern, replace_placeholder_str, obj)
                
                # If after replacement we have a JSON string, try to parse it
                # This handles cases where placeholders result in valid JSON
                replaced_str = replaced_str.strip()
                if (replaced_str.startswith('{') or replaced_str.startswith('[')) and len(matches) > 1:
                    try:
                        parsed = json.loads(replaced_str)
                        # If parsed successfully and it's a complex type, return it as object
                        if isinstance(parsed, (dict, list)):
                            return parsed
                    except json.JSONDecodeError:
                        pass
                
                return replaced_str
            else:
                return obj
        
        # Replace placeholders in the parsed JSON object
        result = replace_in_object(payload_obj)
        
        # Debug: log result type and content
        print(f"[PAYLOAD_TEMPLATE] Result type: {type(result)}, is dict: {isinstance(result, dict)}, keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        
        # Ensure result is a valid dict (not None, not empty string)
        if result is None:
            print(f"[PAYLOAD_TEMPLATE] Warning: Result is None for template: {original_template[:100] if 'original_template' in locals() else 'unknown'}...")
            return {}
        
        # If result is a string, try to parse as JSON first
        if isinstance(result, str):
            if not result.strip():
                print(f"[PAYLOAD_TEMPLATE] Warning: Result is empty string")
                return {}
            
            # Try to parse string as JSON
            result_stripped = result.strip()
            try:
                parsed = json.loads(result_stripped)
                # If successfully parsed, use the parsed object
                result = parsed
                print(f"[PAYLOAD_TEMPLATE] Successfully parsed string result as JSON")
            except json.JSONDecodeError:
                # If not valid JSON, check if it looks like a JSON string that failed
                # This can happen if placeholders weren't replaced properly
                print(f"[PAYLOAD_TEMPLATE] Result is non-JSON string: {result_stripped[:200]}")
                # Try to fix common JSON issues (unescaped quotes, etc.)
                # But don't wrap in {'raw': ...} - return empty dict instead to avoid sending stringified JSON
                return {}
        
        # Ensure it's a dict
        if not isinstance(result, dict):
            print(f"[PAYLOAD_TEMPLATE] Result is not dict, wrapping: {type(result)}")
            return {'value': result}
        
        # Check if result is empty dict
        if len(result) == 0:
            print(f"[PAYLOAD_TEMPLATE] Warning: Result is empty dict after processing")
            # Return original template structure if empty (better than nothing)
            return payload_obj if isinstance(payload_obj, dict) else {}
        
        return result
    
    except (json.JSONDecodeError, ValueError):
        # If template is not valid JSON, process as string template
        def replace_placeholder(match):
            placeholder = match.group(1)
            parts = placeholder.split('.')
            
            if len(parts) < 2:
                return match.group(0)
            
            namespace = parts[0]
            key = '.'.join(parts[1:])
            
            if namespace in namespaces:
                namespace_data = namespaces[namespace]
                value = namespace_data
                
                for part in key.split('.'):
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return match.group(0)
                
                # Convert to string for string template
                # IMPORTANT: When replacing in a JSON string context, we need to properly format values
                # Strings must be wrapped in quotes, numbers and booleans should not be
                if isinstance(value, (dict, list)):
                    return json.dumps(value, ensure_ascii=False)
                elif value is None:
                    return 'null'
                elif isinstance(value, bool):
                    return 'true' if value else 'false'
                elif isinstance(value, (int, float)):
                    return str(value)
                else:
                    # String value - must be wrapped in quotes and escaped
                    # Escape quotes and backslashes in the string
                    escaped_value = str(value).replace('\\', '\\\\').replace('"', '\\"')
                    return f'"{escaped_value}"'
            
            return match.group(0)
        
        pattern = r'\{\{([^}]+)\}\}'
        processed_str = re.sub(pattern, replace_placeholder, payload_str)
        
        # Try to parse as JSON
        processed_str = processed_str.strip()
        if not processed_str:
            return {}
        
        try:
            parsed = json.loads(processed_str)
            # Ensure we return a dict, not a string or other type
            if isinstance(parsed, dict):
                return parsed
            elif isinstance(parsed, str):
                # If parsed result is a string, wrap it
                return {'value': parsed}
            else:
                return {'value': parsed}
        except json.JSONDecodeError:
            # If still not valid JSON, check if it looks like JSON
            # If it starts with { or [, it might be malformed JSON - try to fix common issues
            if processed_str.startswith('{') or processed_str.startswith('['):
                # Try to parse with more lenient handling
                # Remove trailing commas, fix common issues
                try:
                    # Remove trailing commas before closing braces/brackets
                    import re as re_module
                    fixed = re_module.sub(r',(\s*[}\]])', r'\1', processed_str)
                    parsed = json.loads(fixed)
                    if isinstance(parsed, dict):
                        return parsed
                except:
                    pass
            
            # If it's not valid JSON and doesn't look like JSON, return empty dict
            # Don't wrap in {'raw': ...} to avoid sending stringified JSON
            print(f"[PAYLOAD_TEMPLATE] String template result is not valid JSON: {processed_str[:200]}")
            return {}


def get_template_examples() -> Dict[str, str]:
    """
    Get example payload templates with namespace placeholders
    
    Returns:
        Dictionary with example names and templates
    """
    return {
        'basic': {
            'name': 'Básico',
            'template': json.dumps({
                'comparison_id': '{{comparison.id}}',
                'project_id': '{{comparison.project_id}}',
                'total_differences': '{{comparison.total_differences}}',
                'status': '{{comparison.status}}'
            }, indent=2, ensure_ascii=False)
        },
        'difference_detail': {
            'name': 'Detalhe da Diferença',
            'template': json.dumps({
                'comparison': {
                    'id': '{{comparison.id}}',
                    'project_id': '{{comparison.project_id}}',
                    'executed_at': '{{comparison.executed_at}}',
                    'total_differences': '{{comparison.total_differences}}'
                },
                'difference': {
                    'id': '{{difference.id}}',
                    'record_id': '{{difference.record_id}}',
                    'field_name': '{{difference.field_name}}',
                    'source_value': '{{difference.source_value}}',
                    'target_value': '{{difference.target_value}}',
                    'change_type': '{{difference.change_type}}',
                    'detected_at': '{{difference.detected_at}}'
                }
            }, indent=2, ensure_ascii=False)
        },
        'webhook_notification': {
            'name': 'Notificação de Webhook',
            'template': json.dumps({
                'event': 'comparison.difference.detected',
                'timestamp': '{{difference.detected_at}}',
                'data': {
                    'comparison_id': '{{comparison.id}}',
                    'project_id': '{{comparison.project_id}}',
                    'record_id': '{{difference.record_id}}',
                    'field': '{{difference.field_name}}',
                    'old_value': '{{difference.source_value}}',
                    'new_value': '{{difference.target_value}}',
                    'change_type': '{{difference.change_type}}'
                }
            }, indent=2, ensure_ascii=False)
        }
    }

