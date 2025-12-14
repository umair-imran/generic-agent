"""
---
title: MCP Server
category: mcp
tags: [mcp, openai, deepgram]
difficulty: beginner
description: Shows how to create an MCP server for course enrollments that can be used to control a LiveKit room.
demonstrates:
  - Creating an MCP server that can be used to control a LiveKit room.
---
"""
from mcp.server.fastmcp import FastMCP
import asyncio
import concurrent.futures

mcp = FastMCP("Education MCP", host="0.0.0.0", port=8003)

from utils.logger import LOGGER
from mcp_server.enrollment_service import EnrollmentService

# Initialize enrollment service
enrollment_service = EnrollmentService()


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
def save_enrollment_record(student_name: str,
        course_name: str,
        enrollment_date: str,
        course_code: str = "",
        start_date: str = "",
        end_date: str = "",
        instructor_name: str = "",
        contact_phone: str = "",
        contact_email: str = "",
        previous_education: str = "") -> str:
    """
    Enroll a student in a course and save the enrollment to CSV.
    
    Args:
        student_name: Full name of the student
        course_name: Name of the course
        enrollment_date: Enrollment date (format: YYYY-MM-DD)
        course_code: Course code or identifier (optional)
        start_date: Course start date (format: YYYY-MM-DD)
        end_date: Course end date (format: YYYY-MM-DD)
        instructor_name: Name of the instructor
        contact_phone: Contact phone number
        contact_email: Contact email address
        previous_education: Previous education background
    
    Returns:
        Dictionary with enrollment confirmation details
    """
    try:
        enrollment_details = {
            "student_name": student_name,
            "course_name": course_name,
            "course_code": course_code,
            "enrollment_date": enrollment_date,
            "start_date": start_date,
            "end_date": end_date,
            "instructor_name": instructor_name,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
            "previous_education": previous_education
        }
        
        result = enrollment_service.save_enrollment(enrollment_details)
        
        if result["success"]:
            LOGGER.info(f"Enrollment successful: {result['enrollment_id']}")
            return f"Your enrollment has been successfully processed! Your enrollment ID is {result['enrollment_id']}. Welcome to {course_name}!"
        else:
            LOGGER.error(f"Enrollment failed: {result.get('error')}")
            return "I apologize, but there was an issue processing your enrollment. Please try again or contact our admissions office directly."
            
    except Exception as e:
        error_msg = f"Exception during enrollment: {str(e)}"
        LOGGER.error(error_msg)
        return "I apologize, but there was an error processing your enrollment. Please try again."


if __name__ == "__main__":
    mcp.run(transport="sse")
