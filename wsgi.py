import sys
import logging
from app import app

# Set up error logging for Vercel deployment
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("WSGI application initialized successfully")
    # This ensures that any app configuration happens
    # before the request handling starts
except Exception as e:
    logger.error(f"Error during WSGI initialization: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())

# This file is required for Vercel deployment
# It provides the WSGI entry point for the application 