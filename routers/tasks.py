"""
Celery tasks for router management.
"""
from celery import shared_task
from django.utils import timezone
from .models import Router
from .services.mikrotik_api import MikroTikAPIService
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_router_status(router_id):
    """
    Check the status of a specific router.
    
    Args:
        router_id: UUID of the router to check
    """
    try:
        router = Router.objects.get(id=router_id, is_active=True)
        api_service = MikroTikAPIService(router)
        is_online, info = api_service.check_status()
        
        if is_online:
            router.update_status('ONLINE')
            
            # Update router information
            if 'version' in info:
                router.router_version = info['version']
            if 'board_name' in info:
                router.router_model = info['board_name']
            if 'identity' in info:
                router.router_identity = info['identity']
            
            router.save()
            logger.info(f"Router {router.name} is online")
        else:
            router.update_status('OFFLINE')
            logger.warning(f"Router {router.name} is offline: {info.get('error', 'Unknown')}")
        
        return {'router': router.name, 'status': router.status}
        
    except Router.DoesNotExist:
        logger.error(f"Router with ID {router_id} not found")
        return {'error': 'Router not found'}
    except Exception as e:
        logger.error(f"Error checking router status: {str(e)}")
        return {'error': str(e)}


@shared_task
def check_all_routers_status():
    """
    Check the status of all active routers.
    This task is scheduled to run periodically.
    """
    active_routers = Router.objects.filter(is_active=True)
    results = []
    
    for router in active_routers:
        result = check_router_status.delay(str(router.id))
        results.append({
            'router': router.name,
            'task_id': result.id
        })
    
    logger.info(f"Initiated status check for {len(results)} routers")
    return results


@shared_task
def sync_router_users(router_id):
    """
    Synchronize users between database and router.
    Fetches all PPP secrets from router and updates local statistics.
    
    Args:
        router_id: UUID of the router
    """
    try:
        router = Router.objects.get(id=router_id, is_active=True)
        api_service = MikroTikAPIService(router)
        
        success, secrets = api_service.get_all_ppp_secrets()
        
        if success:
            router.total_users = len(secrets)
            router.save()
            logger.info(f"Synced {len(secrets)} users for router {router.name}")
            return {'router': router.name, 'user_count': len(secrets)}
        else:
            logger.error(f"Failed to sync users for router {router.name}")
            return {'error': 'Failed to fetch users'}
            
    except Router.DoesNotExist:
        logger.error(f"Router with ID {router_id} not found")
        return {'error': 'Router not found'}
    except Exception as e:
        logger.error(f"Error syncing router users: {str(e)}")
        return {'error': str(e)}

