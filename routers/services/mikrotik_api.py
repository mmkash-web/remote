"""
MikroTik API Service for connecting and managing MikroTik routers.
Uses librouteros library for API communication.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import socket

try:
    from librouteros import connect
    from librouteros.exceptions import TrapError, FatalError, ConnectionError as RouterOSConnectionError
except ImportError:
    # Fallback if librouteros is not installed
    connect = None
    TrapError = Exception
    FatalError = Exception
    RouterOSConnectionError = Exception

from django.conf import settings
from routers.models import RouterLog

logger = logging.getLogger(__name__)


class MikroTikAPIService:
    """
    Service class for interacting with MikroTik routers via API.
    """
    
    def __init__(self, router):
        """
        Initialize the API service with a router instance.
        
        Args:
            router: Router model instance
        """
        self.router = router
        self.connection = None
        self.timeout = getattr(settings, 'MIKROTIK_API_TIMEOUT', 10)
    
    def connect_router(self) -> Tuple[bool, str]:
        """
        Establish connection to the MikroTik router.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if connect is None:
            return False, "librouteros library is not installed"
        
        try:
            self.connection = connect(
                host=self.router.vpn_ip,
                username=self.router.username,
                password=self.router.password,
                port=self.router.api_port,
                timeout=self.timeout,
            )
            
            self.log_action('INFO', 'Connection established', 'Successfully connected to router')
            return True, "Connection successful"
            
        except (RouterOSConnectionError, socket.timeout, socket.error) as e:
            error_msg = f"Connection failed: {str(e)}"
            self.log_action('ERROR', 'Connection failed', error_msg)
            logger.error(f"Router {self.router.name}: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.log_action('ERROR', 'Connection error', error_msg)
            logger.error(f"Router {self.router.name}: {error_msg}")
            return False, error_msg
    
    def disconnect(self):
        """Close the router connection."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
            except Exception as e:
                logger.warning(f"Error closing connection: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        success, message = self.connect_router()
        if not success:
            raise Exception(message)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def check_status(self) -> Tuple[bool, Dict]:
        """
        Check router status and fetch system information.
        
        Returns:
            Tuple of (is_online: bool, info: dict)
        """
        success, message = self.connect_router()
        
        if not success:
            return False, {'error': message}
        
        try:
            # Get system resource information
            system_resource = self.connection.path('/system/resource')
            resource_data = list(system_resource)
            
            if resource_data:
                resource = resource_data[0]
                info = {
                    'version': resource.get('version', ''),
                    'platform': resource.get('platform', ''),
                    'board_name': resource.get('board-name', ''),
                    'uptime': resource.get('uptime', ''),
                    'cpu_load': resource.get('cpu-load', 0),
                    'free_memory': resource.get('free-memory', 0),
                    'total_memory': resource.get('total-memory', 0),
                }
            else:
                info = {}
            
            # Get system identity
            try:
                identity_path = self.connection.path('/system/identity')
                identity_data = list(identity_path)
                if identity_data:
                    info['identity'] = identity_data[0].get('name', '')
            except Exception:
                pass
            
            self.disconnect()
            return True, info
            
        except Exception as e:
            error_msg = f"Error fetching system info: {str(e)}"
            self.log_action('ERROR', 'Status check failed', error_msg)
            self.disconnect()
            return False, {'error': error_msg}
    
    def create_ppp_secret(self, username: str, password: str, profile: str, 
                          service: str = 'any') -> Tuple[bool, str]:
        """
        Create a PPP secret (user account) on the router.
        
        Args:
            username: Username for the account
            password: Password for the account
            profile: Profile name to assign
            service: Service type (default: 'any')
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        success, message = self.connect_router()
        if not success:
            return False, message
        
        try:
            ppp_secrets = self.connection.path('/ppp/secret')
            
            # Check if user already exists
            existing = list(ppp_secrets.select('name').where('.id', username))
            if existing:
                self.disconnect()
                return False, f"User {username} already exists on this router"
            
            # Add new secret
            ppp_secrets.add(
                name=username,
                password=password,
                profile=profile,
                service=service,
            )
            
            self.log_action('SUCCESS', 'User created', f"Created PPP secret for {username}")
            self.disconnect()
            return True, f"User {username} created successfully"
            
        except TrapError as e:
            error_msg = f"API error creating user: {str(e)}"
            self.log_action('ERROR', 'User creation failed', error_msg)
            self.disconnect()
            return False, error_msg
        except Exception as e:
            error_msg = f"Error creating user: {str(e)}"
            self.log_action('ERROR', 'User creation error', error_msg)
            self.disconnect()
            return False, error_msg
    
    def update_ppp_secret(self, username: str, **kwargs) -> Tuple[bool, str]:
        """
        Update an existing PPP secret.
        
        Args:
            username: Username to update
            **kwargs: Fields to update (password, profile, etc.)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        success, message = self.connect_router()
        if not success:
            return False, message
        
        try:
            ppp_secrets = self.connection.path('/ppp/secret')
            
            # Find the secret
            secrets = list(ppp_secrets.select('.id', 'name').where('name', username))
            if not secrets:
                self.disconnect()
                return False, f"User {username} not found on router"
            
            secret_id = secrets[0]['.id']
            
            # Update the secret
            ppp_secrets.update(**{'.id': secret_id, **kwargs})
            
            self.log_action('SUCCESS', 'User updated', f"Updated PPP secret for {username}")
            self.disconnect()
            return True, f"User {username} updated successfully"
            
        except Exception as e:
            error_msg = f"Error updating user: {str(e)}"
            self.log_action('ERROR', 'User update error', error_msg)
            self.disconnect()
            return False, error_msg
    
    def delete_ppp_secret(self, username: str) -> Tuple[bool, str]:
        """
        Delete a PPP secret from the router.
        
        Args:
            username: Username to delete
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        success, message = self.connect_router()
        if not success:
            return False, message
        
        try:
            ppp_secrets = self.connection.path('/ppp/secret')
            
            # Find and remove the secret
            secrets = list(ppp_secrets.select('.id', 'name').where('name', username))
            if not secrets:
                self.disconnect()
                return False, f"User {username} not found on router"
            
            secret_id = secrets[0]['.id']
            ppp_secrets.remove(secret_id)
            
            self.log_action('SUCCESS', 'User deleted', f"Deleted PPP secret for {username}")
            self.disconnect()
            return True, f"User {username} deleted successfully"
            
        except Exception as e:
            error_msg = f"Error deleting user: {str(e)}"
            self.log_action('ERROR', 'User deletion error', error_msg)
            self.disconnect()
            return False, error_msg
    
    def disable_ppp_secret(self, username: str) -> Tuple[bool, str]:
        """
        Disable a PPP secret (set disabled=yes).
        
        Args:
            username: Username to disable
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        return self.update_ppp_secret(username, disabled='yes')
    
    def enable_ppp_secret(self, username: str) -> Tuple[bool, str]:
        """
        Enable a PPP secret (set disabled=no).
        
        Args:
            username: Username to enable
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        return self.update_ppp_secret(username, disabled='no')
    
    def get_active_connections(self) -> Tuple[bool, List[Dict]]:
        """
        Get list of active PPP connections.
        
        Returns:
            Tuple of (success: bool, connections: list)
        """
        success, message = self.connect_router()
        if not success:
            return False, []
        
        try:
            ppp_active = self.connection.path('/ppp/active')
            connections = []
            
            for conn in ppp_active:
                connections.append({
                    'name': conn.get('name', ''),
                    'address': conn.get('address', ''),
                    'uptime': conn.get('uptime', ''),
                    'caller_id': conn.get('caller-id', ''),
                    'service': conn.get('service', ''),
                })
            
            self.disconnect()
            return True, connections
            
        except Exception as e:
            error_msg = f"Error fetching active connections: {str(e)}"
            self.log_action('ERROR', 'Active connections fetch error', error_msg)
            self.disconnect()
            return False, []
    
    def get_all_ppp_secrets(self) -> Tuple[bool, List[Dict]]:
        """
        Get all PPP secrets from the router.
        
        Returns:
            Tuple of (success: bool, secrets: list)
        """
        success, message = self.connect_router()
        if not success:
            return False, []
        
        try:
            ppp_secrets = self.connection.path('/ppp/secret')
            secrets = []
            
            for secret in ppp_secrets:
                secrets.append({
                    'name': secret.get('name', ''),
                    'profile': secret.get('profile', ''),
                    'service': secret.get('service', ''),
                    'disabled': secret.get('disabled', 'no') == 'yes',
                })
            
            self.disconnect()
            return True, secrets
            
        except Exception as e:
            error_msg = f"Error fetching PPP secrets: {str(e)}"
            self.log_action('ERROR', 'PPP secrets fetch error', error_msg)
            self.disconnect()
            return False, []
    
    def create_ppp_profile(self, name: str, local_address: str, 
                          remote_address: str, rate_limit: str = '') -> Tuple[bool, str]:
        """
        Create a PPP profile on the router.
        
        Args:
            name: Profile name
            local_address: Local IP address/pool
            remote_address: Remote IP address/pool
            rate_limit: Bandwidth limitation (e.g., "5M/5M")
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        success, message = self.connect_router()
        if not success:
            return False, message
        
        try:
            ppp_profiles = self.connection.path('/ppp/profile')
            
            # Check if profile exists
            existing = list(ppp_profiles.select('name').where('name', name))
            if existing:
                self.disconnect()
                return False, f"Profile {name} already exists"
            
            # Create profile
            profile_data = {
                'name': name,
                'local-address': local_address,
                'remote-address': remote_address,
            }
            
            if rate_limit:
                profile_data['rate-limit'] = rate_limit
            
            ppp_profiles.add(**profile_data)
            
            self.log_action('SUCCESS', 'Profile created', f"Created PPP profile {name}")
            self.disconnect()
            return True, f"Profile {name} created successfully"
            
        except Exception as e:
            error_msg = f"Error creating profile: {str(e)}"
            self.log_action('ERROR', 'Profile creation error', error_msg)
            self.disconnect()
            return False, error_msg
    
    def log_action(self, log_type: str, action: str, message: str, details: Dict = None):
        """
        Log an action to the RouterLog model.
        
        Args:
            log_type: Type of log (INFO, WARNING, ERROR, SUCCESS)
            action: Action description
            message: Log message
            details: Additional details as dict
        """
        try:
            RouterLog.objects.create(
                router=self.router,
                log_type=log_type,
                action=action,
                message=message,
                details=details,
            )
        except Exception as e:
            logger.error(f"Failed to create router log: {str(e)}")

