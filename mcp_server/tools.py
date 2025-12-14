"""MCP tools for the hospitality bot."""
from typing import Any, Dict
from mcp_server.booking_service import BookingService
from utils.logger import LOGGER

# Initialize booking service
booking_service = BookingService()


def book_room(guest_name: str, check_in_date: str, check_out_date: str, 
              number_of_guests: int, room_type: str = "Standard",
              contact_phone: str = "", contact_email: str = "", 
              special_requests: str = "") -> Dict[str, Any]:
    """
    Book a room at Al Faisaliah Grand Hotel and save the booking to CSV.
    
    Args:
        guest_name: Full name of the guest
        check_in_date: Check-in date (format: YYYY-MM-DD)
        check_out_date: Check-out date (format: YYYY-MM-DD)
        number_of_guests: Number of guests staying
        room_type: Type of room (Standard, Deluxe, Suite, Executive Suite)
        contact_phone: Contact phone number
        contact_email: Contact email address
        special_requests: Any special requests or preferences
    
    Returns:
        Dictionary with booking confirmation details
    """
    try:
        booking_details = {
            "guest_name": guest_name,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "number_of_guests": number_of_guests,
            "room_type": room_type,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
            "special_requests": special_requests
        }
        
        result = booking_service.save_booking(booking_details)
        
        if result["success"]:
            LOGGER.info(f"Room booking successful: {result['booking_id']}")
            return {
                "success": True,
                "booking_id": result["booking_id"],
                "message": f"Your room has been successfully booked! Your booking ID is {result['booking_id']}. We look forward to welcoming you to Al Faisaliah Grand Hotel.",
                "guest_name": guest_name,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "room_type": room_type
            }
        else:
            LOGGER.error(f"Room booking failed: {result.get('error')}")
            return {
                "success": False,
                "error": result.get("error", "Unknown error occurred"),
                "message": "I apologize, but there was an issue processing your booking. Please try again or contact our reservations team directly."
            }
            
    except Exception as e:
        error_msg = f"Exception during room booking: {str(e)}"
        LOGGER.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "message": "I apologize, but there was an error processing your booking. Please try again."
        }


# Tool definition for OpenAI function calling
BOOK_ROOM_TOOL = {
    "type": "function",
    "function": {
        "name": "book_room",
        "description": "Book a room at Al Faisaliah Grand Hotel. Use this tool when the guest has confirmed they want to proceed with the booking after you have collected all required information (guest name, check-in date, check-out date, number of guests, and contact information).",
        "parameters": {
            "type": "object",
            "properties": {
                "guest_name": {
                    "type": "string",
                    "description": "Full name of the guest making the reservation"
                },
                "check_in_date": {
                    "type": "string",
                    "description": "Check-in date in YYYY-MM-DD format (e.g., 2025-12-15)"
                },
                "check_out_date": {
                    "type": "string",
                    "description": "Check-out date in YYYY-MM-DD format (e.g., 2025-12-20)"
                },
                "number_of_guests": {
                    "type": "integer",
                    "description": "Number of guests that will be staying"
                },
                "room_type": {
                    "type": "string",
                    "description": "Type of room requested. Options: Standard, Deluxe, Suite, Executive Suite. Default is Standard if not specified.",
                    "enum": ["Standard", "Deluxe", "Suite", "Executive Suite"],
                    "default": "Standard"
                },
                "contact_phone": {
                    "type": "string",
                    "description": "Contact phone number for the reservation"
                },
                "contact_email": {
                    "type": "string",
                    "description": "Contact email address for the reservation"
                },
                "special_requests": {
                    "type": "string",
                    "description": "Any special requests or preferences (e.g., room with a view, accessibility needs, early check-in)"
                }
            },
            "required": ["guest_name", "check_in_date", "check_out_date", "number_of_guests"]
        }
    }
}

