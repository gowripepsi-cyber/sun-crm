import os
import shutil
import zipfile
import glob
from datetime import datetime
from pathlib import Path
from settings_manager import settings_mgr
import database

def perform_backup(backup_type="Manual"):
    """
    Creates a ZIP archive containing the SQLite database.
    Saves it in the configured backup folder.
    """
    db_path = settings_mgr.get("db_location")
    backup_folder = settings_mgr.get("backup_folder")
    
    if not db_path or not os.path.exists(db_path):
        return False, "Database file does not exist."
        
    try:
        os.makedirs(backup_folder, exist_ok=True)
        
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"suncrm_backup_{timestamp}.zip"
        backup_path = os.path.join(backup_folder, backup_filename)
        
        # Write SQLite DB to ZIP
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            db_name = os.path.basename(db_path)
            zip_file.write(db_path, arcname=db_name)
            
            # Write a small metadata file
            meta_content = f"Type: {backup_type}\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            zip_file.writestr("backup_info.txt", meta_content)
            
        # Log to DB
        database.log_backup(backup_path, backup_type, "Success")
        database.log_activity("Database Backup", f"Created backup archive: {backup_filename}")
        
        # Perform auto-pruning if configured
        if settings_mgr.get("auto_backup"):
            prune_old_backups()
            
        return True, backup_path
    except Exception as e:
        err_msg = str(e)
        # Log failure
        database.log_backup("N/A", backup_type, f"Failed: {err_msg}")
        database.log_activity("Backup Failure", f"Error backing up database: {err_msg}")
        return False, err_msg

def prune_old_backups():
    """Prunes old zip backups, keeping only the configured limit."""
    backup_folder = settings_mgr.get("backup_folder")
    limit = int(settings_mgr.get("auto_backup_count", 5))
    
    try:
        # Match suncrm_backup_*.zip files
        search_pattern = os.path.join(backup_folder, "suncrm_backup_*.zip")
        backups = glob.glob(search_pattern)
        
        # Sort by creation time / name
        backups.sort(key=os.path.getmtime, reverse=True)
        
        if len(backups) > limit:
            for old_backup in backups[limit:]:
                os.remove(old_backup)
                database.log_activity("Backup Pruned", f"Deleted older backup: {os.path.basename(old_backup)}")
    except Exception as e:
        print(f"Error pruning old backups: {e}")

def restore_backup(zip_path):
    """
    Restores the database from a backup zip archive.
    Creates a pre-restore snapshot database for safety.
    """
    db_path = settings_mgr.get("db_location")
    
    if not os.path.exists(zip_path):
        return False, "Selected backup file does not exist."
        
    try:
        # 1. Validate zip file and extract DB name
        if not zipfile.is_zipfile(zip_path):
            return False, "Selected file is not a valid zip archive."
            
        db_name = os.path.basename(db_path)
        db_in_zip = False
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            if db_name in file_list:
                db_in_zip = True
                
        if not db_in_zip:
            return False, f"Selected backup zip does not contain the database file: {db_name}."
            
        # 2. Make safety copy of current db
        if os.path.exists(db_path):
            snapshot_path = db_path + ".prerestore"
            shutil.copy2(db_path, snapshot_path)
            database.log_activity("Restore Info", f"Created safety database snapshot: {os.path.basename(snapshot_path)}")
            
        # 3. Extract DB to replace the active database
        # Close any lingering connections if we can, but since SQLite handles files directly, 
        # we copy it directly. Note: In PySide app, we will prompt the user to let us reconnect 
        # or we will reinitialize the connection pools immediately after restore.
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extract(db_name, path=os.path.dirname(db_path))
            
        database.log_activity("Database Restore", f"Successfully restored database from: {os.path.basename(zip_path)}")
        return True, "Database restored successfully."
    except Exception as e:
        err_msg = str(e)
        database.log_activity("Restore Failure", f"Failed to restore database: {err_msg}")
        return False, err_msg
