from fastapi import Path

SEQ_PATH = Path(..., description="The Seq of the user's event", ge=1)
