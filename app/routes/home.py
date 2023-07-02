# from fastapi import APIRouter, Request
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates

# router = APIRouter()
# templates = Jinja2Templates(directory="app/templates")

# f_data = "2023 Rikesh Chhetri"

# @router.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     return templates.TemplateResponse("validation.html", {"request": request, "footer_data": f_data})


from fastapi import APIRouter, Request,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

f_data = "2023 Rikesh Chhetri"

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the home page with the validation.html template.

    Args:
        request (Request): FastAPI request object.

    Returns:
        TemplateResponse: HTML template response.

    Raises:
        HTTPException: If there is an error rendering the template.
    """
    try:
        return templates.TemplateResponse("validation.html", {"request": request, "footer_data": f_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
