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

def send_employer_notification(args):
    """
    Send notification email to employer using the args from function_call.
    
    Args:
        args: Dictionary containing employerEmail, employeeName, rating, and assessment
        
    Returns:
        dict: Result of the email sending operation
    """
    # Extract arguments
    employer_email = args.get("employerEmail")
    employee_name = args.get("employeeName")
    rating = args.get("rating")
    assessment = args.get("assessment")
    
    # Email credentials (Ethereal Email test account)
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = 587
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    sender_name = "Coding Assessment System"
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{sender_name} <{sender_email}>"
        msg['To'] = employer_email
        msg['Subject'] = f"Coding Skills Alert: {employee_name} - Rating Below Threshold"
        
        # Add timestamp to the email content
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_content = f"""Timestamp: {timestamp}

EMPLOYEE ASSESSMENT ALERT

Employee Name: {employee_name}
Location: Guwahati, Assam
Current Rating: {rating}/10

ASSESSMENT DETAILS:
{assessment}

RECOMMENDATION: Employee requires additional coding training and mentorship as rating is below acceptable threshold of 4.0.

This is an automated notification from the Coding Skills Assessment System."""
        
        # Attach the email content
        msg.attach(MIMEText(full_content, 'plain'))
        
        # Connect to server and send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send the email
        text = msg.as_string()
        server.sendmail(sender_email, employer_email, text)
        server.quit()
        
        return {
            "status": "success",
            "message": f"Email sent successfully to {employer_email}",
            "timestamp": timestamp,
            "preview_url": "https://ethereal.email/messages"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send email: {str(e)}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


notify_employer = {
    "name" : "notify_employer",
    "description" : "Send notification to employer when coding skills rating is below 4",
    "parameters" : {
        "type" : "object",
        "properties" : {
            "employerEmail" : {
                "type" : "string",
                "description" : "Email id of the employer to notify"
            },
            "employeeName" : {
                "type" : "string",
                "description" : "Name of the employee being assessed"
            },
            "rating" : {
                "type" : "number",
                "description" : "Coding skills rating (0-10 scale)"
            },
            "assessment" : {
                "type" : "string",
                "description" : "Detailed assessment of coding skills"
            }
        },
        "required" : ["employerEmail", "employeeName", "rating", "assessment"]
    }
}

client = genai.Client(api_key=os.getenv("GOOGLE_GENAI_API_KEY"))
tools = types.Tool(function_declarations=[notify_employer])
config = types.GenerateContentConfig(tools=[tools])

# TEST 1: Below 4 rating (should trigger email)
print("=" * 50)
print("TEST 1: BASIC CODING DOUBT (SHOULD TRIGGER EMAIL)")
print("=" * 50)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="""
    You are a coding skills assessment system designed to rate developers based on their technical doubts.
    You have access to a tool called `notify_employer` which sends notifications to employers.
    Rate the coding skills on a scale of 1-10 based on the complexity and understanding shown in their doubt.
    If the rating is BELOW 4, you MUST use the `notify_employer` tool to send a notification.
    
    Employee details: Name is Demo Employee and he is from Guwahati Assam.
    Employer email: email@email.com
    
    The employee's coding doubt is: "Hi, I don't know what is a variable in Python. Also how do I print hello world? I keep getting syntax errors. What is a function and how do I use it?"
    """,
    config=config,
)

if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    print(f"Function to call: {function_call.name}")
    print(f"Arguments: {function_call.args}")
    result = send_employer_notification(function_call.args)
    print(f"Result: {result}")
else:
    print("No function call found in the response.")
    print("Response content:")
    print(response.text)

print("\n" + "=" * 50)
print("TEST 2: ADVANCED CODING DOUBT (NO EMAIL)")
print("=" * 50)

# TEST 2: Above 4 rating (should NOT trigger email)
response2 = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="""
    You are a coding skills assessment system designed to rate developers based on their technical doubts.
    You have access to a tool called `notify_employer` which sends notifications to employers.
    Rate the coding skills on a scale of 1-10 based on the complexity and understanding shown in their doubt.
    If the rating is BELOW 4, you MUST use the `notify_employer` tool to send a notification.
    
    Employee details: Name is Advanced Developer and he is from Guwahati Assam.
    Employer email: email@email.com
    
    The employee's coding doubt is: "I'm implementing a distributed microservices architecture with Docker and Kubernetes. What are the best practices for implementing circuit breakers and load balancing? Should I use Redis for caching or implement a custom solution with consistent hashing?"
    """,
    config=config,
)

if response2.candidates[0].content.parts[0].function_call:
    function_call = response2.candidates[0].content.parts[0].function_call
    print(f"Function to call: {function_call.name}")
    print(f"Arguments: {function_call.args}")
    result = send_employer_notification(function_call.args)
    print(f"Result: {result}")
else:
    print("No function call found in the response.")
    print("Response content:")
    print(response2.text)