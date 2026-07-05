
import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context, ALL, MATCH
import dash_bootstrap_components as dbc
import sqlite3
import uuid
from datetime import datetime, date
import google.generativeai as genai
import pandas as pd
import json
import re
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
import io
from PIL import Image
import requests

# Fix for Python 3.12 SQLite datetime adapter
def adapt_datetime(dt):
    return dt.isoformat()

def convert_datetime(s):
    return datetime.fromisoformat(s.decode())

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("TIMESTAMP", convert_datetime)

# Initialize the app with a modern healthcare theme
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.FLATLY,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ]
)
app.title = "Telesehat - Telemedicine Platform"
server = app.server
app.config.suppress_callback_exceptions = True  # Remove callback error display

# Hardcoded API keys (for demonstration only - use environment variables in production)
GEMINI_API_KEY = "AQ.Ab8RN6IXbccgKM-YWMYBp_4O6IyBQkQgoD3SdVeh3JW_mNyhyA"  # Replace with your actual Gemini API key
AGORA_APP_ID = "79900bea4285434da3095127036de80a"

# Initialize Gemini client
try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-3-flash-preview')
    gemini_vision_model = genai.GenerativeModel('gemini-3-flash-preview')
except Exception as e:
    print(f"Gemini client initialization failed: {e}")
    gemini_model = None
    gemini_vision_model = None
    
# Translations dictionary
translations = {
    "en": {
        "app_title": "Telesehat",
        "login_register": "Login/Register",
        "full_name": "Full Name",
        "select_role": "Select Role",
        "phone": "Phone Number",
        "village": "Village/City",
        "dob": "Date of Birth",
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "other": "Other",
        "submit": "Submit",
        "welcome_back": "Welcome back {}!",
        "registration_success": "Registration successful!",
        "fill_all_fields": "Please fill all fields.",
        "patient": "Patient",
        "doctor": "Doctor",
        "pharmacy": "Pharmacy",
        "patient_dashboard": "Patient Dashboard",
        "doctor_dashboard": "Doctor Dashboard",
        "pharmacy_dashboard": "Pharmacy Dashboard",
        "patient_profile": "Patient Profile",
        "request_consultation": "Request Consultation",
        "consultation_reason": "Reason for consultation...",
        "request_consult_btn": "Request Consultation",
        "video_consultation": "Video Consultation",
        "ai_chatbot": "AI Chatbot",
        "ask_symptoms": "Ask about your symptoms...",
        "send": "Send",
        "medicine_availability": "Medicine Availability",
        "medicine_name": "Medicine name...",
        "search": "Search",
        "pending_consultations": "Pending Consultations",
        "update_stock": "Update Stock",
        "medicine_name_label": "Medicine Name",
        "quantity": "Quantity",
        "price": "Price",
        "update_stock_btn": "Update Stock",
        "current_stock": "Current Stock",
        "no_profile_data": "No profile data",
        "no_pending_consultations": "No pending consultations",
        "no_stock_records": "No stock records",
        "assistant_unavailable": "Sorry, the assistant is unavailable right now. Please try again later.",
        "consultation_requested": "Consultation requested successfully!",
        "stock_updated": "Stock updated successfully!",
        "no_results": "No results found",
        "enter_medicine_name": "Please enter a medicine name",
        "join_consultation": "Join Video Consultation",
        "consultation_instructions": "Click the button below to join your video consultation session. Make sure you have a working camera and microphone.",
        "join_button": "Join Now",
        "dark_mode": "Dark Mode",
        "light_mode": "Light Mode",
        "language": "Language",
        "accept": "Accept",
        "reject": "Reject",
        "patient_info": "Patient Info",
        "typing": "AI is typing...",
        "loading": "Loading...",
        "delete": "Delete",
        "edit": "Edit",
        "save": "Save",
        "actions": "Actions",
        "appointments": "Appointments",
        "schedule_appointment": "Schedule Appointment",
        "appointment_date": "Appointment Date",
        "appointment_time": "Appointment Time",
        "health_metrics": "Health Metrics",
        "blood_pressure": "Blood Pressure",
        "heart_rate": "Heart Rate",
        "temperature": "Temperature",
        "blood_sugar": "Blood Sugar",
        "add_metric": "Add Metric",
        "prescriptions": "Prescriptions",
        "write_prescription": "Write Prescription",
        "order_tracking": "Order Tracking",
        "manage_schedule": "Manage Schedule",
        "available_hours": "Available Hours",
        "day": "Day",
        "start_time": "Start Time",
        "end_time": "End Time",
        "add_slot": "Add Time Slot",
        "upcoming": "Upcoming",
        "past": "Past",
        "status": "Status",
        "date": "Date",
        "time": "Time",
        "tracking_id": "Tracking ID",
        "order_status": "Order Status",
        "track_order": "Track Order",
        "consultation_accepted": "Consultation accepted!",
        "consultation_rejected": "Consultation rejected!",
        "appointment_scheduled": "Appointment scheduled successfully!",
        "stock_deleted": "Stock item deleted successfully!",
        "error_occurred": "An error occurred. Please try again.",
        "logout": "Logout",
        "logout_success": "You have been logged out successfully!",
        "upload_image": "Upload Image",
        "image_analysis": "Image Analysis",
        "prescription_details": "Prescription Details",
        "medicine": "Medicine",
        "dosage": "Dosage",
        "instructions": "Instructions",
        "write_prescription_btn": "Write Prescription",
        "prescription_saved": "Prescription saved successfully!",
        "age": "Age",
        "years": "years",
        "select_doctor": "Select Doctor",
        "select_doctor_placeholder": "Choose a doctor...",
        "my_consultations": "My Consultations",
        "consultation_status": "Consultation Status",
        "requested": "Requested",
        "accepted": "Accepted",
        "rejected": "Rejected",
        "completed": "Completed",
        "no_consultations": "No consultations found",
        "view_details": "View Details",
        "consultation_details": "Consultation Details",
        "doctor": "Doctor",
        "reason": "Reason",
        "created": "Created",
        "no_doctor_available": "No doctors available"
    },
    "hi": {
        "app_title": "टेलीसेहत",
        "login_register": "लॉगिन/पंजीकरण",
        "full_name": "पूरा नाम",
        "select_role": "भूमिका चुनें",
        "phone": "फ़ोन नंबर",
        "village": "गाँव/शहर",
        "dob": "जन्म तिथि",
        "gender": "लिंग",
        "male": "पुरुष",
        "female": "महिला",
        "other": "अन्य",
        "submit": "जमा करें",
        "welcome_back": "वापसी पर स्वागत है {}!",
        "registration_success": "पंजीकरण सफल!",
        "fill_all_fields": "कृपया सभी फ़ील्ड भरें।",
        "patient": "मरीज़",
        "doctor": "डॉक्टर",
        "pharmacy": "फार्मेसी",
        "patient_dashboard": "मरीज़ डैशबोर्ड",
        "doctor_dashboard": "डॉक्टर डैशबोर्ड",
        "pharmacy_dashboard": "फार्मेसी डैशबोर्ड",
        "patient_profile": "मरीज़ प्रोफाइल",
        "request_consultation": "परामर्श का अनुरोध करें",
        "consultation_reason": "परामर्श का कारण...",
        "request_consult_btn": "परामर्श अनुरोध",
        "video_consultation": "वीडियो परामर्श",
        "ai_chatbot": "एआई चैटबॉट",
        "ask_symptoms": "अपने लक्षणों के बारे में पूछें...",
        "send": "भेजें",
        "medicine_availability": "दवा उपलब्धता",
        "medicine_name": "दवा का नाम...",
        "search": "खोजें",
        "pending_consultations": "लंबित परामर्श",
        "update_stock": "स्टॉक अपडेट करें",
        "medicine_name_label": "दवा का नाम",
        "quantity": "मात्रा",
        "price": "कीमत",
        "update_stock_btn": "स्टॉक अपडेट करें",
        "current_stock": "वर्तमान स्टॉक",
        "no_profile_data": "कोई प्रोफ़ाइल डेटा नहीं",
        "no_pending_consultations": "कोई लंबित परामर्श नहीं",
        "no_stock_records": "कोई स्टॉक रिकॉर्ड नहीं",
        "assistant_unavailable": "क्षमा करें, सहायक वर्तमान में उपलब्ध नहीं है। कृपया बाद में पुन: प्रयास करें।",
        "consultation_requested": "परामर्श सफलतापूर्वक अनुरोधित!",
        "stock_updated": "स्टॉक सफलतापूर्वक अपडेट किया गया!",
        "no_results": "कोई परिणाम नहीं मिला",
        "enter_medicine_name": "कृपया दवा का नाम दर्ज करें",
        "join_consultation": "वीडियो परामर्श में शामिल हों",
        "consultation_instructions": "अपने वीडियो परामर्श सत्र में शामिल होने के लिए नीचे दिए गए बटन पर क्लिक करें। सुनिश्चित करें कि आपके पास एक कार्यशील कैमरा और माइक्रोफोन है।",
        "join_button": "अभी जुड़ें",
        "dark_mode": "डार्क मोड",
        "light_mode": "लाइट मोड",
        "language": "भाषा",
        "accept": "स्वीकार करें",
        "reject": "अस्वीकार करें",
        "patient_info": "मरीज़ की जानकारी",
        "typing": "एआई टाइप कर रहा है...",
        "loading": "लोड हो रहा है...",
        "delete": "हटाएं",
        "edit": "संपादित करें",
        "save": "सहेजें",
        "actions": "कार्रवाई",
        "appointments": "अपॉइंटमेंट",
        "schedule_appointment": "अपॉइंटमेंट शेड्यूल करें",
        "appointment_date": "अपॉइंटमेंट की तारीख",
        "appointment_time": "अपॉइंटमेंट का समय",
        "health_metrics": "स्वास्थ्य माप",
        "blood_pressure": "ब्लड प्रेशर",
        "heart_rate": "हृदय गति",
        "temperature": "तापमान",
        "blood_sugar": "ब्लड शुगर",
        "add_metric": "माप जोड़ें",
        "prescriptions": "प्रिस्क्रिप्शन",
        "write_prescription": "प्रिस्क्रिप्शन लिखें",
        "order_tracking": "ऑर्डर ट्रैकिंग",
        "manage_schedule": "शेड्यूल प्रबंधित करें",
        "available_hours": "उपलब्ध समय",
        "day": "दिन",
        "start_time": "प्रारंभ समय",
        "end_time": "समाप्ति समय",
        "add_slot": "समय जोड़ें",
        "upcoming": "आगामी",
        "past": "पिछले",
        "status": "स्थिति",
        "date": "तारीख",
        "time": "समय",
        "tracking_id": "ट्रैकिंग आईडी",
        "order_status": "ऑर्डर स्थिति",
        "track_order": "ऑर्डर ट्रैक करें",
        "consultation_accepted": "परामर्श स्वीकृत!",
        "consultation_rejected": "परामर्श अस्वीकृत!",
        "appointment_scheduled": "अपॉइंटमेंट सफलतापूर्वक शेड्यूल किया गया!",
        "stock_deleted": "स्टॉक आइटम सफलतापूर्वक हटाया गया!",
        "error_occurred": "एक त्रुटि हुई। कृपया पुन: प्रयास करें।",
        "logout": "लॉग आउट",
        "logout_success": "आप सफलतापूर्वक लॉग आउट हो गए हैं!",
        "upload_image": "छवि अपलोड करें",
        "image_analysis": "छवि विश्लेषण",
        "prescription_details": "प्रिस्क्रिप्शन विवरण",
        "medicine": "दवा",
        "dosage": "खुराक",
        "instructions": "निर्देश",
        "write_prescription_btn": "प्रिस्क्रिप्शन लिखें",
        "prescription_saved": "प्रिस्क्रिप्शन सफलतापूर्वक सहेजा गया!",
        "age": "उम्र",
        "years": "वर्ष",
        "select_doctor": "डॉक्टर चुनें",
        "select_doctor_placeholder": "एक डॉक्टर चुनें...",
        "my_consultations": "मेरे परामर्श",
        "consultation_status": "परामर्श स्थिति",
        "requested": "अनुरोधित",
        "accepted": "स्वीकृत",
        "rejected": "अस्वीकृत",
        "completed": "पूर्ण",
        "no_consultations": "कोई परामर्श नहीं मिला",
        "view_details": "विवरण देखें",
        "consultation_details": "परामर्श विवरण",
        "doctor": "डॉक्टर",
        "reason": "कारण",
        "created": "बनाया गया",
        "no_doctor_available": "कोई डॉक्टर उपलब्ध नहीं"
    },
    "pa": {
        "app_title": "ਟੈਲੀਸੇਹਤ",
        "login_register": "ਲਾਗਿਨ/ਰਜਿਸਟਰ",
        "full_name": "ਪੂਰਾ ਨਾਮ",
        "select_role": "ਰੋਲ ਚੁਣੋ",
        "phone": "ਫੋਨ ਨੰਬਰ",
        "village": "ਪਿੰਡ/ਸ਼ਹਿਰ",
        "dob": "ਜਨਮ ਮਿਤੀ",
        "gender": "ਲਿੰਗ",
        "male": "ਮਰਦ",
        "female": "ਔਰਤ",
        "other": "ਹੋਰ",
        "submit": "ਜਮ੍ਹਾਂ ਕਰੋ",
        "welcome_back": "ਵਾਪਸ ਸਵਾਗਤ ਹੈ {}!",
        "registration_success": "ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਸਫਲ!",
        "fill_all_fields": "ਕਿਰਪਾ ਕਰਕੇ ਸਾਰੇ ਖੇਤਰ ਭਰੋ।",
        "patient": "ਮਰੀਜ਼",
        "doctor": "ਡਾਕਟਰ",
        "pharmacy": "ਫਾਰਮੇਸੀ",
        "patient_dashboard": "ਮਰੀਜ਼ ਡੈਸ਼ਬੋਰਡ",
        "doctor_dashboard": "ਡਾਕਟਰ ਡੈਸ਼ਬੋਰਡ",
        "pharmacy_dashboard": "ਫਾਰਮੇਸੀ ਡੈਸ਼ਬੋਰਡ",
        "patient_profile": "ਮਰੀਜ਼ ਪਰੋਫਾਈਲ",
        "request_consultation": "ਸਲਾਹ ਮਸ਼ਵਰਾ ਦੀ ਬੇਨਤੀ ਕਰੋ",
        "consultation_reason": "ਸਲਾਹ ਮਸ਼ਵਰੇ ਦਾ ਕਾਰਨ...",
        "request_consult_btn": "ਸਲਾਹ मशवरा बेनेती",
        "video_consultation": "ਵੀਡੀਓ ਸਲਾਹ ਮਸ਼ਵਰਾ",
        "ai_chatbot": "AI ਚੈਟਬੋਟ",
        "ask_symptoms": "ਆਪਣੇ ਲੱਛਣਾਂ ਬਾਰੇ ਪੁੱਛੋ...",
        "send": "ਭੇਜੋ",
        "medicine_availability": "ਦਵਾਈ ਉਪਲਬਧਤਾ",
        "medicine_name": "ਦਵਾਈ ਦਾ ਨਾਮ...",
        "search": "ਖੋਜੋ",
        "pending_consultations": "ਲੰਬਿਤ ਸਲਾਹ ਮਸ਼ਵਰੇ",
        "update_stock": "ਸਟਾਕ ਅੱਪਡੇਟ ਕਰੋ",
        "medicine_name_label": "ਦਵਾਈ ਦਾ ਨਾਮ",
        "quantity": "ਮਾਤਰਾ",
        "price": "ਕੀਮਤ",
        "update_stock_btn": "ਸਟਾਕ ਅੱਪਡੇਟ ਕਰੋ",
        "current_stock": "ਮੌਜੂਦਾ ਸਟਾਕ",
        "no_profile_data": "ਕੋਈ ਪਰੋਫਾਈल �ڈਾਟਾ ਨਹੀਂ",
        "no_pending_consultations": "ਕੋਈ ਲੰਬਿਤ ਸਲਾਹ मशवरे नहीं",
        "no_stock_records": "ਕੋਈ ਸਟਾਕ ਰਿਕਾਰਡ ਨਹੀਂ",
        "assistant_unavailable": "ਮਾਫ ਕਰਨਾ, ਸਹਾਇਕ ਇਸ ਸਮੇਂ ਉਪਲਬਧ ਨਹੀਂ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਬਾਅਦ ਵਿੱਚ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "consultation_requested": "ਸਲਾਹ मशवरा सफलतापूर्वक बेनेती की्ता गिआ!",
        "stock_updated": "ਸਟਾਕ ਸਫਲਤਾਪੂਰਵਕ ਅੱਪਡੇਟ ਕੀਤਾ ਗਿਆ!",
        "no_results": "ਕੋਈ ਨਤੀਜੇ ਨਹੀਂ ਮਿਲੇ",
        "enter_medicine_name": "ਕਿਰਪਾ ਕਰਕੇ ਦਵਾਈ ਦਾ ਨਾਮ ਦਰਜ ਕਰੋ",
        "join_consultation": "ਵੀਡੀਓ ਸਲਾਹ मशवरा ਵਿੱਚ ਸ਼ਾਮਲ ਹੋਵੋ",
        "consultation_instructions": "ਆਪਣੇ ਵੀਡੀਓ ਸਲਾਹ ਮਸ਼ਵਰਾ ਸੈਸ਼ਨ ਵਿੱਚ ਸ਼ਾਮਲ ਹੋਣ ਲਈ ਹੇਠਾਂ ਦਿੱਤੇ ਬਟਨ 'ਤੇ ਕਲਿੱਕ ਕਰੋ। ਯਕੀਨੀ ਬਣਾਓ ਕਿ ਤੁਹਾਡੇ ਕੋਲ ਕੰਮ ਕਰਨ ਵਾਲਾ ਕੈਮਰਾ ਅਤੇ ਮਾਈਕ੍ਰੋਫੋਨ ਹੈ।",
        "join_button": "ਹੁਣੇ ਜੁੜੋ",
        "dark_mode": "ਡਾਰਕ ਮੋਡ",
        "light_mode": "ਲਾਈਟ ਮੋਡ",
        "language": "ਭਾਸ਼ਾ",
        "accept": "ਸਵੀਕਾਰ ਕਰੋ",
        "reject": "ਰੱਦ ਕਰੋ",
        "patient_info": "ਮਰੀਜ਼ ਦੀ ਜਾਣਕਾਰੀ",
        "typing": "AI ਟਾਈਪ ਕਰ ਰਿਹਾ ਹੈ...",
        "loading": "ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...",
        "delete": "ਹਟਾਓ",
        "edit": "ਸੰਪਾਦਿਤ ਕਰੋ",
        "save": "ਸੇਵ ਕਰੋ",
        "actions": "ਕਾਰਰਵਾਈਆਂ",
        "appointments": "अपाइंटमेंटस",
        "schedule_appointment": "अपाइंटमैंट शैडिऊल करो",
        "appointment_date": "अपाइंटमैंट तारीख",
        "appointment_time": "अपाइंटमैंट समां",
        "health_metrics": "सिहत मैट्रिक्स",
        "blood_pressure": "ब्लड प्रैशर",
        "heart_rate": "दिल दी धड़कन",
        "temperature": "तापमान",
        "blood_sugar": "ब्लड शुगर",
        "add_metric": "मैट्रिक जोड़ो",
        "prescriptions": "प्रैस्क्रिप्शनस",
        "write_prescription": "प्रैस्क्रिप्शन लिखो",
        "order_tracking": "आर्डर ट्रैकिंग",
        "manage_schedule": "शैडिऊल प्रबंधित करो",
        "available_hours": "उपलब्ध घंटे",
        "day": "दिन",
        "start_time": "शुरू समां",
        "end_time": "समाप्ती समां",
        "add_slot": "समां सलाट जोड़ो",
        "upcoming": "आगामी",
        "past": "पिछले",
        "status": "स्थिती",
        "date": "तारीख",
        "time": "समां",
        "tracking_id": "ट्रैकिंग आईडी",
        "order_status": "आर्डर स्थिती",
        "track_order": "आर्डर ट्रैक करो",
        "consultation_accepted": "सलाह मशवरा स्वीकृत!",
        "consultation_rejected": "सलाह मशवरा अस्वीकृत!",
        "appointment_scheduled": "अपाइंटमैंट सफलतापूर्वक शैडिऊल किया गया!",
        "stock_deleted": "स्टॉक आइटम सफलतापूर्वक हटाया गया!",
        "error_occurred": "एक त्रुटि हुई। कृपया पुन: प्रयास करें।",
        "logout": "ਲਾਗ ਆਉਟ",
        "logout_success": "ਤੁਸੀਂ ਸਫਲਤਾਪੂਰਵਕ ਲਾਗ ਆਉਟ ਹੋ ਗਏ ਹੋ!",
        "upload_image": "ਤਸਵੀਰ ਅੱਪਲੋਡ ਕਰੋ",
        "image_analysis": "ਤਸਵੀਰ ਵਿਸ਼ਲੇਸ਼ਣ",
        "prescription_details": "प्रैस्क्रिप्शन विवरण",
        "medicine": "ਦਵਾਈ",
        "dosage": "ਖੁਰਾਕ",
        "instructions": "ਹਦਾਇਤਾਂ",
        "write_prescription_btn": "प्रैस्क्रिप्शन लिखो",
        "prescription_saved": "प्रैस्क्रिप्शन सफलतापूर्वक सहेजा गया!",
        "age": "ਉਮਰ",
        "years": "ਸਾਲ",
        "select_doctor": "ਡਾਕਟਰ ਚੁਣੋ",
        "select_doctor_placeholder": "ਇੱਕ ਡਾਕਟਰ ਚੁਣੋ...",
        "my_consultations": "ਮੇਰੇ ਸਲਾਹ-ਮਸ਼ਵਰੇ",
        "consultation_status": "ਸਲਾਹ-ਮਸ਼ਵਰਾ ਸਥਿਤੀ",
        "requested": "ਬੇਨਤੀ ਕੀਤੀ",
        "accepted": "ਸਵੀਕਾਰ ਕੀਤਾ",
        "rejected": "ਰੱਦ ਕੀਤਾ",
        "completed": "ਪੂਰਾ ਹੋਇਆ",
        "no_consultations": "ਕੋਈ ਸਲਾਹ-ਮਸ਼ਵਰੇ ਨਹੀਂ ਮਿਲੇ",
        "view_details": "ਵੇਰਵੇ ਦੇਖੋ",
        "consultation_details": "ਸਲਾਹ-ਮਸ਼ਵਰਾ ਵੇਰਵੇ",
        "doctor": "ਡਾਕਟਰ",
        "reason": "ਕਾਰਨ",
        "created": "ਬਣਾਇਆ ਗਿਆ",
        "no_doctor_available": "ਕੋਈ ਡਾਕਟਰ ਉਪਲਬਧ ਨਹੀਂ"
    },
    "te": {
        "app_title": "టెలిసెహత్",
        "login_register": "లాగిన్/నమోదు",
        "full_name": "పూర్తి పేరు",
        "select_role": "పాత్ర ఎంచుకోండి",
        "phone": "ఫోన్ నంబర్",
        "village": "గ్రామం/నగరం",
        "dob": "పుట్టిన తేదీ",
        "gender": "లింగం",
        "male": "పురుషుడు",
        "female": "స్త్రీ",
        "other": "ఇతర",
        "submit": "సమర్పించు",
        "welcome_back": "తిరిగి స్వాగతం {}!",
        "registration_success": "నమోదు విజయవంతమైంది!",
        "fill_all_fields": "దయచేసి అన్ని ఫీల్డ్లను పూరించండి.",
        "patient": "రోగి",
        "doctor": "డాక్టర్",
        "pharmacy": "ఫార్మసీ",
        "patient_dashboard": "రోగి డాష్బోర్డ్",
        "doctor_dashboard": "డాక్టర్ డాష్బోర్డ్",
        "pharmacy_dashboard": "ఫార్మసీ డాష్బోర్డ్",
        "patient_profile": "రోగి ప్రొఫైల్",
        "request_consultation": "సంప్రదింపు కోరండి",
        "consultation_reason": "సంప్రదింపు కారణం...",
        "request_consult_btn": "సంప్రదింపు అభ్యర్థన",
        "video_consultation": "వీడియో సంప్రదింపు",
        "ai_chatbot": "AI చాట్బాట్",
        "ask_symptoms": "మీ లక్షణాల గురించి అడగండి...",
        "send": "పంపు",
        "medicine_availability": "ఔషధ లభ్యత",
        "medicine_name": "ఔషధ పేరు...",
        "search": "వెతకండి",
        "pending_consultations": "పెండింగ్ సంప్రదింపులు",
        "update_stock": "స్టాక్ అప్డేట్ చేయండి",
        "medicine_name_label": "ఔషధ పేరు",
        "quantity": "పరిమాణం",
        "price": "ధర",
        "update_stock_btn": "స్టాక్ అప్డేట్ చేయండి",
        "current_stock": "ప్రస్తుత స్టాక్",
        "no_profile_data": "ప్రొఫైల్ డేటా లేదు",
        "no_pending_consultations": "పెండింగ్ సంప్రదింపులు లేవు",
        "no_stock_records": "స్టాక్ రికార్డులు లేవు",
        "assistant_unavailable": "క్షమించండి, సహాయకుడు ప్రస్తుతం అందుబాటులో లేదు. దయచేసి మళ్ళీ ప్రయత్నించండి.",
        "consultation_requested": "సంప్రదింపు విజయవంతంగా అభ్యర్థించబడింది!",
        "stock_updated": "స్టాక్ విజయవంతంగా అప్డేట్ చేయబడింది!",
        "no_results": "ఫలితాలు ఏమీ కనుగొనబడలేదు",
        "enter_medicine_name": "దయచేసి ఔషధ పేరు నమోదు చేయండి",
        "join_consultation": "వీడియో సంప్రదింపులో చేరండి",
        "consultation_instructions": "మీ వీడియో సంప్రదింపు సెషన్లో చేరడానికి దిగువ బటన్ను క్లిక్ చేయండి. మీకు పనిచేసే కెమెరా మరియు మైక్రోఫోన్ ఉన్నాయని నిర్ధారించుకోండి.",
        "join_button": "ఇప్పుడే చేరండి",
        "dark_mode": "డార్క్ మోడ్",
        "light_mode": "లైట్ మోడ్",
        "language": "భాష",
        "accept": "అంగీకరించు",
        "reject": "తిరస్కరించు",
        "patient_info": "రోగి సమాచారం",
        "typing": "AI టైప్ చేస్తోంది...",
        "loading": "లోడ్ అవుతోంది...",
        "delete": "తొలగించు",
        "edit": "సవరించు",
        "save": "సేవ్ చేయి",
        "actions": "చర్యలు",
        "appointments": "అపాయింట్మెంట్లు",
        "schedule_appointment": "అపాయింట్మెంట్ షెడ్యూల్ చేయండి",
        "appointment_date": "అపాయింట్మెంట్ తేదీ",
        "appointment_time": "అపాయింట్మెంట్ సమయం",
        "health_metrics": "ఆరోగ్య కొలమానాలు",
        "blood_pressure": "బ్లడ్ ప్రెషర్",
        "heart_rate": "గుండె చప్పుడు",
        "temperature": "ఉష్ణోగ్రత",
        "blood_sugar": "బ్లడ్ షుగర్",
        "add_metric": "కొలమానం జోడించు",
        "prescriptions": "ప్రిస్క్రిప్షన్లు",
        "write_prescription": "ప్రిస్క్రిప్షన్ రాయండి",
        "order_tracking": "ఆర్డర్ ట్రాకింగ్",
        "manage_schedule": "షెడ్యూల్ నిర్వహించండి",
        "available_hours": "అందుబాటులో ఉన్న గంటలు",
        "day": "రోజు",
        "start_time": "ప్రారంభ సమయం",
        "end_time": "ముగింపు సమయం",
        "add_slot": "సమయ స్లాట్ జోడించు",
        "upcoming": "రాబోయేవి",
        "past": "గత",
        "status": "స్థితి",
        "date": "తేదీ",
        "time": "సమయం",
        "tracking_id": "ట్రాకింగ్ ID",
        "order_status": "ఆర్డర్ స్థితి",
        "track_order": "ఆర్డర్ ట్రాక్ చేయండి",
        "consultation_accepted": "సంప్రదింపు ఆమోదించబడింది!",
        "consultation_rejected": "సంప్రదింపు తిరస్కరించబడింది!",
        "appointment_scheduled": "అపాయింట్మెంట్ విజయవంతంగా షెడ్యూల్ చేయబడింది!",
        "stock_deleted": "స్టాక్ అంశం విజయవంతంగా తొలగించబడింది!",
        "error_occurred": "లోపం సంభవించింది. దయచేసి మళ్ళీ ప్రయత్నించండి.",
        "logout": "లాగౌట్",
        "logout_success": "మీరు విజయవంతంగా లాగౌట్ అయ్యారు!",
        "upload_image": "చిత్రాన్ని అప్లోడ్ చేయండి",
        "image_analysis": "చిత్ర విశ్లేషణ",
        "prescription_details": "ప్రిస్క్రిప్షన్ వివరాలు",
        "medicine": "ఔషధం",
        "dosage": "మోతాదు",
        "instructions": "సూచనలు",
        "write_prescription_btn": "ప్రిస్క్రిప్షన్ రాయండి",
        "prescription_saved": "ప్రిస్క్రిప్షన్ విజయవంతంగా సేవ్ చేయబడింది!",
        "age": "వయస్సు",
        "years": "సంవత్సరాలు",
        "select_doctor": "డాక్టర్‌ను ఎంచుకోండి",
        "select_doctor_placeholder": "డాక్టర్‌ను ఎంచుకోండి...",
        "my_consultations": "నా సంప్రదింపులు",
        "consultation_status": "సంప్రదింపు స్థితి",
        "requested": "అభ్యర్థించబడింది",
        "accepted": "ఆమోదించబడింది",
        "rejected": "తిరస్కరించబడింది",
        "completed": "పూర్తయింది",
        "no_consultations": "సంప్రదింపులు ఏవీ కనుగొనబడలేదు",
        "view_details": "వివరాలు చూడండి",
        "consultation_details": "సంప్రదింపు వివరాలు",
        "doctor": "డాక్టర్",
        "reason": "కారణం",
        "created": "సృష్టించబడింది",
        "no_doctor_available": "డాక్టర్లు అందుబాటులో లేరు"
    }
}

# Initialize database (keep this as is)
def init_db():
    conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY, name TEXT, role TEXT, phone TEXT, 
                 village TEXT, dob TEXT, gender TEXT, created_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS consultations
                 (id TEXT PRIMARY KEY, patient_id TEXT, doctor_id TEXT,
                 status TEXT, reason TEXT, channel TEXT,
                 created_at TIMESTAMP, updated_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS pharmacy_stock
                 (id TEXT PRIMARY KEY, pharmacy_id TEXT, medicine TEXT,
                 qty INTEGER, price REAL, last_updated TIMESTAMP)''')
    
    # New tables for enhanced features
    c.execute('''CREATE TABLE IF NOT EXISTS appointments
                 (id TEXT PRIMARY KEY, patient_id TEXT, doctor_id TEXT,
                 date TEXT, time TEXT, reason TEXT, status TEXT,
                 created_at TIMESTAMP, updated_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS health_metrics
                 (id TEXT PRIMARY KEY, patient_id TEXT, blood_pressure TEXT,
                 heart_rate INTEGER, temperature REAL, blood_sugar REAL,
                 recorded_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS prescriptions
                 (id TEXT PRIMARY KEY, patient_id TEXT, doctor_id TEXT,
                 medicine TEXT, dosage TEXT, instructions TEXT,
                 prescribed_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS doctor_schedule
                 (id TEXT PRIMARY KEY, doctor_id TEXT, day TEXT,
                 start_time TEXT, end_time TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id TEXT PRIMARY KEY, patient_id TEXT, pharmacy_id TEXT,
                 medicine TEXT, qty INTEGER, status TEXT,
                 tracking_id TEXT, created_at TIMESTAMP, updated_at TIMESTAMP)''')
    
    # Insert some sample doctors
    c.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor'")
    if c.fetchone()[0] == 0:
        sample_doctors = [
            (str(uuid.uuid4()), 'Dr. Sharma', 'doctor', '9876543210', 'Delhi', '1975-05-15', 'male', datetime.now()),
            (str(uuid.uuid4()), 'Dr. Patel', 'doctor', '9876543211', 'Mumbai', '1980-08-22', 'female', datetime.now()),
            (str(uuid.uuid4()), 'Dr. Singh', 'doctor', '9876543212', 'Punjab', '1978-12-10', 'male', datetime.now()),
        ]
        c.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", sample_doctors)
    
    # Insert some sample pharmacy data
    c.execute("SELECT COUNT(*) FROM pharmacy_stock")
    if c.fetchone()[0] == 0:
        sample_data = [
            (str(uuid.uuid4()), 'pharmacy_1', 'Paracetamol', 100, 5.50, datetime.now()),
            (str(uuid.uuid4()), 'pharmacy_1', 'Amoxicillin', 50, 12.75, datetime.now()),
            (str(uuid.uuid4()), 'pharmacy_1', 'Ibuprofen', 75, 8.25, datetime.now()),
            (str(uuid.uuid4()), 'pharmacy_2', 'Paracetamol', 80, 5.25, datetime.now()),
            (str(uuid.uuid4()), 'pharmacy_2', 'Vitamin C', 120, 15.99, datetime.now()),
        ]
        c.executemany("INSERT INTO pharmacy_stock VALUES (?, ?, ?, ?, ?, ?)", sample_data)
    
    # Insert sample doctor schedule
    c.execute("SELECT COUNT(*) FROM doctor_schedule")
    if c.fetchone()[0] == 0:
        # Get doctor IDs
        c.execute("SELECT id FROM users WHERE role = 'doctor'")
        doctor_ids = [row[0] for row in c.fetchall()]
        
        if doctor_ids:
            sample_schedule = []
            for doctor_id in doctor_ids:
                sample_schedule.extend([
                    (str(uuid.uuid4()), doctor_id, 'Monday', '09:00', '17:00'),
                    (str(uuid.uuid4()), doctor_id, 'Tuesday', '09:00', '17:00'),
                    (str(uuid.uuid4()), doctor_id, 'Wednesday', '09:00', '17:00'),
                    (str(uuid.uuid4()), doctor_id, 'Thursday', '09:00', '17:00'),
                    (str(uuid.uuid4()), doctor_id, 'Friday', '09:00', '12:00'),
                ])
            c.executemany("INSERT INTO doctor_schedule VALUES (?, ?, ?, ?, ?)", sample_schedule)
    
    conn.commit()
    conn.close()

init_db()

# Custom CSS for additional styling (keep this as is)
custom_css = {
    "card": {
        "boxShadow": "0 4px 8px 0 rgba(0,0,0,0.1)",
        "borderRadius": "12px",
        "border": "none",
        "transition": "all 0.3s ease",
        "fontFamily": "'Inter', sans-serif"
    },
    "card_hover": {
        "boxShadow": "0 8px 16px 0 rgba(0,0,0,0.15)",
        "transform": "translateY(-5px)"
    },
    "navbar": {
        "boxShadow": "0 2px 4px 0 rgba(0,0,0,0.1)",
        "marginBottom": "20px",
        "fontFamily": "'Inter', sans-serif",
        "padding": "0.5rem 1rem"
    },
    "chatUser": {
        "backgroundColor": "#e3f2fd",
        "padding": "12px 16px",
        "borderRadius": "18px 18px 4px 18px",
        "marginBottom": "8px",
        "maxWidth": "80%",
        "marginLeft": "auto",
        "fontFamily": "'Inter', sans-serif",
        "color": "#1a56db"
    },
    "chatAI": {
        "backgroundColor": "#f3f4f6",
        "padding": "12px 16px",
        "borderRadius": "18px 18px 18px 4px",
        "marginBottom": "8px",
        "maxWidth": "80%",
        "fontFamily": "'Inter', sans-serif",
        "color": "#374151"
    },
    "tab_selected": {
        "backgroundColor": "#1a56db",
        "color": "white",
        "border": "none",
        "fontWeight": "600",
        "fontFamily": "'Inter', sans-serif",
        "borderRadius": "8px 8px 0 0"
    },
    "tab": {
        "backgroundColor": "#f9fafb",
        "color": "#6b7280",
        "border": "none",
        "fontFamily": "'Inter', sans-serif",
        "fontWeight": "500",
        "borderRadius": "8px 8px 0 0"
    },
    "primary_color": "#1a56db",
    "secondary_color": "#0e9f6e",
    "accent_color": "#9061f9",
    "light_bg": "#f9fafb"
}


# App layout - Updated with dynamic title and tabs
def create_layout():
    return html.Div([
        dbc.Container([
            # Toast notifications container
            html.Div(id="toast-container"),
            
            # Header/Navbar - Updated with dynamic title and logout button
            dbc.Navbar(
                [
                    dbc.Row([
                        dbc.Col([
                            html.H1([
                                html.I(className="fas fa-hospital me-2", style={"color": custom_css["primary_color"]}),
                                html.Span(id="app-title", style={"color": custom_css["primary_color"], "fontWeight": "700"})
                            ], className="d-flex align-items-center mb-0")
                        ], width="auto", className="me-auto"),
                        dbc.Col([
                            dcc.Dropdown(
                                id='language-selector',
                                options=[
                                    {'label': 'English', 'value': 'en'},
                                    {'label': 'Hindi', 'value': 'hi'},
                                    {'label': 'Punjabi', 'value': 'pa'},
                                    {'label': 'Telugu', 'value': 'te'}
                                ],
                                value='en',
                                clearable=False,
                                style={'width': '120px', 'marginRight': '10px'},
                                className="d-inline-block"
                            ),
                            # Logout button - conditionally shown based on user login status
                            html.Div(id="logout-button-container", className="d-inline-block")
                        ], width="auto", className="d-flex align-items-center")
                    ], align="center", className="g-0 w-100"),
                ],
                color="white",
                sticky="top",
                style=custom_css["navbar"],
                className="px-3"
            ),
            
            # Tabs - Will be populated dynamically based on login status and language
            dcc.Tabs(
                id='tabs', 
                value='tab-login',
                children=[],  # Will be populated by callback
                className="mb-3"
            ),
            
            # Tab content
            html.Div(id='tab-content', className='mt-4'),
            
            # Storage for user data, theme, and language
            dcc.Store(id='user-store', storage_type='session'),
            dcc.Store(id='language-store', data='en', storage_type='session'),
            dcc.Store(id='chat-history-store', data=[], storage_type='session'),
            dcc.Store(id='typing-indicator', data=False, storage_type='session'),
            dcc.Store(id='consultation-data', data={}, storage_type='session'),
            dcc.Store(id='appointment-data', data={}, storage_type='session'),
            dcc.Store(id='health-metrics-data', data={}, storage_type='session'),
            dcc.Store(id='pharmacy-stock-data', data={}, storage_type='session'),
            dcc.Store(id='prescription-data', data={}, storage_type='session'),
            dcc.Store(id='doctor-list-data', data={}, storage_type='session')
        ], fluid=True, className="py-3"),
        
        # Patient Info Modal
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(id="modal-title")),
                dbc.ModalBody(id="modal-body"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
                ),
            ],
            id="patient-modal",
            is_open=False,
            size="lg",
        ),
        
        # Appointment Modal
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(id="appointment-modal-title")),
                dbc.ModalBody([
                    dbc.Select(
                        id='appointment-doctor',
                        placeholder='Select Doctor...',
                        className='mb-2'
                    ),
                    dbc.Input(
                        id='appointment-date',
                        type='date',
                        className='mb-2'
                    ),
                    dbc.Input(
                        id='appointment-time',
                        type='time',
                        className='mb-2'
                    ),
                    dbc.Textarea(
                        id='appointment-reason',
                        placeholder='Reason for appointment...',
                        className='mb-2'
                    )
                ]),
                dbc.ModalFooter([
                    dbc.Button(
                        "Schedule", 
                        id="schedule-appointment-confirm", 
                        color="primary", 
                        className="me-2"
                    ),
                    dbc.Button(
                        "Close", 
                        id="close-appointment-modal", 
                        color="secondary"
                    )
                ]),
            ],
            id="appointment-modal",
            is_open=False,
        ),
        
        # Health Metrics Modal
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(id="health-metric-modal-title")),
                dbc.ModalBody([
                    dbc.Input(
                        id='bp-input', 
                        placeholder='Blood Pressure (e.g., 120/80)', 
                        type='text',
                        className='mb-2'
                    ),
                    dbc.Input(
                        id='hr-input', 
                        placeholder='Heart Rate (bpm)', 
                        type='number',
                        className='mb-2'
                    ),
                    dbc.Input(
                        id='temp-input', 
                        placeholder='Temperature (°C)', 
                        type='number',
                        step='0.1',
                        className='mb-2'
                    ),
                    dbc.Input(
                        id='sugar-input', 
                        placeholder='Blood Sugar (mg/dL)', 
                        type='number',
                        className='mb-2'
                    )
                ]),
                dbc.ModalFooter([
                    dbc.Button(
                        "Save", 
                        id="save-metric-btn", 
                        color="primary", 
                        className="me-2"
                    ),
                    dbc.Button(
                        "Close", 
                        id="close-metric-modal", 
                        color="secondary"
                    )
                ]),
            ],
            id="patient-metric-modal",
            is_open=False,
        ),
        
        # Prescription Modal
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(id="prescription-modal-title")),
                dbc.ModalBody([
                    dbc.Input(
                        id='prescription-medicine',
                        placeholder='Medicine name...',
                        className='mb-2'
                    ),
                    dbc.Input(
                        id='prescription-dosage',
                        placeholder='Dosage (e.g., 500mg twice daily)...',
                        className='mb-2'
                    ),
                    dbc.Textarea(
                        id='prescription-instructions',
                        placeholder='Additional instructions...',
                        className='mb-2'
                    )
                ]),
                dbc.ModalFooter([
                    dbc.Button(
                        "Save Prescription", 
                        id="save-prescription-btn", 
                        color="primary", 
                        className="me-2"
                    ),
                    dbc.Button(
                        "Close", 
                        id="close-prescription-modal", 
                        color="secondary"
                    )
                ]),
            ],
            id="prescription-modal",
            is_open=False,
            size="lg",
        ),
        
        # Consultation Details Modal
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(id="consultation-modal-title")),
                dbc.ModalBody(id="consultation-modal-body"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-consultation-modal", className="ms-auto", n_clicks=0)
                ),
            ],
            id="consultation-modal",
            is_open=False,
            size="lg",
        ),
    ], id="app-container", style={"fontFamily": "'Inter', sans-serif", "minHeight": "100vh", "backgroundColor": custom_css["light_bg"]})

app.layout = create_layout()

# Helper functions for database operations
def upsert_pharmacy_stock(conn, pharmacy_id, medicine, qty, price):
    """Insert or update pharmacy stock"""
    try:
        c = conn.cursor()
        # Check if medicine exists for this pharmacy
        c.execute("SELECT id FROM pharmacy_stock WHERE pharmacy_id = ? AND medicine = ?", 
                 (pharmacy_id, medicine))
        existing = c.fetchone()
        
        if existing:
            # Update existing record
            c.execute("UPDATE pharmacy_stock SET qty = ?, price = ?, last_updated = ? WHERE id = ?",
                     (qty, price, datetime.now(), existing[0]))
        else:
            # Insert new record
            stock_id = str(uuid.uuid4())
            c.execute("INSERT INTO pharmacy_stock VALUES (?, ?, ?, ?, ?, ?)",
                     (stock_id, pharmacy_id, medicine, qty, price, datetime.now()))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error upserting pharmacy stock: {e}")
        return False

def create_consultation(conn, patient_id, doctor_id, reason):
    """Create a new consultation request"""
    try:
        c = conn.cursor()
        consultation_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Insert new consultation with selected doctor_id and status 'requested'
        c.execute("INSERT INTO consultations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                 (consultation_id, patient_id, doctor_id, 'requested', reason, 'general', now, now))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating consultation: {e}")
        return False

def get_doctors(conn):
    """Get list of all doctors"""
    try:
        c = conn.cursor()
        c.execute("SELECT id, name FROM users WHERE role = 'doctor'")
        doctors = c.fetchall()
        return [{'label': doctor[1], 'value': doctor[0]} for doctor in doctors]
    except Exception as e:
        print(f"Error getting doctors: {e}")
        return []

def calculate_age(dob):
    """Calculate age from date of birth"""
    if not dob:
        return None
    today = date.today()
    birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# Callback for language selector → store propagation
@app.callback(
    Output('language-store', 'data'),
    Input('language-selector', 'value')
)
def set_language(language):
    """Update language store when language selector changes"""
    return language

# Callback for dynamic app title based on language
@app.callback(
    Output('app-title', 'children'),
    Input('language-store', 'data')
)
def update_app_title(language):
    return translations[language]["app_title"]

# Callback for logout button visibility
@app.callback(
    Output('logout-button-container', 'children'),
    Input('user-store', 'data'),
    Input('language-store', 'data')
)
def update_logout_button(user_data, language):
    """Show logout button only when user is logged in"""
    if user_data:
        return dbc.Button(
            [
                html.I(className="fas fa-sign-out-alt me-2"),
                translations[language]["logout"]
            ],
            id='logout-btn',
            color='secondary',
            className='ms-2',
            style={"borderRadius": "8px", "padding": "6px 12px"}
        )
    return None

# Callback for logout functionality
@app.callback(
    Output('user-store', 'data', allow_duplicate=True),
    Output('chat-history-store', 'data', allow_duplicate=True),
    Output('consultation-data', 'data', allow_duplicate=True),
    Output('appointment-data', 'data', allow_duplicate=True),
    Output('health-metrics-data', 'data', allow_duplicate=True),
    Output('pharmacy-stock-data', 'data', allow_duplicate=True),
    Output('toast-container', 'children', allow_duplicate=True),
    Output('tabs', 'value', allow_duplicate=True),
    Input('logout-btn', 'n_clicks'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def handle_logout(n_clicks, language):
    """Handle user logout by clearing all session data"""
    if n_clicks:
        # Create logout success toast
        toast = dbc.Toast(
            translations[language]["logout_success"],
            header="Success",
            icon="success",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        
        # Clear all session data and return to login tab
        return None, [], {}, {}, {}, {}, toast, 'tab-login'
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback for dynamic tabs based on login status and language
@app.callback(
    Output('tabs', 'children'),
    Output('tabs', 'value'),
    Input('user-store', 'data'),
    Input('language-store', 'data')
)
def update_tabs(user_data, language):
    # If no user is logged in, show only the login tab
    if not user_data:
        login_tab = dcc.Tab(
            label=translations[language]["login_register"],
            value='tab-login',
            className="custom-tab",
            selected_className="custom-tab--selected",
            style=custom_css["tab"],
            selected_style=custom_css["tab_selected"]
        )
        return [login_tab], 'tab-login'
    
    # If user is logged in, show tabs based on role (no login tab)
    tabs = []
    
    # Always show patient dashboard tab for patients
    if user_data.get('role') == 'patient':
        tabs.append(dcc.Tab(
            label=translations[language]["patient_dashboard"],
            value='tab-patient',
            className="custom-tab",
            selected_className="custom-tab--selected",
            style=custom_css["tab"],
            selected_style=custom_css["tab_selected"]
        ))
    
    # Always show doctor dashboard tab for doctors
    if user_data.get('role') == 'doctor':
        tabs.append(dcc.Tab(
            label=translations[language]["doctor_dashboard"],
            value='tab-doctor',
            className="custom-tab",
            selected_className="custom-tab--selected",
            style=custom_css["tab"],
            selected_style=custom_css["tab_selected"]
        ))
    
    # Always show pharmacy dashboard tab for pharmacies
    if user_data.get('role') == 'pharmacy':
        tabs.append(dcc.Tab(
            label=translations[language]["pharmacy_dashboard"],
            value='tab-pharmacy',
            className="custom-tab",
            selected_className="custom-tab--selected",
            style=custom_css["tab"],
            selected_style=custom_css["tab_selected"]
        ))
    
    # Set active tab based on user role
    if user_data.get('role') == 'patient':
        return tabs, 'tab-patient'
    elif user_data.get('role') == 'doctor':
        return tabs, 'tab-doctor'
    elif user_data.get('role') == 'pharmacy':
        return tabs, 'tab-pharmacy'
    
    return tabs, 'tab-login'

# Login/Register form
def login_form(translations):
    return dbc.Card([
        dbc.CardHeader([
            html.H4([
                html.I(className="fas fa-user-circle me-2"),
                translations["login_register"]
            ], className="mb-0 d-flex align-items-center"),
        ], className='text-white', style={"backgroundColor": custom_css["primary_color"], "borderRadius": "12px 12px 0 0"}),
        dbc.CardBody([
            dbc.Input(
                id='name-input', 
                placeholder=translations["full_name"], 
                type='text', 
                className='mb-3',
                style={"borderRadius": "8px"}
            ),
            dbc.Select(
                id='role-select',
                options=[
                    {'label': translations["patient"], 'value': 'patient'},
                    {'label': translations["doctor"], 'value': 'doctor'},
                    {'label': translations["pharmacy"], 'value': 'pharmacy'}
                ],
                placeholder=translations["select_role"],
                className='mb-3',
                style={"borderRadius": "8px"}
            ),
            dbc.Input(
                id='phone-input', 
                placeholder=translations["phone"], 
                type='tel', 
                className='mb-3',
                style={"borderRadius": "8px"}
            ),
            dbc.Input(
                id='village-input', 
                placeholder=translations["village"], 
                type='text', 
                className='mb-3',
                style={"borderRadius": "8px"}
            ),
            dbc.Input(
                id='dob-input', 
                placeholder=translations["dob"], 
                type='date', 
                className='mb-3',
                style={"borderRadius": "8px"}
            ),
            dbc.Select(
                id='gender-select',
                options=[
                    {'label': translations["male"], 'value': 'male'},
                    {'label': translations["female"], 'value': 'female'},
                    {'label': translations["other"], 'value': 'other'}
                ],
                placeholder=translations["gender"],
                className='mb-3',
                style={"borderRadius": "8px"}
            ),
            dbc.Button(
                [
                    html.I(className="fas fa-sign-in-alt me-2"),
                    translations["submit"]
                ], 
                id='login-btn', 
                color='primary', 
                className='w-100',
                style={"backgroundColor": custom_css["primary_color"], "border": "none", "borderRadius": "8px", "padding": "10px"}
            ),
            html.Div(id='login-message', className='mt-3')
        ])
    ], style=custom_css["card"], className="hover-card")

# Patient dashboard
def patient_dashboard(translations):
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-user me-2"),
                        translations["patient_profile"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["primary_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody(id='patient-profile')
            ], style=custom_css["card"], className='mb-4 hover-card'),
            
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-stethoscope me-2"),
                        translations["request_consultation"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["primary_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    dbc.Select(
                        id='consultation-doctor',
                        placeholder=translations["select_doctor_placeholder"],
                        className='mb-3'
                    ),
                    dbc.Textarea(
                        id='consult-reason', 
                        placeholder=translations["consultation_reason"], 
                        className='mb-3',
                        style={"borderRadius": "8px", "minHeight": "100px"}
                    ),
                    dbc.Button(
                        [
                            html.I(className="fas fa-calendar-check me-2"),
                            translations["request_consult_btn"]
                        ], 
                        id='request-consult-btn', 
                        color='primary', 
                        className='w-100',
                        style={"backgroundColor": custom_css["primary_color"], "border": "none", "borderRadius": "8px", "padding": "10px"}
                    )
                ])
            ], style=custom_css["card"], className='mb-4 hover-card'),
            
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-video me-2"),
                        translations["video_consultation"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["primary_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    html.Div([
                        html.Img(
                            src="/assets/video-placeholder.jpg",
                            style={"width": "100%", "borderRadius": "10px", "marginBottom": "15px"}
                        ),
                        html.P(translations["consultation_instructions"], className="text-muted"),
                        dbc.Button(
                            [
                                html.I(className="fas fa-video me-2"),
                                translations["join_button"]
                            ], 
                            id='join-consult-btn', 
                            color='primary', 
                            className='w-100 mt-3',
                            href='https://meet.jit.si/TelesehatDemo',
                            target='_blank',
                            style={"backgroundColor": custom_css["primary_color"], "border": "none", "borderRadius": "8px", "padding": "10px"}
                        ),
                        html.P(f"Agora App ID: {AGORA_APP_ID}", className='mt-3 text-muted small')
                    ])
                ])
            ], style=custom_css["card"], className="hover-card")
        ], width=12, lg=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-robot me-2"),
                        translations["ai_chatbot"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["secondary_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    html.Div(
                        id='chat-history', 
                        style={
                            'height': '300px', 
                            'overflowY': 'auto', 
                            'marginBottom': '15px',
                            'padding': '10px',
                            'backgroundColor': '#f8f9fa',
                            'borderRadius': '8px'
                        }
                    ),
                    html.Div(id="typing-indicator", style={"display": "none", "marginBottom": "10px"}, children=[
                        html.Div([
                            html.Span(translations["typing"], className="text-muted"),
                            html.Div(className="typing-dots", style={"display": "inline-block", "marginLeft": "5px"})
                        ], style=custom_css["chatAI"])
                    ]),
                    dcc.Upload(
                        id='upload-image',
                        children=dbc.Button([
                            html.I(className="fas fa-image me-2"),
                            translations["upload_image"]
                        ], color="secondary", size="sm", className="me-2"),
                        multiple=False
                    ),
                    dbc.InputGroup([
                        dbc.Input(
                            id='chat-input', 
                            placeholder=translations["ask_symptoms"],
                            className="border-end-0",
                            style={"borderRadius": "8px 0 0 8px"}
                        ),
                        dbc.Button(
                            [
                                html.I(className="fas fa-paper-plane me-1"),
                                translations["send"]
                            ], 
                            id='chat-send-btn', 
                            color='success',
                            className="border-start-0",
                            style={"backgroundColor": custom_css["secondary_color"], "border": "none", "borderRadius": "0 8px 8px 0"}
                        )
                    ])
                ])
            ], style=custom_css["card"], className='mb-4 hover-card'),
            
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-pills me-2"),
                        translations["medicine_availability"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["secondary_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    dbc.InputGroup([
                        dbc.Input(
                            id='medicine-search', 
                            placeholder=translations["medicine_name"],
                            className="border-end-0",
                            style={"borderRadius": "8px 0 0 8px"}
                        ),
                        dbc.Button(
                            [
                                html.I(className="fas fa-search me-1"),
                                translations["search"]
                            ], 
                            id='medicine-search-btn', 
                            color='success',
                            className="border-start-0",
                            style={"backgroundColor": custom_css["secondary_color"], "border": "none", "borderRadius": "0 8px 8px 0"}
                        )
                    ]),
                    html.Div(id='medicine-results', className='mt-3')
                ])
            ], style=custom_css["card"], className="hover-card")
        ], width=12, lg=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-calendar-check me-2"),
                        translations["appointments"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["accent_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    dcc.Tabs([
                        dcc.Tab(
                            label=translations["upcoming"],
                            children=html.Div(id='upcoming-appointments', className='mt-3')
                        ),
                        dcc.Tab(
                            label=translations["past"],
                            children=html.Div(id='past-appointments', className='mt-3')
                        ),
                    ]),
                    dbc.Button(
                        [
                            html.I(className="fas fa-plus me-2"),
                            translations["schedule_appointment"]
                        ],
                        id='schedule-appointment-btn',
                        color='primary',
                        className='w-100 mt-3',
                        style={"backgroundColor": custom_css["accent_color"], "border": "none", "borderRadius": "8px", "padding": "10px"}
                    )
                ])
            ], style=custom_css["card"], className='mb-4 hover-card'),
            
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-heartbeat me-2"),
                        translations["health_metrics"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["accent_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    html.Div(id='health-metrics-chart'),
                    dbc.Button(
                        [
                            html.I(className="fas fa-plus me-2"),
                            translations["add_metric"]
                        ],
                        id='add-metric-btn',
                        color='primary',
                        className='w-100 mt-3',
                        style={"backgroundColor": custom_css["accent_color"], "border": "none", "borderRadius": "8px", "padding": "10px"}
                    )
                ])
            ], style=custom_css["card"], className="hover-card"),
            
            # New card for patient consultations
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-comments me-2"),
                        translations["my_consultations"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["accent_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    html.Div(id='patient-consultations', className='mt-3')
                ])
            ], style=custom_css["card"], className="hover-card")
        ], width=12, lg=4)
    ])

# Doctor dashboard
def doctor_dashboard(translations):
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="fas fa-clock me-2"),
                        translations["pending_consultations"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["primary_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    html.Div(id='consultations-table'),
                    html.Div(id='doctor-message')
                ])
            ], style=custom_css["card"], className="mb-4 hover-card"),
            
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="fas fa-calendar me-2"),
                        translations["manage_schedule"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["primary_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    html.Div(id='doctor-schedule-table'),
                    dbc.Button(
                        [
                            html.I(className="fas fa-plus me-2"),
                            translations["add_slot"]
                        ],
                        id='add-schedule-btn',
                        color='primary',
                        className='w-100 mt-3',
                        style={"backgroundColor": custom_css["primary_color"], "border": "none", "borderRadius": "8px", "padding": "10px"}
                    )
                ])
            ], style=custom_css["card"], className="hover-card")
        ], width=12, lg=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="fas fa-prescription me-2"),
                        translations["prescriptions"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["secondary_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    html.Div(id='prescriptions-table'),
                    dbc.Button(
                        [
                            html.I(className="fas fa-plus me-2"),
                            translations["write_prescription"]
                        ],
                        id='write-prescription-btn',
                        color='primary',
                        className='w-100 mt-3',
                        style={"backgroundColor": custom_css["secondary_color"], "border": "none", "borderRadius": "8px", "padding": "10px"}
                    )
                ])
            ], style=custom_css["card"], className="mb-4 hover-card"),
            
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="fas fa-calendar-alt me-2"),
                        translations["appointments"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["secondary_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    dcc.Tabs([
                        dcc.Tab(
                            label=translations["upcoming"],
                            children=html.Div(id='doctor-upcoming-appointments', className='mt-3')
                        ),
                        dcc.Tab(
                            label=translations["past"],
                            children=html.Div(id='doctor-past-appointments', className='mt-3')
                        ),
                    ])
                ])
            ], style=custom_css["card"], className="hover-card")
        ], width=12, lg=6)
    ])

# Pharmacy dashboard
def pharmacy_dashboard(translations):
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-edit me-2"),
                        translations["update_stock"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["primary_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    dbc.Input(
                        id='medicine-name', 
                        placeholder=translations["medicine_name_label"], 
                        className='mb-3',
                        style={"borderRadius": "8px"}
                    ),
                    dbc.Input(
                        id='medicine-qty', 
                        placeholder=translations["quantity"], 
                        type='number', 
                        className='mb-3',
                        style={"borderRadius": "8px"}
                    ),
                    dbc.Input(
                        id='medicine-price', 
                        placeholder=translations["price"], 
                        type='number', 
                        step='0.01', 
                        className='mb-3',
                        style={"borderRadius": "8px"}
                    ),
                    dbc.Button(
                        [
                            html.I(className="fas fa-save me-2"),
                            translations["update_stock_btn"]
                        ], 
                        id='update-stock-btn', 
                        color='primary', 
                        className='w-100',
                        style={"backgroundColor": custom_css["primary_color"], "border": "none", "borderRadius": "8px", "padding": "10px"}
                    )
                ])
            ], style=custom_css["card"], className='mb-3 hover-card')
        ], width=12, md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-database me-2"),
                        translations["current_stock"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["primary_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    dbc.InputGroup([
                        dbc.Input(
                            id='stock-search', 
                            placeholder="Search medicines...",
                            className="border-end-0",
                            style={"borderRadius": "8px 0 0 8px"}
                        ),
                        dbc.Button(
                            html.I(className="fas fa-search"), 
                            id='stock-search-btn', 
                            color='primary',
                            className="border-start-0",
                            style={"backgroundColor": custom_css["primary_color"], "border": "none", "borderRadius": "0 8px 8px 0"}
                        )
                    ]),
                    html.Div(id='pharmacy-stock-table', className='mt-3')
                ])
            ], style=custom_css["card"], className='mb-3 hover-card'),
            
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-truck me-2"),
                        translations["order_tracking"]
                    ], className="mb-0 d-flex align-items-center"),
                ], className='text-white', style={"backgroundColor": custom_css["secondary_color"], "borderRadius": "12px 12px 0 0" }),
                dbc.CardBody([
                    dbc.InputGroup([
                        dbc.Input(
                            id='order-tracking-id', 
                            placeholder=translations["tracking_id"],
                            className="border-end-0",
                            style={"borderRadius": "8px 0 0 8px"}
                        ),
                        dbc.Button(
                            [
                                html.I(className="fas fa-search me-1"),
                                translations["track_order"]
                            ], 
                            id='track-order-btn', 
                            color='primary',
                            className="border-start-0",
                            style={"backgroundColor": custom_css["secondary_color"], "border": "none", "borderRadius": "0 8px 8px 0"}
                        )
                    ]),
                    html.Div(id='order-tracking-result', className='mt-3')
                ])
            ], style=custom_css["card"], className="hover-card")
        ], width=12, md=8)
    ])

# Callbacks
@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value'),
    Input('user-store', 'data'),
    Input('language-store', 'data')
)
def render_tab(tab, user_data, language):
    # If no user is logged in and trying to access non-login tab, show empty
    if not user_data and tab != 'tab-login':
        return html.Div()
    
    if tab == 'tab-login':
        return login_form(translations[language])
    elif tab == 'tab-patient':
        if user_data and user_data.get('role') == 'patient':
            return patient_dashboard(translations[language])
        return html.Div("Please login as a patient.", className="alert alert-warning")
    elif tab == 'tab-doctor':
        if user_data and user_data.get('role') == 'doctor':
            return doctor_dashboard(translations[language])
        return html.Div("Please login as a doctor.", className="alert alert-warning")
    elif tab == 'tab-pharmacy':
        if user_data and user_data.get('role') == 'pharmacy':
            return pharmacy_dashboard(translations[language])
        return html.Div("Please login as a pharmacy.", className="alert alert-warning")
    return html.Div()

@app.callback(
    Output('user-store', 'data'),
    Output('login-message', 'children'),
    Output('toast-container', 'children', allow_duplicate=True),
    Output('tabs', 'value', allow_duplicate=True),  # NEW: Added to switch tabs after login
    Input('login-btn', 'n_clicks'),
    State('name-input', 'value'),
    State('role-select', 'value'),
    State('phone-input', 'value'),
    State('village-input', 'value'),
    State('dob-input', 'value'),
    State('gender-select', 'value'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def handle_login(n_clicks, name, role, phone, village, dob, gender, language):
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
    if not all([name, role, phone, village, dob, gender]):
        toast = dbc.Toast(
            translations[language]["fill_all_fields"],
            header="Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return dash.no_update, dbc.Alert(translations[language]["fill_all_fields"], color="danger"), toast, dash.no_update
    
    conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    
    # Check if user exists
    c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    user = c.fetchone()
    
    if user:
        user_data = {
            'id': user[0],
            'name': user[1],
            'role': user[2],
            'phone': user[3],
            'village': user[4],
            'dob': user[5],
            'gender': user[6]
        }
        message = dbc.Alert(translations[language]["welcome_back"].format(user[1]), color="success")
        toast = dbc.Toast(
            translations[language]["welcome_back"].format(user[1]),
            header="Welcome",
            icon="success",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        # Set tab based on role
        tab_value = f'tab-{user[2]}'
    else:
        user_id = str(uuid.uuid4())
        created_at = datetime.now()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                 (user_id, name, role, phone, village, dob, gender, created_at))
        conn.commit()
        
        user_data = {
            'id': user_id,
            'name': name,
            'role': role,
            'phone': phone,
            'village': village,
            'dob': dob,
            'gender': gender
        }
        message = dbc.Alert(translations[language]["registration_success"], color="success")
        toast = dbc.Toast(
            translations[language]["registration_success"],
            header="Success",
            icon="success",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        # Set tab based on role
        tab_value = f'tab-{role}'
    
    conn.close()
    return user_data, message, toast, tab_value

@app.callback(
    Output('patient-profile', 'children'),
    Input('user-store', 'data'),
    Input('language-store', 'data')
)
def update_patient_profile(user_data, language):
    if user_data and user_data.get('role') == 'patient':
        age = calculate_age(user_data.get('dob'))
        age_display = f"{translations[language]['age']}: {age} {translations[language]['years']}" if age else ""
        
        return [
            html.H5(user_data['name']),
            html.P(f"{translations[language]['phone']}: {user_data['phone']}"),
            html.P(f"{translations[language]['village']}: {user_data['village']}"),
            html.P(f"{translations[language]['gender']}: {user_data['gender']}"),
            html.P(age_display) if age_display else None
        ]
    return translations[language]["no_profile_data"]

# Get doctors for dropdown
@app.callback(
    Output('consultation-doctor', 'options'),
    Output('appointment-doctor', 'options'),
    Input('user-store', 'data'),
    Input('language-store', 'data')
)
def get_doctors_list(user_data, language):
    if not user_data or user_data.get('role') != 'patient':
        return [], []
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        doctors = get_doctors(conn)
        conn.close()
        
        if not doctors:
            return [{'label': translations[language]["no_doctor_available"], 'value': 'none', 'disabled': True}], [{'label': translations[language]["no_doctor_available"], 'value': 'none', 'disabled': True}]
        
        return doctors, doctors
    except Exception as e:
        print(f"Error getting doctors: {e}")
        return [], []

# Consultation request flow callback
@app.callback(
    Output('toast-container', 'children', allow_duplicate=True),
    Output('consultation-data', 'data', allow_duplicate=True),
    Input('request-consult-btn', 'n_clicks'),
    State('consult-reason', 'value'),
    State('consultation-doctor', 'value'),
    State('user-store', 'data'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def request_consultation(n_clicks, reason, doctor_id, user_data, language):
    """Handle consultation request from patient"""
    if not n_clicks or not reason or not doctor_id:
        return dash.no_update, dash.no_update
    
    if not user_data or user_data.get('role') != 'patient':
        return dash.no_update, dash.no_update
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        
        # Create consultation using helper function
        success = create_consultation(conn, user_data['id'], doctor_id, reason)
        conn.close()
        
        if success:
            toast = dbc.Toast(
                translations[language]["consultation_requested"],
                header="Success",
                icon="success",
                dismissable=True,
                is_open=True,
                duration=4000,
                style={"position": "fixed", "top": 10, "right": 10, "width": 350}
            )
            return toast, {'updated': True}
        else:
            raise Exception("Failed to create consultation")
            
    except Exception as e:
        print(f"Error requesting consultation: {e}")
        toast = dbc.Toast(
            translations[language]["error_occurred"],
            header="Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return toast, dash.no_update

@app.callback(
    Output('consultations-table', 'children'),
    Input('user-store', 'data'),
    Input('tabs', 'value'),
    Input('language-store', 'data'),
    Input('consultation-data', 'data')
)
def update_consultations_table(user_data, tab, language, consultation_data):
    if user_data and user_data.get('role') == 'doctor' and tab == 'tab-doctor':
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        df = pd.read_sql_query(
            "SELECT c.id, u.name, c.reason, c.status, c.created_at FROM consultations c JOIN users u ON c.patient_id = u.id WHERE c.doctor_id = ? ORDER BY c.created_at DESC",
            conn, params=(user_data['id'],)
        )
        conn.close()
        
        if df.empty:
            return html.P(translations[language]["no_pending_consultations"])
        
        # Create a table with action buttons
        table_data = []
        for _, row in df.iterrows():
            # Only show action buttons for requested consultations
            actions = []
            if row['status'] == 'requested':
                actions.extend([
                    dbc.Button(
                        html.I(className="fas fa-check"),
                        id={'type': 'accept-btn', 'index': row['id']},
                        color="success",
                        size="sm",
                        className="me-1"
                    ),
                    dbc.Button(
                        html.I(className="fas fa-times"),
                        id={'type': 'reject-btn', 'index': row['id']},
                        color="danger",
                        size="sm",
                        className="me-1"
                    )
                ])
            
            actions.append(
                dbc.Button(
                    html.I(className="fas fa-info"),
                    id={'type': 'info-btn', 'index': row['id']},
                    color="info",
                    size="sm"
                )
            )
            
            table_data.append({
                'id': row['id'],
                'name': row['name'],
                'reason': row['reason'],
                'status': row['status'],
                'created': row['created_at'],
                'actions': html.Div(actions)
            })
        
        return dash_table.DataTable(
            columns=[
                {'name': 'Patient Name', 'id': 'name'},
                {'name': 'Reason', 'id': 'reason'},
                {'name': 'Status', 'id': 'status'},
                {'name': 'Created', 'id': 'created'},
                {'name': 'Actions', 'id': 'actions'}
            ],
            data=table_data,
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={
                'backgroundColor': 'lightgrey', 
                'fontWeight': 'bold',
                'padding': '10px'
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            page_size=10
        )
    return dash.no_update

# Doctor consultation action callbacks
@app.callback(
    Output('toast-container', 'children', allow_duplicate=True),
    Output('consultation-data', 'data', allow_duplicate=True),
    Input({'type': 'accept-btn', 'index': ALL}, 'n_clicks'),
    Input({'type': 'reject-btn', 'index': ALL}, 'n_clicks'),
    State('user-store', 'data'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def handle_consultation_actions(accept_clicks, reject_clicks, user_data, language):
    """Handle accept/reject actions for consultations"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    # Get the button that was clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    button_info = json.loads(button_id.replace("'", '"'))
    
    consultation_id = button_info['index']
    action = button_info['type']
    
    if not user_data or user_data.get('role') != 'doctor':
        return dash.no_update, dash.no_update
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        
        if action == 'accept-btn':
            # Update consultation status to accepted
            c.execute("UPDATE consultations SET status = 'accepted', updated_at = ? WHERE id = ?",
                     (datetime.now(), consultation_id))
            message = translations[language]["consultation_accepted"]
        elif action == 'reject-btn':
            # Update consultation status to rejected
            c.execute("UPDATE consultations SET status = 'rejected', updated_at = ? WHERE id = ?",
                     (datetime.now(), consultation_id))
            message = translations[language]["consultation_rejected"]
        else:
            conn.close()
            return dash.no_update, dash.no_update
        
        conn.commit()
        conn.close()
        
        toast = dbc.Toast(
            message,
            header="Success",
            icon="success",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return toast, {'updated': True}
        
    except Exception as e:
        print(f"Error handling consultation action: {e}")
        toast = dbc.Toast(
            translations[language]["error_occurred"],
            header="Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return toast, dash.no_update

# Patient consultations display
@app.callback(
    Output('patient-consultations', 'children'),
    Input('user-store', 'data'),
    Input('consultation-data', 'data'),
    Input('language-store', 'data')
)
def update_patient_consultations(user_data, consultation_data, language):
    """Update patient consultations list"""
    if not user_data or user_data.get('role') != 'patient':
        return html.Div()
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        df = pd.read_sql_query(
            "SELECT c.id, u.name as doctor_name, c.reason, c.status, c.created_at FROM consultations c JOIN users u ON c.doctor_id = u.id WHERE c.patient_id = ? ORDER BY c.created_at DESC",
            conn, params=(user_data['id'],)
        )
        conn.close()
        
        if df.empty:
            return html.P(translations[language]["no_consultations"])
        
        consultations = []
        for _, row in df.iterrows():
            # Determine status color
            status_color = "secondary"
            if row['status'] == 'accepted':
                status_color = "success"
            elif row['status'] == 'rejected':
                status_color = "danger"
            elif row['status'] == 'requested':
                status_color = "warning"
            
            consultations.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H6(f"{translations[language]['doctor']}: {row['doctor_name']}", className="card-subtitle"),
                        html.P(f"{translations[language]['reason']}: {row['reason']}"),
                        html.P(f"{translations[language]['created']}: {row['created_at']}"),
                        dbc.Badge(
                            row['status'], 
                            color=status_color, 
                            className="me-1"
                        ),
                        dbc.Button(
                            translations[language]["view_details"],
                            id={'type': 'view-consultation-btn', 'index': row['id']},
                            color="primary",
                            size="sm",
                            className="mt-2"
                        )
                    ])
                ], className="mb-2")
            )
        
        return html.Div(consultations)
        
    except Exception as e:
        print(f"Error loading patient consultations: {e}")
        return html.P(translations[language]["error_occurred"])

# Consultation details modal
@app.callback(
    Output('consultation-modal', 'is_open'),
    Output('consultation-modal-title', 'children'),
    Output('consultation-modal-body', 'children'),
    Input({'type': 'view-consultation-btn', 'index': ALL}, 'n_clicks'),
    Input({'type': 'info-btn', 'index': ALL}, 'n_clicks'),
    Input('close-consultation-modal', 'n_clicks'),
    State('user-store', 'data'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def toggle_consultation_modal(view_clicks, info_clicks, close_clicks, user_data, language):
    ctx = callback_context
    if not ctx.triggered:
        return False, "", ""
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'close-consultation-modal':
        return False, "", ""
    
    # Get consultation ID from button click
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id.startswith("{"):
        button_info = json.loads(button_id.replace("'", '"'))
        consultation_id = button_info['index']
        
        try:
            conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
            c = conn.cursor()
            
            if user_data and user_data.get('role') == 'patient':
                # Patient view - show doctor info
                c.execute("""
                    SELECT c.*, u.name as doctor_name, u.phone as doctor_phone 
                    FROM consultations c 
                    JOIN users u ON c.doctor_id = u.id 
                    WHERE c.id = ? AND c.patient_id = ?
                """, (consultation_id, user_data['id']))
            elif user_data and user_data.get('role') == 'doctor':
                # Doctor view - show patient info
                c.execute("""
                    SELECT c.*, u.name as patient_name, u.phone as patient_phone, u.dob as patient_dob, u.gender as patient_gender 
                    FROM consultations c 
                    JOIN users u ON c.patient_id = u.id 
                    WHERE c.id = ? AND c.doctor_id = ?
                """, (consultation_id, user_data['id']))
            else:
                conn.close()
                return False, "", ""
            
            consultation = c.fetchone()
            conn.close()
            
            if consultation:
                if user_data.get('role') == 'patient':
                    modal_title = translations[language]["consultation_details"]
                    modal_body = [
                        html.P(f"{translations[language]['doctor']}: {consultation[8]}"),
                        html.P(f"{translations[language]['phone']}: {consultation[9]}"),
                        html.P(f"{translations[language]['reason']}: {consultation[4]}"),
                        html.P(f"{translations[language]['status']}: {consultation[3]}"),
                        html.P(f"{translations[language]['created']}: {consultation[6]}"),
                    ]
                else:  # Doctor view
                    modal_title = translations[language]["patient_info"]
                    age = calculate_age(consultation[9]) if consultation[9] else None
                    age_display = f"{translations[language]['age']}: {age} {translations[language]['years']}" if age else ""
                    
                    modal_body = [
                        html.P(f"{translations[language]['patient']}: {consultation[8]}"),
                        html.P(f"{translations[language]['phone']}: {consultation[9]}"),
                        html.P(f"{translations[language]['gender']}: {consultation[11]}"),
                        html.P(age_display) if age_display else None,
                        html.P(f"{translations[language]['reason']}: {consultation[4]}"),
                        html.P(f"{translations[language]['status']}: {consultation[3]}"),
                        html.P(f"{translations[language]['created']}: {consultation[6]}"),
                    ]
                
                return True, modal_title, modal_body
        
        except Exception as e:
            print(f"Error loading consultation details: {e}")
    
    return False, "", ""

# Pharmacy stock update callback
@app.callback(
    Output('toast-container', 'children', allow_duplicate=True),
    Output('pharmacy-stock-data', 'data', allow_duplicate=True),
    Input('update-stock-btn', 'n_clicks'),
    State('medicine-name', 'value'),
    State('medicine-qty', 'value'),
    State('medicine-price', 'value'),
    State('user-store', 'data'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def update_stock(n_clicks, medicine, qty, price, user_data, language):
    """Update pharmacy stock - insert or update medicine"""
    if not n_clicks or not medicine or not qty or not price:
        return dash.no_update, dash.no_update
    
    if not user_data or user_data.get('role') != 'pharmacy':
        return dash.no_update, dash.no_update
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        
        # Use helper function to upsert stock
        success = upsert_pharmacy_stock(conn, user_data['id'], medicine, int(qty), float(price))
        conn.close()
        
        if success:
            toast = dbc.Toast(
                translations[language]["stock_updated"],
                header="Success",
                icon="success",
                dismissable=True,
                is_open=True,
                duration=4000,
                style={"position": "fixed", "top": 10, "right": 10, "width": 350}
            )
            return toast, {'updated': True}
        else:
            raise Exception("Failed to update stock")
            
    except Exception as e:
        print(f"Error updating stock: {e}")
        toast = dbc.Toast(
            translations[language]["error_occurred"],
            header="Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return toast, dash.no_update

@app.callback(
    Output('pharmacy-stock-table', 'children'),
    Input('user-store', 'data'),
    Input('update-stock-btn', 'n_clicks'),
    Input('stock-search-btn', 'n_clicks'),
    Input('pharmacy-stock-data', 'data'),
    Input({'type': 'delete-btn', 'index': ALL}, 'n_clicks'),
    State('language-store', 'data'),
    State('stock-search', 'value'),
    prevent_initial_call=True
)
def update_stock_table(user_data, update_clicks, search_clicks, stock_data, delete_clicks, language, search_term):
    """Update pharmacy stock table with search and delete functionality"""
    if user_data and user_data.get('role') == 'pharmacy':
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        
        query = "SELECT id, medicine, qty, price, last_updated FROM pharmacy_stock WHERE pharmacy_id = ?"
        params = [user_data['id']]
        
        if search_term:
            query += " AND LOWER(medicine) LIKE LOWER(?)"
            params.append(f"%{search_term}%")
            
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if df.empty:
            return html.P(translations[language]["no_stock_records"])
        
        # Create editable table with delete buttons
        table_data = []
        for _, row in df.iterrows():
            table_data.append({
                'id': row['id'],
                'medicine': row['medicine'],
                'qty': row['qty'],
                'price': row['price'],
                'last_updated': row['last_updated'],
                'actions': html.Div([
                    dbc.Button(
                        html.I(className="fas fa-trash"),
                        id={'type': 'delete-btn', 'index': row['id']},
                        color="danger",
                        size="sm",
                        className="me-1"
                    )
                ])
            })
        
        return dash_table.DataTable(
            id='stock-table',
            columns=[
                {'name': 'Medicine', 'id': 'medicine', 'editable': True},
                {'name': 'Quantity', 'id': 'qty', 'editable': True, 'type': 'numeric'},
                {'name': 'Price', 'id': 'price', 'editable': True, 'type': 'numeric'},
                {'name': 'Last Updated', 'id': 'last_updated'},
                {'name': 'Actions', 'id': 'actions'}
            ],
            data=table_data,
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={
                'backgroundColor': 'lightgrey', 
                'fontWeight': 'bold',
                'padding': '10px'
            },
            page_size=10,
            editable=True
        )
    return dash.no_update

# Pharmacy stock delete callback
@app.callback(
    Output('toast-container', 'children', allow_duplicate=True),
    Output('pharmacy-stock-data', 'data', allow_duplicate=True),
    Input({'type': 'delete-btn', 'index': ALL}, 'n_clicks'),
    State('user-store', 'data'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def delete_stock_item(delete_clicks, user_data, language):
    """Delete a pharmacy stock item"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    # Get the button that was clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    button_info = json.loads(button_id.replace("'", '"'))
    
    stock_id = button_info['index']
    
    if not user_data or user_data.get('role') != 'pharmacy':
        return dash.no_update, dash.no_update
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        
        # Delete the stock item
        c.execute("DELETE FROM pharmacy_stock WHERE id = ?", (stock_id,))
        
        conn.commit()
        conn.close()
        
        toast = dbc.Toast(
            translations[language]["stock_deleted"],
            header="Success",
            icon="success",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return toast, {'updated': True}
        
    except Exception as e:
        print(f"Error deleting stock item: {e}")
        toast = dbc.Toast(
            translations[language]["error_occurred"],
            header="Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return toast, dash.no_update

# Pharmacy stock table edit callback
@app.callback(
    Output('toast-container', 'children', allow_duplicate=True),
    Output('pharmacy-stock-data', 'data', allow_duplicate=True),
    Input('stock-table', 'data'),
    State('user-store', 'data'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def update_stock_from_table(table_data, user_data, language):
    """Update stock when table is edited"""
    if not table_data or not user_data or user_data.get('role') != 'pharmacy':
        return dash.no_update, dash.no_update
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        
        # Update each row in the table
        for row in table_data:
            c.execute("UPDATE pharmacy_stock SET medicine = ?, qty = ?, price = ?, last_updated = ? WHERE id = ?",
                     (row['medicine'], row['qty'], row['price'], datetime.now(), row['id']))
        
        conn.commit()
        conn.close()
        
        toast = dbc.Toast(
            translations[language]["stock_updated"],
            header="Success",
            icon="success",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return toast, {'updated': True}
        
    except Exception as e:
        print(f"Error updating stock from table: {e}")
        toast = dbc.Toast(
            translations[language]["error_occurred"],
            header="Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return toast, dash.no_update

# Medicine search callback
@app.callback(
    Output('medicine-results', 'children'),
    Input('medicine-search-btn', 'n_clicks'),
    Input('pharmacy-stock-data', 'data'),
    State('medicine-search', 'value'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def search_medicine(n_clicks, stock_data, search_term, language):
    """Search for medicine across all pharmacies"""
    if not search_term:
        return html.P(translations[language]["enter_medicine_name"])
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        
        # Search across all pharmacies with pharmacy name
        query = """
        SELECT ps.medicine, ps.qty, ps.price, u.name as pharmacy_name 
        FROM pharmacy_stock ps 
        LEFT JOIN users u ON ps.pharmacy_id = u.id 
        WHERE LOWER(ps.medicine) LIKE LOWER(?)
        """
        df = pd.read_sql_query(query, conn, params=(f"%{search_term}%",))
        conn.close()
        
        if df.empty:
            return html.P(translations[language]["no_results"])
        
        # Create result cards
        results = []
        for _, row in df.iterrows():
            results.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H5(row['medicine'], className="card-title"),
                        html.P(f"{translations[language]['quantity']}: {row['qty']}"),
                        html.P(f"{translations[language]['price']}: ${row['price']:.2f}"),
                        html.P(f"{translations[language]['pharmacy']}: {row['pharmacy_name']}"),
                        dbc.Button(
                            translations[language]["order_tracking"],
                            color="primary",
                            size="sm"
                        )
                    ])
                ], className="mb-2")
            )
        
        return html.Div(results)
        
    except Exception as e:
        print(f"Error searching medicine: {e}")
        return html.P(translations[language]["error_occurred"])

# Appointment modal callbacks
@app.callback(
    Output('appointment-modal', 'is_open'),
    Input('schedule-appointment-btn', 'n_clicks'),
    Input('close-appointment-modal', 'n_clicks'),
    Input('schedule-appointment-confirm', 'n_clicks'),
    State('appointment-modal', 'is_open'),
    prevent_initial_call=True
)
def toggle_appointment_modal(schedule_clicks, close_clicks, confirm_clicks, is_open):
    """Toggle appointment modal visibility"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id in ['schedule-appointment-btn', 'close-appointment-modal', 'schedule-appointment-confirm']:
        return not is_open
    
    return is_open

# Schedule appointment callback
@app.callback(
    Output('toast-container', 'children', allow_duplicate=True),
    Output('appointment-data', 'data', allow_duplicate=True),
    Input('schedule-appointment-confirm', 'n_clicks'),
    State('appointment-date', 'value'),
    State('appointment-time', 'value'),
    State('appointment-reason', 'value'),
    State('appointment-doctor', 'value'),
    State('user-store', 'data'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def schedule_appointment(n_clicks, date, time, reason, doctor_id, user_data, language):
    """Schedule a new appointment"""
    if not n_clicks or not date or not time or not reason or not doctor_id:
        return dash.no_update, dash.no_update
    
    if not user_data or user_data.get('role') != 'patient':
        return dash.no_update, dash.no_update
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        
        # Create appointment with selected doctor
        appointment_id = str(uuid.uuid4())
        now = datetime.now()
        
        c.execute("INSERT INTO appointments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (appointment_id, user_data['id'], doctor_id, date, time, reason, 'requested', now, now))
        
        conn.commit()
        conn.close()
        
        toast = dbc.Toast(
            translations[language]["appointment_scheduled"],
            header="Success",
            icon="success",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return toast, {'updated': True}
        
    except Exception as e:
        print(f"Error scheduling appointment: {e}")
        toast = dbc.Toast(
            translations[language]["error_occurred"],
            header="Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return toast, dash.no_update

# Patient appointments callback
@app.callback(
    Output('upcoming-appointments', 'children'),
    Output('past-appointments', 'children'),
    Input('user-store', 'data'),
    Input('appointment-data', 'data'),
    Input('language-store', 'data')
)
def update_patient_appointments(user_data, appointment_data, language):
    """Update patient appointments list"""
    if not user_data or user_data.get('role') != 'patient':
        return html.Div(), html.Div()
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        
        # Get upcoming appointments
        upcoming_df = pd.read_sql_query(
            "SELECT a.id, a.date, a.time, a.reason, a.status, u.name as doctor_name FROM appointments a JOIN users u ON a.doctor_id = u.id WHERE a.patient_id = ? AND a.date >= date('now') ORDER BY a.date, a.time",
            conn, params=(user_data['id'],)
        )
        
        # Get past appointments
        past_df = pd.read_sql_query(
            "SELECT a.id, a.date, a.time, a.reason, a.status, u.name as doctor_name FROM appointments a JOIN users u ON a.doctor_id = u.id WHERE a.patient_id = ? AND a.date < date('now') ORDER BY a.date DESC, a.time DESC",
            conn, params=(user_data['id'],)
        )
        
        conn.close()
        
        # Create appointment lists
        def create_appointment_list(df):
            if df.empty:
                return html.P(translations[language]["no_results"])
            
            appointments = []
            for _, row in df.iterrows():
                appointments.append(
                    dbc.Card([
                        dbc.CardBody([
                            html.H6(f"{row['date']} {row['time']}", className="card-subtitle"),
                            html.P(f"{translations[language]['doctor']}: {row['doctor_name']}"),
                            html.P(f"{translations[language]['reason']}: {row['reason']}"),
                            html.Small(f"{translations[language]['status']}: {row['status']}", className="text-muted")
                        ])
                    ], className="mb-2")
                )
            return html.Div(appointments)
        
        return create_appointment_list(upcoming_df), create_appointment_list(past_df)
        
    except Exception as e:
        print(f"Error loading appointments: {e}")
        return html.P(translations[language]["error_occurred"]), html.P(translations[language]["error_occurred"])

# Doctor appointments callback
@app.callback(
    Output('doctor-upcoming-appointments', 'children'),
    Output('doctor-past-appointments', 'children'),
    Input('user-store', 'data'),
    Input('appointment-data', 'data'),
    Input('language-store', 'data')
)
def update_doctor_appointments(user_data, appointment_data, language):
    """Update doctor appointments list"""
    if not user_data or user_data.get('role') != 'doctor':
        return html.Div(), html.Div()
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        
        # Get upcoming appointments
        upcoming_df = pd.read_sql_query(
            "SELECT a.id, a.date, a.time, a.reason, a.status, u.name as patient_name FROM appointments a JOIN users u ON a.patient_id = u.id WHERE a.doctor_id = ? AND a.date >= date('now') ORDER BY a.date, a.time",
            conn, params=(user_data['id'],)
        )
        
        # Get past appointments
        past_df = pd.read_sql_query(
            "SELECT a.id, a.date, a.time, a.reason, a.status, u.name as patient_name FROM appointments a JOIN users u ON a.patient_id = u.id WHERE a.doctor_id = ? AND a.date < date('now') ORDER by a.date DESC, a.time DESC",
            conn, params=(user_data['id'],)
        )
        
        conn.close()
        
        # Create appointment lists
        def create_appointment_list(df):
            if df.empty:
                return html.P(translations[language]["no_results"])
            
            appointments = []
            for _, row in df.iterrows():
                appointments.append(
                    dbc.Card([
                        dbc.CardBody([
                            html.H6(f"{row['date']} {row['time']}", className="card-subtitle"),
                            html.P(f"{translations[language]['patient']}: {row['patient_name']}"),
                            html.P(f"{translations[language]['reason']}: {row['reason']}"),
                            html.Small(f"{translations[language]['status']}: {row['status']}", className="text-muted")
                        ])
                    ], className="mb-2")
                )
            return html.Div(appointments)
        
        return create_appointment_list(upcoming_df), create_appointment_list(past_df)
        
    except Exception as e:
        print(f"Error loading doctor appointments: {e}")
        return html.P(translations[language]["error_occurred"]), html.P(translations[language]["error_occurred"])

# Health Metrics Modal callbacks
@app.callback(
    Output('patient-metric-modal', 'is_open'),
    Input('add-metric-btn', 'n_clicks'),
    Input('close-metric-modal', 'n_clicks'),
    Input('save-metric-btn', 'n_clicks'),
    State('patient-metric-modal', 'is_open'),
    prevent_initial_call=True
)
def toggle_metric_modal(add_clicks, close_clicks, save_clicks, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id in ['add-metric-btn', 'close-metric-modal', 'save-metric-btn']:
        return not is_open
    return is_open

@app.callback(
    Output('health-metrics-data', 'data', allow_duplicate=True),
    Output('toast-container', 'children', allow_duplicate=True),
    Input('save-metric-btn', 'n_clicks'),
    State('bp-input', 'value'),
    State('hr-input', 'value'),
    State('temp-input', 'value'),
    State('sugar-input', 'value'),
    State('user-store', 'data'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def save_health_metric(n_clicks, bp, hr, temp, sugar, user_data, language):
    if not n_clicks:
        return dash.no_update, dash.no_update
    
    if not user_data or user_data.get('role') != 'patient':
        return dash.no_update, dash.no_update
    
    # Validate inputs
    if not all([bp, hr, temp, sugar]):
        toast = dbc.Toast(
            "Please fill all fields",
            header="Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return dash.no_update, toast
    
    # Validate blood pressure format
    if not re.match(r'^\d+\/\d+$', bp):
        toast = dbc.Toast(
            "Blood pressure must be in format '120/80'",
            header="Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return dash.no_update, toast
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        
        # Insert health metric
        metric_id = str(uuid.uuid4())
        recorded_at = datetime.now()
        
        c.execute(
            "INSERT INTO health_metrics (id, patient_id, blood_pressure, heart_rate, temperature, blood_sugar, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (metric_id, user_data['id'], bp, int(hr), float(temp), float(sugar), recorded_at)
        )
        
        conn.commit()
        conn.close()
        
        toast = dbc.Toast(
            "Health metric saved successfully",
            header="Success",
            icon="success",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        
        # Return updated data to trigger chart refresh
        return {'updated': True}, toast
        
    except Exception as e:
        print(f"Error saving health metric: {e}")
        toast = dbc.Toast(
            "Error saving health metric",
            header="Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return dash.no_update, toast

@app.callback(
    Output('health-metrics-chart', 'children'),
    Input('user-store', 'data'),
    Input('health-metrics-data', 'data'),
    Input('language-store', 'data')
)
def update_health_metrics_chart(user_data, health_data, language):
    if not user_data or user_data.get('role') != 'patient':
        return html.Div()
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        df = pd.read_sql_query(
            "SELECT recorded_at, blood_pressure, heart_rate, temperature, blood_sugar FROM health_metrics WHERE patient_id = ? ORDER BY recorded_at",
            conn, 
            params=(user_data['id'],)
        )
        conn.close()
        
        if df.empty:
            return html.P(translations[language]["no_profile_data"])
        
        # Convert recorded_at to datetime
        df['recorded_at'] = pd.to_datetime(df['recorded_at'])
        
        # Create charts
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Heart Rate', 'Temperature', 'Blood Sugar'),
            vertical_spacing=0.1
        )
        
        # Heart Rate chart
        fig.add_trace(
            go.Scatter(x=df['recorded_at'], y=df['heart_rate'], name='Heart Rate', mode='lines+markers'),
            row=1, col=1
        )
        
        # Temperature chart
        fig.add_trace(
            go.Scatter(x=df['recorded_at'], y=df['temperature'], name='Temperature', mode='lines+markers'),
            row=2, col=1
        )
        
        # Blood Sugar chart
        fig.add_trace(
            go.Scatter(x=df['recorded_at'], y=df['blood_sugar'], name='Blood Sugar', mode='lines+markers'),
            row=3, col=1
        )
        
        fig.update_layout(height=600, showlegend=False, title_text="Health Metrics Over Time")
        fig.update_xaxes(title_text="Date", row=3, col=1)
        fig.update_yaxes(title_text="BPM", row=1, col=1)
        fig.update_yaxes(title_text="°C", row=2, col=1)
        fig.update_yaxes(title_text="mg/dL", row=3, col=1)
        
        return dcc.Graph(figure=fig)
        
    except Exception as e:
        print(f"Error loading health metrics: {e}")
        return html.P("Error loading health metrics data")

# Prescription Modal callbacks
@app.callback(
    Output('prescription-modal', 'is_open'),
    Input('write-prescription-btn', 'n_clicks'),
    Input('close-prescription-modal', 'n_clicks'),
    Input('save-prescription-btn', 'n_clicks'),
    State('prescription-modal', 'is_open'),
    prevent_initial_call=True
)
def toggle_prescription_modal(write_clicks, close_clicks, save_clicks, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id in ['write-prescription-btn', 'close-prescription-modal', 'save-prescription-btn']:
        return not is_open
    return is_open

@app.callback(
    Output('toast-container', 'children', allow_duplicate=True),
    Output('prescription-data', 'data', allow_duplicate=True),
    Input('save-prescription-btn', 'n_clicks'),
    State('prescription-medicine', 'value'),
    State('prescription-dosage', 'value'),
    State('prescription-instructions', 'value'),
    State('user-store', 'data'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def save_prescription(n_clicks, medicine, dosage, instructions, user_data, language):
    if not n_clicks:
        return dash.no_update, dash.no_update
    
    if not user_data or user_data.get('role') != 'doctor':
        return dash.no_update, dash.no_update
    
    if not all([medicine, dosage]):
        toast = dbc.Toast(
            "Please fill medicine and dosage fields",
            header="Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return dash.no_update, toast
    
    try:
        conn = sqlite3.connect('telesehat.db', detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        
        # Create prescription (for demo, using a fixed patient ID)
        prescription_id = str(uuid.uuid4())
        prescribed_at = datetime.now()
        
        # In a real app, you would select a patient from the consultations or appointments
        c.execute(
            "INSERT INTO prescriptions (id, patient_id, doctor_id, medicine, dosage, instructions, prescribed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (prescription_id, 'patient_demo_id', user_data['id'], medicine, dosage, instructions, prescribed_at)
        )
        
        conn.commit()
        conn.close()
        
        toast = dbc.Toast(
            translations[language]["prescription_saved"],
            header="Success",
            icon="success",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        
        return toast, {'updated': True}
        
    except Exception as e:
        print(f"Error saving prescription: {e}")
        toast = dbc.Toast(
            translations[language]["error_occurred"],
            header="Error",
            icon="danger",
            dismissable=True,
            is_open=True,
            duration=4000,
            style={"position": "fixed", "top": 10, "right": 10, "width": 350}
        )
        return toast, dash.no_update

# Chat callback with image upload support
@app.callback(
    Output('chat-history', 'children'),
    Output('chat-history-store', 'data'),
    Output('typing-indicator', 'style'),
    Input('chat-send-btn', 'n_clicks'),
    Input('upload-image', 'contents'),
    Input('user-store', 'data'),
    State('chat-input', 'value'),
    State('chat-history-store', 'data'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def update_chat(n_clicks, image_content, user_data, message, chat_history, language):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, {"display": "none"}
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Show typing indicator
    typing_style = {"display": "block", "marginBottom": "10px"}
    
    if trigger_id == 'upload-image' and image_content:
        # Handle image upload
        try:
            # Decode the image
            content_type, content_string = image_content.split(',')
            decoded = base64.b64decode(content_string)
            image = Image.open(io.BytesIO(decoded))
            
            # Add image message to chat history
            user_msg = {
                'sender': 'user',
                'message': 'Uploaded image',
                'image': image_content,
                'timestamp': datetime.now().strftime("%H:%M")
            }
            
            # Create chat display with typing indicator
            chat_display = create_chat_display(chat_history + [user_msg])
            
            # Return immediately with typing indicator
            return chat_display + [html.Div([
                html.Div(
                    translations[language]["typing"],
                    style=custom_css["chatAI"]
                )
            ], style={"marginBottom": "15px"})], chat_history + [user_msg], typing_style
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return dash.no_update, dash.no_update, {"display": "none"}
    
    elif trigger_id == 'chat-send-btn' and message:
        # Add user message to chat history
        user_msg = {
            'sender': 'user',
            'message': message,
            'timestamp': datetime.now().strftime("%H:%M")
        }
        
        # Create chat display with typing indicator
        chat_display = create_chat_display(chat_history + [user_msg])
        
        # Return immediately with typing indicator
        return chat_display + [html.Div([
            html.Div(
                translations[language]["typing"],
                style=custom_css["chatAI"]
            )
        ], style={"marginBottom": "15px"})], chat_history + [user_msg], typing_style
    
    return dash.no_update, dash.no_update, {"display": "none"}

@app.callback(
    Output('chat-history', 'children', allow_duplicate=True),
    Output('chat-history-store', 'data', allow_duplicate=True),
    Output('typing-indicator', 'style', allow_duplicate=True),
    Input('chat-history-store', 'data'),
    Input('user-store', 'data'),
    State('language-store', 'data'),
    prevent_initial_call=True
)
def add_ai_response(chat_history, user_data, language):
    if not chat_history or not user_data:
        return dash.no_update, dash.no_update, {"display": "none"}
    
    # Check if the last message is from user (need AI response)
    if chat_history and chat_history[-1]['sender'] == 'user':
        # Get AI response using Gemini - with safety checks
        try:
            last_message = chat_history[-1]
            
            if 'image' in last_message:
                # Handle image analysis
                if gemini_vision_model:
                    # Decode the image
                    content_type, content_string = last_message['image'].split(',')
                    decoded = base64.b64decode(content_string)
                    image = Image.open(io.BytesIO(decoded))
                    
                    # Analyze the image
                    response = gemini_vision_model.generate_content([
                        "Analyze this medical image. Describe what you see and provide potential insights. "
                        "Remember to always advise consulting with a healthcare professional for proper diagnosis.",
                        image
                    ])
                    ai_response = response.text
                else:
                    ai_response = "I'm here to help with medical information. For accurate diagnosis and treatment, please consult with a healthcare professional."
            else:
                # Handle text message
                if gemini_model:
                    response = gemini_model.generate_content(
                        f"You are a medical assistant. Provide helpful information but always advise to consult with a real doctor for medical advice. User question: {last_message['message']}"
                    )
                    ai_response = response.text
                else:
                    ai_response = "I'm here to help with medical information. For accurate diagnosis and treatment, please consult with a healthcare professional."
        except Exception as e:
            print(f"Gemini API error: {e}")
            ai_response = translations[language]["assistant_unavailable"]
        
        ai_msg = {
            'sender': 'ai',
            'message': ai_response,
            'timestamp': datetime.now().strftime("%H:%M")
        }
        
        # Update chat history
        updated_chat = chat_history + [ai_msg]
        
        # Create chat display
        chat_display = create_chat_display(updated_chat)
        
        return chat_display, updated_chat, {"display": "none"}
    
    return dash.no_update, dash.no_update, {"display": "none"}

def create_chat_display(chat_history):
    chat_display = []
    for msg in chat_history:
        if msg['sender'] == 'user':
            if 'image' in msg:
                chat_display.append(
                    html.Div([
                        html.Div([
                            html.Img(
                                src=msg['image'],
                                style={"maxWidth": "100%", "maxHeight": "200px", "borderRadius": "8px"}
                            ),
                            html.Small(
                                msg['timestamp'],
                                style={'textAlign': 'right', 'display': 'block', 'color': '#6c757d'}
                            )
                        ], style={'textAlign': 'right'})
                    ], style={'marginBottom': '15px'})
                )
            else:
                chat_display.append(
                    html.Div([
                        html.Div(
                            msg['message'],
                            style=custom_css["chatUser"]
                        ),
                        html.Small(
                            msg['timestamp'],
                            style={'textAlign': 'right', 'display': 'block', 'color': '#6c757d'}
                        )
                    ], style={'marginBottom': '15px'})
                )
        else:
            chat_display.append(
                html.Div([
                    html.Div(
                        msg['message'],
                        style=custom_css["chatAI"]
                    ),
                    html.Small(
                        msg['timestamp'],
                        style={'color': '#6c757d'}
                    )
                ], style={'marginBottom': '15px'})
            )
    
    return chat_display

# Run the app without debug mode to prevent callback errors from showing
if __name__ == '__main__':
    app.run(debug=False)
