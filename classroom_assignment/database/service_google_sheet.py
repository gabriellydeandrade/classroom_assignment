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


@cache_to_csv("cache/get_section_allocation.csv", refresh_time=settings.APP_CACHE_TTL)
def get_secion_allocation():
    page_name = "alocacao!A:J"

    df = read_google_sheet_to_dataframe(settings.SAMPLE_SPREADSHEET_ID, page_name)

    df.rename(
        columns={
            "Instituto responsável": "responsable_institute",
            "Nome curto professor": "professor",
            "Código disciplina": "course_id",
            "Nome disciplina": "course_name",
            "Dia da semana": "day",
            "Horário": "time",
            "Qtd alunos": "capacity",
            "Tipo sala": "classroom_type",
        },
        inplace=True,
    )

    return df


@cache_to_csv("cache/get_classrooms_available.csv", refresh_time=settings.APP_CACHE_TTL)
def get_classrooms_available():
    page_name = "salas!A:L"

    df = read_google_sheet_to_dataframe(settings.SAMPLE_SPREADSHEET_ID, page_name)

    classrooms = df.loc[df["Disponível"] == "TRUE"].filter(
        [
            "Nome",
            "Instituto responsável",
            "Tipo sala",
            "Capacidade SIGA",
            "Capacidade real"
        ]
    )
    classrooms.rename(
        columns={
            "Nome": "classroom_name",
            "Instituto responsável": "responsable_institute",
            "Tipo sala": "classroom_type",
            "Capacidade SIGA": "capacity_siga",
            "Capacidade real": "capacity",
        },
        inplace=True,
    )
    classrooms.set_index("classroom_name", inplace=True)

    return classrooms


