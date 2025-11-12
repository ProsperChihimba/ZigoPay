# WhatsApp Bot Setup Guide

## Overview
The WhatsApp bot automatically replies with "WELCOME TO ZIGO PAY" when someone sends a message to your WhatsApp Business number.

## Configuration

### Credentials (Already Configured)
- **WhatsApp Token**: Configured in `settings.py`
- **Phone Number ID**: `537559402774394`
- **Business Account ID**: `528995370286469`
- **Verify Token**: `c2a49926-a81c-11ef-b864-0242ac120002`

## API Endpoints

### Webhook Endpoint (For Facebook)
```
GET/POST /api/whatsapp/webhook/
```
This is the endpoint Facebook will call when:
- **GET**: Webhook verification (during setup)
- **POST**: Incoming messages from users

### Test Endpoint
```
POST /api/whatsapp/test/
Body: {
  "phone_number": "255712345678",
  "message": "WELCOME TO ZIGO PAY"
}
```

## Setting Up Webhook in Facebook

1. Go to [Facebook Developers Console](https://developers.facebook.com/)
2. Select your WhatsApp Business App
3. Go to **Configuration** → **Webhooks**
4. Click **Edit** on the webhook
5. Set **Callback URL**: `https://your-domain.com/api/whatsapp/webhook/`
6. Set **Verify Token**: `c2a49926-a81c-11ef-b864-0242ac120002`
7. Subscribe to **messages** event
8. Save and verify

## How It Works

1. **User sends message** to your WhatsApp Business number
2. **Facebook sends webhook** to `/api/whatsapp/webhook/`
3. **Bot extracts** sender phone number and message
4. **Bot replies** with "WELCOME TO ZIGO PAY"
5. **User receives** the welcome message

## Testing

### Test Webhook Verification
```bash
curl "http://localhost:8000/api/whatsapp/webhook/?hub.mode=subscribe&hub.verify_token=c2a49926-a81c-11ef-b864-0242ac120002&hub.challenge=test123"
```

Expected response: `test123`

### Test Sending Message
```bash
curl -X POST http://localhost:8000/api/whatsapp/test/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "255712345678",
    "message": "WELCOME TO ZIGO PAY"
  }'
```

## Production Deployment

### Requirements
1. **HTTPS**: Facebook requires HTTPS for webhooks
2. **Public URL**: Your server must be accessible from the internet
3. **SSL Certificate**: Valid SSL certificate required

### Using ngrok for Local Testing
```bash
# Install ngrok
# Run your Django server
python manage.py runserver

# In another terminal, expose port 8000
ngrok http 8000

# Use the ngrok URL in Facebook webhook configuration
# Example: https://abc123.ngrok.io/api/whatsapp/webhook/
```

## Message Flow

```
User → WhatsApp → Facebook API → Your Webhook → Bot Reply → Facebook API → User
```

## Troubleshooting

### Webhook Not Receiving Messages
1. Check webhook is verified in Facebook Console
2. Verify callback URL is accessible (use HTTPS)
3. Check server logs for errors
4. Ensure phone number is registered in WhatsApp Business

### Messages Not Sending
1. Verify WhatsApp token is valid
2. Check phone number ID is correct
3. Ensure phone number format (remove +, use country code)
4. Check Facebook API response for errors

### Common Errors
- **403 Forbidden**: Verify token mismatch
- **400 Bad Request**: Invalid JSON or missing fields
- **500 Error**: Check server logs for details

## Security Notes

1. **Verify Token**: Keep your verify token secret
2. **HTTPS Only**: Always use HTTPS in production
3. **Token Rotation**: Rotate tokens periodically
4. **Rate Limiting**: Consider adding rate limiting

## Next Steps

To enhance the bot:
1. Add command handlers (e.g., "TRACK", "BALANCE")
2. Integrate with cargo tracking system
3. Add wallet balance queries
4. Support multiple languages
5. Add conversation flow management

## Files

- `apps/whatsapp/views.py` - Bot logic and webhook handler
- `apps/whatsapp/urls.py` - URL routing
- `zigopay/settings.py` - WhatsApp credentials

