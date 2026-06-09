
import csv
import re
import os

class EmailChecker:
    COMMON_DOMAINS = {
        'gmail.com': ['gamil.com', 'gmal.com', 'gmial.com', 'gimail.com', 'gmai.com', 'gmaill.com', 'gmail.co', 'gmil.com'],
        'yahoo.com': ['yaho.com', 'yahooo.com', 'yhoo.com', 'yahoo.co'],
        'outlook.com': ['outlok.com', 'outlook.co', 'outloo.com'],
        'hotmail.com': ['hotmal.com', 'hotmai.com', 'homail.com', 'otmail.com']
    }

    @staticmethod
    def correct_email(email):
        """
        Validates and corrects email address.
        Returns: (corrected_email, is_modified, is_valid)
        """
        if not email:
            return "", False, False
        
        original = email
        email = email.lower().strip()
        
        # 1. SPECIAL CASE: Missing @ but has space (e.g. "user gmail.com")
        if "@" not in email and " " in email:
            # Assume the last space was meant to be an @
            # e.g. "john doe gmail.com" -> "johndoe@gmail.com"
            parts = email.rsplit(" ", 1)
            if len(parts) == 2:
                # We'll join with @, then later strip remaining spaces
                email = f"{parts[0]}@{parts[1]}"
        
        # 2. Remove all spaces
        email = email.replace(" ", "")
        
        # 3. Check for @
        if "@" not in email:
            # Cannot automatically fix missing @ without assumptions
            return email, (email != original), False
        
        try:
            parts = email.split('@')
            if len(parts) != 2:
                return email, (email != original), False
                
            user, domain = parts
            
            # 3. Add .com if missing (heuristic for known providers)
            if '.' not in domain:
                if domain in ['gmail', 'yahoo', 'outlook', 'hotmail', 'rediff', 'aol']:
                    domain += '.com'
            
            # 4. Correct spelling of common domains
            for correct, typos in EmailChecker.COMMON_DOMAINS.items():
                if domain in typos:
                    domain = correct
                    break
            
            email = f"{user}@{domain}"
            
        except Exception:
            pass
            
        is_modified = (email != original)
        is_valid = ('@' in email and '.' in email)
        
        return email, is_modified, is_valid

    @staticmethod
    def process_csv_file(filepath, include_cc=False):
        """
        Process CSV file: 
        Col A: To (Multiple allowed with ;)
        Col B: Name (optional)
        Col C: Status
        Col D: OldEmail (backup)
        Col E: CC (Multiple allowed with ;)
        Returns: (corrections_list, list_for_sending, error_msg)
        """
        corrections = []
        rows_for_sending = [] # list of dicts {email, name, row_idx, cc_emails}
        
        try:
            all_rows = []
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                all_rows = list(reader)
                
            if not all_rows:
                return [], [], "Empty file"

            modified_count = 0
            
            # Determine if first row is header
            start_row = 0
            if all_rows and 'email' in str(all_rows[0][0]).lower():
                start_row = 1
                
            for i in range(start_row, len(all_rows)):
                row = all_rows[i]
                
                # Ensure minimum 5 columns (A, B, C, D, E)
                while len(row) < 5:
                    row.append("")
                
                # Handle TO (Col A) - potentially multiple
                original_to = row[0]
                to_parts = [p.strip() for p in original_to.split(';') if p.strip()]
                corrected_to_parts = []
                any_to_invalid = False
                to_modified = False
                
                for p in to_parts:
                    corr, mod, val = EmailChecker.correct_email(p)
                    if mod: to_modified = True
                    if not val: any_to_invalid = True
                    corrected_to_parts.append(corr)
                
                new_to = "; ".join(corrected_to_parts)
                
                if to_modified:
                    # Move original to Col D (Index 3) if not already there
                    if not row[3]:
                        row[3] = original_to
                    row[0] = new_to
                    
                    corrections.append({
                        'row': i + 1,
                        'old': original_to,
                        'new': new_to
                    })
                    modified_count += 1
                
                # Extract CC (Col E) - potentially multiple
                original_cc = ""
                if include_cc:
                    original_cc = row[4]
                
                # Add to sending list if TO part is valid
                if to_parts and not any_to_invalid:
                    name = row[1] if len(row) > 1 and row[1] else corrected_to_parts[0].split('@')[0]
                    rec_dict = {
                        'email': new_to, # String of recipients
                        'name': name,
                        'row_idx': i,
                        'status': row[2]
                    }
                    if include_cc:
                        rec_dict['cc_emails'] = original_cc
                    rows_for_sending.append(rec_dict)
                    
            # Performance Gap Fix: Only rewrite if we actually changed something or added columns
            if modified_count > 0 or len(all_rows[0]) < 5:
                try:
                    with open(filepath, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerows(all_rows)
                except Exception as write_e:
                    # Log but continue if write-protected
                    print(f"⚠️ Warning: Could not save corrections to disk: {write_e}")
                
            return corrections, rows_for_sending, None
            
        except PermissionError:
            return [], [], "Permission denied: The file is currently open in another program (like Excel). Please close it and try again."
        except Exception as e:
            return [], [], str(e)

    _cached_rows = {} # {filepath: rows_list}
    
    @staticmethod
    def update_status(filepath, row_idx, status, use_cache=False, defer_write=False):
        """Update status in Column C (Index 2) for a specific row.
        - use_cache: If True, uses/updates the in-memory cache.
        - defer_write: If True, skips writing to disk (useful for batches).
        """
        try:
            rows = []
            if use_cache and filepath in EmailChecker._cached_rows:
                rows = EmailChecker._cached_rows[filepath]
            else:
                if not os.path.exists(filepath): return False
                with open(filepath, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                if use_cache:
                    EmailChecker._cached_rows[filepath] = rows
            
            if 0 <= row_idx < len(rows):
                while len(rows[row_idx]) < 3:
                     rows[row_idx].append("")
                
                rows[row_idx][2] = status # Col C
                
                if not defer_write:
                    # Sync disk immediately
                    with open(filepath, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerows(rows)
                return True
        except PermissionError:
            print(f"Error updating status: Permission denied.")
            return False
        except Exception as e:
            print(f"Error updating status: {e}")
            return False

    @staticmethod
    def flush_cache(filepath):
        """Force write cached rows to disk."""
        if filepath in EmailChecker._cached_rows:
            try:
                rows = EmailChecker._cached_rows[filepath]
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)
                return True
            except Exception as e:
                print(f"Error flushing cache: {e}")
                return False
        return False

    @staticmethod
    def clear_cache(filepath=None):
        if filepath:
            EmailChecker._cached_rows.pop(filepath, None)
        else:
            EmailChecker._cached_rows.clear()
