import os
import re
import csv
import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Strict Email Regex
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Ignored Emails (System / Fake / Docs)
IGNORED_EMAILS = {
    "noreply@github.com", "example@gmail.com", "info@domain.com", 
    "user@gmail.com", "admin@domain.com", "support@github.com"
}

# Indian States & Tech Hubs for Strict Filtering
INDIAN_LOCATIONS = [
    "india", "bangalore", "bengaluru", "mumbai", "delhi", "noida", 
    "gurugram", "gurgaon", "pune", "hyderabad", "chennai", "ahmedabad", 
    "kolkata", "surat", "jaipur", "indore", "kochi", "kerala"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def is_valid_email(email):
    """Filters out garbage, system, and dummy emails."""
    email_lower = email.lower()
    if email_lower in IGNORED_EMAILS:
        return False
    if any(email_lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif"]):
        return False
    return True

def is_indian_location(text):
    """Checks if location or text belongs to India."""
    if not text:
        return False
    text_lower = text.lower()
    return any(loc in text_lower for loc in INDIAN_LOCATIONS)

def search_github_india_leads(role_query, max_results=30):
    """Fetches verified Indian freshers/freelancers from GitHub API."""
    print(f"[+] Scraping GitHub India for: {role_query}")
    # Explicitly targeted for India
    query = f"{role_query} location:india"
    url = f"https://api.github.com/search/users?q={query}&per_page={max_results}"
    
    gh_headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        gh_headers["Authorization"] = f"token {token}"

    leads = []
    try:
        res = requests.get(url, headers=gh_headers, timeout=10)
        if res.status_code == 200:
            users = res.json().get("items", [])
            for u in users:
                u_detail = requests.get(u["url"], headers=gh_headers, timeout=10).json()
                
                location = u_detail.get("location") or ""
                # Strict check for India location
                if not is_indian_location(location):
                    continue

                email = u_detail.get("email")
                bio = u_detail.get("bio") or ""
                blog = u_detail.get("blog") or ""

                # Extract email from bio/blog if not in profile email
                if not email:
                    found_emails = re.findall(EMAIL_REGEX, f"{bio} {blog}")
                    if found_emails:
                        email = found_emails[0]

                if email and is_valid_email(email):
                    leads.append({
                        "id": u_detail.get("id"),
                        "name": u_detail.get("name") or u_detail.get("login"),
                        "email": email.lower(),
                        "role": role_query,
                        "location": location,
                        "source": "GitHub",
                        "profile_url": u_detail.get("html_url"),
                        "date_extracted": datetime.now().strftime("%Y-%m-%d")
                    })
    except Exception as e:
        print(f"[-] GitHub Search Error: {e}")

    return leads

def search_google_dorks_india(dork_query, role_tag):
    """Extracts public Indian freelancer emails via Google Search Dorking."""
    print(f"[+] Executing Google Dork: {dork_query}")
    url = f"https://www.google.com/search?q={dork_query}&num=30"
    
    leads = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            text = soup.get_text()
            
            raw_emails = re.findall(EMAIL_REGEX, text)
            for email in set(raw_emails):
                email_clean = email.lower()
                if is_valid_email(email_clean) and not any(k in email_clean for k in ["github", "google"]):
                    leads.append({
                        "id": f"g_{hash(email_clean)}",
                        "name": "Indian Freelancer",
                        "email": email_clean,
                        "role": role_tag,
                        "location": "India",
                        "source": "LinkedIn / Search Dork",
                        "profile_url": "Public Search Result",
                        "date_extracted": datetime.now().strftime("%Y-%m-%d")
                    })
    except Exception as e:
        print(f"[-] Google Dork Error: {e}")

    return leads

def save_structured_leads(leads, csv_file="leads.csv", json_file="leads.json"):
    """Saves leads into both CSV and JSON formats with strict de-duplication."""
    if not leads:
        print("[-] No new leads found in this run.")
        return

    # Load existing emails to avoid duplicates across multiple runs
    existing_emails = set()
    if os.path.exists(csv_file):
        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("email"):
                    existing_emails.add(row["email"].lower())

    # Filter out duplicate emails
    fresh_leads = [l for l in leads if l["email"] not in existing_emails]

    if not fresh_leads:
        print("[!] All scraped leads are already saved in the database.")
        return

    # 1. Save to CSV
    fieldnames = ["id", "name", "email", "role", "location", "source", "profile_url", "date_extracted"]
    file_exists = os.path.exists(csv_file)
    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(fresh_leads)

    # 2. Save/Update JSON (Perfect for API & Automation Integration)
    all_json_data = []
    if os.path.exists(json_file):
        try:
            with open(json_file, mode="r", encoding="utf-8") as jf:
                all_json_data = json.load(jf)
        except json.JSONDecodeError:
            all_json_data = []

    all_json_data.extend(fresh_leads)
    with open(json_file, mode="w", encoding="utf-8") as jf:
        json.dump(all_json_data, jf, indent=4)

    print(f"[✓] SUCCESS: Saved {len(fresh_leads)} NEW Indian leads to {csv_file} and {json_file}")

if __name__ == "__main__":
    collected_leads = []

    # 1. GitHub Indian Keywords Target
    gh_roles = [
        "fresher web designer",
        "freelance UI UX designer",
        "frontend developer freelancer",
        "fresher web developer"
    ]
    for role in gh_roles:
        collected_leads.extend(search_github_india_leads(role))
        time.sleep(1)

    # 2. Google LinkedIn Dorks (Targeting @gmail.com for Indian Designers & Freshers)
    google_dorks = [
        ('site:linkedin.com/in/ "web designer" "freelancer" "India" "@gmail.com"', "Web Designer"),
        ('site:linkedin.com/in/ "fresher web developer" "India" "@gmail.com"', "Fresher Web Developer"),
        ('site:linkedin.com/in/ "UI/UX designer" "India" "@gmail.com"', "UI/UX Designer")
    ]
    for dork, role_tag in google_dorks:
        collected_leads.extend(search_google_dorks_india(dork, role_tag))
        time.sleep(2)

    # Save outputs
    save_structured_leads(collected_leads)
