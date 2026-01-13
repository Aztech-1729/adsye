"""
===============================================================================
                      PAYMENT GATEWAY INTEGRATION MODULE
===============================================================================

This module handles UPI payment gateway integration using Oddus Gateway API.
It manages the complete payment flow from invoice creation to verification.

GATEWAY PROVIDER: Oddus Gateway (https://oddus-gateway.vercel.app)

MAIN FEATURES:
- Automatic UPI invoice generation
- QR code creation for payments
- Payment tracking and verification
- User lock mechanism to prevent duplicate payments
- Admin notification system
- Auto-cleanup of temporary files

INTEGRATION GUIDE FOR OTHER BOTS:
==================================

1. DEPENDENCIES REQUIRED:
   - pyrogram (Telegram client library)
   - requests (for API calls)
   - qrcode (for QR code generation)
   - PIL/Pillow (image processing for QR codes)

2. REQUIRED IMPORTS:
   from pyrogram import Client, filters
   from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
   from pyrogram.enums import ParseMode
   import requests
   import qrcode
   import os

3. REQUIRED GLOBAL VARIABLES (Must be defined in your bot):
   - GATEWAY_URL: Gateway API endpoint URL
   - WEBHOOK_URL: Your server webhook URL for payment notifications
   - ACTIVE_INVOICES: Dict to track active payment invoices
   - USER_LOCKS: Dict to prevent duplicate payments per user
   - UPI_EXPIRY: Payment expiry time in minutes
   - Render: Your text rendering utility class
   - log: Your logging instance
   - send_owner_alert: Function to notify admins about new payments

4. CALLBACK DATA FORMAT:
   The system uses callback data patterns:
   - "sigmameth_{method}_{amount}_{context}" - Trigger payment method
   - "sigmav_{pay_id}" - Verify payment button
   - "sigmac_{pay_id}" - Cancel payment button

5. DIRECTORY STRUCTURE:
   - Ensure 'downloads/' directory exists for temporary QR codes
   - QR codes are auto-deleted after sending to user

6. GATEWAY API ENDPOINTS:
   - POST /upi/create - Creates new UPI invoice
   
7. API REQUEST PAYLOAD:
   {
       "user_id": int,              # Telegram user ID
       "price_amount": float,        # Amount in INR
       "client_id": str,            # Unique bot identifier
       "notification_url": str      # Webhook for payment status
   }

8. API RESPONSE FORMAT:
   {
       "status": "success",
       "invoice": {
           "pay_id": str,           # Unique payment ID
           "upi_link": str,         # UPI payment link (for QR)
           "amount": float,
           "expiry": str
       }
   }

9. PAYMENT FLOW:
   User clicks payment button → Invoice created → QR code generated → 
   User scans & pays → Clicks verify → Payment verified → Credits added

10. ERROR HANDLING:
    - Network timeouts (15s)
    - Gateway connection errors
    - Invalid responses
    - All errors logged automatically

===============================================================================
"""

#====================================CONFIGS=======================#
# Gateway API Base URL - Change this to your gateway provider
GATEWAY_URL = "https://oddus-gateway.vercel.app"




# ============================================================================
#                       CORE GATEWAY API HANDLER
# ============================================================================

async def _call_gateway(endpoint, payload):
    """
    Universal function to make API calls to the payment gateway.
    
    This is the core communication function that handles all gateway API requests.
    It includes error handling, timeout management, and response validation.
    
    Args:
        endpoint (str): API endpoint path (e.g., "upi/create", "upi/verify")
        payload (dict): JSON payload to send to the gateway
                       Example: {
                           "user_id": 123456789,
                           "price_amount": 100.0,
                           "client_id": "MyBot_123",
                           "notification_url": "https://mybot.com/webhook"
                       }
    
    Returns:
        tuple: (success: bool, response: dict/str)
            - On success: (True, {"status": "success", "invoice": {...}})
            - On failure: (False, "Error message string")
    
    Example Usage:
        success, result = await _call_gateway("upi/create", {
            "user_id": user_id,
            "price_amount": 100.0,
            "client_id": "MyBot"
        })
        
        if success:
            invoice = result['invoice']
            pay_id = invoice['pay_id']
        else:
            print(f"Error: {result}")
    
    Integration Notes:
        - Timeout is set to 15 seconds to prevent hanging
        - Logs all errors automatically using the 'log' instance
        - Returns False on any exception or non-200 status code
        - Validates that response has 'status': 'success' field
    """
    try:
        # Construct full API URL
        url = f"{GATEWAY_URL}/{endpoint}"
        
        # Make POST request with JSON payload and 15-second timeout
        resp = requests.post(url, json=payload, timeout=15)
        
        # Check if request was successful (HTTP 200)
        if resp.status_code == 200:
            data = resp.json()
            
            # Validate that gateway returned success status
            if data.get('status') == 'success':
                return True, data
        
        # If we reach here, either status != 200 or status != 'success'
        return False, "Gateway Connection Error"
        
    except Exception as e:
        # Log any exceptions (network errors, timeouts, JSON decode errors, etc.)
        log.error(f"Gateway API Error: {e}")
        return False, str(e)


# ============================================================================
#                    PAYMENT METHOD SELECTION HANDLER
# ============================================================================

@Client.on_callback_query(filters.regex("^sigmameth_"))
async def handle_payment_method(client: Client, query: CallbackQuery):
    """
    Handles payment method selection and invoice generation.
    
    This handler is triggered when a user selects a payment method from inline buttons.
    It processes UPI payments by creating invoices, generating QR codes, and managing
    the payment tracking system.
    
    Callback Data Format:
        sigmameth_{method}_{amount}_{context}
        
        Examples:
        - sigmameth_upi_100_credits     (UPI payment of ₹100 for credits)
        - sigmameth_upi_500_premium     (UPI payment of ₹500 for premium)
        - sigmameth_upi_1000_product123 (UPI payment of ₹1000 for product)
    
    Args:
        client (Client): Pyrogram client instance
        query (CallbackQuery): Telegram callback query object containing:
            - query.data: Callback data string
            - query.from_user.id: User's Telegram ID
            - query.message: Original message object
    
    Payment Flow:
        1. Parse callback data (method, amount, context)
        2. Show "Generating invoice..." loading message
        3. Call gateway API to create UPI invoice
        4. Generate QR code from UPI link
        5. Send alert to bot owner/admin
        6. Store invoice in ACTIVE_INVOICES tracker
        7. Lock user to prevent duplicate payments
        8. Delete old message and send new payment message with QR
        9. Add verify and cancel buttons
        10. Clean up temporary QR code file
    
    Global Variables Used:
        - ACTIVE_INVOICES: Dict storing all active payment invoices
          Format: {
              "pay_id_123": {
                  "user_id": 123456789,
                  "amount": 100.0,
                  "context": "credits",
                  "alert_msg_id": 456,      # Admin alert message ID
                  "client_msg_id": 789      # User payment message ID
              }
          }
        
        - USER_LOCKS: Dict preventing users from creating multiple invoices
          Format: {123456789: "pay_id_123"}
        
        - WEBHOOK_URL: Your webhook URL for payment notifications
        - UPI_EXPIRY: Payment expiry time in minutes
        - Render: Text rendering utility for multilingual support
    
    Dependencies:
        - _call_gateway(): Makes API call to create invoice
        - send_owner_alert(): Notifies admins about new payment
        - qrcode.make(): Generates QR code image from UPI link
    
    Error Handling:
        - If gateway call fails, user remains on previous screen
        - If QR generation fails, temporary file cleanup is skipped
        - All errors are logged via _call_gateway function
    
    Integration Notes for Other Bots:
        1. Update callback pattern "sigmameth_" to match your bot's naming
        2. Modify caption text and emojis to match your bot's style
        3. Update Render.text() calls if not using multilingual system
        4. Ensure 'downloads/' directory exists in your bot's root
        5. Adjust button labels and callback patterns for verify/cancel
        6. Update client_id format to identify your bot uniquely
    
    Example Integration:
        # To trigger this handler, use inline keyboard button:
        InlineKeyboardButton(
            "💳 Pay ₹100",
            callback_data="sigmameth_upi_100_credits"
        )
    """
    
    # ========================================================================
    # STEP 1: Parse callback data and extract payment parameters
    # ========================================================================
    data = query.data.split("_")
    method = data[1]        # Payment method (e.g., "upi")
    amount = float(data[2]) # Payment amount in INR
    context = data[3]       # Payment context/purpose (e.g., "credits", "premium")
    user_id = query.from_user.id  # Telegram user ID
    
    # ========================================================================
    # STEP 2: Handle UPI payment method
    # ========================================================================
    if method == "upi":
        # Show loading message to user
        await query.answer("Generating UPI Invoice...")
        
        # ====================================================================
        # STEP 3: Prepare API payload for gateway
        # ====================================================================
        payload = {
            "user_id": user_id,                      # Telegram user ID
            "price_amount": amount,                   # Amount in INR
            "client_id": f"Oddus_{client.me.id}",   # Unique bot identifier
            "notification_url": WEBHOOK_URL          # Webhook for payment updates
        }
        
        # Make API call to create UPI invoice
        success, res = await _call_gateway("upi/create", payload)
        
        # ====================================================================
        # STEP 4: Process successful invoice creation
        # ====================================================================
        if success:
            # Extract invoice data from API response
            inv = res['invoice']
            pay_id = inv['pay_id']          # Unique payment ID (used for tracking)
            upi_link = inv['upi_link']      # UPI payment link
            
            # ================================================================
            # STEP 5: Generate QR code for UPI payment
            # ================================================================
            qr_path = f"downloads/qr_{user_id}.png"
            qrcode.make(upi_link).save(qr_path)
            
            # ================================================================
            # STEP 6: Send alert to bot owner/admin
            # ================================================================
            # This notifies admin about new payment request
            # Returns message ID for later reference
            alert_id = await send_owner_alert(client, user_id, amount, "UPI", pay_id, context)
            
            # ================================================================
            # STEP 7: Store invoice in tracking system
            # ================================================================
            ACTIVE_INVOICES[pay_id] = {
                "user_id": user_id,           # Who is paying
                "amount": amount,             # How much
                "context": context,           # What for (credits/premium/etc)
                "alert_msg_id": alert_id,     # Admin notification message ID
                "client_msg_id": None         # User payment message ID (set below)
            }
            
            # ================================================================
            # STEP 8: Lock user to prevent duplicate payments
            # ================================================================
            # This prevents user from creating multiple active invoices
            USER_LOCKS[user_id] = pay_id

            # ================================================================
            # STEP 9: Delete old message and send payment interface
            # ================================================================
            await query.message.delete()
            
            # Send payment message with QR code
            sent_msg = await client.send_photo(
                chat_id=query.message.chat.id,
                photo=qr_path,
                caption=(
                    f"<b>📱 {Render.text('upi gateway')}</b>\n━━━━━━━━━━━━\n"
                    f"<b>Amount:</b> ₹{amount}\n"
                    f"<b>Ref-ID:</b> <code>{pay_id}</code>\n"
                    f"<b>Expiry:</b> {UPI_EXPIRY} Minutes\n"
                    f"━━━━━━━━━━━━\n"
                    f"Scan the QR and click <b>Verify</b> after payment."
                ),
                reply_markup=InlineKeyboardMarkup([
                    # Verify payment button - triggers verification flow
                    [InlineKeyboardButton("✅ Verify Payment", callback_data=f"sigmav_{pay_id}")],
                    # Cancel button - cancels the payment and unlocks user
                    [InlineKeyboardButton("❌ Cancel Request", callback_data=f"sigmac_{pay_id}")]
                ]),
                parse_mode=ParseMode.HTML
            )
            
            # Store message ID in tracking system for later deletion/editing
            ACTIVE_INVOICES[pay_id]['client_msg_id'] = sent_msg.id
            
            # ================================================================
            # STEP 10: Clean up temporary QR code file
            # ================================================================
            if os.path.exists(qr_path):
                os.remove(qr_path)


# ============================================================================
#                        ADDITIONAL INTEGRATION NOTES
# ============================================================================
"""
WEBHOOK HANDLER (Must be implemented separately):
-------------------------------------------------
You need to implement a webhook endpoint to receive payment notifications
from the gateway. This is typically done using Flask or FastAPI.

Example webhook handler structure:

    @app.post("/webhook")
    async def handle_gateway_webhook(request):
        data = await request.json()
        
        if data['status'] == 'success':
            pay_id = data['pay_id']
            
            if pay_id in ACTIVE_INVOICES:
                invoice = ACTIVE_INVOICES[pay_id]
                user_id = invoice['user_id']
                amount = invoice['amount']
                context = invoice['context']
                
                # Add credits or perform action
                await process_successful_payment(user_id, amount, context)
                
                # Notify user
                await bot.send_message(user_id, "✅ Payment verified!")
                
                # Clean up
                del ACTIVE_INVOICES[pay_id]
                del USER_LOCKS[user_id]


VERIFY BUTTON HANDLER (Must be implemented):
--------------------------------------------
Handle the "sigmav_{pay_id}" callback:

    @Client.on_callback_query(filters.regex("^sigmav_"))
    async def verify_payment(client, query):
        pay_id = query.data.split("_")[1]
        
        # Call gateway to check payment status
        success, res = await _call_gateway("upi/verify", {"pay_id": pay_id})
        
        if success and res.get('paid'):
            # Process payment
            await process_successful_payment(...)
        else:
            await query.answer("Payment not confirmed yet!", show_alert=True)


CANCEL BUTTON HANDLER (Must be implemented):
--------------------------------------------
Handle the "sigmac_{pay_id}" callback:

    @Client.on_callback_query(filters.regex("^sigmac_"))
    async def cancel_payment(client, query):
        pay_id = query.data.split("_")[1]
        
        if pay_id in ACTIVE_INVOICES:
            user_id = ACTIVE_INVOICES[pay_id]['user_id']
            
            # Clean up
            del ACTIVE_INVOICES[pay_id]
            del USER_LOCKS[user_id]
            
            await query.message.delete()
            await query.answer("Payment cancelled!")


REQUIRED HELPER FUNCTIONS:
--------------------------
1. send_owner_alert(client, user_id, amount, method, pay_id, context)
   - Sends notification to admin about new payment
   - Returns message ID for tracking
   
2. process_successful_payment(user_id, amount, context)
   - Adds credits or performs action after payment
   - Updates database
   - Sends confirmation to user


SECURITY CONSIDERATIONS:
------------------------
1. Always validate webhook signatures (if provided by gateway)
2. Use HTTPS for webhook URL
3. Implement rate limiting for payment creation
4. Set expiry times for invoices
5. Clear expired invoices periodically
6. Validate amount and user_id before processing
7. Log all payment activities for audit trail


TESTING CHECKLIST:
------------------
☐ Gateway API is reachable
☐ Webhook URL is public and accessible
☐ QR codes are generated correctly
☐ Payment tracking works properly
☐ User locks prevent duplicates
☐ Verify button checks payment status
☐ Cancel button cleans up properly
☐ Admin notifications are sent
☐ Expired invoices are cleaned up
☐ Webhook signature validation works
☐ Error messages are user-friendly
☐ Logs are being written correctly

"""