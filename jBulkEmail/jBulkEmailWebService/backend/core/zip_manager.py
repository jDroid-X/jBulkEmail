import os
import io
import zipfile
import base64

class ZipManager:
    """
    Phase 1 Dynamic Compression Engine
    Zips large files in-memory to reduce Deep Packet Inspection penalties
    and save disk I/O.
    """
    
    @staticmethod
    def compress_to_memory(file_path, threshold_mb=1.0, max_cap_mb=25.0):
        """
        Reads a file. If larger than threshold_mb, compresses it in memory.
        If larger than max_cap_mb, bypasses memory compression to prevent RAM exhaustion.
        Returns a tuple: (filename, bytes_data, is_zipped)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File missing: {file_path}")
            
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        # Phase 1 Bugfix (TC-D06.2): Block massive files from RAM exhaustion
        if file_size_mb > max_cap_mb:
            print(f"⚠️ SAFETY: {file_path} ({file_size_mb:.1f}MB) exceeds {max_cap_mb}MB limit. Bypassing compression.")
            with open(file_path, "rb") as f:
                return os.path.basename(file_path), f.read(), False
        
        with open(file_path, "rb") as f:
            original_data = f.read()
            
        # If below threshold, return original
        if file_size_mb <= threshold_mb:
            return os.path.basename(file_path), original_data, False
            
        # Compress in memory
        zip_buffer = io.BytesIO()
        base_name = os.path.basename(file_path)
        zip_name = f"{os.path.splitext(base_name)[0]}.zip"
        
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr(base_name, original_data)
            
        return zip_name, zip_buffer.getvalue(), True
