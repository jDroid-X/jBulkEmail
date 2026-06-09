# Application Architecture

## Active Components
The following files are the core components of the Bulk Email Sender application:

1.  **bulk_email_sender.py** (Main Application)
    *   **Role**: Entry point, GUI Controller, Email Logic.
    *   **Responsibilities**:
        *   Initializes the main window and UI layout.
        *   Manages user input (recipients, subject, templates).
        *   Handles the email sending process (SMTP connection, batching).
        *   Integrates the `RichTextEditor` component.
        *   Loads and saves configuration.

2.  **RichContentManager.py** (Helper Module)
    *   **Role**: Rich Text Editor Logic & formatting.
    *   **Responsibilities**:
        *   `RichTextEditor`: The class controlling the text widget, toolbar, and shortcuts.
        *   `RichContentManager`: Logic for clipboard handling (images, HTML paste).
        *   `LinkPreviewFetcher`: Utility for fetching link metadata.

## Archived Components
Redundant files have been moved to the `archive/` folder:
*   `google_Authenticate.py`: Obsolete authentication script.
*   `web/`: Legacy HTML rendering folder (replaced by native Tkinter text).
*   `sample_recipents.csv`: Duplicate file (typo).

## Execution Flow
1.  User runs `bulk_email_sender.py`.
2.  `setup_ui()` initializes the main window and grid layout.
3.  `RichTextEditor` is instantiated and its toolbar is placed at the top of the email body frame.
4.  User interacts with the UI (compose email, formatting).
5.  `send_emails_thread()` handles the sending process in a background thread.
