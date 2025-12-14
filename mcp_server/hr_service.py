"""Service for handling HR requests and saving to CSV."""
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import LOGGER


class HRService:
    """Service to handle HR operations and CSV storage."""
    
    def __init__(self, csv_file_path: str = "hr_requests.csv"):
        """
        Initialize the HR service.
        
        Args:
            csv_file_path: Path to the CSV file where HR requests will be saved
        """
        self.csv_file_path = Path(csv_file_path)
        self.fieldnames = [
            "request_id",
            "employee_name",
            "employee_id",
            "request_type",
            "request_date",
            "department",
            "contact_phone",
            "contact_email",
            "request_description",
            "priority",
            "request_timestamp",
            "status"
        ]
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Ensure the CSV file exists with headers if it doesn't."""
        if not self.csv_file_path.exists():
            with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                writer.writeheader()
            LOGGER.info(f"Created HR requests CSV file at {self.csv_file_path}")
    
    def save_hr_request(self, request_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save HR request details to CSV file.
        
        Args:
            request_details: Dictionary containing HR request information with keys:
                - employee_name (required)
                - request_type (required)
                - request_date (required)
                - employee_id (optional)
                - department (optional)
                - contact_phone (optional)
                - contact_email (optional)
                - request_description (optional)
                - priority (optional)
        
        Returns:
            Dictionary with request_id and status
        """
        try:
            # Generate request ID
            request_id = f"HR{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Prepare request record
            request_record = {
                "request_id": request_id,
                "employee_name": request_details.get("employee_name", ""),
                "employee_id": request_details.get("employee_id", ""),
                "request_type": request_details.get("request_type", ""),
                "request_date": request_details.get("request_date", ""),
                "department": request_details.get("department", ""),
                "contact_phone": request_details.get("contact_phone", ""),
                "contact_email": request_details.get("contact_email", ""),
                "request_description": request_details.get("request_description", ""),
                "priority": request_details.get("priority", "Normal"),
                "request_timestamp": datetime.now().isoformat(),
                "status": "Submitted"
            }
            
            # Validate required fields
            required_fields = ["employee_name", "request_type", "request_date"]
            missing_fields = [field for field in required_fields if not request_record.get(field)]
            
            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                LOGGER.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "request_id": None
                }
            
            # Append to CSV
            with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                writer.writerow(request_record)
            
            LOGGER.info(f"HR request saved successfully: {request_id} for {request_record['employee_name']}")
            
            return {
                "success": True,
                "request_id": request_id,
                "message": f"HR request submitted with ID: {request_id}",
                "request_details": request_record
            }
            
        except Exception as e:
            error_msg = f"Failed to save HR request: {str(e)}"
            LOGGER.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "request_id": None
            }
    
    def get_hr_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an HR request by ID from CSV.
        
        Args:
            request_id: The request ID to search for
        
        Returns:
            Dictionary with request details or None if not found
        """
        try:
            if not self.csv_file_path.exists():
                return None
            
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get("request_id") == request_id:
                        return row
            return None
        except Exception as e:
            LOGGER.error(f"Error retrieving HR request {request_id}: {str(e)}")
            return None
