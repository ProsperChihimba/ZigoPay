"""
Payment Gateway Service (Dummy Implementation)
Replace with actual payment gateway integration later
"""
import uuid
from decimal import Decimal
from django.conf import settings


class PaymentGatewayService:
    """Dummy payment gateway service"""
    
    @staticmethod
    def process_deposit(amount, payment_method, customer_phone=None, customer_email=None):
        """
        Process deposit to wallet via payment gateway
        Returns: (success: bool, reference: str, gateway_response: dict)
        """
        # Dummy implementation - replace with actual gateway call
        reference = f"DEP-{uuid.uuid4().hex[:12].upper()}"
        
        # Simulate gateway response
        gateway_response = {
            "status": "success",
            "transaction_id": reference,
            "amount": str(amount),
            "payment_method": payment_method,
            "message": "Payment processed successfully (Dummy Gateway)",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        return True, reference, gateway_response
    
    @staticmethod
    def verify_payment(reference):
        """
        Verify payment status from gateway
        Returns: (verified: bool, gateway_response: dict)
        """
        # Dummy implementation
        gateway_response = {
            "status": "verified",
            "transaction_id": reference,
            "verified": True,
            "message": "Payment verified (Dummy Gateway)"
        }
        
        return True, gateway_response
    
    @staticmethod
    def process_refund(amount, original_reference):
        """
        Process refund via payment gateway
        Returns: (success: bool, reference: str, gateway_response: dict)
        """
        # Dummy implementation
        reference = f"REF-{uuid.uuid4().hex[:12].upper()}"
        
        gateway_response = {
            "status": "success",
            "refund_id": reference,
            "original_transaction": original_reference,
            "amount": str(amount),
            "message": "Refund processed successfully (Dummy Gateway)"
        }
        
        return True, reference, gateway_response

