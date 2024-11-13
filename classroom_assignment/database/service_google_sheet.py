# https://developers.google.com/sheets/api/quickstart/python

import os.path
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from cache_pandas import cache_to_csv

import settings

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def read_google_sheet_to_dataframe(spreadsheet_id, range_name):
    """Reads data from a Google Sheet and returns it as a pandas DataFrame."""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        sheet = service.spreadsheets()
        result = (
            sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return pd.DataFrame()

        df = pd.DataFrame(values[1:], columns=values[0])
        return df

    except HttpError as err:
        print(err)
        return pd.DataFrame()


@cache_to_csv("cache/get_required_courses.csv", refresh_time=settings.APP_CACHE_TTL)
def get_required_courses() -> pd.DataFrame:
    page_name = "disciplinas_obrigatorias!A:Q"
    df = read_google_sheet_to_dataframe(settings.SAMPLE_SPREADSHEET_ID, page_name)

    courses = df.loc[df["Alocar"] == "TRUE"].filter(
        [
            "Código único turma",
            "Código disciplina",
            "Qtd de créditos",
            "Dia da semana",
            "Horário",
            "Tipo disciplina",
        ]
    )
    courses.rename(
        columns={
            "Código único turma": "course_class_id",
            "Código disciplina": "course_id",
            "Qtd de créditos": "credits",
            "Dia da semana": "day",
            "Horário": "time",
            "Tipo disciplina": "course_type",
        },
        inplace=True,
    )
    courses.set_index("course_class_id", inplace=True)

    return courses


@cache_to_csv("cache/get_elective_courses.csv", refresh_time=settings.APP_CACHE_TTL)
def get_elective_courses():
    page_name = "disciplinas_eletivas!A:K"
    df = read_google_sheet_to_dataframe(settings.SAMPLE_SPREADSHEET_ID, page_name)

    courses = df.loc[df["Alocar"] == "TRUE"].filter(
        [
            "Código único turma",
            "Código disciplina",
            "Qtd de créditos",
            "Perfil",
            "Tipo disciplina",
            "Tipo turma",
        ]
    )
    courses.rename(
        columns={
            "Código único turma": "course_class_id",
            "Código disciplina": "course_id",
            "Qtd de créditos": "credits",
            "Perfil": "knowledge_area",
            "Tipo disciplina": "course_type",
            "Tipo turma": "class_type",
        },
        inplace=True,
    )
    courses.set_index("course_class_id", inplace=True)

    return courses


@cache_to_csv("cache/get_substitute_professor.csv", refresh_time=settings.APP_CACHE_TTL)
def get_substitute_professor():
    page_name = "professores!A:K"
    df = read_google_sheet_to_dataframe(settings.SAMPLE_SPREADSHEET_ID, page_name)

    professors_availables = df.loc[df["Alocar"] == "TRUE"].filter(
        ["Nome curto", "Disciplinas aptas", "Área de conhecimento", "Categoria"]
    )
    professors_availables.rename(
        columns={
            "Nome curto": "professor",
            "Disciplinas aptas": "qualified_courses",
            "Área de conhecimento": "expertise",
            "Categoria": "category",
        },
        inplace=True,
    )
    professors_availables.set_index("professor", inplace=True)

    substitute = professors_availables.loc[(professors_availables["category"] == "PS")]

    return substitute


@cache_to_csv("cache/get_permanent_professors.csv", refresh_time=settings.APP_CACHE_TTL)
def get_permanent_professors():
    page_name = "professores!A:K"
    df = read_google_sheet_to_dataframe(settings.SAMPLE_SPREADSHEET_ID, page_name)

    professors_availables = df.loc[df["Alocar"] == "TRUE"].filter(
        ["Nome curto", "Disciplinas aptas", "Área de conhecimento", "Categoria"]
    )
    professors_availables.rename(
        columns={
            "Nome curto": "professor",
            "Disciplinas aptas": "qualified_courses",
            "Área de conhecimento": "expertise",
            "Categoria": "category",
        },
        inplace=True,
    )
    professors_availables.set_index("professor", inplace=True)

    permanent = professors_availables.loc[
        (~professors_availables["category"].isin(["PS", "EX", "AP"]))
    ]

    return permanent


def get_professors():
    return get_permanent_professors(), get_substitute_professor()


@cache_to_csv("cache/get_manual_allocation.csv", refresh_time=settings.APP_CACHE_TTL)
def get_manual_allocation():
    page_name = "alocacao_manual!A:I"

    df = read_google_sheet_to_dataframe(settings.SAMPLE_SPREADSHEET_ID, page_name)

    manual_allocation = df.filter(
        [
            "Nome curto professor",
            "Código único turma",
            "Código disciplina",
            "Qtd de créditos",
            "Tipo disciplina",
            "Dia da semana",
            "Horário",
        ]
    )
    manual_allocation.rename(
        columns={
            "Nome curto professor": "professor",
            "Código único turma": "course_class_id",
            "Código disciplina": "course_id",
            "Qtd de créditos": "credits",
            "Tipo disciplina": "course_type",
            "Dia da semana": "day",
            "Horário": "time",
        },
        inplace=True,
    )
    manual_allocation.set_index("course_class_id", inplace=True)

    return manual_allocation
