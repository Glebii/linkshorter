from http import HTTPStatus
from typing import Union


class Response:
    def __init__(self, status: HTTPStatus = HTTPStatus.OK, headers={}, body=b""):
        self._status = status
        self._body = body  # type: Union[bytes, str]
        self._headers = headers

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: HTTPStatus):
        self._status = value

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value: Union[bytes, str]):
        self._body = value
        self._updateContentLength()

    def addHeader(self, key: str, value: str):
        """ Добавить новый заголовок """
        self._headers[key] = value

    def delHeader(self, key: str):
        """ Удалить заголовок из объекта ответа """
        self._headers.pop(key, 0)

        self._updateContentLength()

    def _updateContentLength(self):
        """
        Метод будет добавлять заголовок 'Content-Length' определяя длину self._body
        """
        self.addHeader(
            "Content-Length",
            str(
                len(self._body.encode() if isinstance(self._body, str) else self._body)
            ),
        )

    def _getHeaders(self) -> str:
        """
        Сформировать строку содержащую:
        - стартовая строка HTTP ответа
        - заголовки
        """
        return (
            # стартовая строка
            f"HTTP/1.1 {self._status} {self._status.phrase}\n"
            +
            # конкатенируем заголовки через перенос строки
            ("\n".join([f"{key}: {value}" for key, value in self._headers.items()]))
        )

    def encode(self) -> bytes:
        """
        Представить текущий ответ в bytes
        """
        self._updateContentLength()
        print("!", self._getHeaders())
        http_response_bytes = bytearray(self._getHeaders(), "utf-8")  # type: bytearray
        if self._body:
            http_response_bytes.extend(b"\r\n\r\n")
            http_response_bytes += (
                #      👇 - в случае когда self.body – строка
                self._body.encode()
                if isinstance(self._body, str)
                #      👇 - self.body – bytes
                else self._body
            )
        return bytes(http_response_bytes)


class TextResponse(Response):
    """ Класс для ответа с Content-Type 'text/plain' """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addHeader("Content-Type", "text/plain; charset=UTF-8")


class HtmlResponse(Response):
    """ Класс для ответа с Content-Type 'text/html' """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addHeader("Content-Type", "text/html; charset=UTF-8")


class JsonResponse(Response):
    """ Класс для ответа с Content-Type 'application/json' """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addHeader("Content-Type", "application/json; charset=UTF-8")

class RedirectResponse(Response):
    def __init__ (self, location:str ,*args ,**kwargs):
        super().__init__(HTTPStatus.FOUND ,*args,**kwargs)
        self.body = ''
        self.addHeader("Location",location)
