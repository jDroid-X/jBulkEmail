import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

def add_shading(cell, fill_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), fill_color)
    shading.set(qn('w:val'), 'clear')
    tcPr.append(shading)

def header_format(table):
    for cell in table.rows[0].cells:
        add_shading(cell, "002060")
        for p in cell.paragraphs:
            for run in p.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

def create_full_dev_sow():
    doc = docx.Document()
    styles = doc.styles
    
    # Styles
    title_style = styles.add_style('DocTitle', WD_STYLE_TYPE.PARAGRAPH)
    title_style.font.name, title_style.font.size, title_style.font.bold = 'Arial', Pt(24), True
    title_style.font.color.rgb = RGBColor(0, 32, 96)
    title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    sub_style = styles.add_style('DocSub', WD_STYLE_TYPE.PARAGRAPH)
    sub_style.font.name, sub_style.font.size, sub_style.font.bold = 'Arial', Pt(18), True
    sub_style.font.color.rgb = RGBColor(0, 112, 192)
    sub_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Title Page
    doc.add_paragraph("jBulkEmailSender (jBES Discovery)", style='DocTitle')
    doc.add_paragraph("Phase 1 - Advanced Relay Integrations & Dynamic Operations", style='DocSub')
    p = doc.add_paragraph("Comprehensive End-to-End Developer Implementation Specification")
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    
    t0 = doc.add_table(rows=5, cols=2)
    t0.style = 'Table Grid'
    md = [
        ("Attribute", "Details"),
        ("Platform", "jBulkEmailSender - Enterprise Bulk Email Transmission Suite"),
        ("Phase", "Phase 1 - Advanced Relay Integrations"),
        ("Primary Goal", "Create a robust API-based transmission branch (SendGrid/Mailgun) and dynamic memory compression engine to bypass Port 25 throttling."),
        ("Prerequisite", "Phase 0 Foundation Setup completed: Monolithic engine, Tkinter UI, AppData mapping, and Zero-Gap Checkpoints.")
    ]
    for i, (k, v) in enumerate(md):
        t0.rows[i].cells[0].text, t0.rows[i].cells[1].text = k, v
    header_format(t0)
    
    p = doc.add_paragraph("\nImportant developer note: Phase 1 must be implemented as an extension to the Phase 0 monolith. Do not rewrite the SMTP engine; rather, build the HTTP Relay API alongside it as a parallel pipeline. This phase introduces memory-safe dynamic attachment compression and external API routing.")
    p.runs[0].bold = True

    # 1. Executive Summary
    doc.add_heading('1. Executive Summary', level=1)
    doc.add_paragraph("• Phase 1 establishes the enterprise API relay layer for jBulkEmailSender.", style='List Bullet')
    doc.add_paragraph("• This layer integrates 3rd-party APIs (SendGrid/Mailgun) allowing HTTP-based email dispatch, bypassing the 14-second outbound port-25/587 throttling common in Antivirus setups.", style='List Bullet')
    doc.add_paragraph("• Introduces Dynamic Attachment Compression to automatically ZIP attachments over a threshold (1MB), reducing DPI (Deep Packet Inspection) delays.", style='List Bullet')
    doc.add_paragraph("• Implements a Live OTP Security Dispatch Gateway inside Phase 0, enforcing true zero-trust hardware binding via self-authenticated SMTP credentials.", style='List Bullet')
    doc.add_paragraph("• Incorporates an Enterprise QA/UX Audit defining absolute dependency mappings, integration checkpoints, and UI accessibility.", style='List Bullet')

    # 2. Scope
    doc.add_heading('2. Phase 1 Scope and Boundaries', level=1)
    t2 = doc.add_table(rows=5, cols=2)
    t2.style = 'Table Grid'
    sd = [
        ("In Scope", "Out of Scope for Phase 1"),
        ("SendGrid / Mailgun HTTP REST API Integration", "Custom self-hosted proxy servers"),
        ("Dynamic ZIP compression for attachments > 1MB", "Automated CAPTCHA / OAuth2 browser solving"),
        ("Secure API Key Vault using Windows DPAPI", "Advanced cloud-based telemetry dashboards"),
        ("Accessibility Audit (Tab Sequence/Enter logic)", "Multi-node distributed clustering")
    ]
    for i, (ins, outs) in enumerate(sd):
        t2.rows[i].cells[0].text, t2.rows[i].cells[1].text = ins, outs
    header_format(t2)

    # 3. Principles
    doc.add_heading('3. Implementation Principles', level=1)
    doc.add_paragraph("• API-First Routing: Prefer HTTP POST over SMTP when an active API key is present.", style='List Bullet')
    doc.add_paragraph("• Graceful Fallback: Seamless downgrade to Phase 0 SMTP if API returns 429 Rate Limit.", style='List Bullet')
    doc.add_paragraph("• Extensible Metadata: Use JSON for API responses to easily adapt to SendGrid vs Mailgun schema differences.", style='List Bullet')
    doc.add_paragraph("• UI Thread Safety: The frontend must remain completely detached from the transmission blocking calls.", style='List Bullet')

    # 4. Modules
    doc.add_heading('4. Phase 1 Functional Modules', level=1)
    t4 = doc.add_table(rows=4, cols=3)
    t4.style = 'Table Grid'
    m_data = [
        ("Module", "Purpose", "Key Data Captured"),
        ("HTTP Relay Engine", "Dispatches payloads via 3rd-party REST endpoints", "API Key, Provider Type, HTTP Status Code"),
        ("Compression Engine", "Dynamically zips files in-memory to save Disk I/O", "Original Size, Compressed Size, Ratio"),
        ("Secrets Vault", "Locally encrypts API Keys", "Encrypted string, Provider identifier")
    ]
    for i, row in enumerate(m_data):
        t4.rows[i].cells[0].text, t4.rows[i].cells[1].text, t4.rows[i].cells[2].text = row
    header_format(t4)

    # 5. Architecture
    doc.add_heading('5. End-to-End Architecture & User Flow', level=1)
    doc.add_heading('5.1 Architecture – Phase 1', level=2)
    img_path = r"C:\Users\MAnish\.gemini\antigravity\brain\f7f21723-1591-456e-950f-3dcbde7d5779\jbes_architecture_diagram_1780407132765.png"
    if os.path.exists(img_path):
        doc.add_picture(img_path, width=Inches(6.0))
        p = doc.add_paragraph("Figure 1: Architecture with API Relay")
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.style.font.italic = True
    
    doc.add_heading('5.2 User Flow', level=2)
    doc.add_paragraph("1. Admin logs in via OTP gateway (Phase 0). Provides Admin Email and App Password for Live OTP SMTP Dispatch.")
    doc.add_paragraph("2. Admin navigates to Relay Settings and enters SendGrid Key.")
    doc.add_paragraph("3. System securely encrypts the key to AppData/config.")
    doc.add_paragraph("4. Admin loads a CSV and heavy attachments (2MB+).")
    doc.add_paragraph("5. Compression Engine zips the files automatically.")
    doc.add_paragraph("6. HTTP Relay Engine takes over, dispatching JSON payloads at 10+ msgs/sec.")

    # 6 & 7. Backend/Frontend Arch
    doc.add_heading('6. Backend Architecture for Phase 1', level=1)
    doc.add_paragraph("core/\n  api_relay_engine.py\n  zip_manager.py\n  secrets_vault.py\n  http_client.py", style='No Spacing')
    
    doc.add_heading('7. Frontend Architecture for Phase 1', level=1)
    doc.add_paragraph("components/\n  RelayConfigTab.py\n  APIKeyModal.py\n  CompressionIndicatorBadge.py", style='No Spacing')

    # 8. Core Data Model Overview
    doc.add_heading('8. Core Data Model Overview', level=1)
    t8 = doc.add_table(rows=4, cols=3)
    t8.style = 'Table Grid'
    d8 = [
        ("Entity", "Why It Exists", "Primary Relationships"),
        ("API Credential", "Authenticate with external relays", "Tied to specific sender profile/domain"),
        ("Relay Payload", "JSON representation of the email", "Consumes templates, attachments, CSV row"),
        ("Compressed Buffer", "Memory-safe zip representation", "Overrides original attachment during Relay")
    ]
    for i, row in enumerate(d8):
        t8.rows[i].cells[0].text, t8.rows[i].cells[1].text, t8.rows[i].cells[2].text = row
    header_format(t8)

    # 9. Storage Specification
    doc.add_heading('9. Local Storage & Vault Specification', level=1)
    t9 = doc.add_table(rows=4, cols=4)
    t9.style = 'Table Grid'
    d9 = [
        ("Key / File", "Type", "Constraint", "Description"),
        ("relay_keys.json", "JSON File", "Encrypted (DPAPI)", "Stores the API keys securely in AppData"),
        ("provider_id", "String", "Unique, Not Null", "e.g., 'sendgrid', 'mailgun'"),
        ("is_active", "Boolean", "Default True", "Whether to route traffic here first")
    ]
    for i, row in enumerate(d9):
        for j in range(4): t9.rows[i].cells[j].text = row[j]
    header_format(t9)

    # 10. Enumerations
    doc.add_heading('10. Enumerations and Reference Values', level=1)
    t10 = doc.add_table(rows=3, cols=2)
    t10.style = 'Table Grid'
    d10 = [
        ("Enum", "Allowed Values"),
        ("Relay Provider", "SENDGRID, MAILGUN, AMAZON_SES, CUSTOM_HTTP"),
        ("Compression Status", "UNCOMPRESSED, ZIPPED_IN_MEMORY, SKIPPED_DUE_TO_TYPE")
    ]
    for i, (k, v) in enumerate(d10):
        t10.rows[i].cells[0].text, t10.rows[i].cells[1].text = k, v
    header_format(t10)

    # 11 & 12. API Standards & Contracts
    doc.add_heading('11. Integration Standards for Phase 1', level=1)
    doc.add_paragraph("All internal function calls must return a standardized dictionary containing status, message, and data to prevent hard crashes.")
    doc.add_heading('12. Detailed API Contracts (SendGrid Example)', level=1)
    doc.add_paragraph("POST https://api.sendgrid.com/v3/mail/send\nHeaders: Authorization: Bearer <KEY>\nPayload: { \"personalizations\": [...], \"content\": [...] }")

    # 13. Backend Service Logic
    doc.add_heading('13. Backend Service Logic', level=1)
    t13 = doc.add_table(rows=4, cols=2)
    t13.style = 'Table Grid'
    d13 = [
        ("Function", "Logic"),
        ("dispatch_http_payload()", "Construct JSON. Post to Relay. Catch 429, retry, or fallback to SMTP."),
        ("compress_attachment()", "Read bytes. If > 1MB, gzip in memory. Return base64 encoded string."),
        ("store_api_key()", "Invoke DPAPI CryptProtectData. Write encrypted blob to disk.")
    ]
    for i, (k, v) in enumerate(d13):
        t13.rows[i].cells[0].text, t13.rows[i].cells[1].text = k, v
    header_format(t13)

    # 14. Validation Rules & Scenarios
    doc.add_heading('14. Validation Rules by Scenario', level=1)
    t14 = doc.add_table(rows=5, cols=2)
    t14.style = 'Table Grid'
    d14 = [
        ("Scenario / Action", "Validation Rule"),
        ("Pre-Flight Launch Verification", "Validate sender_email == security_email exactly. Reject if mismatched. Case-insensitive lookup."),
        ("Connection Interruptions", "Catch SMTP/HTTP disconnects in loop. Do NOT fail mission. Sever connection and re-initiate handshake. Max retries: 2."),
        ("Disk I/O Latency Buffer", "Use 'use_cache=True, defer_write=True'. Only flush to disk when successful sends % 50 == 0. Zero-gap writing."),
        ("Throttling Defense", "Proactively quit the server socket and rotate to the next account every 10 emails.")
    ]
    for i, (k, v) in enumerate(d14):
        t14.rows[i].cells[0].text, t14.rows[i].cells[1].text = k, v
    header_format(t14)

    # 15. Status Transition Rules
    doc.add_heading('15. Status Transition Rules', level=1)
    t15 = doc.add_table(rows=3, cols=3)
    t15.style = 'Table Grid'
    d15 = [
        ("Current Status", "Allowed Next Status", "Notes"),
        ("IDLE", "COMPRESSING, CONNECTING", "Mission started"),
        ("TRANSMITTING", "HALTED, COMPLETED", "Active dispatch loop")
    ]
    for i, row in enumerate(d15):
        for j in range(3): t15.rows[i].cells[j].text = row[j]
    header_format(t15)

    # 16. Relationship Rules
    doc.add_heading('16. Integration Relationship Rules', level=1)
    doc.add_paragraph("• Threading: `send_emails_thread` MUST spawn as `daemon=True` so UI never freezes.")
    doc.add_paragraph("• Fallback: HTTP Engine -> USES -> SMTP Engine (on failure).")

    # 17. Audit Logging
    doc.add_heading('17. Transmission Audit Logging Specification', level=1)
    doc.add_paragraph("• All atomic logs must capture [Build: X.XXs | Data: X.XXs] metrics.")
    doc.add_paragraph("• Never store API keys in plain text inside `logs/`.")

    # 18. Frontend Screens
    doc.add_heading('18. Frontend Screen Specifications', level=1)
    doc.add_paragraph("• Relay Config Tab: Contains dropdown for provider, masked entry for API Key, Save button.")

    # 19. Component Behavior & 20. Tab Sequence
    doc.add_heading('19. Frontend Component Behavior & UI Accessibility', level=1)
    doc.add_paragraph("Enterprise Audit Rule: Every form must support keyboard navigation.")
    t19 = doc.add_table(rows=4, cols=3)
    t19.style = 'Table Grid'
    d19 = [
        ("Page / Modal Scenario", "Tab Sequence (Order)", "Enter Key Binding Function"),
        ("System Access (Auth Gate)", "Email Input -> App PW -> Send OTP -> OTP Input -> Verify", "<Enter> triggers 'Verify' button."),
        ("Relay Config", "Provider -> API Key -> Save", "<Enter> inside Key field triggers Save."),
        ("Mission Setup", "CSV Path -> Load -> Subject -> Body", "<Enter> inside Subject shifts focus to Body.")
    ]
    for i, row in enumerate(d19):
        for j in range(3): t19.rows[i].cells[j].text = row[j]
    header_format(t19)

    # 21 - 25. Security, Errors, Testing
    doc.add_heading('21. Seed Data', level=1)
    doc.add_paragraph("Not applicable - Local execution environment.")
    
    doc.add_heading('22. Security and RBAC Requirements', level=1)
    doc.add_paragraph("• Hardware Binding: Phase 0 OTP enforces 1-to-1 machine-to-license restriction.")
    
    doc.add_heading('23. Error Handling Requirements', level=1)
    t23 = doc.add_table(rows=4, cols=3)
    t23.style = 'Table Grid'
    d23 = [
        ("Scenario", "Error Status", "Action"),
        ("Missing Link: File Deleted", "FileNotFoundError", "Gracefully skip attachment, log warning, continue mission."),
        ("Missing Link: Corrupted Checkpoint", "JSONDecodeError", "Drop file from recovery list, do not crash UI."),
        ("Rate Limit", "HTTP 429", "Switch to SMTP Fallback Engine.")
    ]
    for i, row in enumerate(d23):
        for j in range(3): t23.rows[i].cells[j].text = row[j]
    header_format(t23)

    doc.add_heading('24. Testing Strategy', level=1)
    doc.add_paragraph("• Unit: Test Compression Engine memory boundaries.")
    doc.add_paragraph("• Integration: Force-delete active CSV during transmission to verify graceful stop without hard crash.")

    doc.add_heading('25. Test Cases & Acceptance Criteria', level=1)
    doc.add_paragraph("TC-01: Upload 5MB PDF. Verify Compression Engine reduces it before Relay dispatch.")
    doc.add_paragraph("TC-02: Revoke API key mid-mission. Verify fallback to SMTP occurs within 1 second.")

    # 26 - 31. Execution & Handoff
    doc.add_heading('26. Development Sequence for Team Execution', level=1)
    doc.add_paragraph("1. Build Secrets Vault.")
    doc.add_paragraph("2. Implement HTTP Client.")
    doc.add_paragraph("3. Build Compression Engine.")
    doc.add_paragraph("4. Update Tkinter UI.")

    doc.add_heading('27. Recommended Developer Task Breakdown', level=1)
    doc.add_paragraph("• Backend Lead: Relay Engine & Compression")
    doc.add_paragraph("• Security Dev: Secrets Vault DPAPI")
    doc.add_paragraph("• Frontend Dev: Relay Config UI & Tab Sequences")

    doc.add_heading('28. Definition of Done', level=1)
    doc.add_paragraph("• Transmission speed > 10 emails/sec.")
    doc.add_paragraph("• Accessibility rules pass (100% keyboard navigable).")

    doc.add_heading('29. Key Risks and Mitigations', level=1)
    doc.add_paragraph("Risk: RAM exhaustion on massive zips. Mitigation: Cap max file size to 25MB before rejecting.")

    doc.add_heading('30. Handover Checklist for Phase 1 Completion', level=1)
    doc.add_paragraph("• DPAPI encryption verified on Windows 10/11.")
    doc.add_paragraph("• SMTP fallback verified.")
    doc.add_paragraph("• BuildExecutable.bat generates updated zero-footprint MSI.")

    doc.add_heading('31. Phase 1 Final Outcome', level=1)
    doc.add_paragraph("At the end of Phase 1, jBulkEmailSender transforms from a traditional SMTP client into a hybrid, highly evasive transmission engine capable of routing around port throttling using modern HTTP APIs and dynamic payload compression.")

    # --- NEW: Phase 2 SaaS Web Migration & Deep Dive Due Diligence ---
    doc.add_heading('Phase 2: Deep Dive Due Diligence & Multi-Agent Migration Blueprint', level=1)
    doc.add_paragraph("Based on the requirement for modern, flexible UI features, Phase 2 will execute the migration of jBulkEmailSender from a local Tkinter monolith to a Cloud-Native Web Application.")
    
    doc.add_heading('1. Tech Stack', level=2)
    doc.add_paragraph("• Frontend: Next.js (React) + TailwindCSS + Shadcn/UI for a highly responsive, modern, premium interface.")
    doc.add_paragraph("• Backend: FastAPI (Python) wrapping the existing monolithic engine (`bulk_email_sender.py` core logic) to expose RESTful APIs.")
    doc.add_paragraph("• Database: PostgreSQL (RBAC, User Auth, Mission Metadata) and Redis (Live WebSocket state).")
    doc.add_paragraph("• Cloud Storage: AWS S3 (Handling CSV uploads and attachments to bypass local file-system restrictions in web apps).")

    doc.add_heading('2. Deep Dive Technical Specifications', level=2)
    doc.add_paragraph("A direct decoupled approach will cause missing link failures because web servers cannot read local C:\\ drives. The architecture must map local file I/O to Cloud I/O.")
    
    t_tech = doc.add_table(rows=5, cols=3)
    t_tech.style = 'Table Grid'
    d_tech = [
        ("Sub-System", "Phase 1 (Legacy)", "Phase 2 (Cloud SaaS)"),
        ("Auth Gateway", "Local config.json OTP", "AWS Cognito / JWT via PostgreSQL"),
        ("File Handling", "os.path.exists (Local Drive)", "AWS S3 Boto3 Pre-Signed URLs"),
        ("Live Logging", "Tkinter Threading Textbox", "Socket.io (WebSocket) streaming"),
        ("Memory Cache", "Python in-memory dict", "Redis ephemeral cache")
    ]
    for i, row in enumerate(d_tech):
        for j in range(3): t_tech.rows[i].cells[j].text = row[j]
    header_format(t_tech)

    doc.add_heading('2.1 Operations Mode Selector (Online vs Local)', level=3)
    doc.add_paragraph("On the first-boot authentication gate, after entering the 6-Digit Passcode, the user is presented with an Operations Mode Dialog Box containing two radio buttons:")
    doc.add_paragraph("• 🌐 Online Mode: Scaffolds directories under the user's home path (`~/jBulkEmail/data` and `~/jBulkEmail/webservice`) to store metadata and configurations locally. The application core executes dynamically synced directly from the cloud repository path: https://github.com/jDroid-X/jBulkEmail.")
    doc.add_paragraph("• 💻 Local System Mode: Automatically initiates a local dependency installation process by downloading the full jBulkEmail package from GitHub, unpacking files to `~/jBulkEmail`, and configuring all dependent modules for local standalone execution.")
    
    doc.add_heading('3. Multi-Agent AI Prompts (ROCAS Format)', level=2)
    doc.add_paragraph("To ensure flawless execution, this migration must be handed over to a swarm of specialized AI Agents using the following ROCAS prompts:")
    
    # Frontend Agent
    doc.add_heading('Agent 1: Frontend UI/UX Architect', level=3)
    doc.add_paragraph("R: Elite Next.js/React Designer.\nO: Decouple Tkinter UI into a premium React dashboard using TailwindCSS.\nC: Read existing Python UI logic and map it to REST components. Must support glassmorphism and WebSocket log rendering.\nA: A clean /frontend Next.js repository.\nS: Premium, modern, accessible.")
    
    # Backend Agent
    doc.add_heading('Agent 2: FastAPI Integration Engineer', level=3)
    doc.add_paragraph("R: Senior Python Backend Developer.\nO: Wrap bulk_email_sender.py in FastAPI without breaking the existing APIRelayEngine or ZipManager.\nC: Convert local Tkinter inputs into JSON payload receivers.\nA: A highly scalable /backend API repository.\nS: Secure, resilient, robust.")

    # Database Agent
    doc.add_heading('Agent 3: PostgreSQL & Cloud DB Administrator', level=3)
    doc.add_paragraph("R: Cloud Database Architect.\nO: Migrate config.json and local CSV readers to PostgreSQL and AWS S3.\nC: Web apps lose state; DB must track mission progress persistently.\nA: Prisma/SQLAlchemy schemas and S3 Boto3 adapters.\nS: Zero-data-loss, ACID compliant.")

    # QA Agent
    doc.add_heading('Agent 4: Due Diligence Integration Auditor', level=3)
    doc.add_paragraph("R: Enterprise QA Automation Lead.\nO: Identify missing links, broken dependencies, and integration gaps between React and FastAPI.\nC: Audit cross-device responsive layout and socket disconnections.\nA: A final QA report mapping dependencies.\nS: Strict, audit-focused, zero-tolerance for bugs.")

    # Save to the new web service folder
    out_dir = r"C:\Users\dell\jAnitGravity\jBulkEmailSender\jBulkEmailWebService"
    os.makedirs(out_dir, exist_ok=True)
    
    output_path = os.path.join(out_dir, 'jBES_WebService_TechSpec_SOW.docx')
    doc.save(output_path)
    print(f"Technical Specification SOW saved to {output_path}")

create_full_dev_sow()
