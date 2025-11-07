# Wallet Feature Documentation

## Overview
The wallet feature allows customers to pre-fund their accounts and enables automatic payment of invoices when cargo arrives. This streamlines the payment process and improves cash flow.

## Features

### 1. Customer Wallet
- Each customer can have one wallet
- Tracks balance in USD (configurable currency)
- Auto-payment option (enabled/disabled per customer)
- Wallet can be activated/deactivated

### 2. Wallet Operations
- **Deposit**: Add money to wallet via payment gateway
- **Withdraw**: Remove money from wallet
- **Pay Invoice**: Pay invoices directly from wallet balance
- **Auto-Payment**: Automatically pay invoices when generated (if enabled)

### 3. Transaction History
- Complete audit trail of all wallet transactions
- Tracks balance before and after each transaction
- Links to invoices and payments
- Stores payment gateway responses

## API Endpoints

### Wallet Management

#### Create Wallet
```
POST /api/payments/wallets/
Body: {
  "customer_id": 1,
  "auto_payment_enabled": false
}
```

#### Get Wallet Details
```
GET /api/payments/wallets/{wallet_id}/
```

#### Get Wallet by Customer
```
GET /api/payments/wallets/customer/{customer_id}/
```

#### Update Wallet Settings
```
PATCH /api/payments/wallets/{wallet_id}/
Body: {
  "auto_payment_enabled": true,
  "is_active": true
}
```

#### List All Wallets
```
GET /api/payments/wallets/
Query Params: ?customer_id=1
```

### Wallet Operations

#### Deposit Money
```
POST /api/payments/wallets/{wallet_id}/deposit/
Body: {
  "amount": 1000,
  "payment_method": "mobile_money",
  "description": "Initial deposit"
}
```

#### Withdraw Money
```
POST /api/payments/wallets/{wallet_id}/withdraw/
Body: {
  "amount": 500,
  "description": "Withdrawal request"
}
```

#### Pay Invoice from Wallet
```
POST /api/payments/wallets/{wallet_id}/pay-invoice/
Body: {
  "invoice_id": 1
}
```

#### Get Transaction History
```
GET /api/payments/wallets/{wallet_id}/transactions/
Query Params: ?transaction_type=deposit
```

## Auto-Payment Flow

1. **Invoice Generated**: When cargo status changes to "arrived" or invoice is manually generated
2. **Check Wallet**: System checks if customer has wallet with auto-payment enabled
3. **Check Balance**: Verifies wallet has sufficient balance
4. **Process Payment**: If conditions met, automatically:
   - Deducts amount from wallet
   - Creates payment record
   - Updates invoice status to "paid"
   - Generates release order
   - Creates transaction records

## Payment Gateway Integration

Currently using **dummy payment gateway** (`apps/payments/services.py`). 

### To Replace with Real Gateway:

1. Update `PaymentGatewayService` in `apps/payments/services.py`
2. Implement actual API calls to your payment provider
3. Handle gateway responses and errors
4. Store gateway responses in `WalletTransaction.gateway_response`

### Supported Payment Methods (Dummy):
- Mobile Money
- Bank Transfer
- Cash

## Example Workflow

### 1. Create Wallet for Customer
```bash
POST /api/payments/wallets/
{
  "customer_id": 1,
  "auto_payment_enabled": true
}
```

### 2. Deposit Money
```bash
POST /api/payments/wallets/1/deposit/
{
  "amount": 2000,
  "payment_method": "mobile_money"
}
```

### 3. Cargo Arrives (Auto-Payment)
- When cargo status changes to "arrived"
- Invoice is auto-generated ($1500)
- System checks wallet (balance: $2000, auto-payment: enabled)
- Automatically pays invoice from wallet
- Balance after: $500
- Release order generated automatically

### 4. Manual Payment (Alternative)
```bash
POST /api/payments/wallets/1/pay-invoice/
{
  "invoice_id": 1
}
```

## Database Models

### Wallet
- `wallet_id`: Primary key
- `customer`: OneToOne relationship with Customer
- `balance`: Current balance (Decimal)
- `currency`: Currency code (default: USD)
- `is_active`: Wallet status
- `auto_payment_enabled`: Auto-payment flag

### WalletTransaction
- `transaction_id`: Primary key
- `wallet`: Foreign key to Wallet
- `transaction_type`: deposit, withdrawal, payment, refund, auto_payment
- `amount`: Transaction amount
- `balance_before`: Balance before transaction
- `balance_after`: Balance after transaction
- `reference`: Transaction reference
- `invoice`: Link to invoice (if payment)
- `payment`: Link to payment record
- `gateway_response`: JSON response from payment gateway

## Security Considerations

1. **Balance Validation**: All operations check sufficient balance
2. **Transaction Logging**: Complete audit trail
3. **Gateway Verification**: Payment gateway responses stored
4. **User Permissions**: All endpoints require authentication
5. **Amount Validation**: Positive amounts only

## Error Handling

- **Insufficient Balance**: Returns error with required/available amounts
- **Wallet Not Found**: 404 error
- **Invalid Amount**: Validation error
- **Gateway Errors**: Stored in transaction record

## Future Enhancements

1. **Wallet Limits**: Set minimum/maximum balance limits
2. **Refund Processing**: Automatic refunds to wallet
3. **Multi-Currency**: Support multiple currencies
4. **Wallet Transfers**: Transfer between customer wallets
5. **Interest/Charges**: Apply interest or charges
6. **Notifications**: Notify on wallet transactions

## Testing

Test the wallet feature:
1. Create wallet for customer
2. Deposit money
3. Enable auto-payment
4. Register cargo and mark as arrived
5. Verify auto-payment processed
6. Check wallet balance and transaction history

