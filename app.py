from http import HTTPStatus
from server.response import RedirectResponse
import jinja2
import logging 
import re  
from urllib.parse import parse_qs
from logging import error
# Настраиваем логгер
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from server import HtmlResponse, Request, Response, Route, Router, Server, serve
from services import LinksService  
from connection import connection



with open("./templates/index.html", "r") as f:
    index_template = jinja2.Template(f.read())


def create_link_view(req:Request) -> Response:
    resi  = parse_qs(req.body.decode())
    urls = resi.get("url")
    res = Response(HTTPStatus.NOT_FOUND)
    if urls :
       new_link = LinksService.createNewLink(urls[0])
       res = Response(HTTPStatus.FOUND )
       res.addHeader("Location",f'/?success={new_link[0]}')
       
    return res

def get_link_by_id(links,id):
    """ поучает список линков и находит линк по подхоядщему ID  """
    for link in links:
        if link["id"] == id:
            return link

def index_view(req: Request) -> Response:
    res = HtmlResponse()
    success_ids = parse_qs(req.qs).get("success")
    links = LinksService.getAllLinks()
    link = None
    if success_ids:
        link = get_link_by_id(links, int(success_ids[0]))
    if req.method == "POST":
        create_link_view
    print(success_ids)
    res.body = index_template.render(links=links, link=link)

    return res


def redirect_to_link(req: Request) -> Response:
    
    code = req.path[1:]
    cur = connection.cursor()
    cur.execute("SELECT id FROM links WHERE code=%s" , (code,))
    only = cur.fetchone()
    LinksService.increase_views_count(only[0])
    cur.execute("SELECT original_url FROM links WHERE code=%s" , (code,))
    orig = cur.fetchone()
    res = RedirectResponse(orig[0])
    return res 
       

def main():
    router = Router()
    router.add_route(
        Route(r"^/(?P<code>[a-zA-Z0-9]{6,8})/?$", redirect_to_link)
    )
    router.add_route(Route(r"^/create_link$", create_link_view))
    router.add_route(Route(r"^/$", index_view))
    router.add_route(Route(r"^/static", serve("./static", "/static")))
    server = Server(router=router, addr=("localhost", 9999))
    server.start_loop()


if __name__ == "__main__":
    main()
