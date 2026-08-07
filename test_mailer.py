import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Secrets se automatic fetch karega
SENDER_EMAIL = "maviyaattar4@gmail.com"
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

SENDER_NAME = "Maviya Attar"
WEBSITE_URL = "https://maviyaattar.vercel.app"
WHATSAPP_NUM = "9272486121"
WHATSAPP_LINK = "https://wa.me/919272486121"
CUSTOM_SIGNATURE = "معاویہ 『AM』"

def build_html_email(recipient_name="Maviya", role="Full-Stack Developer & UI/UX Designer"):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 20px; color: #0f172a; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 14px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); }}
            .header {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 32px 24px; color: #ffffff; text-align: left; }}
            .header h2 {{ margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px; }}
            .body-content {{ padding: 28px 24px; line-height: 1.65; font-size: 15px; color: #334155; }}
            .highlight {{ color: #2563eb; font-weight: 600; background: #eff6ff; padding: 2px 6px; border-radius: 4px; }}
            .btn-wrapper {{ margin: 28px 0; }}
            .btn {{ display: inline-block; background-color: #2563eb; color: #ffffff !important; text-decoration: none; padding: 12px 22px; border-radius: 8px; font-weight: 600; font-size: 14px; margin-right: 8px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2); }}
            .btn-whatsapp {{ background-color: #25d366; color: #ffffff !important; box-shadow: 0 4px 12px rgba(37, 211, 102, 0.2); }}
            .signature-box {{ margin-top: 32px; padding-top: 20px; border-top: 2px dashed #e2e8f0; font-size: 14px; color: #64748b; }}
            .sig-author {{ font-size: 16px; font-weight: 700; color: #0f172a; display: block; }}
            .sig-brand {{ font-size: 18px; font-weight: 700; color: #2563eb; display: block; margin-bottom: 6px; }}
            .contact-link {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Project Collaboration & Client Network 🚀</h2>
            </div>
            <div class="body-content">
                <p>Hi <strong>{recipient_name}</strong>,</p>

                <p>I came across your profile and noticed your strong background as a <span class="highlight">{role}</span>.</p>

                <p>I am building a network of skilled full-stack developers, UI/UX designers, and tech freelancers across India for expanding client web service projects, custom design workflows, and active development opportunities.</p>

                <p>Whether you are currently open for freelance projects, technical collaboration, or client work partnerships, I’d love to connect with you!</p>

                <div class="btn-wrapper">
                    <a href="{WEBSITE_URL}" class="btn" target="_blank">🌐 Portfolio Website</a>
                    <a href="{WHATSAPP_LINK}" class="btn btn-whatsapp" target="_blank">💬 Chat on WhatsApp</a>
                </div>

                <p>If you're interested in discussing upcoming projects, feel free to reply directly or ping me on WhatsApp.</p>

                <div class="signature-box">
                    <span class="sig-author">{SENDER_NAME}</span>
                    <span class="sig-brand">{CUSTOM_SIGNATURE}</span>
                    <span>Full-Stack Developer & UI/UX Designer</span><br>
                    <span>Solapur, Maharashtra, India</span><br><br>
                    🌐 Website: <a href="{WEBSITE_URL}" class="contact-link">{WEBSITE_URL}</a><br>
                    📱 WhatsApp: <a href="{WHATSAPP_LINK}" class="contact-link">+91 {WHATSAPP_NUM}</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

def send_test_mail():
    if not SENDER_PASSWORD:
        print("[-] ERROR: SENDER_PASSWORD GitHub Secret / Env variable me nahi mila!")
        return

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print("[+] Gmail SMTP Login Successful!")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🧪 [TEST] Collaboration Opportunity Preview Email"
        msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg["To"] = SENDER_EMAIL

        msg.attach(MIMEText(build_html_email(), "html"))
        server.sendmail(SENDER_EMAIL, SENDER_EMAIL, msg.as_string())
        server.quit()

        print(f"[✓] TEST EMAIL SENT SUCCESSFULLY TO: {SENDER_EMAIL}")
    except Exception as e:
        print(f"[-] SMTP Error: {e}")

if __name__ == "__main__":
    send_test_mail()
