from models import Ticket

KB_ARTICLES = {
    "API Rate Limits": "Cloud API standard rate limit is 1000 requests per minute. Upgrade to Enterprise for 10000 req/min. Exceeding limits returns HTTP 429 Too Many Requests.",
    "Authentication Tokens": "Use Bearer tokens for API auth. Generate them in the Developer Dashboard under 'Security'. Tokens expire every 90 days.",
    "Data Retention Policy": "Free tier retains data for 7 days. Pro tier 30 days. Deleted data cannot be recovered after the retention period.",
    "Refund Policy": "Refunds are processed within 14 days of purchase. Only unused API credits are eligible. Contact billing@cloudapi.com.",
    "Account Deletion": "To delete an account, navigate to Organization Settings -> Danger Zone -> Terminate. Warning: Irreversible.",
    "Webhook Timeouts": "Webhooks time out after 5 seconds. Ensure your endpoint responds with 2xx HTTP status code quickly.",
    "Pagination Strategies": "Our API uses cursor-based pagination. Look for 'next_cursor' in the response JSON to fetch the next page.",
    "SLA Constraints": "Enterprise customers receive 99.99% uptime SLA. Pro tier receives 99.9% uptime. Downtime compensation is prorated.",
    "Server Outage - US-East": "INCIDENT ONGOING: US-East-1 is experiencing degraded API latency. ETA for resolution is 2 hours.",
    "Supported SDKs": "We officially support Python, Node.js, and Go SDKs. Community SDKs exist for Rust and Ruby but are unmaintained.",
    "Database Backups": "Automated backups run nightly for Pro users. To restore, use the CLI command 'cloudapi db restore --latest'.",
    "Invalid JSON Payload Errors": "HTTP 400 Bad Request indicates malformed JSON. Ensure you send Content-Type: application/json header.",
    "Rate Limit Headers": "Check the X-RateLimit-Remaining header in the HTTP response to monitor your quota.",
    "CORS Configuration": "Allowed origins must be explicitly configured in the Dashboard under API Settings -> CORS.",
    "Billing Invoices": "Monthly invoices are generated on the 1st. You can download PDF copies under the Billing tab.",
}

def T(tid, sub, body, prio):
    return Ticket(ticket_id=tid, subject=sub, body=body, priority=prio)

TASKS = {
    "easy_classify": [
        T("T01", "Need invoice copy", "Can I get my latest API usage invoice?", "Low"), # Billing
        T("T02", "SDK question", "Do you support Rust officially?", "Low"), # Technical
        T("T03", "Reset password", "I am locked out.", "High"), # Account
        T("T04", "Upgrade to Pro", "How do I pay for Pro?", "Medium"), # Billing
        T("T05", "Change email", "Need to change my admin email.", "Low"), # Account
    ],
    "medium_kb_reply": [
        T("M01", "HTTP 429", "My scripts are failing with Too Many Requests, what is the limit?", "High"), # Reply: 1000 requests
        T("M02", "Pagination", "How do I get the second page of users?", "Medium"), # Reply: cursor-based
        T("M03", "Node SDK Error", "Is Node.js officially supported?", "Low"), # Reply: Yes
        T("M04", "Webhooks failing", "My webhooks terminate early. How long do they stay open?", "High"), # Reply: 5 seconds
        T("M05", "Refund request", "I didn't use my API credits, can I get a refund?", "Medium"), # Reply: within 14 days
    ],
    "hard_mixed_queue": [
        T("H01", "PRODUCTION DOWN", "Your update wiped my production database. I am escalating to legal immediately!", "Critical"), # Escalate
        T("H02", "CORS issue", "Browser says CORS blocked from localhost.", "Medium"), # Technical, reply
        T("H03", "Lost data", "I accidentally deleted my account yesterday. Can you recover it?", "Critical"), # Escalate
        T("H04", "Where is the invoice", "Send invoice", "Low"), # Billing, reply
        T("H05", "US East timing out", "My requests to us-east are taking 30 seconds.", "High"), # Technical, reply Outage
        T("H06", "Enterprise contact", "I need 500,000 req/min limits. Let me talk to a sales manager.", "High"), # Escalate
        T("H07", "Bearer token", "How long before my token expires?", "Low"), # Technical, reply 90 days
        T("H08", "What is cloud?", "Can you tell me a joke about clouds?", "Low"), # Other, reply 
        T("H09", "Nightly backup", "How do I restore latest db?", "Medium"), # Technical, reply
        T("H10", "Cancel everything", "I am moving to AWS. Delete my org now.", "High") # Account, Reply Account Deletion
    ]
}

def get_task_data(task_id: str):
    return TASKS[task_id].copy()
