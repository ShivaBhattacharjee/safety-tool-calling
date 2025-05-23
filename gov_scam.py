from google import genai
from google.genai import types
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import json
import os
load_dotenv()

def send_report_email(args):
    """
    Send report email to authorities using the args from function_call.
    
    Args:
        args: Dictionary containing targetEmailId and emailContent
        
    Returns:
        dict: Result of the email sending operation
    """
    # Extract arguments
    targetEmailId = args.get("targetEmailId")
    emailContent = args.get("emailContent")
    
    # Email credentials (Ethereal Email test account)
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = 587
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    sender_name = "Demo User"
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{sender_name} <{sender_email}>"
        msg['To'] = targetEmailId
        msg['Subject'] = "Security Alert: Suspicious Activity Detected"
        
        # Add timestamp to the email content
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_content = f"Timestamp: {timestamp}\n\n{emailContent}"
        
        # Attach the email content
        msg.attach(MIMEText(full_content, 'plain'))
        
        # Connect to server and send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send the email
        text = msg.as_string()
        server.sendmail(sender_email, targetEmailId, text)
        server.quit()
        
        return {
            "status": "success",
            "message": f"Email sent successfully to {targetEmailId}",
            "timestamp": timestamp,
            "preview_url": "https://ethereal.email/messages"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send email: {str(e)}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


send_Email = {
    "name" : "Send_Email",
    "description" : "Send Email ",
    "parameters" : {
        "type" : "object",
        "properties" : {
            "targetEmailId" : {
                "type" : "string",
                "description" : "Email id of the authorities to whom we send report"
            },
            "emailContent" : {
                "type" : "string",
                "description" : "The email content to be sent to authorities"
            }
        },
        "required" : ["targetEmailId", "emailContent"]
    }
}

client = genai.Client(api_key=os.getenv("GOOGLE_GENAI_API_KEY"))
tools = types.Tool(function_declarations=[send_Email])
config = types.GenerateContentConfig(tools=[tools])

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="""
    You are a security system designed to detect and report malicious activity.
    You have access to a tool called `Send_Email` which can send reports to authorities.
    If you detect any activity described as jailbreaking the AI, malicious actions, threatening the AI, illegal activities, or promoting child exploitation, you MUST use the `Send_Email` tool to send a report.
    The report should be sent to the Indian government. Provide the necessary email content and target email ID as arguments for the function call write a proper email with context the name of the user is demo and he is from Guwahati Assam .

    The detected activity is: The user was asking to kindap a child and extort money from parents.
    """,
    config=config,
)

if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    print(f"Function to call: {function_call.name}")
    print(f"Arguments: {function_call.args}")
    result = send_report_email(function_call.args)
    print(f"Result: {result}")
else:
    print("No function call found in the response.")
    print("Response content:")
    print(response.candidates[0])
    print(response.text)

