"""Service for handling course enrollments and saving to CSV."""
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import LOGGER


class EnrollmentService:
    """Service to handle course enrollment operations and CSV storage."""
    
    def __init__(self, csv_file_path: str = "enrollments.csv"):
        """
        Initialize the enrollment service.
        
        Args:
            csv_file_path: Path to the CSV file where enrollments will be saved
        """
        self.csv_file_path = Path(csv_file_path)
        self.fieldnames = [
            "enrollment_id",
            "student_name",
            "course_name",
            "course_code",
            "enrollment_date",
            "start_date",
            "end_date",
            "instructor_name",
            "contact_phone",
            "contact_email",
            "previous_education",
            "enrollment_timestamp",
            "status"
        ]
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Ensure the CSV file exists with headers if it doesn't."""
        if not self.csv_file_path.exists():
            with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                writer.writeheader()
            LOGGER.info(f"Created enrollments CSV file at {self.csv_file_path}")
    
    def save_enrollment(self, enrollment_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save enrollment details to CSV file.
        
        Args:
            enrollment_details: Dictionary containing enrollment information with keys:
                - student_name (required)
                - course_name (required)
                - course_code (optional)
                - enrollment_date (required)
                - start_date (optional)
                - end_date (optional)
                - instructor_name (optional)
                - contact_phone (optional)
                - contact_email (optional)
                - previous_education (optional)
        
        Returns:
            Dictionary with enrollment_id and status
        """
        try:
            # Generate enrollment ID
            enrollment_id = f"ENR{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Prepare enrollment record
            enrollment_record = {
                "enrollment_id": enrollment_id,
                "student_name": enrollment_details.get("student_name", ""),
                "course_name": enrollment_details.get("course_name", ""),
                "course_code": enrollment_details.get("course_code", ""),
                "enrollment_date": enrollment_details.get("enrollment_date", ""),
                "start_date": enrollment_details.get("start_date", ""),
                "end_date": enrollment_details.get("end_date", ""),
                "instructor_name": enrollment_details.get("instructor_name", ""),
                "contact_phone": enrollment_details.get("contact_phone", ""),
                "contact_email": enrollment_details.get("contact_email", ""),
                "previous_education": enrollment_details.get("previous_education", ""),
                "enrollment_timestamp": datetime.now().isoformat(),
                "status": "Enrolled"
            }
            
            # Validate required fields
            required_fields = ["student_name", "course_name", "enrollment_date"]
            missing_fields = [field for field in required_fields if not enrollment_record.get(field)]
            
            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                LOGGER.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "enrollment_id": None
                }
            
            # Append to CSV
            with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                writer.writerow(enrollment_record)
            
            LOGGER.info(f"Enrollment saved successfully: {enrollment_id} for {enrollment_record['student_name']}")
            
            return {
                "success": True,
                "enrollment_id": enrollment_id,
                "message": f"Enrollment confirmed with ID: {enrollment_id}",
                "enrollment_details": enrollment_record
            }
            
        except Exception as e:
            error_msg = f"Failed to save enrollment: {str(e)}"
            LOGGER.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "enrollment_id": None
            }
    
    def get_enrollment(self, enrollment_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an enrollment by ID from CSV.
        
        Args:
            enrollment_id: The enrollment ID to search for
        
        Returns:
            Dictionary with enrollment details or None if not found
        """
        try:
            if not self.csv_file_path.exists():
                return None
            
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get("enrollment_id") == enrollment_id:
                        return row
            return None
        except Exception as e:
            LOGGER.error(f"Error retrieving enrollment {enrollment_id}: {str(e)}")
            return None
