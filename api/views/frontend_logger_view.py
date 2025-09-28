# views/frontend_logger_view.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
import logging

frontend_logger = logging.getLogger("frontend")

@api_view(["POST"])
def frontend_log_receiver(request):
    logs = request.data.get("logs", [])
    for entry in logs:
        level = entry.get("level", "info")
        msg = f"[FRONTEND] {entry.get('timestamp')} | {entry.get('message')}"

        if level == "error":
            frontend_logger.error(msg)
        elif level == "warn":
            frontend_logger.warning(msg)
        else:
            frontend_logger.info(msg)

    return Response({"status": "ok"})