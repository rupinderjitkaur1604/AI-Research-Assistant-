from langchain_core.tools import tool
from datetime import datetime


@tool
def get_current_time() -> str:
    """
    Returns the current date and time.
    """


    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
