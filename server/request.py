import re
from typing import Dict


class Request:
    """
    Объект запроса на сервер
    ip - ip адрес клинета
    port - port клинета
    method - GET/POST/DELETE/PUT/PATCH
    path - URI; Example: /some/path/
    query - Queystring; Example: ?key=value&key2=value
    headers - Dict[str, str]; Example: {"Accept": "*/*"}
    """

    HTTP_START_LINE_RE = re.compile(
        r"^(?P<method>[A-Z]+?)\s(?P<path>.+?)(\?(?P<querystring>.+?))?\sHTTP\/[1-9\.]{1,4}$"
    )
    HTTP_HEADER_RE = re.compile(r"^(?P<key>.+?):(?P<value>.+?)$")

    @classmethod
    def from_http_bytes(cls, addr: tuple, http_data: bytearray):
        lines = http_data.splitlines()
        # Парсим стартовую строку
        start_line = lines[0].decode("utf-8")
        start_line_match = Request.HTTP_START_LINE_RE.match(start_line)
        if start_line_match:
            method = start_line_match.group("method")
            path = start_line_match.group("path")
            querystring = start_line_match.group("querystring")
        else:
            raise Exception("Invalid start line in HTTP request")
        # Парсим заголовки
        body_start_line = None
        headers = {}  # [(key: value)]
        for line in lines[1:]:
            if not line:
                body_start_line = lines.index(line)
                break
            header_line = line.decode("utf-8")
            header_line_match = Request.HTTP_HEADER_RE.match(header_line)
            if header_line_match:
                headers[
                    header_line_match.group("key").strip()
                ] = header_line_match.group("value").strip()
        # Сохраняем body в отдельную переменную
        body = None
        if body_start_line:
            body = b"\r\n".join(lines[body_start_line + 1 :])

        return cls(addr[0], addr[1], method, path, querystring, headers, body)

    def __init__(self, ip, port, method, path, qs, headers, body):
        self.ip = ip  # type: str
        self.port = port  # type: int
        self.method = method  # type: str
        self.path = path  # type: str
        self.qs = qs  # type: str
        self.headers = headers  # type: Dict[str, str]
        self.body = body  # type: bytes

    def __str__(self):
        return f"<Request ip={self.ip} port={self.port} path={self.path} method={self.method} headers={self.headers}>"
