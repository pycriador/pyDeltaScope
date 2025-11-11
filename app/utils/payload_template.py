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
    project: Optional[Dict[str, Any]] = None
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
    
    try:
        # Parse template as JSON
        payload = json.loads(template)
    except json.JSONDecodeError:
        # If not valid JSON, try to process as string
        payload_str = template
    else:
        # Convert back to string for processing
        payload_str = json.dumps(payload)
    
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
    
    if project:
        namespaces['project'] = {
            'id': project.get('id', ''),
            'name': project.get('name', ''),
            'description': project.get('description', ''),
            'source_table': project.get('source_table', ''),
            'target_table': project.get('target_table', '')
        }
    
    # Replace placeholders using regex
    def replace_placeholder(match):
        placeholder = match.group(1)  # Get content inside {{ }}
        parts = placeholder.split('.')
        
        if len(parts) < 2:
            return match.group(0)  # Return original if invalid format
        
        namespace = parts[0]
        key = '.'.join(parts[1:])  # Support nested keys like metadata.something
        
        if namespace in namespaces:
            namespace_data = namespaces[namespace]
            
            # Handle nested keys
            value = namespace_data
            for part in key.split('.'):
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return match.group(0)  # Return original if key not found
            
            # Convert to JSON string if complex type
            if isinstance(value, (dict, list)):
                return json.dumps(value)
            elif value is None:
                return 'null'
            else:
                return str(value)
        
        return match.group(0)  # Return original if namespace not found
    
    # Pattern to match {{namespace.key}} or {{namespace.nested.key}}
    pattern = r'\{\{([^}]+)\}\}'
    processed_str = re.sub(pattern, replace_placeholder, payload_str)
    
    # Parse back to JSON
    try:
        return json.loads(processed_str)
    except json.JSONDecodeError:
        # If parsing fails, return as string
        return {'raw': processed_str}


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

