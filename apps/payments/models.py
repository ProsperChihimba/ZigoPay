from django.db import models
from apps.core.models import TimestampedModel


class Payment(TimestampedModel):
    payment_id = models.AutoField(primary_key=True)
    invoice = models.ForeignKey('invoices.Invoice', on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=50, choices=[
        ('mobile_money', 'Mobile Money'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('wallet', 'Wallet'),
    ])
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    processed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='processed_payments')
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Payment {self.payment_reference} - ${self.amount_paid}"


class Transaction(TimestampedModel):
    transaction_id = models.AutoField(primary_key=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=50, choices=[
        ('cargo_payment', 'Cargo Payment'),
        ('storage_fee', 'Storage Fee'),
        ('refund', 'Refund'),
        ('penalty', 'Penalty'),
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('failed', 'Failed'),
    ])
    reference = models.CharField(max_length=100)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='transactions')
    transaction_details = models.JSONField(blank=True, null=True, help_text="Additional transaction details like bank name, account number, etc.")
    
    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.transaction_type} - ${self.amount} - {self.status}"


class ReleaseOrder(TimestampedModel):
    release_order_id = models.AutoField(primary_key=True)
    cargo = models.ForeignKey('cargo.Cargo', on_delete=models.CASCADE, related_name='release_orders')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='release_orders')
    release_code = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('used', 'Used'),
        ('expired', 'Expired'),
    ], default='active')
    generated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='generated_release_orders')
    generated_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'release_orders'
        verbose_name = 'Release Order'
        verbose_name_plural = 'Release Orders'
        
    def __str__(self):
        return f"{self.release_code} - {self.cargo.tracking_number}"


class Wallet(TimestampedModel):
    """Customer wallet for pre-funded payments"""
    wallet_id = models.AutoField(primary_key=True)
    customer = models.OneToOneField('customers.Customer', on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='USD')
    is_active = models.BooleanField(default=True)
    auto_payment_enabled = models.BooleanField(default=False, help_text="Auto-pay invoices from wallet when generated")
    
    class Meta:
        db_table = 'wallets'
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        
    def __str__(self):
        return f"Wallet - {self.customer.customer_name} - ${self.balance}"
    
    def has_sufficient_balance(self, amount):
        """Check if wallet has sufficient balance"""
        return self.balance >= amount
    
    def deposit(self, amount, reference, description=None):
        """Deposit money into wallet"""
        from apps.payments.models import WalletTransaction
        
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        balance_before = self.balance
        self.balance += amount
        self.save()
        
        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            transaction_type='deposit',
            amount=amount,
            balance_before=balance_before,
            balance_after=self.balance,
            reference=reference,
            description=description or f"Deposit of ${amount}",
            status='success'
        )
        
        return self.balance
    
    def withdraw(self, amount, reference, description=None):
        """Withdraw money from wallet"""
        from apps.payments.models import WalletTransaction
        
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if not self.has_sufficient_balance(amount):
            raise ValueError("Insufficient wallet balance")
        
        balance_before = self.balance
        self.balance -= amount
        self.save()
        
        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            transaction_type='withdrawal',
            amount=amount,
            balance_before=balance_before,
            balance_after=self.balance,
            reference=reference,
            description=description or f"Withdrawal of ${amount}",
            status='success'
        )
        
        return self.balance
    
    def pay_invoice(self, invoice, amount, description=None):
        """Pay invoice from wallet"""
        from apps.payments.models import WalletTransaction
        
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        if not self.has_sufficient_balance(amount):
            raise ValueError("Insufficient wallet balance")
        
        balance_before = self.balance
        self.balance -= amount
        self.save()
        
        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            transaction_type='payment',
            amount=amount,
            balance_before=balance_before,
            balance_after=self.balance,
            reference=f"INV-{invoice.control_number}",
            description=description or f"Payment for invoice {invoice.control_number}",
            invoice=invoice,
            status='success'
        )
        
        return self.balance


class WalletTransaction(TimestampedModel):
    """Wallet transaction history"""
    transaction_id = models.AutoField(primary_key=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=50, choices=[
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('auto_payment', 'Auto Payment'),
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_before = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    invoice = models.ForeignKey('invoices.Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='wallet_transactions')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='wallet_transactions')
    status = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ], default='success')
    gateway_response = models.JSONField(blank=True, null=True, help_text="Response from payment gateway")
    
    class Meta:
        db_table = 'wallet_transactions'
        verbose_name = 'Wallet Transaction'
        verbose_name_plural = 'Wallet Transactions'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.transaction_type} - ${self.amount} - {self.wallet.customer.customer_name}"

