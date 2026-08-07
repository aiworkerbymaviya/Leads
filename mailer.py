import os
import csv
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==================== CONFIGURATION ====================
# Hardcoded Sender Email as requested
SENDER_EMAIL = "maviyaattar4@gmail.com"
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

SENDER_NAME = "Maviya Attar"
BRAND_NAME = "TargetData Pro"
LANDING_PAGE_URL = "https://targetdatapro.vercel.app"
WHATSAPP_LINK = "https://wa.me/919272486121?text=Hi%20Maviya,%20I%20want%20to%20order%20B2B%20Leads"
WHATSAPP_NUM = "9272486121"
CUSTOM_SIGNATURE = "معاویہ 『AM』"

SENT_HISTORY_FILE = "sent_leads.json"
# =======================================================

def load_sent_history():
    if os.path.exists(SENT_HISTORY_FILE):
        try:
            with open(SENT_HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_sent_history(sent_set):
    with open(SENT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(sent_set), f, indent=4)

def build_b2b_sales_email(client_name="there", is_test=False):
    first_name = "there"
    if client_name and client_name.strip() and client_name != "Indian Freelancer":
        first_name = client_name.strip().split()[0].capitalize()

    test_banner = """
    <div style="background:#fef08a; color:#854d0e; text-align:center; padding:8px; font-weight:bold; font-size:12px; letter-spacing:1px;">
        ⚡ PREVIEW TEST EMAIL SENT TO SENDER INBOX
    </div>
    """ if is_test else ""

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 0; color: #0f172a; }}
            .wrapper {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); }}
            .header {{ background: #0f172a; padding: 32px 24px; color: #ffffff; text-align: left; }}
            .brand-badge {{ background: #2563eb; color: #ffffff; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; display: inline-block; margin-bottom: 12px; }}
            .header h1 {{ margin: 0; font-size: 22px; font-weight: 800; line-height: 1.3; color: #ffffff; }}
            .header p {{ margin: 8px 0 0 0; color: #94a3b8; font-size: 14px; }}
            .content {{ padding: 28px 24px; line-height: 1.65; font-size: 15px; color: #334155; }}
            .price-tag {{ background: #f1f5f9; border-left: 4px solid #2563eb; padding: 12px 16px; border-radius: 0 8px 8px 0; margin: 20px 0; font-weight: 600; color: #1e293b; }}
            .grid {{ display: table; width: 100%; margin: 20px 0; border-collapse: separate; border-spacing: 8px; }}
            .card {{ display: table-cell; background: #fafafa; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; text-align: center; width: 33%; }}
            .card-title {{ font-size: 13px; font-weight: 700; color: #475569; text-transform: uppercase; }}
            .card-count {{ font-size: 16px; font-weight: 800; color: #2563eb; margin: 4px 0; }}
            .card-price {{ font-size: 12px; color: #16a34a; font-weight: 700; }}
            .btn-container {{ margin: 28px 0; text-align: left; }}
            .btn {{ display: inline-block; background: #2563eb; color: #ffffff !important; text-decoration: none; padding: 13px 26px; border-radius: 8px; font-weight: 700; font-size: 14px; margin-right: 8px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25); }}
            .btn-wa {{ background: #16a34a !important; box-shadow: 0 4px 12px rgba(22, 163, 74, 0.25); }}
            .signature {{ margin-top: 32px; padding-top: 20px; border-top: 2px dashed #e2e8f0; font-size: 14px; color: #64748b; }}
            .sig-name {{ font-size: 16px; font-weight: 800; color: #0f172a; display: block; }}
            .sig-brand {{ font-size: 18px; font-weight: 800; color: #2563eb; display: block; margin-top: 2px; }}
            .footer-link {{ color: #2563eb; text-decoration: none; font-weight: 600; }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            {test_banner}
            <div class="header">
                <span class="brand-badge">TargetData Pro</span>
                <h1>100% Verified B2B Lead Intelligence Datasets</h1>
                <p>Scale your client outreach with precision-targeted local business leads.</p>
            </div>
            
            <div class="content">
                <p>Hi <strong>{first_name}</strong>,</p>

                <p>Are you looking to scale your web design, agency services, or client outreach with high-intent B2B business leads in India?</p>

                <p>At <strong>TargetData Pro</strong>, we extract clean, decision-maker B2B datasets filtered specifically for web developers, marketers, and lead brokers.</p>

                <div class="price-tag">
                    🏷️ Standard Transparent Pricing: <strong>Flat ₹1 / Lead</strong> (Zero Hidden Fees)
                </div>

                <p><strong>Popular Niche Categories Ready For Instant Excel Export:</strong></p>

                <div class="grid">
                    <div class="card">
                        <div class="card-title">Healthcare</div>
                        <div class="card-count">2,547 Leads</div>
                        <div class="card-price">₹2,547</div>
                    </div>
                    <div class="card">
                        <div class="card-title">Hospitality</div>
                        <div class="card-count">2,917 Leads</div>
                        <div class="card-price">₹2,917</div>
                    </div>
                    <div class="card">
                        <div class="card-title">Wellness</div>
                        <div class="card-count">576 Leads</div>
                        <div class="card-price">₹576</div>
                    </div>
                </div>

                <ul style="padding-left: 20px; color: #475569;">
                    <li><strong>Franchise Filtered:</strong> Excludes big chains (OYO, KFC, etc.) so you focus on real local clients.</li>
                    <li><strong>10-Digit Mobile Numbers:</strong> Valid contacts for Cold Calling, WhatsApp & SMS.</li>
                    <li><strong>Instant Delivery:</strong> Clean Excel (.xlsx) file sent immediately.</li>
                </ul>

                <div class="btn-container">
                    <a href="{LANDING_PAGE_URL}" class="btn" target="_blank">🌐 View Landing Page</a>
                    <a href="{WHATSAPP_LINK}" class="btn btn-wa" target="_blank">💬 Order via WhatsApp</a>
                </div>

                <p>Need a custom lead count? Order any quantity at ₹1/lead directly from our calculator on the website.</p>

                <div class="signature">
                    <span class="sig-name">{SENDER_NAME}</span>
                    <span class="sig-brand">{CUSTOM_SIGNATURE}</span>
                    <span>Founder & Lead Data Engineer @ TargetData Pro</span><br>
                    <span>Solapur, Maharashtra, India</span><br><br>
                    🌐 Website: <a href="{LANDING_PAGE_URL}" class="footer-link">{LANDING_PAGE_URL}</a><br>
                    📱 WhatsApp: <a href="{WHATSAPP_LINK}" class="footer-link">+91 {WHATSAPP_NUM}</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_code

def send_b2b_campaign(csv_file="leads.csv"):
    clean_password = SENDER_PASSWORD.replace(" ", "").strip() if SENDER_PASSWORD else ""

    if not clean_password:
        print("[-] ERROR: SENDER_PASSWORD secret is missing or empty in GitHub Settings!")
        return

    # SMTP Connection via TLS (Port 587)
    try:
        print(f"[+] Connecting to Gmail SMTP via TLS Port 587 for {SENDER_EMAIL}...")
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SENDER_EMAIL, clean_password)
        print("[+] SUCCESS: Authenticated with Gmail SMTP!")
    except Exception as e:
        print(f"[-] SMTP Connection Failed: {e}")
        return

    # STEP 1: Send Test Email Preview
    print("\n[1/2] Sending Test Email Preview to Sender...")
    try:
        test_msg = MIMEMultipart("alternative")
        test_msg["Subject"] = "🧪 [PREVIEW TEST] TargetData Pro B2B Sales Email"
        test_msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        test_msg["To"] = SENDER_EMAIL
        test_msg.attach(MIMEText(build_b2b_sales_email("Maviya", is_test=True), "html"))
        
        server.sendmail(SENDER_EMAIL, SENDER_EMAIL, test_msg.as_string())
        print(f"[✓] TEST EMAIL PREVIEW SENT TO: {SENDER_EMAIL}\n")
    except Exception as e:
        print(f"[-] Failed to send test email: {e}")

    # STEP 2: Send Email to Saved Leads
    if not os.path.exists(csv_file):
        print(f"[-] ERROR: {csv_file} not found!")
        server.quit()
        return

    sent_history = load_sent_history()
    sent_count = 0
    skipped_count = 0

    print("[2/2] Processing Leads from repo leads.csv...")
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get("email", "").strip().lower()
            name = row.get("name", "Freelancer")

            if not email or "@" not in email:
                continue

            if email in sent_history:
                skipped_count += 1
                continue

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Verified B2B Lead Datasets at ₹1/Lead | TargetData Pro"
            msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
            msg["To"] = email
            msg.attach(MIMEText(build_b2b_sales_email(name), "html"))

            try:
                server.sendmail(SENDER_EMAIL, email, msg.as_string())
                sent_count += 1
                sent_history.add(email)
                print(f"[✓] Sent [{sent_count}]: {name} ({email})")
                time.sleep(2)
            except Exception as e:
                print(f"[-] Failed to send to {email}: {e}")

    server.quit()
    save_sent_history(sent_history)

    print(f"\n==========================================")
    print(f"[✓] Campaign Finished Successfully!")
    print(f"[+] Total Emails Sent    : {sent_count}")
    print(f"[!] Skipped (Already Sent): {skipped_count}")
    print(f"==========================================")

if __name__ == "__main__":
    send_b2b_campaign()
