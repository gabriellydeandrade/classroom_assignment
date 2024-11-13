from typing import Tuple


def get_qualified_courses_for_professor(
    courses_set: dict, professors_set: dict, professor: str
) -> set:
    """
    Verifies if the professor is qualified to teach the discipline.
    Returns a set with the disciplines they can teach.

    Args:
        professors_set (dict): A dictionary containing professor information.
        professor (str): The name or identifier of the professor.

    Returns:
        set: A set of disciplines the professor is qualified to teach.
    """
    qualified_course_class_id = []

    if professor == "DUMMY":
        # In the case of a DUMMY professor, they can teach any discipline from all areas
        qualified_course_class_id = list(courses_set.keys())
    else:
        try:
            qualified_courses = professors_set[professor]["qualified_courses"]
        except KeyError:
            print(f"Professor {professor} not found in the list of discipline profiles")
            return set()

        for course_class_id in courses_set.keys():
            if courses_set[course_class_id]["course_id"] in qualified_courses:
                qualified_course_class_id.append(course_class_id)

    return set(qualified_course_class_id)


def get_possible_schedules(courses: dict) -> Tuple[list, list]:
    """
    Extracts and returns the unique days and times from a dictionary of courses.
    Args:
        courses (dict): A dictionary where the keys are course identifiers and the values are dictionaries
                        containing course details, specifically 'day' and 'time'.
    Returns:
        tuple: A tuple containing two lists:
            - days (list): A list of unique days on which the courses are scheduled.
            - time (list): A list of unique times at which the courses are scheduled.
    """
    days = []
    times = []

    for _, course_details in courses.items():
        day = course_details["day"]
        time = course_details["time"]

        days.append(day)
        times.append(time)

    days = list(set(days))
    times = list(set(times))

    return days, times


def get_course_schedule(courses_set: dict, course_class_id: str) -> Tuple[str, str]:
    """
    Retrieve the schedule for a specific course class.

    Args:
        courses_set (dict): A dictionary containing course information.
        course_class_id (str): The ID of the course class to retrieve the schedule for.

    Returns:
        tuple: A tuple containing the day and time of the course class.
    """

    day = courses_set[course_class_id]["day"]
    time = courses_set[course_class_id]["time"]

    return (day, time)


def get_all_course_class_id(courses: dict) -> set:
    result = set([d for d in courses.keys() if courses[d]["course_type"] != "SVC"])
    return result


def get_all_elective_courses_with_professor_qualified(courses: dict, professors: dict):
    result = set()
    for course_class_id, details in courses.items():
        if details["course_type"] == "OPT":
            for professor in professors.keys():
                if details["course_id"] in professors[professor]["qualified_courses"]:
                    result.add(course_class_id)
    return result


def get_all_available_courses_for_allocation(
    required_courses: dict, elective_courses: dict, professors: dict
):
    elective_available_courses = get_all_elective_courses_with_professor_qualified(
        elective_courses, professors
    )

    available_courses = dict()

    for course in elective_courses:
        if course in elective_available_courses:
            available_courses[course] = elective_courses[course].copy()
            if "day" not in available_courses[course]:
                available_courses[course]["day"] = "NÃO DEFINIDO"
            if "time" not in available_courses[course]:
                available_courses[course]["time"] = "NÃO DEFINIDO"

    available_courses.update(required_courses)

    return available_courses


def remove_courses(courses: set, manual_courses: dict) -> set:
    """
    Removes courses that are manually specified from the set of available courses.

    Args:
        courses (set): A set of course IDs representing all available courses.
        manual_courses (dict): A dictionary where keys are course IDs that should be removed from the available courses.

    Returns:
        set: A set of course IDs representing the available courses after removing the manually specified courses.
    """

    courses_available = courses.copy()

    for course_id in manual_courses.keys():
        courses_available.remove(course_id)

    return courses_available


def add_manual_allocation_courses(
    professor: str, courses: set, manual_courses: dict
) -> set:
    """
    Adds courses that are manually specified to the set of available courses.

    Args:
        courses (set): A set of course IDs representing all available courses.
        manual_courses (dict): A dictionary where keys are course IDs that should be added to the available courses.

    Returns:
        set: A set of course IDs representing the available courses after adding the manually specified courses.
    """

    courses_available = courses.copy()

    for course_id in manual_courses.keys():
        if professor == manual_courses[course_id]["professor"]:
            courses_available.add(course_id)

    return courses_available


def get_courses_by_time(courses: dict, time: str) -> set:
    """
    Returns a set of courses that have classes at the specified time.

    Args:
        courses (dict): Dictionary containing course details.
        time (str): The time to filter courses by.

    Returns:
        set: A set of courses that have classes at the specified time.
    """

    result = []

    for course_id, details in courses.items():
        if type(details["time"]) == str:
            for course_time in details["time"].split(","):
                if course_time == time:
                    result.append(course_id)

    return set(result)


def get_courses_by_day(courses: dict, day: str) -> set:
    """
    Returns a set of courses that have classes on the specified day.

    Args:
        courses (dict): Dictionary containing course details.
        day (str): The day to filter courses by.

    Returns:
        set: A set of courses that have classes on the specified day.
    """
    result = []

    for course_id, details in courses.items():
        if type(details["day"]) == str:
            for course_day in details["day"].split(","):
                if course_day == day:
                    result.append(course_id)

    return set(result)
