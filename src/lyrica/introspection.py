import logging
import json

logger = logging.getLogger(__name__)

def introspect_object(obj, name="object", max_depth=3, current_depth=0):
    """Recursively introspect an object to see its structure and contents"""
    indent = "  " * current_depth
    logger.info(f"{indent}{name}: {type(obj).__name__}")
    
    if current_depth >= max_depth:
        logger.info(f"{indent}  (max depth reached)")
        return
    
    # Try to get the object's dict if it has one
    if hasattr(obj, '__dict__'):
        logger.info(f"{indent}  __dict__ contents:")
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):  # Skip private attributes
                logger.info(f"{indent}    {key}: {type(value).__name__} = {repr(value)[:100]}")
                if current_depth < max_depth - 1 and hasattr(value, '__dict__'):
                    introspect_object(value, f"{name}.{key}", max_depth, current_depth + 1)
    
    # Show public attributes and methods
    public_attrs = [attr for attr in dir(obj) if not attr.startswith('_')]
    if public_attrs:
        logger.info(f"{indent}  Public attributes: {public_attrs[:10]}...")  # Show first 10
    
    # Try to convert to dict or show string representation
    try:
        if hasattr(obj, 'to_dict'):
            dict_repr = obj.to_dict()
            logger.info(f"{indent}  to_dict(): {json.dumps(dict_repr, indent=2, default=str)[:500]}...")
        elif hasattr(obj, '__dict__'):
            simple_dict = {k: str(v)[:50] for k, v in obj.__dict__.items() if not k.startswith('_')}
            logger.info(f"{indent}  simplified dict: {simple_dict}")
    except Exception as e:
        logger.info(f"{indent}  Could not serialize to dict: {e}")
    
    logger.info(f"{indent}  String representation: {str(obj)[:200]}...") 