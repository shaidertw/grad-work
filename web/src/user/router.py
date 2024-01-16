from fastapi import APIRouter, Depends, status, Request, HTTPException
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

#import src.user.service as service
from src.user import service
from src.schemas import DefaultResponse
from src.user.schemas import UserResponse, ListUserResponse, UserRequest, ListUser
from src.config import logger

router = APIRouter(
    prefix="/api/user",
    tags=["User"]
)

templates = Jinja2Templates(directory="src/templates")

@router.get("")
def get_base_page(request: Request):
    return templates.TemplateResponse(
        'users.html',
        {
            'request': request,
            'elements': service.get_orgs_list()
        }
    )

@router.get("/orgs_hash",
          response_class=RedirectResponse,
          status_code=302,
          )
def orgs_hash(request: Request, org_name=None):
    a = service.get_orgs_hash(org_name)
    return templates.TemplateResponse(
        'users.html',
        {
            'request': request,
            'hashes': a,
            'elements': service.get_orgs_list()
        }
    )


@router.post("/delete_hashes",
          response_class=RedirectResponse,
          status_code=302,
          )
def delete_hash(request: Request, org_name: str = Form()):
    service.delete_hashes_by_org_name(org_name)
    return '/api/user'

