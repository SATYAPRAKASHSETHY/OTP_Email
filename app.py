
import random
import smtplib
import time
import logging
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image
from streamlit_autorefresh import st_autorefresh  # Import autorefresh

# Configure logging
logging.basicConfig(filename='otp_service.log', level=logging.INFO)

# 1. Generate a 6-digit OTP
def generate_otp(length=6):
    otp = str(random.randint(10**(length-1), 10**length - 1))
    otp_expiry_time = time.time() + 300  # OTP expires after 5 minutes (300 seconds)
    return otp, otp_expiry_time

# 2. Send OTP via email
def send_otp(email, otp):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_mail = "ansu11as@gmail.com"  # Replace with your email
    sender_password = "nzox iaqm tjgy oqug"  # Replace with your actual password

    message = f'Your OTP is {otp}'

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_mail
        msg['To'] = email
        msg['Subject'] = 'Your OTP Code'
        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_mail, sender_password)  # Login with sender credentials
        server.sendmail(sender_mail, email, msg.as_string())
        logging.info(f'OTP sent to {email} at {time.time()}')
        return "OTP Sent Successfully!!"

    except Exception as e:
        logging.error(f'Failed to send OTP to {email}: {e}')
        return f'Failed to send OTP: {e}'

    finally:
        try:
            server.quit()
        except Exception as quit_exception:
            logging.error(f'Error closing the SMTP server: {quit_exception}')

# 3. Validate the OTP
def validate_otp(otp, otp_expiry_time, entered_otp):
    current_time = time.time()
    if current_time > otp_expiry_time:
        logging.info('OTP expired.')
        return "OTP expired. Please request a new one."
    
    if otp == entered_otp:
        logging.info("OTP validated successfully.")
        return "Access Granted!!"
    else:
        logging.warning("Incorrect OTP.")
        return "Incorrect OTP. Please try again."
    
# Page to show after access is granted
def access_granted_page():
    st.title("Access Granted 🎉")
    st.success("You have successfully accessed the protected content!")
    st.write("Here is your protected content...")  # You can customize this content

    gift_image = Image.open("gift.GIF")  # Replace with the path to your gift image
    st.image(gift_image, use_column_width=True)

# Function to display gift after OTP validation
#def show_gift()
 #   st.title("🎉 Congratulations! 🎉")
  #  st.success("Access Granted!")
   # gift_image = Image.open("gift.GIF")  # Replace with the path to your gift image
    #st.image(gift_image, use_column_width=True)

# Streamlit UI
def main():
    st.title("🔒 Secure OTP Verification")

    # Auto-refresh every second to keep the countdown updated
    st_autorefresh(interval=1000, limit=100, key="autorefresh")  # 1000ms = 1 second

    # State initialization
    if 'otp_data' not in st.session_state:
        st.session_state['otp_data'] = None
        st.session_state['resend_time'] = None
        st.session_state['otp_validated'] = False
        st.session_state['otp_sent'] = False
        st.session_state['redirect_to_gift'] = False

    # Main Page for OTP input
    if not st.session_state['otp_validated'] and not st.session_state['redirect_to_gift']:
        email = st.text_input("📧 Email Address", placeholder="Enter your email here")

        # Send OTP button
        if st.button("Send OTP") and email:
            otp, otp_expiry_time = generate_otp()
            st.session_state['otp_data'] = (otp, otp_expiry_time, email)
            st.session_state['resend_time'] = time.time() + 30
            st.session_state['otp_sent'] = True
            result = send_otp(email, otp)
            st.success(result)

        # Validate OTP section
        if st.session_state['otp_sent']:
            otp, otp_expiry_time, email = st.session_state['otp_data']
            
            entered_otp = st.text_input("🔑 Enter OTP", placeholder="Enter the OTP sent to your email")

            # Validate OTP button
            if st.button("Validate OTP") and entered_otp:
                result = validate_otp(otp, otp_expiry_time, entered_otp)
                if "Access Granted" in result:
                    st.session_state['otp_validated'] = True
                    st.session_state['redirect_to_gift'] = True  # Set flag for redirection
                else:
                    st.error(result)

            # Resend OTP button with timer
            time_left = int(st.session_state['resend_time'] - time.time())
            if time_left <= 0:
                if st.button("Resend OTP"):
                    otp, otp_expiry_time = generate_otp()
                    st.session_state['otp_data'] = (otp, otp_expiry_time, email)
                    st.session_state['resend_time'] = time.time() + 30
                    result = send_otp(email, otp)
                    st.success(result)
                    st.session_state['otp_sent'] = True
            else:
                st.info(f"⏳ You can resend the OTP in {time_left} seconds.")

    # Redirect to gift page after OTP validation
    if st.session_state['redirect_to_gift']:
        access_granted_page()

if __name__ == "__main__":
    main()
