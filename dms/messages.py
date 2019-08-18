from starlette.requests import Request

SUCCESS = "success"
INFO = "info"
DANGER = "danger"

KEY = "messages"


def add(request: Request, text: str, content: str = None, type: str = SUCCESS):
    messages = request.session.get(KEY) or []
    messages.append({"text": text, "content": content, "type": type})
    request.session[KEY] = messages


def get(request: Request):
    messages = request.session.get(KEY)
    request.session.pop(KEY, None)
    return messages
