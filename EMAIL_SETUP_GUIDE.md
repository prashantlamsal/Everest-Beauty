# Email Notification Setup Guide

## Current Status
✅ Email notifications are configured and will send after successful order placement
✅ Logo is set up at `static/img/brand-logo.svg`
✅ Professional HTML email template is ready
✅ Graceful failure handling (order placement won't fail if email fails)

## Default Behavior (Development)
By default, emails print to the **server console** instead of being sent. This is perfect for testing without needing SMTP credentials.

When you place an order, check the Django runserver terminal - you'll see the full email HTML printed there.

## To Send Real Emails

### Option 1: Gmail (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Create an App Password**:
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. **Create/update `.env` file** in project root:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=zfcx wqam ksbq khof
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   
   BRAND_NAME=Everest Beauty
   SUPPORT_EMAIL=support@everestbeauty.com
   SUPPORT_PHONE=+977-9800000000
   BUSINESS_HOURS=Sun-Fri 9am-6pm
   ```
4. **Restart the server**
5. **Place a test order** - email will be sent to the customer's email

### Option 2: Other SMTP Providers

**SendGrid:**
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

**Mailgun:**
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@your-domain.mailgun.org
EMAIL_HOST_PASSWORD=your-mailgun-password
```

**AWS SES:**
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-ses-smtp-user
EMAIL_HOST_PASSWORD=your-ses-smtp-password
```

### Option 3: Development Testing with Mailtrap

Perfect for testing without sending real emails:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-mailtrap-username
EMAIL_HOST_PASSWORD=your-mailtrap-password
```

Sign up at https://mailtrap.io (free tier available) - all emails will be caught in their inbox.

## Email Content

The confirmation email includes:
- ✅ Brand logo (SVG)
- ✅ Branded color scheme (#f43f5e and #0ea5e9)
- ✅ Order ID and date
- ✅ Customer name
- ✅ Complete item list with quantities and prices
- ✅ Total amount paid
- ✅ Payment method
- ✅ Estimated delivery date
- ✅ Support contact info
- ✅ Thank you message with "Visit Store" button
- ✅ Responsive design for mobile

## Testing

1. **Console Backend (Default)**:
   - Place order
   - Check terminal output for email HTML

2. **Real SMTP**:
   - Configure .env as shown above
   - Restart server
   - Place order
   - Check inbox at the email address used during checkout

## Troubleshooting

**Email not received?**
- Check spam/junk folder
- Verify SMTP credentials in .env
- Check server console for "Email send failed" errors
- Verify EMAIL_BACKEND is set to smtp backend
- Ensure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct

**Gmail "Less secure app" error?**
- Use App Password instead of regular password
- Enable 2FA first

**Logo not showing?**
- Run `python manage.py collectstatic` to copy static files
- Verify `static/img/brand-logo.svg` exists
- Check email client allows external images (some block by default)

## Logo Customization

Replace `static/img/brand-logo.svg` with your own logo (PNG or SVG):
- Recommended size: 240x60px
- Format: PNG or SVG
- Update filename in `order_management/utils.py` if using PNG

## Production Checklist

- [ ] Set EMAIL_BACKEND to smtp
- [ ] Configure SMTP credentials securely
- [ ] Test email delivery
- [ ] Add real support contact information
- [ ] Customize brand logo
- [ ] Set proper DEFAULT_FROM_EMAIL domain
- [ ] Consider using dedicated transactional email service (SendGrid, Mailgun, AWS SES)
