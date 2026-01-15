# TESTING "PLACE ORDER SECURELY" BUTTON

## Quick Test Steps (5 minutes)

### Step 1: Open Browser Console
```
Press F12 on your keyboard
Go to "Console" tab
Keep it open while testing
```

### Step 2: Go to Cart
```
URL: http://127.0.0.1:8000/cart/
Make sure you have items in cart
Note the subtotal amount
```

### Step 3: Go to Checkout
```
URL: http://127.0.0.1:8000/orders/checkout/
Or click "Proceed to Checkout" button from cart
```

### Step 4: Fill Form
```
First Name: John
Last Name: Doe
Phone: 9800000000
Address: 123 Main Street
City: Kathmandu
Province: Bagmati
Postal Code: 44600
Delivery Method: Standard Delivery (default selected)
Payment Method: Khalti or Cash on Delivery
```

### Step 5: Click "Place Order Securely"
```
Button location: Bottom of the page
Color: Pink gradient
Text: "Place Order Securely" with lock icon
```

### Step 6: Watch Console
You should see:
```
Form submitted
Form validation result: true
Form data contents:
  first_name: John
  last_name: Doe
  phone: 9800000000
  address: 123 Main Street
  city: Kathmandu
  postal_code: 44600
  province: Bagmati
  delivery_method: standard
  payment_method: khalti (or cod)
Set delivery_method: standard
Submitting order to /orders/checkout/...
Response status: 200
Response data: { success: true, order_id: 123 }
Payment method: khalti
Initiating Khalti payment...
```

### Step 7: Watch for Payment Page
```
Khalti payment widget should appear
OR
COD success page should appear
```

### Step 8: Check Terminal
```
Look at Django terminal for:
Checkout POST data: first_name=John, last_name=Doe, ...
Order totals: subtotal=XXXX, delivery_fee=YYY, order_total=ZZZ
Order created: 123
Creating order item: Product Name x 2
Cart cleared
```

## If Something Goes Wrong

### Red Errors in Console?
```
Screenshot and share the error message
Note the line number (in checkout.html)
```

### Form Validation Failed?
```
1. Click in each field
2. Make sure no fields are empty
3. Check that phone number has 10 digits
4. Province must be selected (not blank)
```

### Network Tab Shows 404?
```
1. Check URL is /orders/checkout/
2. Restart Django server
3. Try again
```

### Network Tab Shows 500 Error?
```
1. Look at Django terminal
2. See what error is printed
3. Share that error message
```

### Button Stays Disabled?
```
1. Refresh page (F5)
2. Try again
3. Check console for errors
```

## Expected Behavior Timeline

```
t=0:
- User clicks "Place Order Securely"
- Button says "Processing..."
- Loading overlay appears (semi-transparent black)
- Loading spinner rotates

t=1-2 seconds:
- Network request sent to /orders/checkout/
- Server processes order
- Server logs printed

t=3-4 seconds:
- Response received
- If success: Khalti widget appears OR COD page loads
- If error: Alert shows error message, button re-enables

t=5-30 seconds (if Khalti):
- User completes Khalti payment
- Order marked as paid

t=5-10 seconds (if COD):
- Order summary page shown
- "Order placed successfully" message
```

## What Each Part Does

### Form
- Collects shipping address
- Selects delivery method
- Selects payment method
- Sends to /orders/checkout/

### JavaScript
- Validates all fields are filled
- Prevents page reload
- Shows loading state
- Parses payment method
- Routes to Khalti or COD based on selection
- Shows errors in alerts

### Django Backend
- Receives form data
- Creates Order record
- Creates OrderItem records (one per cart item)
- Clears cart
- Returns order ID
- Prints debug info to terminal

### Khalti Integration
- Receives order ID from backend
- Shows Khalti payment widget
- Handles payment confirmation
- Redirects to payment success page

### COD Integration
- Receives order ID from backend
- Creates payment record
- Redirects to COD success page
- Shows order details

## Files Involved

```
Frontend (HTML/JavaScript):
  templates/order_management/checkout.html
  - Line 698: Form element
  - Line 916: getCookie function
  - Line 1093: validateForm function
  - Line 1151: Form submission handler
  - Line 1227: initiateCOD function
  - Line 1252: initiateKhalti function

Backend (Python):
  order_management/views.py
  - Line 11: checkout view
  - Line 19: POST request handling
  - Line 54: Order creation

URLs:
  POST http://127.0.0.1:8000/orders/checkout/
  GET http://127.0.0.1:8000/orders/checkout/

Database:
  Order model
  OrderItem model
  Cart model
```

## Common Questions

### Q: Do I have to be logged in?
A: Yes, @login_required decorator requires authentication

### Q: Do I need items in cart?
A: Yes, must have at least one item to checkout

### Q: Which payment method should I test?
A: Test both:
  1. Khalti (if configured)
  2. Cash on Delivery (always available)

### Q: Will the order be saved?
A: Yes, after successful payment (Khalti) or COD selection

### Q: Can I see the order later?
A: Yes, go to /orders/orders/ to view order history

### Q: What if I cancel payment?
A: Order is created, but payment stays pending

### Q: Can I modify the order?
A: No, orders are read-only after creation

## Debug Checklist

- [ ] F12 console open
- [ ] No JavaScript errors in red
- [ ] All form fields filled
- [ ] Delivery method selected
- [ ] Payment method selected
- [ ] Button says "Place Order Securely"
- [ ] Click button once (don't click multiple times)
- [ ] Loading overlay appears
- [ ] Console shows "Response status: 200"
- [ ] Payment page appears (Khalti or COD)
- [ ] Django terminal shows order creation logs

## Terminal Command to Watch Logs

```powershell
# In another PowerShell window:
cd D:\Everest-Beauty-main
python manage.py runserver
# Watch the output for print statements
```

## Success Indicators

1. ✅ Console shows "Response data: { success: true, order_id: XXX }"
2. ✅ Loading overlay disappears
3. ✅ Khalti widget OR COD page appears
4. ✅ Django terminal shows order creation logs
5. ✅ Order appears in /orders/orders/ page

If you see ALL of these, the "Place Order" feature works!
