from fastapi import FastAPI, Form, Request, status, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse, FileResponse
from pathlib import Path
from typing import Optional
from app.extractor.scrape import get_notes


def clean_up(filename):
    file_path = Path.cwd().joinpath(filename)
    if file_path.exists():
        file_path.unlink()

FOLDER_PATH  = Path.cwd().joinpath(__file__).parent
STATIC_PATH = FOLDER_PATH.joinpath('static')
TEMPLATE_PATH = FOLDER_PATH.joinpath('templates')
print(f'{STATIC_PATH=}')

app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
templates = Jinja2Templates(directory=TEMPLATE_PATH)


@app.get("/", response_class=HTMLResponse)
def index_html(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})


@app.post("/get_form")
def get_form(
    request: Request,
    note_source: str = Form(),
    output_name:  Optional[str]= Form(None),
):
    if not output_name:
        return error_page("please enter the output file name.", request)
    if not output_name.endswith(".txt"):
        output_name = output_name + ".txt"
    try:

        get_notes(note_source, output_name)

    except Exception as e:
        return error_page(str(e), request)
    return RedirectResponse(
        f"/result/{output_name}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get(
    "/result/{file_name}",
    response_class=HTMLResponse,
)
def get_result(
    file_name: str,
    request: Request,
):
    return templates.TemplateResponse(
   'result.html',
        {
            "request": request,
            "file_name": file_name,
        },
    )


@app.get(
    "/file/{file_name}",
    response_class=FileResponse,
)
async def file(file_name: str, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(clean_up, file_name)
    return FileResponse(
        file_name,
        media_type="text/plain",
        background=bg_tasks,
    )


def error_page(error: str, request: Request):
    return templates.TemplateResponse(
    'error.html',
        {
            "request": request,
            "error": error,
        },
    )
