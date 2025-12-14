"""
---
title: MCP Server
category: mcp
tags: [mcp, openai, deepgram]
difficulty: beginner
description: Shows how to create an MCP server for medical appointments that can be used to control a LiveKit room.
demonstrates:
  - Creating an MCP server that can be used to control a LiveKit room.
---
"""
from mcp.server.fastmcp import FastMCP
import asyncio
import concurrent.futures

mcp = FastMCP("Medical MCP", host="0.0.0.0", port=8002)

from utils.logger import LOGGER
from mcp_server.appointment_service import AppointmentService

# Initialize appointment service
appointment_service = AppointmentService()


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
def save_appointment_record(patient_name: str,
        appointment_date: str,
        appointment_time: str,
        doctor_name: str = "",
        department: str = "General Medicine",
        contact_phone: str = "",
        contact_email: str = "",
        symptoms: str = "") -> str:
    """
    Schedule a medical appointment and save the appointment to CSV.
    
    Args:
        patient_name: Full name of the patient
        appointment_date: Appointment date (format: YYYY-MM-DD)
        appointment_time: Appointment time (format: HH:MM)
        doctor_name: Name of the doctor (optional)
        department: Medical department (General Medicine, Cardiology, Pediatrics, etc.)
        contact_phone: Contact phone number
        contact_email: Contact email address
        symptoms: Description of symptoms or reason for visit
    
    Returns:
        Dictionary with appointment confirmation details
    """
    try:
        appointment_details = {
            "patient_name": patient_name,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "doctor_name": doctor_name,
            "department": department,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
            "symptoms": symptoms
        }
        
        result = appointment_service.save_appointment(appointment_details)
        
        if result["success"]:
            LOGGER.info(f"Appointment scheduled successfully: {result['appointment_id']}")
            return f"Your appointment has been successfully scheduled! Your appointment ID is {result['appointment_id']}. Please arrive 15 minutes before your scheduled time."
        else:
            LOGGER.error(f"Appointment scheduling failed: {result.get('error')}")
            return "I apologize, but there was an issue processing your appointment request. Please try again or contact our reception directly."
            
    except Exception as e:
        error_msg = f"Exception during appointment scheduling: {str(e)}"
        LOGGER.error(error_msg)
        return "I apologize, but there was an error processing your appointment. Please try again."


if __name__ == "__main__":
    mcp.run(transport="sse")
