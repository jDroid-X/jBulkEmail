import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_shading_to_table_cell(cell, fill_color):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), fill_color)
    shading.set(qn('w:val'), 'clear')
    tcPr.append(shading)

def create_sow_document():
    doc = docx.Document()
    
    # Define styles
    styles = doc.styles
    
    title_style = styles.add_style('DocumentTitle', WD_STYLE_TYPE.PARAGRAPH)
    title_style.font.name = 'Arial'
    title_style.font.size = Pt(24)
    title_style.font.bold = True
    title_style.font.color.rgb = RGBColor(0, 32, 96) # Dark Blue
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
    
    heading1_style = styles['Heading 1']
    heading1_style.font.name = 'Arial'
    heading1_style.font.size = Pt(16)
    heading1_style.font.bold = True
    heading1_style.font.color.rgb = RGBColor(0, 32, 96)
    
    heading2_style = styles['Heading 2']
    heading2_style.font.name = 'Arial'
    heading2_style.font.size = Pt(14)
    heading2_style.font.bold = True
    heading2_style.font.color.rgb = RGBColor(0, 32, 96)
    
    # Title Section
    doc.add_paragraph("jBulkEmailSender (jBES Discovery)", style='DocumentTitle')
    doc.add_paragraph("Phase 6: Enterprise Stabilization & Optimization", style='DocumentSubtitle')
    doc.add_paragraph("Detailed End-to-End Implementation Specification & Developer Guide", style='Tagline')
    doc.add_paragraph()
    
    # Purpose Box
    p = doc.add_paragraph()
    p.style.font.name = 'Arial'
    p.style.font.size = Pt(10)
    run = p.add_run("Purpose: Establish the secure, scalable, standardized foundation on which the jBulkEmailSender (jBES Discovery) operates. Phase 6 must be completed before introducing third-party SMTP relays, dynamic attachments compression, and advanced telemetry analytics.")
    run.bold = True
    p.paragraph_format.left_indent = Inches(0.2)
    p.paragraph_format.right_indent = Inches(0.2)
    # Simple border representation using dashes since box drawing is complex in python-docx
    doc.add_paragraph("-" * 90)
    doc.add_paragraph()
    
    # Document Metadata Table
    table = doc.add_table(rows=6, cols=2)
    table.style = 'Table Grid'
    
    metadata = [
        ("Document Item", "Details"),
        ("Product", "jBulkEmailSender - Enterprise-grade, portable bulk email transmission suite"),
        ("Phase", "Phase 6 - Enterprise Stabilization & Optimization"),
        ("Audience", "Product Owner, Technical Architect, Core Developers"),
        ("Primary Outcome", "A working monolithic platform with proactive account rotation, sticky persistent SMTP connections, binary MIME slicing, and high-fidelity logging."),
        ("Next Phase Enabled", "Phase 7 - Advanced Relay Integrations")
    ]
    
    for i, (item, detail) in enumerate(metadata):
        row = table.rows[i].cells
        row[0].text = item
        row[1].text = detail
        if i == 0:
            for cell in row:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                add_shading_to_table_cell(cell, "002060") # Dark Blue Background
    doc.add_paragraph()
    
    # 1. Executive Summary
    doc.add_heading('1. Executive Summary', level=1)
    doc.add_paragraph("Phase 6 focuses on the stabilization, optimization, and architectural monolithic compliance of jBulkEmailSender. The goal is to prepare a secure, highly portable, zero-footprint baseline capable of bypassing standard provider throttling.")
    doc.add_paragraph("• Consolidate legacy MVC architecture into a stable, single-file monolith (bulk_email_sender.py).", style='List Bullet')
    doc.add_paragraph("• Implement TCP socket tuning (1MB buffers) for high-speed transmission.", style='List Bullet')
    doc.add_paragraph("• Define a sticky connection strategy with 10-email proactive rotation.", style='List Bullet')
    doc.add_paragraph("• Create high-fidelity atomic logs (Build vs. Data latency).", style='List Bullet')
    doc.add_paragraph("• Ensure data compliance by migrating write operations to Windows %AppData%.", style='List Bullet')
    doc.add_paragraph()
    
    # 2. Phase 6 Scope
    doc.add_heading('2. Phase 6 Scope', level=1)
    scope_table = doc.add_table(rows=6, cols=2)
    scope_table.style = 'Table Grid'
    scope_data = [
        ("In Scope", "Out of Scope"),
        ("Monolithic architecture and zero-footprint MSI portability", "Web-based dashboards"),
        ("Environment setup: AppData dynamic migration", "Advanced AI/LLM integration"),
        ("TCP Socket Tuning (SO_SNDBUF) and Sticky Sessions", "Third-party bulk email APIs (SendGrid)"),
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
    doc.add_paragraph()
    
    # 3. Phase 6 Implementation Workstreams
    doc.add_heading('3. Phase 6 Implementation Workstreams', level=1)
    work_table = doc.add_table(rows=5, cols=5)
    work_table.style = 'Table Grid'
    work_headers = ["Step", "Workstream", "Objective", "Primary Owner", "Dependency"]
    work_data = [
        ("6.1", "Architecture Consolidation", "Merge MVC to Monolith for portability", "Tech Lead", "None"),
        ("6.2", "Data Portability", "Migrate Config/Logs to %AppData%", "Backend Developer", "6.1"),
        ("6.3", "Transmission Engine", "Implement sticky sessions & socket tuning", "Architect", "6.1"),
        ("6.4", "Payload Processing", "Binary MIME pre-encoding for speed", "Backend Developer", "6.3")
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
    doc.add_paragraph()
    
    # 4. Target Architecture for Phase 6
    doc.add_heading('4. Target Architecture for Phase 6', level=1)
    doc.add_paragraph("Phase 6 establishes a clean monolithic structure allowing portable Windows deployment without external dependencies. The table below represents the architectural mapping replacing the conceptual diagram from the foundation specification.")
    
    arch_table = doc.add_table(rows=6, cols=3)
    arch_table.style = 'Table Grid'
    arch_headers = ["Layer", "Responsibility", "Phase 6 Deliverable"]
    arch_data = [
        ("Frontend Layer", "User interface, mission dashboard, L7 Enterprise aesthetics", "Tkinter with tkinterweb for HTML editing, 3D HUD"),
        ("Orchestrator Layer", "Transmission logic, SMTP connections, thread management", "bulk_email_sender.py monolith"),
        ("Storage Layer", "Templates, Config, Mission logs, Checkpoints", "Local %AppData% JSON/CSV mapping"),
        ("Security Layer", "App password management, TLS/SSL handshake", "smtplib with integrated retry hooks"),
        ("Observability Layer", "Logging, forensic tracking of Build/Data latency", "send_logs.txt with atomic writes")
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
    doc.add_paragraph()

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
    doc.add_paragraph()

    # 6. Step 6.1 - Project Structure
    doc.add_heading('6. Step 6.1 - Project Structure', level=1)
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
    doc.add_paragraph()

    # 7. Step 6.2 - Delivery & Verification
    doc.add_heading('7. Step 6.2 - Delivery & Verification', level=1)
    doc.add_heading('7.1 Deliverables', level=2)
    doc.add_paragraph("• Repository structured as a portable monolith.", style='List Bullet')
    doc.add_paragraph("• Transmission engine optimized to <0.01s build latency.", style='List Bullet')
    doc.add_paragraph("• TCP Socket tuning enabled for 1MB buffers.", style='List Bullet')
    doc.add_paragraph("• Checkpointing and mission recovery active.", style='List Bullet')
    
    doc.add_heading('7.2 Acceptance Criteria', level=2)
    doc.add_paragraph("• Developer can build executable via BuildExecutable.bat.", style='List Bullet')
    doc.add_paragraph("• Application starts without Python installed on target machine.", style='List Bullet')
    doc.add_paragraph("• Network transmission reflects true environmental limits (e.g., 14s AV scan) rather than code bottlenecks.", style='List Bullet')
    
    doc.save('Enterprise_SOW_jBES_Discovery.docx')

create_sow_document()
