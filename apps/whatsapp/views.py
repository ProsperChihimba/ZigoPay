"""
WhatsApp Bot Integration
Handles incoming messages and sends replies
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import requests
import json


WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"
WHATSAPP_TOKEN = getattr(settings, 'WHATSAPP_TOKEN', '')
WHATSAPP_PHONE_NUMBER_ID = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
WHATSAPP_BUSINESS_ACCOUNT_ID = getattr(settings, 'WHATSAPP_BUSINESS_ACCOUNT_ID', '')
WHATSAPP_VERIFY_TOKEN = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', '')


def send_whatsapp_message(phone_number, message):
    """
    Send WhatsApp message using Facebook Graph API
    """
    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"WhatsApp API Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def whatsapp_webhook(request):
    """
    WhatsApp webhook endpoint
    GET: Webhook verification
    POST: Handle incoming messages
    """
    if request.method == 'GET':
        # Webhook verification
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        if mode == 'subscribe' and token == WHATSAPP_VERIFY_TOKEN:
            print("Webhook verified successfully")
            return HttpResponse(challenge, status=200)
        else:
            print(f"Webhook verification failed. Mode: {mode}, Token match: {token == WHATSAPP_VERIFY_TOKEN}")
            return HttpResponse("Forbidden", status=403)
    
    elif request.method == 'POST':
        # Handle incoming messages
        try:
            body = json.loads(request.body)
            
            # Check if it's a WhatsApp message
            if 'entry' in body:
                for entry in body['entry']:
                    if 'changes' in entry:
                        for change in entry['changes']:
                            if 'value' in change:
                                value = change['value']
                                
                                # Check for messages
                                if 'messages' in value:
                                    for message in value['messages']:
                                        # Get sender phone number
                                        sender_phone = message.get('from', '').replace('+', '')
                                        
                                        # Get message text
                                        if message.get('type') == 'text':
                                            message_text = message.get('text', {}).get('body', '')
                                            
                                            # Reply with welcome message
                                            reply_message = "WELCOME TO ZIGO PAY"
                                            
                                            # Send reply
                                            result = send_whatsapp_message(sender_phone, reply_message)
                                            
                                            if result:
                                                print(f"Message sent successfully to {sender_phone}")
                                            else:
                                                print(f"Failed to send message to {sender_phone}")
            
            return HttpResponse("OK", status=200)
            
        except json.JSONDecodeError:
            print("Invalid JSON in webhook request")
            return HttpResponse("Invalid JSON", status=400)
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return HttpResponse("Error", status=500)
    
    return HttpResponse("Method not allowed", status=405)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_test_message(request):
    """
    Test endpoint to send WhatsApp message
    For testing purposes only
    """
    phone_number = request.data.get('phone_number')
    message = request.data.get('message', 'WELCOME TO ZIGO PAY')
    
    if not phone_number:
        return Response({
            'success': False,
            'error': 'Phone number is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Remove + if present
    phone_number = phone_number.replace('+', '')
    
    result = send_whatsapp_message(phone_number, message)
    
    if result:
        return Response({
            'success': True,
            'message': 'Message sent successfully',
            'data': result
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'error': 'Failed to send message'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

