"""Service for handling medical appointments and saving to CSV."""
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import LOGGER


class AppointmentService:
    """Service to handle medical appointment operations and CSV storage."""
    
    def __init__(self, csv_file_path: str = "appointments.csv"):
        """
        Initialize the appointment service.
        
        Args:
            csv_file_path: Path to the CSV file where appointments will be saved
        """
        self.csv_file_path = Path(csv_file_path)
        self.fieldnames = [
            "appointment_id",
            "patient_name",
            "appointment_date",
            "appointment_time",
            "doctor_name",
            "department",
            "contact_phone",
            "contact_email",
            "symptoms",
            "appointment_timestamp",
            "status"
        ]
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Ensure the CSV file exists with headers if it doesn't."""
        if not self.csv_file_path.exists():
            with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                writer.writeheader()
            LOGGER.info(f"Created appointments CSV file at {self.csv_file_path}")
    
    def save_appointment(self, appointment_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save appointment details to CSV file.
        
        Args:
            appointment_details: Dictionary containing appointment information with keys:
                - patient_name (required)
                - appointment_date (required)
                - appointment_time (required)
                - doctor_name (optional)
                - department (optional)
                - contact_phone (optional)
                - contact_email (optional)
                - symptoms (optional)
        
        Returns:
            Dictionary with appointment_id and status
        """
        try:
            # Generate appointment ID
            appointment_id = f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Prepare appointment record
            appointment_record = {
                "appointment_id": appointment_id,
                "patient_name": appointment_details.get("patient_name", ""),
                "appointment_date": appointment_details.get("appointment_date", ""),
                "appointment_time": appointment_details.get("appointment_time", ""),
                "doctor_name": appointment_details.get("doctor_name", ""),
                "department": appointment_details.get("department", "General Medicine"),
                "contact_phone": appointment_details.get("contact_phone", ""),
                "contact_email": appointment_details.get("contact_email", ""),
                "symptoms": appointment_details.get("symptoms", ""),
                "appointment_timestamp": datetime.now().isoformat(),
                "status": "Scheduled"
            }
            
            # Validate required fields
            required_fields = ["patient_name", "appointment_date", "appointment_time"]
            missing_fields = [field for field in required_fields if not appointment_record.get(field)]
            
            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                LOGGER.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "appointment_id": None
                }
            
            # Append to CSV
            with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                writer.writerow(appointment_record)
            
            LOGGER.info(f"Appointment saved successfully: {appointment_id} for {appointment_record['patient_name']}")
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "message": f"Appointment scheduled with ID: {appointment_id}",
                "appointment_details": appointment_record
            }
            
        except Exception as e:
            error_msg = f"Failed to save appointment: {str(e)}"
            LOGGER.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "appointment_id": None
            }
    
    def get_appointment(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an appointment by ID from CSV.
        
        Args:
            appointment_id: The appointment ID to search for
        
        Returns:
            Dictionary with appointment details or None if not found
        """
        try:
            if not self.csv_file_path.exists():
                return None
            
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get("appointment_id") == appointment_id:
                        return row
            return None
        except Exception as e:
            LOGGER.error(f"Error retrieving appointment {appointment_id}: {str(e)}")
            return None
