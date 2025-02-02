import csv
from typing import Tuple


def is_blackboard(classroom: dict) -> bool:
    board_type = classroom["board_type"]
    if board_type:
        if "giz" in board_type.lower():
            return True
    return False


def get_courses_by_exact_day_and_time(courses: dict, day: str, time: str) -> set:

    result = []

    for course_id, details in courses.items():
        days = details["day"].split(",")
        times = details["time"].split(",")

        # Repete o horário para os dias no caso de agendamento de mesma hora. Ex.: SEG,QUA 10h às 12h
        if len(times) < len(days):
            times = [times[0]] * len(days)

        for i, course_day in enumerate(days):
            if course_day == day:
                for j, course_time in enumerate(times):
                    if i == j and course_time == time:
                        result.append(course_id)

    return set(result)


def get_possible_schedules(sections: dict) -> Tuple[list, list]:
    """
    Extracts and returns the unique days and times from a dictionary of sections.
    Args:
        sections (dict): A dictionary where the keys are course identifiers and the values are dictionaries
                        containing course details, specifically 'day' and 'time'.
    Returns:
        tuple: A tuple containing two lists:
            - days (list): A list of unique days on which the sections are scheduled.
            - time (list): A list of unique times at which the sections are scheduled.
    """

    unique_schedules = set()

    for _, course_details in sections.items():
        day = course_details["day"]
        time = course_details["time"]
        unique_schedules.add((day, time))

    days = list(day for day, _ in unique_schedules)
    times = list(time for _, time in unique_schedules)

    return days, times


def get_possible_schedules_v2(sections: dict) -> Tuple[list, list]:
    """
    Extracts and returns the unique days and times from a dictionary of sections.
    Args:
        sections (dict): A dictionary where the keys are course identifiers and the values are dictionaries
                        containing course details, specifically 'day' and 'time'.
    Returns:
        tuple: A tuple containing two lists:
            - days (list): A list of unique days on which the sections are scheduled.
            - time (list): A list of unique times at which the sections are scheduled.
    """

    unique_schedules = set()

    for _, course_details in sections.items():
        day_original = course_details["day"]
        time_original = course_details["time"]

        days = day_original.split(",") if day_original else []
        times = time_original.split(",") if time_original else []

        # Repete o horário para os dias no caso de agendamento de mesma hora. Ex.: SEG,QUA 10h às 12h
        if len(times) < len(days):
            times = [times[0]] * len(days)

        for day, time in zip(days, times):
            unique_schedules.add((day, time))

    days = []
    times = []
    for day, time in unique_schedules:
        days.append(day)
        times.append(time)

    return days, times


def get_section_schedule(courses_set: dict, course_class_id: str) -> Tuple[list, list]:
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

    days = day.split(",") if day else []
    times = time.split(",") if time else []

    if len(times) < len(days):
        times = [times[0]] * len(days)

    return (days, times)


def save_results_to_csv(data: list, filename: str) -> None:
    with open(filename, "w") as file:
        spamwriter = csv.writer(
            file, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        for line in data:
            spamwriter.writerow(line)


def treat_and_save_results(timeschedule: list, courses: dict):
    timeschedule_treated = []
    cap_diff = []
    pnc = []

    for schedule in timeschedule:

        if "CapDiff" in schedule:
            cap_diff.append([schedule])
        elif "PNC" in schedule:
            pnc.append([schedule])
        else:

            schedule, _ = schedule.split("#")
            allocation = schedule.split("_")
            classroom_name = allocation[0]
            course_class_id = int(allocation[1])

            professor = courses[course_class_id]["professor"]
            graduation_course = courses[course_class_id]["graduation_course"]
            course_id = courses[course_class_id]["course_id"]
            course_name = courses[course_class_id]["course_name"]
            term = courses[course_class_id]["term"]

            day = allocation[2]
            time = allocation[3]

            result = [
                classroom_name,
                professor,
                graduation_course,
                course_id,
                course_name,
                term,
                day,
                time,
            ]

            timeschedule_treated.append(result)

    save_results_to_csv(
        timeschedule_treated, "classroom_assignment/results/assignment.csv"
    )
    save_results_to_csv(cap_diff, "classroom_assignment/results/cap_diff.csv")
    save_results_to_csv(pnc, "classroom_assignment/results/pnc.csv")

    return timeschedule_treated, cap_diff
