from flask import Blueprint, request, jsonify
from app.models.webhook_config import WebhookConfig, WebhookPayload, WebhookParams
from app import db
from app.utils.security import token_required
from app.utils.encryption import PasswordEncryption
import requests
import json
from datetime import datetime

webhooks_bp = Blueprint('webhooks', __name__)


@webhooks_bp.route('/configs', methods=['GET'])
@token_required
def list_webhook_configs(user):
    """List all webhook configurations for the user"""
    try:
        configs = WebhookConfig.query.filter_by(user_id=user.id).order_by(WebhookConfig.created_at.desc()).all()
        return jsonify({
            'configs': [config.to_dict() for config in configs]
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error listing webhook configs: {str(e)}'}), 500


@webhooks_bp.route('/configs/<int:config_id>', methods=['GET'])
@token_required
def get_webhook_config(user, config_id):
    """Get a specific webhook configuration"""
    config = WebhookConfig.query.filter_by(id=config_id, user_id=user.id).first()
    
    if not config:
        return jsonify({'message': 'Webhook config not found'}), 404
    
    # Return with decrypted credentials since user owns this config
    return jsonify(config.to_dict_with_credentials()), 200


@webhooks_bp.route('/configs', methods=['POST'])
@token_required
def create_webhook_config(user):
    """Create a new webhook configuration"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    required_fields = ['name', 'url', 'method']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    try:
        # Encrypt sensitive auth data
        auth_config = data.get('auth_config', {}).copy() if data.get('auth_config') else {}
        auth_type = data.get('auth_type', 'none')
        
        if auth_type == 'bearer' and 'token' in auth_config:
            token = auth_config.get('token', '')
            if token and token != '***':
                auth_config['token'] = PasswordEncryption.encrypt_password(token)
        elif auth_type == 'basic':
            password = auth_config.get('password', '')
            if password and password != '***':
                auth_config['password'] = PasswordEncryption.encrypt_password(password)
        elif auth_type == 'api_key':
            key_value = auth_config.get('key_value', '')
            if key_value and key_value != '***':
                auth_config['key_value'] = PasswordEncryption.encrypt_password(key_value)
        
        config = WebhookConfig(
            name=data['name'],
            description=data.get('description', ''),
            url=data['url'],
            method=data['method'].upper(),
            headers=data.get('headers', {}),
            auth_type=auth_type,
            auth_config=auth_config,
            default_payload=data.get('default_payload', ''),
            is_active=data.get('is_active', True),
            user_id=user.id
        )
        
        db.session.add(config)
        db.session.commit()
        
        return jsonify({
            'message': 'Webhook config created successfully',
            'config': config.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating webhook config: {str(e)}'}), 500


@webhooks_bp.route('/configs/<int:config_id>', methods=['PUT'])
@token_required
def update_webhook_config(user, config_id):
    """Update a webhook configuration"""
    config = WebhookConfig.query.filter_by(id=config_id, user_id=user.id).first()
    
    if not config:
        return jsonify({'message': 'Webhook config not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    try:
        if 'name' in data:
            config.name = data['name']
        if 'description' in data:
            config.description = data['description']
        if 'url' in data:
            config.url = data['url']
        if 'method' in data:
            config.method = data['method'].upper()
        if 'headers' in data:
            config.headers = data['headers']
        if 'auth_type' in data:
            config.auth_type = data['auth_type']
        if 'default_payload' in data:
            config.default_payload = data.get('default_payload', '')
        if 'auth_config' in data:
            new_auth_config = data['auth_config'].copy()
            auth_type = data.get('auth_type', config.auth_type)
            
            # Get existing decrypted config once for efficiency
            existing_decrypted = config.get_decrypted_auth_config() if config.auth_config else {}
            
            # Encrypt sensitive data, preserving existing if not provided
            if auth_type == 'bearer':
                token = new_auth_config.get('token', '')
                if token and token != '***' and token != '':
                    # Encrypt new token
                    new_auth_config['token'] = PasswordEncryption.encrypt_password(token)
                elif not token or token == '':
                    # Preserve existing token if not provided
                    if existing_decrypted and existing_decrypted.get('token'):
                        # Re-encrypt existing token
                        new_auth_config['token'] = PasswordEncryption.encrypt_password(existing_decrypted['token'])
                    elif config.auth_config and config.auth_config.get('token'):
                        # Keep existing encrypted token if decryption failed
                        new_auth_config['token'] = config.auth_config['token']
            elif auth_type == 'basic':
                password = new_auth_config.get('password', '')
                username = new_auth_config.get('username', '')
                if password and password != '***' and password != '':
                    # Encrypt new password
                    new_auth_config['password'] = PasswordEncryption.encrypt_password(password)
                elif not password or password == '':
                    # Preserve existing password if not provided
                    if existing_decrypted and existing_decrypted.get('password'):
                        # Re-encrypt existing password
                        new_auth_config['password'] = PasswordEncryption.encrypt_password(existing_decrypted['password'])
                    elif config.auth_config and config.auth_config.get('password'):
                        # Keep existing encrypted password if decryption failed
                        new_auth_config['password'] = config.auth_config['password']
                if not username or username == '':
                    # Preserve existing username if not provided
                    if existing_decrypted and existing_decrypted.get('username'):
                        new_auth_config['username'] = existing_decrypted['username']
                    elif config.auth_config and config.auth_config.get('username'):
                        new_auth_config['username'] = config.auth_config['username']
            elif auth_type == 'api_key':
                key_value = new_auth_config.get('key_value', '')
                key_name = new_auth_config.get('key_name', '')
                if key_value and key_value != '***' and key_value != '':
                    # Encrypt new key value
                    new_auth_config['key_value'] = PasswordEncryption.encrypt_password(key_value)
                elif not key_value or key_value == '':
                    # Preserve existing key value if not provided
                    if existing_decrypted and existing_decrypted.get('key_value'):
                        # Re-encrypt existing key value
                        new_auth_config['key_value'] = PasswordEncryption.encrypt_password(existing_decrypted['key_value'])
                    elif config.auth_config and config.auth_config.get('key_value'):
                        # Keep existing encrypted key value if decryption failed
                        new_auth_config['key_value'] = config.auth_config['key_value']
                if not key_name or key_name == '':
                    # Preserve existing key name if not provided
                    if existing_decrypted and existing_decrypted.get('key_name'):
                        new_auth_config['key_name'] = existing_decrypted['key_name']
                    elif config.auth_config and config.auth_config.get('key_name'):
                        new_auth_config['key_name'] = config.auth_config['key_name']
            
            config.auth_config = new_auth_config
        if 'is_active' in data:
            config.is_active = data['is_active']
        
        config.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Webhook config updated successfully',
            'config': config.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating webhook config: {str(e)}'}), 500


@webhooks_bp.route('/configs/<int:config_id>', methods=['DELETE'])
@token_required
def delete_webhook_config(user, config_id):
    """Delete a webhook configuration"""
    config = WebhookConfig.query.filter_by(id=config_id, user_id=user.id).first()
    
    if not config:
        return jsonify({'message': 'Webhook config not found'}), 404
    
    try:
        db.session.delete(config)
        db.session.commit()
        
        return jsonify({'message': 'Webhook config deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting webhook config: {str(e)}'}), 500


@webhooks_bp.route('/configs/<int:config_id>/test', methods=['POST'])
@token_required
def test_webhook_config(user, config_id):
    """Test a webhook configuration by sending a test request"""
    config = WebhookConfig.query.filter_by(id=config_id, user_id=user.id).first()
    
    if not config:
        return jsonify({'message': 'Webhook config not found'}), 404
    
    if not config.is_active:
        return jsonify({'message': 'Webhook config is not active'}), 400
    
    data = request.get_json() or {}
    test_payload = data.get('payload', {})
    
    try:
        # Prepare headers
        headers = config.headers.copy() if config.headers else {}
        headers.setdefault('Content-Type', 'application/json')
        
        # Add authentication (use decrypted config)
        decrypted_auth = config.get_decrypted_auth_config()
        if config.auth_type == 'bearer' and decrypted_auth:
            token = decrypted_auth.get('token', '')
            if token:
                headers['Authorization'] = f'Bearer {token}'
        elif config.auth_type == 'api_key' and decrypted_auth:
            key_name = decrypted_auth.get('key_name', 'X-API-Key')
            key_value = decrypted_auth.get('key_value', '')
            if key_value:
                headers[key_name] = key_value
        elif config.auth_type == 'basic' and decrypted_auth:
            import base64
            username = decrypted_auth.get('username', '')
            password = decrypted_auth.get('password', '')
            if username and password:
                credentials = base64.b64encode(f'{username}:{password}'.encode()).decode()
                headers['Authorization'] = f'Basic {credentials}'
        
        # Send request
        response = requests.request(
            method=config.method,
            url=config.url,
            headers=headers,
            json=test_payload if config.method in ['POST', 'PUT', 'PATCH'] else None,
            params=test_payload if config.method in ['GET', 'DELETE'] else None,
            timeout=30
        )
        
        return jsonify({
            'message': 'Test request sent',
            'status_code': response.status_code,
            'response': response.text[:1000],  # Limit response size
            'headers': dict(response.headers)
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error testing webhook: {str(e)}'}), 500


@webhooks_bp.route('/payloads', methods=['GET'])
@token_required
def list_webhook_payloads(user):
    """List all webhook payload templates for the user"""
    try:
        payloads = WebhookPayload.query.filter_by(user_id=user.id).order_by(WebhookPayload.created_at.desc()).all()
        return jsonify({
            'payloads': [payload.to_dict() for payload in payloads]
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error listing webhook payloads: {str(e)}'}), 500


@webhooks_bp.route('/payloads/<int:payload_id>', methods=['GET'])
@token_required
def get_webhook_payload(user, payload_id):
    """Get a specific webhook payload template"""
    payload = WebhookPayload.query.filter_by(id=payload_id, user_id=user.id).first()
    
    if not payload:
        return jsonify({'message': 'Webhook payload not found'}), 404
    
    return jsonify(payload.to_dict()), 200


@webhooks_bp.route('/payloads', methods=['POST'])
@token_required
def create_webhook_payload(user):
    """Create a new webhook payload template"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    required_fields = ['name', 'payload_template']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # Validate JSON
    try:
        json.loads(data['payload_template'])
    except json.JSONDecodeError:
        return jsonify({'message': 'Invalid JSON in payload_template'}), 400
    
    if 'payload_example' in data and data['payload_example']:
        try:
            json.loads(data['payload_example'])
        except json.JSONDecodeError:
            return jsonify({'message': 'Invalid JSON in payload_example'}), 400
    
    try:
        payload = WebhookPayload(
            name=data['name'],
            description=data.get('description', ''),
            payload_template=data['payload_template'],
            payload_example=data.get('payload_example', ''),
            user_id=user.id
        )
        
        db.session.add(payload)
        db.session.commit()
        
        return jsonify({
            'message': 'Webhook payload created successfully',
            'payload': payload.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating webhook payload: {str(e)}'}), 500


@webhooks_bp.route('/payloads/<int:payload_id>', methods=['PUT'])
@token_required
def update_webhook_payload(user, payload_id):
    """Update a webhook payload template"""
    payload = WebhookPayload.query.filter_by(id=payload_id, user_id=user.id).first()
    
    if not payload:
        return jsonify({'message': 'Webhook payload not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    # Validate JSON if provided
    if 'payload_template' in data:
        try:
            json.loads(data['payload_template'])
        except json.JSONDecodeError:
            return jsonify({'message': 'Invalid JSON in payload_template'}), 400
    
    if 'payload_example' in data and data['payload_example']:
        try:
            json.loads(data['payload_example'])
        except json.JSONDecodeError:
            return jsonify({'message': 'Invalid JSON in payload_example'}), 400
    
    try:
        if 'name' in data:
            payload.name = data['name']
        if 'description' in data:
            payload.description = data['description']
        if 'payload_template' in data:
            payload.payload_template = data['payload_template']
        if 'payload_example' in data:
            payload.payload_example = data['payload_example']
        
        payload.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Webhook payload updated successfully',
            'payload': payload.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating webhook payload: {str(e)}'}), 500


@webhooks_bp.route('/payloads/<int:payload_id>', methods=['DELETE'])
@token_required
def delete_webhook_payload(user, payload_id):
    """Delete a webhook payload template"""
    payload = WebhookPayload.query.filter_by(id=payload_id, user_id=user.id).first()
    
    if not payload:
        return jsonify({'message': 'Webhook payload not found'}), 404
    
    try:
        db.session.delete(payload)
        db.session.commit()
        
        return jsonify({'message': 'Webhook payload deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting webhook payload: {str(e)}'}), 500


@webhooks_bp.route('/send', methods=['POST'])
@token_required
def send_webhook(user):
    """Send a webhook request manually"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    required_fields = ['url', 'method']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    try:
        # Prepare headers
        headers = data.get('headers', {})
        headers.setdefault('Content-Type', 'application/json')
        
        # Prepare payload - process template if it's a string with placeholders
        payload = data.get('payload', {})
        
        # If payload is a string (template), try to process it
        if isinstance(payload, str):
            from app.utils.payload_template import process_payload_template
            # For manual sends, use empty context (placeholders won't be replaced)
            # User can test with actual values later
            try:
                payload = process_payload_template(payload)
            except:
                # If processing fails, use as-is
                pass
        
        # Send request
        response = requests.request(
            method=data['method'].upper(),
            url=data['url'],
            headers=headers,
            json=payload if data['method'].upper() in ['POST', 'PUT', 'PATCH'] else None,
            params=payload if data['method'].upper() in ['GET', 'DELETE'] else None,
            timeout=30
        )
        
        return jsonify({
            'message': 'Request sent successfully',
            'status_code': response.status_code,
            'response': response.text[:5000],  # Limit response size
            'headers': dict(response.headers)
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error sending webhook: {str(e)}'}), 500


@webhooks_bp.route('/process-template', methods=['POST'])
@token_required
def process_template(user):
    """Process a payload template with provided data"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    if 'template' not in data:
        return jsonify({'message': 'Missing template field'}), 400
    
    try:
        from app.utils.payload_template import process_payload_template
        
        template = data['template']
        comparison = data.get('comparison')
        difference = data.get('difference')
        project = data.get('project')
        
        processed = process_payload_template(
            template=template,
            comparison=comparison,
            difference=difference,
            project=project
        )
        
        return jsonify({
            'processed': processed
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error processing template: {str(e)}'}), 500


# Webhook Parameters Routes
@webhooks_bp.route('/params', methods=['GET'])
@token_required
def list_webhook_params(user):
    """List all webhook parameter templates for the user"""
    try:
        params = WebhookParams.query.filter_by(user_id=user.id).order_by(WebhookParams.created_at.desc()).all()
        return jsonify({
            'params': [param.to_dict() for param in params]
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error listing webhook params: {str(e)}'}), 500


@webhooks_bp.route('/params/<int:param_id>', methods=['GET'])
@token_required
def get_webhook_params(user, param_id):
    """Get a specific webhook parameter template"""
    param = WebhookParams.query.filter_by(id=param_id, user_id=user.id).first()
    
    if not param:
        return jsonify({'message': 'Webhook params not found'}), 404
    
    return jsonify(param.to_dict()), 200


@webhooks_bp.route('/params', methods=['POST'])
@token_required
def create_webhook_params(user):
    """Create a new webhook parameter template"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    required_fields = ['name', 'params_template']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # Validate JSON
    try:
        json.loads(data['params_template'])
    except json.JSONDecodeError:
        return jsonify({'message': 'Invalid JSON in params_template'}), 400
    
    if 'params_example' in data and data['params_example']:
        try:
            json.loads(data['params_example'])
        except json.JSONDecodeError:
            return jsonify({'message': 'Invalid JSON in params_example'}), 400
    
    try:
        param = WebhookParams(
            name=data['name'],
            description=data.get('description', ''),
            params_template=data['params_template'],
            params_example=data.get('params_example', ''),
            user_id=user.id
        )
        
        db.session.add(param)
        db.session.commit()
        
        return jsonify({
            'message': 'Webhook params created successfully',
            'params': param.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating webhook params: {str(e)}'}), 500


@webhooks_bp.route('/params/<int:param_id>', methods=['PUT'])
@token_required
def update_webhook_params(user, param_id):
    """Update a webhook parameter template"""
    param = WebhookParams.query.filter_by(id=param_id, user_id=user.id).first()
    
    if not param:
        return jsonify({'message': 'Webhook params not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    # Validate JSON if provided
    if 'params_template' in data:
        try:
            json.loads(data['params_template'])
        except json.JSONDecodeError:
            return jsonify({'message': 'Invalid JSON in params_template'}), 400
    
    if 'params_example' in data and data['params_example']:
        try:
            json.loads(data['params_example'])
        except json.JSONDecodeError:
            return jsonify({'message': 'Invalid JSON in params_example'}), 400
    
    try:
        if 'name' in data:
            param.name = data['name']
        if 'description' in data:
            param.description = data['description']
        if 'params_template' in data:
            param.params_template = data['params_template']
        if 'params_example' in data:
            param.params_example = data['params_example']
        
        param.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Webhook params updated successfully',
            'params': param.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating webhook params: {str(e)}'}), 500


@webhooks_bp.route('/params/<int:param_id>', methods=['DELETE'])
@token_required
def delete_webhook_params(user, param_id):
    """Delete a webhook parameter template"""
    param = WebhookParams.query.filter_by(id=param_id, user_id=user.id).first()
    
    if not param:
        return jsonify({'message': 'Webhook params not found'}), 404
    
    try:
        db.session.delete(param)
        db.session.commit()
        
        return jsonify({'message': 'Webhook params deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting webhook params: {str(e)}'}), 500

