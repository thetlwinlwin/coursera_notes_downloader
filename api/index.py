from fastapi import FastAPI, Form, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse, FileResponse
from pathlib import Path
from typing import Optional
from api.extractor.scrape import get_notes


def clean_up(filename):
    file_path = Path.cwd().joinpath(filename)
    if file_path.exists():
        file_path.unlink()


FOLDER_PATH = Path.cwd().joinpath(__file__).parent
STATIC_PATH = FOLDER_PATH.joinpath("static")
TEMPLATE_PATH = FOLDER_PATH.joinpath("templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
templates = Jinja2Templates(directory=TEMPLATE_PATH)


@app.get("/", response_class=HTMLResponse, name="home")
def index_html(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/get_form")
def get_form(
    request: Request,
    note_source: Optional[str] = Form(None),
    output_name: Optional[str] = Form(None),
):
    if not output_name or not note_source:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="please fill every input.",
        )
    if not output_name.endswith(".txt"):
        output_name = output_name + ".txt"
    try:
        get_notes(note_source, output_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=str(e),
        )
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
    data = {"request": request, "file_name": file_name}
    file = FOLDER_PATH.joinpath(file_name)

    if not file.exists():
        data["error"] = "file not found"
        print(f"{data = }")

    return templates.TemplateResponse(
        "result.html",
        data,
    )


@app.get(
    "/file/{file_name}",
    response_class=FileResponse,
)
async def file(file_name: str, bg_tasks: BackgroundTasks):
    file = FOLDER_PATH.joinpath(file_name)
    if not file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your file has been cancelled. Please restart the whole process again.",
        )

    bg_tasks.add_task(clean_up, file_name)
    return FileResponse(
        file_name,
        media_type="text/plain",
        background=bg_tasks,
    )


@app.exception_handler(HTTPException)
def handle_exceptions(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error": exc.detail,
        },
        status_code=exc.status_code,
    )
