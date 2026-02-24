import functools

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.utilities.parser import ValidationError
from botocore.exceptions import ClientError

logger = Logger(child=True)

def handle_api_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation failed: {e}")
            return Response(
                status_code=400,
                body={"error": "Invalid input", "details": e.errors()}
            )
        except ClientError as e:
            logger.exception("Infrastructure (AWS) error")
            return Response(
                status_code=500,
                body={"error": "Downstream service error"}
            )
        except Exception:
            logger.exception("Unexpected system error")
            return Response(
                status_code=500,
                body={"error": "Internal server error"}
            )
    return wrapper