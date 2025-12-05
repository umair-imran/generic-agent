"""
---
title: MCP Server
category: mcp
tags: [mcp, openai, deepgram]
difficulty: beginner
description: Shows how to create an MCP server that can be used to control a LiveKit room.
demonstrates:
  - Creating an MCP server that can be used to control a LiveKit room.
---
"""
from mcp.server.fastmcp import FastMCP
import asyncio
import concurrent.futures

mcp = FastMCP("Hospitality MCP", host="0.0.0.0", port=8001)

from utils.logger import LOGGER
from mcp_server.booking_service import BookingService

# Initialize booking service
booking_service = BookingService()


def run_async(coroutine):
    """
    Helper function to run a coroutine either in the current loop or a new one
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coroutine)
                return future.result()
        else:
            return loop.run_until_complete(coroutine)
    except RuntimeError:
        return asyncio.run(coroutine)

@mcp.tool()
def save_booking_record(guest_name: str,
        check_in_date: str,
        check_out_date: str,
        number_of_guests: int,
        room_type: str = "Standard",
        contact_phone: str = "",
        contact_email: str = "",
        special_requests: str = "") -> str:
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
            return f"Your room has been successfully booked! Your booking ID is {result['booking_id']}. We look forward to welcoming you to Al Faisaliah Grand Hotel."
        else:
            LOGGER.error(f"Room booking failed: {result.get('error')}")
            return "I apologize, but there was an issue processing your booking. Please try again or contact our reservations team directly."
            
    except Exception as e:
        error_msg = f"Exception during room booking: {str(e)}"
        LOGGER.error(error_msg, exc_info=True)
        return "I apologize, but there was an error processing your booking. Please try again."


if __name__ == "__main__":
    mcp.run(transport="sse")