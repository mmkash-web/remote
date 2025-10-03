"""
API views for payment callbacks and integrations.
"""
import json
import logging
from decimal import Decimal

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Payment, PaymentGatewayLog
from customers.models import Customer
from core.models import Notification, ActivityLog

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
@require_POST
def payment_callback(request):
    """
    Generic payment callback endpoint.
    This can be used by any payment gateway that sends JSON data.
    
    Expected JSON format:
    {
        "transaction_id": "ABC123XYZ",
        "customer_username": "customer1",
        "amount": 50.00,
        "currency": "KES",
        "status": "success",
        "reference": "Optional reference",
        "payment_method": "MPESA"
    }
    """
    try:
        # Parse JSON data
        data = json.loads(request.body)
        
        # Log the callback
        PaymentGatewayLog.objects.create(
            log_type='CALLBACK',
            gateway='GENERIC',
            request_data=data,
            message='Received payment callback',
            ip_address=get_client_ip(request),
        )
        
        # Extract required fields
        transaction_id = data.get('transaction_id')
        customer_username = data.get('customer_username')
        amount = Decimal(str(data.get('amount', 0)))
        currency = data.get('currency', 'KES')
        status = data.get('status', '').lower()
        reference = data.get('reference', '')
        payment_method = data.get('payment_method', 'OTHER')
        
        # Validate required fields
        if not all([transaction_id, customer_username, amount]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields: transaction_id, customer_username, or amount'
            }, status=400)
        
        # Find customer
        try:
            customer = Customer.objects.get(username=customer_username)
        except Customer.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'Customer {customer_username} not found'
            }, status=404)
        
        # Check if transaction already exists
        if Payment.objects.filter(transaction_id=transaction_id).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Transaction already processed'
            }, status=400)
        
        # Create payment record
        payment = Payment.objects.create(
            customer=customer,
            profile=customer.profile,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            transaction_id=transaction_id,
            reference_code=reference,
            gateway_response=data,
        )
        
        # Update gateway log with payment reference
        PaymentGatewayLog.objects.filter(
            log_type='CALLBACK',
            gateway='GENERIC',
            payment__isnull=True
        ).order_by('-created_at').first().payment = payment
        
        # Process based on status
        if status in ['success', 'completed', 'paid']:
            payment.mark_completed(transaction_id=transaction_id)
            
            # Log activity
            ActivityLog.objects.create(
                action='PAYMENT',
                model_name='Payment',
                description=f"Payment received via callback for {customer_username}: {currency} {amount}",
                ip_address=get_client_ip(request),
            )
            
            # Send notification
            if customer.created_by:
                Notification.objects.create(
                    user=customer.created_by,
                    title='Payment Received',
                    message=f"Payment of {currency} {amount} received for {customer_username}",
                    notification_type='SUCCESS',
                    link=f'/payments/{payment.id}/'
                )
            
            logger.info(f"Payment completed: {transaction_id} for {customer_username}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Payment processed successfully',
                'customer': customer_username,
                'expires_at': customer.expires_at.isoformat() if customer.expires_at else None,
            })
        else:
            payment.mark_failed(f"Payment status: {status}")
            
            logger.warning(f"Payment failed: {transaction_id} for {customer_username}")
            
            return JsonResponse({
                'status': 'failed',
                'message': 'Payment failed',
            })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    
    except Exception as e:
        logger.error(f"Error processing payment callback: {str(e)}")
        
        PaymentGatewayLog.objects.create(
            log_type='ERROR',
            gateway='GENERIC',
            message=f"Error processing callback: {str(e)}",
            ip_address=get_client_ip(request),
        )
        
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)


@csrf_exempt
@require_POST
def mpesa_callback(request):
    """
    M-Pesa specific callback endpoint.
    Handles M-Pesa STK Push and C2B callbacks.
    
    M-Pesa sends data in their specific format - this is a simplified handler.
    """
    try:
        data = json.loads(request.body)
        
        # Log the callback
        PaymentGatewayLog.objects.create(
            log_type='CALLBACK',
            gateway='MPESA',
            request_data=data,
            message='Received M-Pesa callback',
            ip_address=get_client_ip(request),
        )
        
        # Extract M-Pesa specific fields
        # This is simplified - actual M-Pesa callback structure is more complex
        result_code = data.get('ResultCode', 1)
        transaction_id = data.get('TransactionID') or data.get('MpesaReceiptNumber')
        amount = data.get('Amount', 0)
        phone_number = data.get('PhoneNumber', '')
        
        if result_code == 0:  # Success
            # Try to find customer by phone number
            try:
                customer = Customer.objects.get(phone_number=phone_number)
                
                # Create and complete payment
                payment = Payment.objects.create(
                    customer=customer,
                    profile=customer.profile,
                    amount=amount,
                    currency='KES',
                    payment_method='MPESA',
                    transaction_id=transaction_id,
                    gateway_response=data,
                )
                
                payment.mark_completed(transaction_id=transaction_id)
                
                logger.info(f"M-Pesa payment completed: {transaction_id}")
                
                return JsonResponse({
                    'ResultCode': 0,
                    'ResultDesc': 'Success'
                })
            
            except Customer.DoesNotExist:
                logger.warning(f"Customer not found for phone: {phone_number}")
                return JsonResponse({
                    'ResultCode': 1,
                    'ResultDesc': 'Customer not found'
                })
        
        return JsonResponse({
            'ResultCode': result_code,
            'ResultDesc': 'Payment processed'
        })
    
    except Exception as e:
        logger.error(f"Error processing M-Pesa callback: {str(e)}")
        return JsonResponse({
            'ResultCode': 1,
            'ResultDesc': 'Error processing callback'
        }, status=500)


@csrf_exempt
@require_POST
def paypal_callback(request):
    """
    PayPal IPN (Instant Payment Notification) callback endpoint.
    """
    try:
        data = json.loads(request.body)
        
        # Log the callback
        PaymentGatewayLog.objects.create(
            log_type='CALLBACK',
            gateway='PAYPAL',
            request_data=data,
            message='Received PayPal callback',
            ip_address=get_client_ip(request),
        )
        
        # Extract PayPal specific fields
        payment_status = data.get('payment_status', '').lower()
        transaction_id = data.get('txn_id')
        amount = Decimal(str(data.get('mc_gross', 0)))
        custom = data.get('custom', '')  # Customer username passed in custom field
        
        if payment_status == 'completed':
            try:
                customer = Customer.objects.get(username=custom)
                
                # Check for duplicate
                if not Payment.objects.filter(transaction_id=transaction_id).exists():
                    payment = Payment.objects.create(
                        customer=customer,
                        profile=customer.profile,
                        amount=amount,
                        currency=data.get('mc_currency', 'USD'),
                        payment_method='PAYPAL',
                        transaction_id=transaction_id,
                        gateway_response=data,
                    )
                    
                    payment.mark_completed(transaction_id=transaction_id)
                    
                    logger.info(f"PayPal payment completed: {transaction_id}")
                
                return JsonResponse({'status': 'success'})
            
            except Customer.DoesNotExist:
                logger.warning(f"Customer not found: {custom}")
                return JsonResponse({'status': 'error', 'message': 'Customer not found'})
        
        return JsonResponse({'status': 'received'})
    
    except Exception as e:
        logger.error(f"Error processing PayPal callback: {str(e)}")
        return JsonResponse({'status': 'error'}, status=500)


@csrf_exempt
@require_POST
def initiate_payment(request):
    """
    API endpoint for initiating a payment (for customer self-service portal).
    Creates a pending payment record and returns payment instructions.
    """
    try:
        data = json.loads(request.body)
        
        customer_username = data.get('customer_username')
        payment_method = data.get('payment_method', 'MPESA')
        
        # Find customer
        try:
            customer = Customer.objects.get(username=customer_username)
        except Customer.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Customer not found'
            }, status=404)
        
        # Create pending payment
        payment = Payment.objects.create(
            customer=customer,
            profile=customer.profile,
            amount=customer.profile.price,
            currency=customer.profile.currency,
            payment_method=payment_method,
            status='PENDING',
        )
        
        # Return payment instructions based on method
        instructions = {
            'payment_id': str(payment.id),
            'amount': float(payment.amount),
            'currency': payment.currency,
            'customer': customer_username,
        }
        
        if payment_method == 'MPESA':
            instructions['instructions'] = (
                f"Send {payment.currency} {payment.amount} to Paybill 174379, "
                f"Account: {customer_username}"
            )
        elif payment_method == 'PAYPAL':
            instructions['paypal_email'] = 'payments@example.com'
            instructions['instructions'] = 'Pay via PayPal using the provided email'
        
        return JsonResponse({
            'status': 'success',
            'payment': instructions
        })
    
    except Exception as e:
        logger.error(f"Error initiating payment: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)

