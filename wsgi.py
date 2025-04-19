import sys
import logging
import os
from app import app

# Set up error logging for Vercel deployment
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("WSGI application initialized successfully")
    
    # Check if templates directory exists
    templates_path = os.path.join(os.path.dirname(__file__), 'templates')
    if os.path.exists(templates_path):
        logger.info(f"Templates directory found at {templates_path}")
        try:
            template_files = os.listdir(templates_path)
            logger.info(f"Templates available: {template_files}")
        except Exception as e:
            logger.error(f"Failed to list templates: {str(e)}")
    else:
        logger.error(f"Templates directory not found at {templates_path}")
    
    # Check if static directory exists
    static_path = os.path.join(os.path.dirname(__file__), 'static')
    if os.path.exists(static_path):
        logger.info(f"Static directory found at {static_path}")
        try:
            static_files = os.listdir(static_path)
            logger.info(f"Static files available: {static_files}")
        except Exception as e:
            logger.error(f"Failed to list static files: {str(e)}")
    else:
        logger.error(f"Static directory not found at {static_path}")
    
except Exception as e:
    logger.error(f"Error during WSGI initialization: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())

# This file is required for Vercel deployment
# It provides the WSGI entry point for the application 