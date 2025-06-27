import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings
import os


def send_order_to_google_sheets(order):
    """Send order data to Google Sheets"""
    try:
        # Check if credentials file exists
        if not os.path.exists(settings.GOOGLE_SHEETS_CREDENTIALS_FILE):
            print("Google Sheets credentials file not found")
            return
        
        # Set up credentials
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            settings.GOOGLE_SHEETS_CREDENTIALS_FILE, 
            scope
        )
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet = client.open(settings.GOOGLE_SHEETS_NAME).sheet1
        
        # Prepare order items
        items_str = ", ".join([
            f"{item.product.name} (x{item.quantity})" 
            for item in order.items.all()
        ])
        
        # Prepare the row
        row = [
            order.id,
            order.first_name,
            order.last_name,
            order.email,
            order.phone,
            order.address,
            order.city,
            order.postal_code,
            float(order.total),
            order.status,
            order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            items_str
        ]
        
        # Append the row
        sheet.append_row(row)
        print(f"Order #{order.id} sent to Google Sheets successfully")
        
    except Exception as e:
        print(f"Error sending order to Google Sheets: {e}")
        raise e