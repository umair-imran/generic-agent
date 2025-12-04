"""Service for handling room bookings and saving to CSV."""
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import LOGGER


class BookingService:
    """Service to handle room booking operations and CSV storage."""
    
    def __init__(self, csv_file_path: str = "bookings.csv"):
        """
        Initialize the booking service.
        
        Args:
            csv_file_path: Path to the CSV file where bookings will be saved
        """
        self.csv_file_path = Path(csv_file_path)
        self.fieldnames = [
            "booking_id",
            "guest_name",
            "check_in_date",
            "check_out_date",
            "number_of_guests",
            "room_type",
            "contact_phone",
            "contact_email",
            "special_requests",
            "booking_timestamp",
            "status"
        ]
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Ensure the CSV file exists with headers if it doesn't."""
        if not self.csv_file_path.exists():
            with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                writer.writeheader()
            LOGGER.info(f"Created bookings CSV file at {self.csv_file_path}")
    
    def save_booking(self, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save booking details to CSV file.
        
        Args:
            booking_details: Dictionary containing booking information with keys:
                - guest_name (required)
                - check_in_date (required)
                - check_out_date (required)
                - number_of_guests (required)
                - room_type (optional)
                - contact_phone (optional)
                - contact_email (optional)
                - special_requests (optional)
        
        Returns:
            Dictionary with booking_id and status
        """
        try:
            # Generate booking ID
            booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Prepare booking record
            booking_record = {
                "booking_id": booking_id,
                "guest_name": booking_details.get("guest_name", ""),
                "check_in_date": booking_details.get("check_in_date", ""),
                "check_out_date": booking_details.get("check_out_date", ""),
                "number_of_guests": str(booking_details.get("number_of_guests", "")),
                "room_type": booking_details.get("room_type", "Standard"),
                "contact_phone": booking_details.get("contact_phone", ""),
                "contact_email": booking_details.get("contact_email", ""),
                "special_requests": booking_details.get("special_requests", ""),
                "booking_timestamp": datetime.now().isoformat(),
                "status": "Confirmed"
            }
            
            # Validate required fields
            required_fields = ["guest_name", "check_in_date", "check_out_date", "number_of_guests"]
            missing_fields = [field for field in required_fields if not booking_record.get(field)]
            
            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                LOGGER.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "booking_id": None
                }
            
            # Append to CSV
            with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                writer.writerow(booking_record)
            
            LOGGER.info(f"Booking saved successfully: {booking_id} for {booking_record['guest_name']}")
            
            return {
                "success": True,
                "booking_id": booking_id,
                "message": f"Booking confirmed with ID: {booking_id}",
                "booking_details": booking_record
            }
            
        except Exception as e:
            error_msg = f"Failed to save booking: {str(e)}"
            LOGGER.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg,
                "booking_id": None
            }
    
    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a booking by ID from CSV.
        
        Args:
            booking_id: The booking ID to search for
        
        Returns:
            Dictionary with booking details or None if not found
        """
        try:
            if not self.csv_file_path.exists():
                return None
            
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row.get("booking_id") == booking_id:
                        return row
            return None
        except Exception as e:
            LOGGER.error(f"Error retrieving booking {booking_id}: {str(e)}")
            return None

