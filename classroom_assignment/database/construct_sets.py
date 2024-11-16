from database.service_google_sheet import (
    get_classrooms_available,
    get_secion_allocation,
)
from database.transform_data import (
    transform_to_dict,
)


def get_sections_set() -> dict[str, dict]:
    """
    Retrieves a set of required courses and transforms them into a dictionary format.

    Returns:
        dict: A dictionary containing the transformed required courses.
    """
    sections = get_secion_allocation()
    sections_set = transform_to_dict(sections)

    return sections_set


def get_classrooms_set():
    """
    Retrieves a set of elective courses and transforms them into a dictionary format.
    Obs.: Do not contain a time schedule due to the nature of elective courses.

    Returns:
        dict: A dictionary containing the elective courses.
    """
    classrooms = get_classrooms_available()
    classrooms_set = transform_to_dict(classrooms)

    return classrooms_set
