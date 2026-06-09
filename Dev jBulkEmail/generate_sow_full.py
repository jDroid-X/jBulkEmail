import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

def add_shading_to_table_cell(cell, fill_color):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), fill_color)
    shading.set(qn('w:val'), 'clear')
    tcPr.append(shading)

def create_full_sow_document():
    doc = docx.Document()
    styles = doc.styles
    
    title_style = styles.add_style('DocumentTitle', WD_STYLE_TYPE.PARAGRAPH)
    title_style.font.name = 'Arial'
    title_style.font.size = Pt(24)
    title_style.font.bold = True
    title_style.font.color.rgb = RGBColor(0, 32, 96) 
    title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle_style = styles.add_style('DocumentSubtitle', WD_STYLE_TYPE.PARAGRAPH)
    subtitle_style.font.name = 'Arial'
    subtitle_style.font.size = Pt(18)
    subtitle_style.font.bold = True
    subtitle_style.font.color.rgb = RGBColor(0, 112, 192)
    subtitle_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    tagline_style = styles.add_style('Tagline', WD_STYLE_TYPE.PARAGRAPH)
    tagline_style.font.name = 'Arial'
    tagline_style.font.size = Pt(12)
    tagline_style.font.color.rgb = RGBColor(89, 89, 89)
    tagline_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Title Section
    doc.add_paragraph("jBulkEmailSender (jBES Discovery)", style='DocumentTitle')
    doc.add_paragraph("Phase 0: Enterprise Stabilization & Optimization", style='DocumentSubtitle')
    doc.add_paragraph("Detailed End-to-End Implementation Specification & Developer Guide", style='Tagline')
    doc.add_paragraph()
    
    # Purpose Box
    p = doc.add_paragraph()
    p.style.font.name = 'Arial'
    p.style.font.size = Pt(10)
    run = p.add_run("Purpose: Establish the secure, scalable, standardized foundation on which the jBulkEmailSender (jBES Discovery) operates. Phase 0 must be completed before introducing third-party SMTP relays, dynamic attachments compression, and advanced telemetry analytics.")
    run.bold = True
    p.paragraph_format.left_indent = Inches(0.2)
    p.paragraph_format.right_indent = Inches(0.2)
    doc.add_paragraph("-" * 90)
    doc.add_paragraph()
    
    # Document Metadata Table
    table = doc.add_table(rows=6, cols=2)
    table.style = 'Table Grid'
    metadata = [
        ("Document Item", "Details"),
        ("Product", "jBulkEmailSender - Enterprise-grade, portable bulk email transmission suite"),
        ("Phase", "Phase 0 - Enterprise Stabilization & Optimization"),
        ("Audience", "Product Owner, Technical Architect, Core Developers"),
        ("Primary Outcome", "A working monolithic platform with proactive account rotation, sticky persistent SMTP connections, binary MIME slicing, and high-fidelity logging."),
        ("Next Phase Enabled", "Phase 1 - Advanced Relay Integrations")
    ]
    for i, (item, detail) in enumerate(metadata):
        row = table.rows[i].cells
        row[0].text = item
        row[1].text = detail
        if i == 0:
            for cell in row:
                add_shading_to_table_cell(cell, "002060") 
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
    doc.add_paragraph()
    
    # 1. Executive Summary
    doc.add_heading('1. Executive Summary', level=1)
    doc.add_paragraph("Phase 0 focuses on the stabilization, optimization, and architectural monolithic compliance of jBulkEmailSender. The goal is to prepare a secure, highly portable, zero-footprint baseline capable of bypassing standard provider throttling without rework.")
    doc.add_paragraph("• Consolidate legacy MVC architecture into a stable, single-file monolith (bulk_email_sender.py).", style='List Bullet')
    doc.add_paragraph("• Implement TCP socket tuning (1MB buffers) for high-speed transmission.", style='List Bullet')
    doc.add_paragraph("• Define a sticky connection strategy with 10-email proactive rotation.", style='List Bullet')
    doc.add_paragraph("• Create high-fidelity atomic logs (Build vs. Data latency).", style='List Bullet')
    doc.add_paragraph("• Ensure data compliance by migrating write operations to Windows %AppData%.", style='List Bullet')
    doc.add_paragraph("• Establish strict First-Time System Authentication, OTP Verification, and Run-Mode checks (Online vs Local).", style='List Bullet')
    
    # 2. Phase 0 Scope
    doc.add_heading('2. Phase 0 Scope', level=1)
    scope_table = doc.add_table(rows=7, cols=2)
    scope_table.style = 'Table Grid'
    scope_data = [
        ("In Scope", "Out of Scope"),
        ("Monolithic architecture and zero-footprint MSI portability", "Web-based dashboards"),
        ("Environment setup: AppData dynamic migration", "Advanced AI/LLM integration"),
        ("TCP Socket Tuning (SO_SNDBUF) and Sticky Sessions", "Third-party bulk email APIs (SendGrid)"),
        ("System Authentication (First-time OTP, Confirmations, Mode Checks)", "Enterprise SSO identity management"),
        ("Binary MIME slice pre-encoding for attachments", "Dynamic real-time attachment compression"),
        ("Sub-second forensic logging and checkpointing", "Enterprise network proxy automatic bypass")
    ]
    for i, (ins, outs) in enumerate(scope_data):
        row = scope_table.rows[i].cells
        row[0].text = ins
        row[1].text = outs
        if i == 0:
            for cell in row:
                add_shading_to_table_cell(cell, "002060")
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
    
    # 3. Phase 0 Implementation Workstreams
    doc.add_heading('3. Phase 0 Implementation Workstreams', level=1)
    work_table = doc.add_table(rows=6, cols=5)
    work_table.style = 'Table Grid'
    work_headers = ["Step", "Workstream", "Objective", "Primary Owner", "Dependency"]
    work_data = [
        ("0.1", "Architecture Consolidation", "Merge MVC to Monolith for portability", "Tech Lead", "None"),
        ("0.2", "Data Portability", "Migrate Config/Logs to %AppData%", "Backend Developer", "0.1"),
        ("0.3", "Transmission Engine", "Implement sticky sessions & socket tuning", "Architect", "0.1"),
        ("0.4", "Payload Processing", "Binary MIME pre-encoding for speed", "Backend Developer", "0.3"),
        ("0.5", "Closed-Loop Access Control", "Implement OTP Login, Confirmations & Mode checks", "Security Arch", "0.1")
    ]
    for j, header in enumerate(work_headers):
        work_table.rows[0].cells[j].text = header
        add_shading_to_table_cell(work_table.rows[0].cells[j], "002060")
        for paragraph in work_table.rows[0].cells[j].paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
    for i, row_data in enumerate(work_data):
        for j, val in enumerate(row_data):
            work_table.rows[i+1].cells[j].text = val

    # 4. Target Architecture for Phase 0
    doc.add_heading('4. Target Architecture for Phase 0', level=1)
    doc.add_paragraph("Phase 0 establishes a clean monolithic structure allowing portable Windows deployment without external dependencies. The architecture integrates a closed-loop feedback mechanism to monitor delivery failures and dynamically update targeting parameters.")
    
    # Insert Picture
    img_path = r"C:\Users\MAnish\.gemini\antigravity\brain\f7f21723-1591-456e-950f-3dcbde7d5779\jbes_architecture_diagram_1780407132765.png"
    if os.path.exists(img_path):
        doc.add_picture(img_path, width=Inches(6.0))
        p = doc.add_paragraph("Figure 1: jBulkEmailSender Software Architecture")
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.style.font.italic = True
    else:
        doc.add_paragraph("[Architecture Diagram Image Not Found]")

    arch_table = doc.add_table(rows=6, cols=3)
    arch_table.style = 'Table Grid'
    arch_headers = ["Layer", "Responsibility", "Phase 0 Deliverable"]
    arch_data = [
        ("Frontend Layer", "User interface, mission dashboard, OTP Login Screen", "Tkinter with tkinterweb for HTML editing, 3D HUD"),
        ("Orchestrator Layer", "Transmission logic, SMTP connections, thread management", "bulk_email_sender.py monolith"),
        ("Storage Layer", "Templates, Config, Mission logs, Checkpoints", "Local %AppData% JSON/CSV mapping"),
        ("Security Layer", "OTP verification, App password management", "smtplib with integrated retry & auth hooks"),
        ("Observability Layer", "Logging, forensic tracking of Build/Data latency", "send_logs.txt with atomic writes, Closed-loop reporting")
    ]
    for j, header in enumerate(arch_headers):
        arch_table.rows[0].cells[j].text = header
        add_shading_to_table_cell(arch_table.rows[0].cells[j], "002060")
        for paragraph in arch_table.rows[0].cells[j].paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
    for i, row_data in enumerate(arch_data):
        for j, val in enumerate(row_data):
            arch_table.rows[i+1].cells[j].text = val

    # 5. Recommended Technology Baseline
    doc.add_heading('5. Recommended Technology Baseline', level=1)
    tech_table = doc.add_table(rows=5, cols=3)
    tech_table.style = 'Table Grid'
    tech_headers = ["Area", "Recommended Choice", "Notes"]
    tech_data = [
        ("Frontend", "Tkinter + ttk + tkinterweb", "Native Windows UI, zero footprint requirements"),
        ("Backend", "Python 3.x", "Highly optimized for script-to-exe portability"),
        ("Email Engine", "smtplib + email.mime", "Standard library, modified for SO_SNDBUF tuning"),
        ("Deployment", "PyInstaller + VBScript", "Generates single-click portable MSI/Zip")
    ]
    for j, header in enumerate(tech_headers):
        tech_table.rows[0].cells[j].text = header
        add_shading_to_table_cell(tech_table.rows[0].cells[j], "002060")
        for paragraph in tech_table.rows[0].cells[j].paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
    for i, row_data in enumerate(tech_data):
        for j, val in enumerate(row_data):
            tech_table.rows[i+1].cells[j].text = val

    # 6. Step 0.1 - Project Structure
    doc.add_heading('6. Step 0.1 - Project Structure', level=1)
    doc.add_paragraph("Objective: Create a clean portable repository structure for developers to build the MSI.")
    code = """jBulkEmailSender/
├── PACKAGE_READY_TO_ZIP/
├── app/                  (Deprecated MVC)
├── assets/               (UI Icons, Branding)
├── build/
├── config/               (User preferences)
├── core/
│   ├── RichContentManager.py
│   ├── diag.py
│   ├── email_check.py
├── exports/
├── logs/
├── bulk_email_sender.py  (Master Orchestrator)
├── main.py               (Wrapper)
├── BuildExecutable.bat
└── Deploy_Mission_Control.vbs"""
    p = doc.add_paragraph(code)
    p.style.font.name = 'Consolas'
    p.style.font.size = Pt(9)

    # 7. Step 0.2 - Authentication & Transmission Foundation
    doc.add_heading('7. Step 0.2 - Authentication & System Access', level=1)
    doc.add_paragraph("Objective: Establish secure login protocols for system access, terms acceptance, run-mode verification, and backend SMTP transmission.")
    
    doc.add_heading('7.1 System Access Control (OTP & Run Mode)', level=2)
    doc.add_paragraph("Before launching the Mission Control dashboard, the user must clear the Security Gateway:")
    doc.add_paragraph("• First-Time Login & OTP Verification: Upon first execution, the system prompts for a registered email. A one-time verification code (OTP) is dispatched and must be entered to bind the hardware to the user.", style='List Bullet')
    doc.add_paragraph("• Terms & Usage Confirmations: The user must explicitly accept a digital EULA/Confirmation dialog allowing the application to execute transmission on their behalf.", style='List Bullet')
    doc.add_paragraph("• Run Mode Validation: The orchestrator performs a connectivity check to determine if it should operate in 'Online Run Mode' (telemetry and license ping active) or fallback/restrict to 'Local Run Mode' (offline testing bounds).", style='List Bullet')

    doc.add_heading('7.2 Connection Roles (SMTP Account Types)', level=2)
    roles_table = doc.add_table(rows=3, cols=3)
    roles_table.style = 'Table Grid'
    for j, h in enumerate(["Role", "Purpose", "Typical Access"]):
        roles_table.rows[0].cells[j].text = h
        add_shading_to_table_cell(roles_table.rows[0].cells[j], "002060")
    roles_data = [
        ("Primary_Sender", "Main communication anchor", "Full SMTP rights, highest volume limit"),
        ("Rotation_Node", "Avoids provider tarpitting", "Rotates every 10 emails")
    ]
    for i, d in enumerate(roles_data):
        for j, val in enumerate(d):
            roles_table.rows[i+1].cells[j].text = val

    doc.add_heading('7.3 Required Core Functions', level=2)
    funcs_table = doc.add_table(rows=5, cols=2)
    funcs_table.style = 'Table Grid'
    for j, h in enumerate(["Function", "Purpose"]):
        funcs_table.rows[0].cells[j].text = h
        add_shading_to_table_cell(funcs_table.rows[0].cells[j], "002060")
    funcs_data = [
        ("verify_system_access", "Triggers OTP dispatch and validates user credentials/terms"),
        ("check_run_mode", "Pings gateway to lock interface to Local or Online operation"),
        ("smtp_connect", "Creates sticky TLS session with 30s timeout and 1MB buffer tuning"),
        ("smtp_send_with_retry", "Auto-reconnects on dropped connections before failure"),
    ]
    for i, d in enumerate(funcs_data):
        for j, val in enumerate(d):
            funcs_table.rows[i+1].cells[j].text = val

    # 8. Step 0.3 - Common Transmission Data Model
    doc.add_heading('8. Step 0.3 - Common Transmission Data Model', level=1)
    doc.add_paragraph("Objective: Define the shared domain objects that jBES will use for tracking progress.")
    model_table = doc.add_table(rows=5, cols=3)
    model_table.style = 'Table Grid'
    for j, h in enumerate(["Core Object", "Definition", "Why It Matters"]):
        model_table.rows[0].cells[j].text = h
        add_shading_to_table_cell(model_table.rows[0].cells[j], "002060")
    model_data = [
        ("Email Target", "Destination payload with mapped variables", "Base object for mail construction"),
        ("Checkpoint", "Saved state of an interrupted mission", "Required for zero-loss recovery"),
        ("MIME Slice", "Pre-encoded binary attachment data", "Speeds up build latency to <0.01s"),
        ("Feedback Event", "Closed-loop failure notification (e.g., hard bounce)", "Prevents retry loops on dead accounts")
    ]
    for i, d in enumerate(model_data):
        for j, val in enumerate(d):
            model_table.rows[i+1].cells[j].text = val

    # 9. Step 0.4 - Storage Setup
    doc.add_heading('9. Step 0.4 - Storage Setup', level=1)
    doc.add_paragraph("Objective: Create the base file structure and logic for persisting configuration and progress.")
    doc.add_paragraph("• Config storage: AppData/jBES_Discovery/config/", style='List Bullet')
    doc.add_paragraph("• Zero-Gap CSV: Writes flushed to disk every 50 emails.", style='List Bullet')

    # 10. Step 0.5 - Code Standards & Closed-Loop Design
    doc.add_heading('10. Step 0.5 - Code Standards & Closed-Loop Design', level=1)
    doc.add_paragraph("Objective: Ensure uniform error handling, retry mechanisms, and feedback loops.")
    doc.add_paragraph("• Standard Exception Handling for smtplib errors.", style='List Bullet')
    doc.add_paragraph("• Closed-Loop Feedback: Any hard failures (e.g. SMTPRecipientRefused) instantly update the GUI and are permanently logged in the 'exports/failed/' directory to purge dead leads from future CSV lists, creating a self-cleaning data ecosystem.", style='List Bullet')
    doc.add_paragraph("• GUI thread separation from SMTP engine.", style='List Bullet')

    # 11. Step 0.6 - Logging, Monitoring and Audit Foundation
    doc.add_heading('11. Step 0.6 - Logging, Monitoring and Audit Foundation', level=1)
    doc.add_paragraph("Objective: Capture traceability from day one with micro-second accuracy.")
    log_table = doc.add_table(rows=4, cols=2)
    log_table.style = 'Table Grid'
    for j, h in enumerate(["Capability", "Requirement"]):
        log_table.rows[0].cells[j].text = h
        add_shading_to_table_cell(log_table.rows[0].cells[j], "002060")
    log_data = [
        ("Build Metric", "Track precise seconds taken to construct MIME object"),
        ("Data Metric", "Track precise seconds taken by network/AV to upload"),
        ("Access Audit", "Log OTP verification success/failure and runtime mode")
    ]
    for i, d in enumerate(log_data):
        for j, val in enumerate(d):
            log_table.rows[i+1].cells[j].text = val

    # 12. Frontend Foundation Requirements
    doc.add_heading('12. Frontend Foundation Requirements', level=1)
    doc.add_paragraph("• System Access Gate: Initial Tkinter popup requiring Email entry and OTP validation.", style='List Bullet')
    doc.add_paragraph("• EULA Dialog: Confirmation screen explicitly requiring user agreement before unlocking transmission tools.", style='List Bullet')
    doc.add_paragraph("• Mode Indicator: HUD element displaying 'ONLINE' or 'LOCAL' run status.", style='List Bullet')
    doc.add_paragraph("• GUI Built on Tkinter with L7 Enterprise aesthetics.", style='List Bullet')

    # 13. Backend Foundation Requirements
    doc.add_heading('13. Backend Foundation Requirements', level=1)
    doc.add_paragraph("• Authentication API integration to dispatch and verify OTP codes.", style='List Bullet')
    doc.add_paragraph("• Threading implementation preventing UI freezes during OTP validation or SMTP sends.", style='List Bullet')
    doc.add_paragraph("• Monolithic architecture in bulk_email_sender.py.", style='List Bullet')

    # 14. Developer Execution Plan
    doc.add_heading('14. Developer Execution Plan', level=1)
    plan_table = doc.add_table(rows=5, cols=3)
    plan_table.style = 'Table Grid'
    for j, h in enumerate(["Day", "Focus", "Expected Output"]):
        plan_table.rows[0].cells[j].text = h
        add_shading_to_table_cell(plan_table.rows[0].cells[j], "002060")
    plan_data = [
        ("Day 1", "Codebase consolidation & Access Gateway", "Monolith runs with OTP Login overlay"),
        ("Day 2", "Run Mode & Confirmations", "Local vs Online checks active; EULA confirmation enforced"),
        ("Day 3", "Sticky Connections & Socket Tuning", "Send latency isolated to network restrictions"),
        ("Day 4", "MIME Slicing & Closed-Loop Feedback", "Sub-second builds; failed emails automatically flagged")
    ]
    for i, d in enumerate(plan_data):
        for j, val in enumerate(d):
            plan_table.rows[i+1].cells[j].text = val

    # 15. Testing Strategy
    doc.add_heading('15. Testing Strategy', level=1)
    doc.add_paragraph("• Verify OTP dispatch triggers accurately upon first launch.", style='List Bullet')
    doc.add_paragraph("• Disconnect network adapter to validate graceful fallback to 'Local Mode'.", style='List Bullet')
    doc.add_paragraph("• Verify 'Data:' metric correlates to attachment size in isolated networks.", style='List Bullet')
    doc.add_paragraph("• Validate 50-email boundary CSV flushes and closed-loop failure logging.", style='List Bullet')

    # 16. Definition of Done for Phase 0
    doc.add_heading('16. Definition of Done for Phase 0', level=1)
    doc.add_paragraph("• User must successfully pass OTP/Terms check to access the main orchestrator.", style='List Bullet')
    doc.add_paragraph("• BuildExecutable.bat generates a flawless zero-footprint MSI.", style='List Bullet')
    doc.add_paragraph("• Application adapts UI based on Online vs Local checks.", style='List Bullet')

    # 17. Risks and Mitigation
    doc.add_heading('17. Risks and Mitigation', level=1)
    risk_table = doc.add_table(rows=4, cols=3)
    risk_table.style = 'Table Grid'
    for j, h in enumerate(["Risk", "Impact", "Mitigation"]):
        risk_table.rows[0].cells[j].text = h
        add_shading_to_table_cell(risk_table.rows[0].cells[j], "002060")
    risk_data = [
        ("Authentication API Downtime", "Users cannot bypass OTP gateway", "Implement secure offline fallback/cache for previously authenticated machines"),
        ("Antivirus Deep Scan", "Throttles SMTP throughput regardless of code speed", "Provide UI instruction to whitelist pythonw.exe"),
        ("Gmail Tarpitting", "Hard-halts rapid email bursts", "Implement 10-email rotation strategy")
    ]
    for i, d in enumerate(risk_data):
        for j, val in enumerate(d):
            risk_table.rows[i+1].cells[j].text = val

    # 18. Handover Checklist
    doc.add_heading('18. Handover Checklist to Start Phase 1', level=1)
    doc.add_paragraph("• Does the OTP and run-mode gateway block unauthorized access effectively?", style='List Bullet')
    doc.add_paragraph("• Does rotation bypass initial throttling?", style='List Bullet')
    doc.add_paragraph("• Do closed-loop failure mechanisms accurately filter bad recipients?", style='List Bullet')

    # 19. Phase 1 Readiness Output
    doc.add_heading('19. Phase 1 Readiness Output', level=1)
    doc.add_paragraph("At the end of Phase 0, the core engine is fully optimized and securely gated. The next phase will leverage this robust foundation to introduce dynamic attachment compression and 3rd-party SMTP relay providers (e.g. SendGrid) to completely bypass environmental limitations.")

    doc.save('jBES_Discovery_SOW_Foundation.docx')

create_full_sow_document()
