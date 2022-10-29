from typing import IO, DefaultDict
from bs4 import BeautifulSoup as bs
import re
from collections import defaultdict
import logging


LIST_CLASS: str = "css-qmttav"
PARA_CLASS: str = "cds-137 css-1j071wf cds-139"
ALLOWED_TYPES: tuple = ("txt", "html")
DEFAULT_SUFFIX: str = "EditDelete"
DEFAULT_PREFIX: str = "Go to video"
ADDED_NOTES_HEADER: str = "Your Notes"
MY_REGEX: str = "\d:\d\d"


def remove(input_text: str, to_remove=ADDED_NOTES_HEADER) -> str:
    return "".join(re.split(to_remove, input_text))


def note_from_source(input_text: str):
    result_list = re.split(MY_REGEX, input_text)

    video_name = result_list[0]
    unmodified_note = result_list.pop()

    if ADDED_NOTES_HEADER in unmodified_note:
        modified_note = remove(unmodified_note)
        return [video_name, modified_note]

    return [video_name, unmodified_note]


def file_handler(filename, mode="r"):
    try:
        is_valid = any(filter(lambda x: filename.endswith(x), ALLOWED_TYPES))
        if is_valid:
            file = open(filename, mode)
            return file
        else:
            raise Exception("Unsupported input data type.")
    except OSError as e:
        logging.warning(str(e))
        raise Exception(
            "Something is not right with your file. Make sure filename is correct and file location to be as same as downloader file."
        )


def merge_dict(result: list[str]) -> DefaultDict[str, list]:
    d = defaultdict(list)
    for k, v in result:
        d[k].append(v)
    return d


def extract_notes(target_file: IO) -> list[str]:
    result = []
    soup = bs(target_file, "html.parser")
    li = soup.find_all("li", {"class": LIST_CLASS})
    for i in li:

        stripped = i.text.lstrip(DEFAULT_PREFIX).rstrip(DEFAULT_SUFFIX)
        x = note_from_source(stripped)

        result.append(x)
    if not result:
        raise Exception("Unsupported input data type.")

    return result


def write_output(output_file: IO, notes: DefaultDict[str, list]):
    for k, v in notes.items():
        output_file.write("Video - " + k + "\n\n")
        for index, val in enumerate(v, start=1):
            output_file.write(str(index) + " - " + val + "\n")
        output_file.write("\n-------\n")


def input_processing(input: str) -> DefaultDict[str, list]:
    notes = extract_notes(input)
    return merge_dict(notes)


def output_processing(
    notes: DefaultDict[str, list],
    output_name: str,
) -> None:
    output = file_handler(output_name, mode="w")
    write_output(output, notes)
    output.close()


def get_notes(
    ipnut_string: str,
    output_name: str = "result.txt",
):
    notes: DefaultDict[str, list] = input_processing(input=ipnut_string)
    output_processing(notes, output_name)
