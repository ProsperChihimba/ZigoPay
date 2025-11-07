"""
Wallet utility functions for auto-payment
"""
from datetime import datetime
import uuid
from apps.payments.models import Wallet, Payment, Transaction, ReleaseOrder
from apps.payments.services import PaymentGatewayService


def generate_release_code():
    """Generate unique release code"""
    return f"RO-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def process_auto_payment(invoice, user=None):
    """
    Process auto-payment from wallet if customer has auto-payment enabled
    Returns: (success: bool, message: str, data: dict)
    """
    try:
        customer = invoice.cargo.customer
        
        # Check if customer has wallet
        if not hasattr(customer, 'wallet'):
            return False, "Customer does not have a wallet", {}
        
        wallet = customer.wallet
        
        # Check if auto-payment is enabled
        if not wallet.auto_payment_enabled or not wallet.is_active:
            return False, "Auto-payment not enabled for this wallet", {}
        
        # Check if invoice is already paid
        if invoice.status == 'paid':
            return False, "Invoice already paid", {}
        
        amount = float(invoice.amount)
        
        # Check if wallet has sufficient balance
        if not wallet.has_sufficient_balance(amount):
            return False, f"Insufficient wallet balance. Required: ${amount}, Available: ${wallet.balance}", {
                'required': float(amount),
                'available': float(wallet.balance),
                'shortfall': float(amount - wallet.balance)
            }
        
        # Process payment from wallet
        balance_before = wallet.balance
        wallet.pay_invoice(invoice, amount, f"Auto-payment for invoice {invoice.control_number}")
        
        # Create payment record
        payment = Payment.objects.create(
            invoice=invoice,
            amount_paid=amount,
            payment_reference=f"WLT-AUTO-{uuid.uuid4().hex[:8].upper()}",
            payment_method='wallet',
            status='completed',
            processed_by=user,
            processed_at=datetime.now()
        )
        
        # Update wallet transaction with payment reference
        transaction = wallet.transactions.filter(
            invoice=invoice,
            transaction_type='payment'
        ).order_by('-created_at').first()
        if transaction:
            transaction.payment = payment
            transaction.transaction_type = 'auto_payment'
            transaction.save()
        
        # Update invoice
        invoice.status = 'paid'
        invoice.payment_method = 'wallet'
        invoice.save()
        
        # Create transaction record
        Transaction.objects.create(
            payment=payment,
            transaction_type='cargo_payment',
            amount=amount,
            currency='USD',
            status='success',
            reference=payment.payment_reference,
            created_by=user
        )
        
        # Generate release order
        release_order = ReleaseOrder.objects.create(
            cargo=invoice.cargo,
            payment=payment,
            release_code=generate_release_code(),
            status='active',
            generated_by=user
        )
        
        return True, "Auto-payment processed successfully", {
            'payment_id': payment.payment_id,
            'release_order_id': release_order.release_order_id,
            'release_code': release_order.release_code,
            'balance_before': float(balance_before),
            'balance_after': float(wallet.balance)
        }
    
    except Exception as e:
        return False, f"Auto-payment failed: {str(e)}", {}

