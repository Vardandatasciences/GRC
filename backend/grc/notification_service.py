import smtplib
import requests
import json
import mysql.connector
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("notification_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("notification_service")

class NotificationService:
    def __init__(self):
        # Database connection
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'root'),
            'database': os.getenv('DB_NAME', 'grc_test')
        }
        
        # WhatsApp configuration
        self.whatsapp_config = {
            'api_version': 'v17.0',
            'phone_number_id': os.getenv('WHATSAPP_PHONE_NUMBER_ID', ''),
            'access_token': os.getenv('WHATSAPP_ACCESS_TOKEN', ''),
            'default_language': 'en_US',
            'sender_phone': os.getenv('WHATSAPP_SENDER_PHONE', '')
        }
        
        # Email configuration
        self.email_configs = {
            'gmail': {
                'service': 'gmail',
                'host': 'smtp.gmail.com',
                'port': 587,
                'auth': {
                    'user': os.getenv('GMAIL_USER', 'vardaan.rcms@gmail.com'),
                    'pass': os.getenv('GMAIL_APP_PASSWORD', 'aynlltagpthlzqgd')
                }
            },
            'microsoft': {
                'service': 'outlook',
                'host': 'smtp.office365.com',
                'port': 587,
                'auth': {
                    'user': os.getenv('MICROSOFT_USER', ''),
                    'pass': os.getenv('MICROSOFT_APP_PASSWORD', ''),
                },
                # Microsoft Graph API configuration

                'graph_api': {
                    'client_id': os.getenv('MICROSOFT_CLIENT_ID', '1a9a4d27-4a49-400d-9bfb-a6cfa08f1b15'),
                    'client_secret': os.getenv('MICROSOFT_CLIENT_SECRET', 'YUI8Q~svY7gzjgY6uGqpVKV1gTtbiYhj5fLPEdms'),
                    'tenant_id': os.getenv('MICROSOFT_TENANT_ID', 'aa7c8c45-41a3-4453-bc9a-3adfe8ff5fb6'),
                    'authority': os.getenv('MICROSOFT_AUTHORITY', f'https://login.microsoftonline.com/aa7c8c45-41a3-4453-bc9a-3adfe8ff5fb6'),
                    'redirect_uri': os.getenv('MICROSOFT_REDIRECT_URI', 'http://localhost:5000/getAToken'),
                    'scopes': ['https://graph.microsoft.com/.default'],
                    'endpoint': 'https://graph.microsoft.com/v1.0'
                }
            }
        }
        
        self.default_from = {
            'email': os.getenv('DEFAULT_FROM_EMAIL', 'vardaan.rcms@gmail.com'),
            'name': os.getenv('DEFAULT_FROM_NAME', 'GRC System')
        }
        
        # Initialize templates
        self.init_templates()
    
    def get_db_connection(self):
        """Establish database connection"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            return conn
        except mysql.connector.Error as err:
            logger.error(f"Database connection error: {err}")
            raise
    
    def init_templates(self):
        """Initialize notification templates"""
        # Email templates
        self.email_templates = {
            'welcome': {
                'subject': 'Welcome to Our Service!',
                'template': lambda user_name, team_name: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #3498db; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Welcome!</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello {user_name},</p>
                    <p style="color: #333333; font-size: 16px;">Welcome to our service! We're excited to have you on board.</p>
                    <p style="color: #333333; margin-top: 20px;">Best regards,<br>The {team_name} Team</p>
                  </div>
                </div>
                """
            },
            'passwordReset': {
                'subject': 'Password Reset Request',
                'template': lambda user_name, reset_link: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #e74c3c; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Password Reset</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello {user_name},</p>
                    <p style="color: #333333; font-size: 16px;">We received a request to reset your password. Click the link below to reset it:</p>
                    <p style="text-align: center; margin: 20px 0;">
                      <a href="{reset_link}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
                    </p>
                    <p style="color: #333333; font-size: 14px;">If you didn't request this, please ignore this email.</p>
                  </div>
                </div>
                """
            },
            'accountUpdate': {
                'subject': 'Account Update Notification',
                'template': lambda user_name, update_details: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #2ecc71; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Account Update</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello {user_name},</p>
                    <p style="color: #333333; font-size: 16px;">Your account has been updated with the following changes:</p>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                      {update_details}
                    </div>
                    <p style="color: #333333; margin-top: 20px;">Best regards,<br>Support Team</p>
                  </div>
                </div>
                """
            },
            # Policy notification templates
            'policySubmitted': {
                'subject': 'Policy "{policy_title}" Submitted for Your Review',
                'template': lambda reviewer_name, policy_title, submitter_name, due_date: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #3498db; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Policy Review Required</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello {reviewer_name},</p>
                    <p style="color: #333333; font-size: 16px;">{submitter_name} has submitted <strong>"{policy_title}"</strong> for approval. Please review and either approve or reject by {due_date}.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'policyApproved': {
                'subject': 'Your Policy "{policy_title}" Has Been Approved',
                'template': lambda submitter_name, policy_title, reviewer_name, date_time: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #2ecc71; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Policy Approved</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hi {submitter_name},</p>
                    <p style="color: #333333; font-size: 16px;">Your policy <strong>"{policy_title}"</strong> was approved by {reviewer_name} on {date_time}. It is now active.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'policyRejected': {
                'subject': 'Your Policy "{policy_title}" Was Rejected',
                'template': lambda submitter_name, policy_title, reviewer_name, reviewer_comment: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #e74c3c; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Policy Rejected</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello {submitter_name},</p>
                    <p style="color: #333333; font-size: 16px;">Your policy <strong>"{policy_title}"</strong> was rejected by {reviewer_name} for the following reason:</p>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                      <p style="color: #333333; font-style: italic;">"{reviewer_comment}"</p>
                    </div>
                    <p style="color: #333333; font-size: 16px;">Please revise and resubmit.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'policyNewVersion': {
                'subject': 'New Version of Policy "{policy_title}" Published',
                'template': lambda user_name, policy_title, version, link: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #9b59b6; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">New Policy Version Available</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Dear {user_name},</p>
                    <p style="color: #333333; font-size: 16px;">A new version (v{version}) of <strong>"{policy_title}"</strong> is now available. <a href="{link}" style="color: #3498db;">View it here</a>.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'policyStatusChange': {
                'subject': 'Policy "{policy_title}" {status}',
                'template': lambda user_name, policy_title, status, actor_name, date_time: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #f39c12; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Policy Status Update</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello {user_name},</p>
                    <p style="color: #333333; font-size: 16px;">The policy <strong>"{policy_title}"</strong> has just been <strong>{status}</strong> by {actor_name} on {date_time}.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'complianceAssigned': {
                'subject': 'New Compliance Task: "{item_title}"',
                'template': lambda officer_name, item_title, assignor_name, due_date: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #3498db; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">New Compliance Task</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hi {officer_name},</p>
                    <p style="color: #333333; font-size: 16px;">You've been assigned the compliance item <strong>"{item_title}"</strong> by {assignor_name}. Due by {due_date}.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'complianceDueReminder': {
                'subject': 'Reminder: Compliance "{item_title}" Due in 2 Days',
                'template': lambda officer_name, item_title, due_date: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #f39c12; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Compliance Due Reminder</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello {officer_name},</p>
                    <p style="color: #333333; font-size: 16px;">This is a reminder that <strong>"{item_title}"</strong> is due on {due_date}.</p>
                    <p style="color: #333333; font-size: 16px;">Please update your progress.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'complianceCompleted': {
                'subject': 'Compliance "{item_title}" Ready for Review',
                'template': lambda reviewer_name, item_title, officer_name, review_due_date: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #2ecc71; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Compliance Ready for Review</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hi {reviewer_name},</p>
                    <p style="color: #333333; font-size: 16px;"><strong>"{item_title}"</strong> has been completed by {officer_name}.</p>
                    <p style="color: #333333; font-size: 16px;">Please review and approve or reject by {review_due_date}.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'complianceReviewed': {
                'subject': 'Your Compliance "{item_title}" Was {status}',
                'template': lambda officer_name, item_title, status, reviewer_name, reviewer_comment: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: {'#2ecc71' if status == 'Approved' else '#e74c3c'}; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Compliance {status}</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello {officer_name},</p>
                    <p style="color: #333333; font-size: 16px;">Your compliance item <strong>"{item_title}"</strong> was <strong>{status}</strong> by {reviewer_name}.</p>
                    {f'<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;"><p style="color: #333333; font-style: italic;">{reviewer_comment}</p></div>' if reviewer_comment else ''}
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'auditAssigned': {
                'subject': 'New Audit Assigned: "{audit_title}"',
                'template': lambda auditor_name, audit_title, scope, start_date: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #3498db; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">New Audit Assignment</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hi {auditor_name},</p>
                    <p style="color: #333333; font-size: 16px;">You have been assigned audit <strong>"{audit_title}"</strong> covering {scope}. Start by {start_date}.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'auditStartReminder': {
                'subject': 'Audit "{audit_title}" Starts Today',
                'template': lambda auditor_name, audit_title: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #f39c12; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Audit Start Reminder</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello {auditor_name},</p>
                    <p style="color: #333333; font-size: 16px;">Your audit <strong>"{audit_title}"</strong> begins today. Please begin your fieldwork.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'auditCompleted': {
                'subject': 'Audit "{audit_title}" Ready for Review',
                'template': lambda reviewer_name, audit_title, auditor_name, review_due_date: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #2ecc71; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Audit Ready for Review</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hi {reviewer_name},</p>
                    <p style="color: #333333; font-size: 16px;">{auditor_name} has completed <strong>"{audit_title}"</strong>. Please review the findings by {review_due_date}.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'auditReviewed': {
                'subject': 'Your Audit "{audit_title}" Review Is Complete',
                'template': lambda auditor_name, audit_title, status, reviewer_name, reviewer_comment: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: {'#2ecc71' if status == 'Approved' else '#e74c3c'}; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Audit {status}</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello {auditor_name},</p>
                    <p style="color: #333333; font-size: 16px;">Your audit <strong>"{audit_title}"</strong> was <strong>{status}</strong> by {reviewer_name}.</p>
                    {f'<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;"><p style="color: #333333; font-style: italic;">{reviewer_comment}</p></div>' if reviewer_comment else ''}
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'riskIdentified': {
                'subject': 'New Risk "{risk_title}" Logged',
                'template': lambda risk_mgr, risk_title, category, creator_name: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #e74c3c; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">New Risk Identified</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello {risk_mgr},</p>
                    <p style="color: #333333; font-size: 16px;">A new risk <strong>"{risk_title}"</strong> (Category: {category}) was identified by {creator_name}.</p>
                    <p style="color: #333333; font-size: 16px;">Please assess it.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'riskMitigationAssigned': {
                'subject': 'Risk Mitigation Task: "{risk_title}"',
                'template': lambda mitigator, risk_title, due_date: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #3498db; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Risk Mitigation Assigned</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hi {mitigator},</p>
                    <p style="color: #333333; font-size: 16px;">You've been assigned mitigation for risk <strong>"{risk_title}"</strong> due {due_date}.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'riskMitigationCompleted': {
                'subject': 'Mitigation for "{risk_title}" Ready for Review',
                'template': lambda reviewer_name, risk_title, mitigator, review_due_date: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #2ecc71; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Risk Mitigation Completed</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello {reviewer_name},</p>
                    <p style="color: #333333; font-size: 16px;">{mitigator} has completed mitigation for <strong>"{risk_title}"</strong>. Review by {review_due_date}.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'riskScoreUpdated': {
                'subject': 'Risk "{risk_title}" Score Updated',
                'template': lambda risk_mgr, risk_title, old_score, new_score, actor_name: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #f39c12; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Risk Score Updated</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Dear {risk_mgr},</p>
                    <p style="color: #333333; font-size: 16px;">The score for <strong>"{risk_title}"</strong> has been updated from {old_score} to {new_score} by {actor_name}.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'incidentEscalated': {
                'subject': 'Incident "{incident_title}" Escalated',
                'template': lambda manager_name, incident_title, escalator_name: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #e74c3c; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Incident Escalated</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello {manager_name},</p>
                    <p style="color: #333333; font-size: 16px;">Incident <strong>"{incident_title}"</strong> was escalated by {escalator_name}. Please review immediately.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'incidentAssigned': {
                'subject': 'New Incident Assigned: "{incident_title}"',
                'template': lambda assignee_name, incident_title, due_date: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #3498db; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">New Incident Assignment</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hi {assignee_name},</p>
                    <p style="color: #333333; font-size: 16px;">You've been assigned incident <strong>"{incident_title}"</strong>. Please investigate by {due_date}.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'incidentResolved': {
                'subject': 'Incident "{incident_title}" Resolved',
                'template': lambda incident_title, assignee_name, date_time: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #2ecc71; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Incident Resolved</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hello,</p>
                    <p style="color: #333333; font-size: 16px;">Incident <strong>"{incident_title}"</strong> has been resolved by {assignee_name} on {date_time}.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'roleAssignmentChanged': {
                'subject': 'Your GRC Role Has Been Updated',
                'template': lambda user_name, new_role, admin_name: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #3498db; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Role Update</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Hi {user_name},</p>
                    <p style="color: #333333; font-size: 16px;">Your role has been updated to <strong>{new_role}</strong> by {admin_name}. Effective immediately.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            },
            'systemMaintenance': {
                'subject': 'Scheduled Maintenance on {date}',
                'template': lambda date, start_time, end_time: f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                  <div style="background-color: #f39c12; padding: 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px;">System Maintenance</h1>
                  </div>
                  <div style="padding: 20px;">
                    <p style="color: #333333; font-size: 16px;">Dear User,</p>
                    <p style="color: #333333; font-size: 16px;">GRC will undergo maintenance from {start_time} to {end_time}. The system will be unavailable during this window.</p>
                    <p style="color: #333333; margin-top: 20px;">– GRC Team</p>
                  </div>
                </div>
                """
            }
        }
        
        # WhatsApp templates
        self.whatsapp_templates = {
            'welcome': {
                'name': 'welcome_message',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['userName', 'teamName'],
                    },
                ],
            },
            'passwordReset': {
                'name': 'password_reset',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['userName', 'resetLink'],
                    },
                ],
            },
            'accountUpdate': {
                'name': 'account_update',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['userName', 'updateDetails'],
                    },
                ],
            },
            'policySubmitted': {
                'name': 'policy_submitted_for_review',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['reviewerName', 'policyTitle', 'submitterName', 'dueDate'],
                    },
                ],
            },
            'policyApproved': {
                'name': 'policy_approved',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['submitterName', 'policyTitle', 'reviewerName', 'dateTime'],
                    },
                ],
            },
            'policyRejected': {
                'name': 'policy_rejected',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['submitterName', 'policyTitle', 'reviewerName', 'reviewerComment'],
                    },
                ],
            },
            'policyNewVersion': {
                'name': 'policy_new_version',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['userName', 'policyTitle', 'version', 'link'],
                    },
                ],
            },
            'policyStatusChange': {
                'name': 'policy_status_change',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['userName', 'policyTitle', 'status', 'actorName', 'dateTime'],
                    },
                ],
            },
            'complianceAssigned': {
                'name': 'compliance_assigned',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['officerName', 'itemTitle', 'assignorName', 'dueDate'],
                    },
                ],
            },
            'complianceDueReminder': {
                'name': 'compliance_due_reminder',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['officerName', 'itemTitle', 'dueDate'],
                    },
                ],
            },
            'complianceCompleted': {
                'name': 'compliance_completed',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['reviewerName', 'itemTitle', 'officerName', 'reviewDueDate'],
                    },
                ],
            },
            'complianceReviewed': {
                'name': 'compliance_reviewed',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['officerName', 'itemTitle', 'status', 'reviewerName', 'reviewerComment'],
                    },
                ],
            },
            'auditAssigned': {
                'name': 'audit_assigned',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['auditorName', 'auditTitle', 'scope', 'startDate'],
                    },
                ],
            },
            'auditStartReminder': {
                'name': 'audit_start_reminder',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['auditorName', 'auditTitle'],
                    },
                ],
            },
            'auditCompleted': {
                'name': 'audit_completed',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['reviewerName', 'auditTitle', 'auditorName', 'reviewDueDate'],
                    },
                ],
            },
            'auditReviewed': {
                'name': 'audit_reviewed',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['auditorName', 'auditTitle', 'status', 'reviewerName', 'reviewerComment'],
                    },
                ],
            },
            'riskIdentified': {
                'name': 'risk_identified',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['riskMgr', 'riskTitle', 'category', 'creatorName'],
                    },
                ],
            },
            'riskMitigationAssigned': {
                'name': 'risk_mitigation_assigned',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['mitigator', 'riskTitle', 'dueDate'],
                    },
                ],
            },
            'riskMitigationCompleted': {
                'name': 'risk_mitigation_completed',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['reviewerName', 'riskTitle', 'mitigator', 'reviewDueDate'],
                    },
                ],
            },
            'riskScoreUpdated': {
                'name': 'risk_score_updated',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['riskMgr', 'riskTitle', 'oldScore', 'newScore', 'actorName'],
                    },
                ],
            },
            'incidentEscalated': {
                'name': 'incident_escalated',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['managerName', 'incidentTitle', 'escalatorName'],
                    },
                ],
            },
            'incidentAssigned': {
                'name': 'incident_assigned',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['assigneeName', 'incidentTitle', 'dueDate'],
                    },
                ],
            },
            'incidentResolved': {
                'name': 'incident_resolved',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['incidentTitle', 'assigneeName', 'dateTime'],
                    },
                ],
            },
            'roleAssignmentChanged': {
                'name': 'role_assignment_changed',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['userName', 'newRole', 'adminName'],
                    },
                ],
            },
            'systemMaintenance': {
                'name': 'system_maintenance',
                'components': [
                    {
                        'type': 'body',
                        'parameters': ['date', 'startTime', 'endTime'],
                    },
                ],
            }
        }

    def send_email(self, to, email_type, notification_type, template_data):
        """Send email notification"""
        try:
            # Get email config based on type
            config = self.email_configs.get(email_type.lower())
            if not config:
                raise ValueError(f"Unsupported email type: {email_type}")
            
            # Get template
            template = self.email_templates.get(notification_type)
            if not template:
                raise ValueError(f"Unsupported notification type: {notification_type}")
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = f"{self.default_from['name']} <{self.default_from['email']}>"
            msg['To'] = to
            
            # Format subject with template data if needed
            subject = template['subject']
            if '{policy_title}' in subject and len(template_data) >= 2:
                subject = subject.replace('{policy_title}', template_data[1])
            if '{incident_title}' in subject and len(template_data) >= 2:
                subject = subject.replace('{incident_title}', template_data[1])
            
            msg['Subject'] = subject
            
            # Apply template data to create HTML content
            html_content = template['template'](*template_data)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Connect to SMTP server and send email - handling Microsoft differently
            if email_type.lower() == 'microsoft':
                with smtplib.SMTP(config['host'], config['port']) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    username = config['auth']['user']
                    password = config['auth']['pass']
                    logger.info(f"Attempting Microsoft SMTP auth with username: {username}")
                    server.login(username, password)
                    server.send_message(msg)
                    logger.info(f"Microsoft email sent successfully to {to}")
            else:
                with smtplib.SMTP(config['host'], config['port']) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(config['auth']['user'], config['auth']['pass'])
                    server.send_message(msg)

            
            logger.info(f"Email sent successfully to {to}, type: {notification_type}")
            
            # Log notification in database
            self.log_notification(to, notification_type, 'email', True)
            
            return {"success": True, "to": to, "type": notification_type}
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            # Log failed notification
            self.log_notification(to, notification_type, 'email', False, str(e))
            return {"success": False, "error": str(e)}
    
    def send_whatsapp(self, to, notification_type, template_parameters):
        """Send WhatsApp notification"""
        try:
            # Get template
            template = self.whatsapp_templates.get(notification_type)
            if not template:
                raise ValueError(f"Unsupported WhatsApp template: {notification_type}")
            
            # Create WhatsApp API client
            url = f"https://graph.facebook.com/{self.whatsapp_config['api_version']}/{self.whatsapp_config['phone_number_id']}/messages"
            headers = {
                'Authorization': f"Bearer {self.whatsapp_config['access_token']}",
                'Content-Type': 'application/json'
            }
            
            # Prepare message payload
            payload = {
                'messaging_product': 'whatsapp',
                'to': to,
                'type': 'template',
                'template': {
                    'name': template['name'],
                    'language': {'code': self.whatsapp_config['default_language']},
                    'components': [
                        {
                            'type': comp['type'],
                            'parameters': [
                                {'type': 'text', 'text': template_parameters[i]}
                                for i, param in enumerate(comp['parameters'])
                            ]
                        } for comp in template['components']
                    ]
                }
            }
            
            # Send message
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            
            response_data = response.json()
            message_id = response_data.get('messages', [{}])[0].get('id', 'unknown')
            
            logger.info(f"WhatsApp message sent successfully to {to}, type: {notification_type}, id: {message_id}")
            
            # Log notification in database
            self.log_notification(to, notification_type, 'whatsapp', True)
            
            return {"success": True, "to": to, "type": notification_type, "messageId": message_id}
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            # Log failed notification
            self.log_notification(to, notification_type, 'whatsapp', False, str(e))
            return {"success": False, "error": str(e)}
    
    def log_notification(self, recipient, notification_type, channel, success, error=None):
        """Log notification in database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO notifications 
            (recipient, type, channel, success, error, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            values = (
                recipient, 
                notification_type, 
                channel, 
                success, 
                error, 
                datetime.now()
            )
            
            cursor.execute(query, values)
            conn.commit()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging notification: {str(e)}")
    
    def send_multi_channel_notification(self, notification_data):
        """Send notification through multiple channels"""
        results = {
            "email": None,
            "whatsapp": None,
            "errors": []
        }
        
        notification_type = notification_data.get('notification_type')
        if not notification_type:
            return {"success": False, "error": "Missing notification_type"}
        
        # Send email if email details provided
        if notification_data.get('email') and notification_data.get('email_type'):
            try:
                email_result = self.send_email(
                    notification_data['email'],
                    notification_data['email_type'],
                    notification_type,
                    notification_data.get('template_data', [])
                )
                
                if email_result.get('success'):
                    results['email'] = {
                        'to': notification_data['email'],
                        'type': notification_data['email_type']
                    }
                else:
                    results['errors'].append({
                        'channel': 'email',
                        'error': email_result.get('error')
                    })
            except Exception as e:
                results['errors'].append({
                    'channel': 'email',
                    'error': str(e)
                })
        
        # Send WhatsApp if number provided
        if notification_data.get('whatsapp_number'):
            try:
                whatsapp_result = self.send_whatsapp(
                    notification_data['whatsapp_number'],
                    notification_type,
                    notification_data.get('template_data', [])
                )
                
                if whatsapp_result.get('success'):
                    results['whatsapp'] = {
                        'to': notification_data['whatsapp_number'],
                        'messageId': whatsapp_result.get('messageId')
                    }
                else:
                    results['errors'].append({
                        'channel': 'whatsapp',
                        'error': whatsapp_result.get('error')
                    })
            except Exception as e:
                results['errors'].append({
                    'channel': 'whatsapp',
                    'error': str(e)
                })
        
        # If both channels failed
        if len(results['errors']) == 2:
            return {
                "success": False,
                "error": "Failed to send notifications to all channels",
                "details": results['errors']
            }
        
        # Return success with results
        return {
            "success": True,
            "message": "Notifications sent successfully",
            "details": {
                "email": results['email'],
                "whatsapp": results['whatsapp'],
                "errors": results['errors'] if results['errors'] else None
            }
        }
    
    # 
    
# # Example usage
# if __name__ == "__main__":
#     # Initialize notification service
#     notification_service = NotificationService()
    
#     # # Create database tables
#     # try:
#     #     notification_service.create_database_tables()
#     # except Exception as e:
#     #     logger.error(f"Failed to create database tables: {str(e)}")
    
#     # Example 1: Welcome email
#     welcome_data = {
#         'notification_type': 'welcome',
#         'email': 'syammuni916@gmail.com',
#         'email_type': 'gmail',
#         'template_data': ['Muni syam putthuru', 'GRC']
#     }
    
#     # Example 2: Policy submitted notification (both email and WhatsApp)
#     policy_data = {
#         'notification_type': 'policySubmitted',
#         'email': 'syammuni916@gmail.com',
#         'email_type': 'gmail',
#         # 'whatsapp_number': '1234567890',
#         'template_data': ['Jane Smith', 'Data Privacy Policy', 'John Doe', '2023-08-15']
#     }
    
#     # Example 3: Incident assigned notification
#     incident_data = {
#         'notification_type': 'incidentAssigned',
#         'email': 'security@example.com',
#         'email_type': 'gmail',
#         'whatsapp_number': '9876543210',
#         'template_data': ['Security Team', 'Data Breach Investigation', '2023-08-10']
#     }
    
#     # Send notifications using multi-channel method
#     # print("Sending welcome notification...")
#     # result1 = notification_service.send_multi_channel_notification(welcome_data)
#     # print(f"Result: {result1}")
    
#     print("\nSending policy notification...")
#     result2 = notification_service.send_multi_channel_notification(policy_data)
#     print(f"Result: {result2}")
    
#     # print("\nSending incident notification...")
#     # result3 = notification_service.send_multi_channel_notification(policy_data)
#     # print(f"Result: {result3}")
