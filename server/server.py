import logging
import socket
from datetime import datetime

from .exceptions import HttpServerException
from .request import Request
from .response import TextResponse
from .router import Router

logger = logging.getLogger(__name__)


class Server:
    def __init__(self, router: Router, addr=("localhost", 8000)):
        self.addr = addr
        self.router = router

    def create_socket(self):
        """ Функция создает, настраивает сокет """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(self.addr)
        sock.listen(5)
        return sock

    def handle_http_request(self, data, conn, addr):
        """
        Обработать сырой http запрос (Обработка полученных от клиента байтиков)
        """
        req = Request.from_http_bytes(addr, data)
        start_time = datetime.now()
        response = None
        try:
            response = self.router.process_request(req)  # bytes -> Response
        except HttpServerException as e:
            logger.exception(e)
            response = TextResponse()
            response.status = e.status
            response.body = e.msg
        if response:
            conn.sendall(response if isinstance(response, bytes) else response.encode())
            logger.debug(
                f"[{response.status}][{datetime.now() - start_time}] {req.path}"
            )
        # Закрываем соединение
        logger.info(f"Close connection: {addr}")
        conn.close()

    def start_loop(self):
        """
        Начать луп в котором мы будем получать соединения, затем данные из соединения
        (HTTP запросы) и делегировать обработку запросов методу handle_http_request
        """
        with self.create_socket() as sock:
            logger.info(f"Listen on: {self.addr}")
            while True:
                conn, addr = sock.accept()
                logger.debug(f"New connection: {addr}")
                data = bytearray()  # Все данные от клиента
                while True:
                    r_data = conn.recv(1024)
                    data.extend(r_data)
                    if len(r_data) < 1024:
                        break
                # Обрабатываем http запрос
                self.handle_http_request(data, conn, addr)
