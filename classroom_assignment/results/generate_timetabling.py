import streamlit as st
import pandas as pd

df = pd.read_csv(
    "classroom_assignment/results/assignment.csv",
    delimiter=";",
    names=[
        "classroom_name",
        "professor",
        "graduation_course",
        "course_id",
        "course_name",
        "term",
        "day",
        "time"
    ],
)


st.set_page_config(
    layout="wide",
)

st.title("Classroom Assignment - Resultados")
st.header("Alocação final de salas", divider="rainbow")

with st.container(border=True) as general:

    st.subheader("Visão geral")

    st.dataframe(
        df,
        column_config={
            "classroom_name": "Sala",
            "graduation_course": "Curso",
            "professor": "Docente",
            "course_id": "Código disciplina",
            "course_name": "Nome disciplina",
            "term": "Período",
            "day": st.column_config.ListColumn(
                "Dia da Semana",
                help="Dia da semana que a disciplina é ministrada",
                width="medium",
            ),
            "time": st.column_config.ListColumn(
                "Horário",
                help="Horário que a disciplina é ministrada",
                width="medium",
            ),
        },
        hide_index=True,
        use_container_width=False,
    )

