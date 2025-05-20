import logging
import uuid
from sqlalchemy.exc import SQLAlchemyError

from database import get_db
from models import Facebook, X, Tiktok, Instagram
# # from core.extract_content import extract_content_from_transcript
# from ..worker.schema import TaskStatus

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_distinct_user_ids_from_db(platform=None):
    """Get distinct user IDs from database"""
    db = get_db()
    try:
        if platform == "X":
            return db.query(X.user_id).distinct().all()
        elif platform == "tiktok":
            return db.query(Tiktok.user_id).distinct().all()
        elif platform == "instagram":
            return db.query(Instagram.user_id).distinct().all()
        else:
            # Default to Facebook if no platform is specified
            # or if the platform is not recognized
            return db.query(Facebook.user_id).distinct().all()
    except SQLAlchemyError as e:
        logger.error(f"Error when query database: {str(e)}")
        return None
    finally:
        db.close()

def get_all_videos_from_db(platform=None):
    """Get all data from database"""
    db = get_db()
    try:
        if platform == "X":
            return db.query(X).all()
        elif platform == "tiktok":
            return db.query(Tiktok).all()
        elif platform == "instagram":
            return db.query(Instagram).all()
        else:
            # Default to Facebook if no platform is specified
            # or if the platform is not recognized
            return db.query(Facebook).all()
    except SQLAlchemyError as e:
        logger.error(f"Error when query database: {str(e)}")
        return None
    finally:
        db.close()

def get_info_by_user_id(user_id, platform=None):
    """Get all data from database"""
    db = get_db()
    try:
        if platform == "X":
            return db.query(X).filter(X.user_id == user_id).all()
        elif platform == "tiktok":
            return db.query(Tiktok).filter(Tiktok.user_id == user_id).all()
        elif platform == "instagram":
            return db.query(Instagram).filter(Instagram.user_id == user_id).all()
        else:
            # Default to Facebook if no platform is specified
            # or if the platform is not recognized
            return db.query(Facebook).filter(Facebook.user_id == user_id).all()
    except SQLAlchemyError as e:
        logger.error(f"Error when query database: {str(e)}")
        return None
    finally:
        db.close()

def delete_user_by_id(user_id, platform=None):
    """Delete user by ID from database"""
    db = get_db()
    try:
        if platform == "X":
            db.query(X).filter(X.user_id == user_id).delete()
        elif platform == "tiktok":
            db.query(Tiktok).filter(Tiktok.user_id == user_id).delete()
        elif platform == "instagram":
            db.query(Instagram).filter(Instagram.user_id == user_id).delete()
        else:
            # Default to Facebook if no platform is specified
            # or if the platform is not recognized
            db.query(Facebook).filter(Facebook.user_id == user_id).delete()
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Error when delete user: {str(e)}")
        db.rollback()
    finally:
        db.close()        