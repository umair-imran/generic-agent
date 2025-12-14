"""
---
title: MCP Server
category: mcp
tags: [mcp, openai, deepgram]
difficulty: beginner
description: Shows how to create an MCP server for HR requests that can be used to control a LiveKit room.
demonstrates:
  - Creating an MCP server that can be used to control a LiveKit room.
---
"""
from mcp.server.fastmcp import FastMCP
import asyncio
import concurrent.futures

mcp = FastMCP("HR MCP", host="0.0.0.0", port=8004)

from utils.logger import LOGGER
from mcp_server.hr_service import HRService

# Initialize HR service
hr_service = HRService()


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
def save_hr_request_record(employee_name: str,
        request_type: str,
        request_date: str,
        employee_id: str = "",
        department: str = "",
        contact_phone: str = "",
        contact_email: str = "",
        request_description: str = "",
        priority: str = "Normal") -> str:
    """
    Submit an HR request and save the request to CSV.
    
    Args:
        employee_name: Full name of the employee
        request_type: Type of HR request (Leave Request, Payroll Inquiry, Benefits, Training, etc.)
        request_date: Request date (format: YYYY-MM-DD)
        employee_id: Employee ID number (optional)
        department: Employee department
        contact_phone: Contact phone number
        contact_email: Contact email address
        request_description: Detailed description of the request
        priority: Priority level (Low, Normal, High, Urgent)
    
    Returns:
        Dictionary with request confirmation details
    """
    try:
        request_details = {
            "employee_name": employee_name,
            "request_type": request_type,
            "request_date": request_date,
            "employee_id": employee_id,
            "department": department,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
            "request_description": request_description,
            "priority": priority
        }
        
        result = hr_service.save_hr_request(request_details)
        
        if result["success"]:
            LOGGER.info(f"HR request submitted successfully: {result['request_id']}")
            return f"Your HR request has been successfully submitted! Your request ID is {result['request_id']}. Our HR team will review it and get back to you soon."
        else:
            LOGGER.error(f"HR request submission failed: {result.get('error')}")
            return "I apologize, but there was an issue processing your HR request. Please try again or contact the HR department directly."
            
    except Exception as e:
        error_msg = f"Exception during HR request submission: {str(e)}"
        LOGGER.error(error_msg)
        return "I apologize, but there was an error processing your HR request. Please try again."


if __name__ == "__main__":
    mcp.run(transport="sse")
