import csv
from typing import Tuple


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
    days = []
    times = []

    for _, course_details in sections.items():
        day = course_details["day"]
        time = course_details["time"]

        days.append(day)
        times.append(time)

    days = list(set(days))
    times = list(set(times))

    return days, times


def get_section_schedule(courses_set: dict, course_class_id: str) -> Tuple[str, str]:
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


def get_section_by_time(courses: dict, time: str) -> set:
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


def get_section_by_day(courses: dict, day: str) -> set:
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

def save_results_to_csv(data: list, filename: str) -> None:
    with open(filename, "w") as file:
        spamwriter = csv.writer(file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for line in data:
            spamwriter.writerow(line)

def treat_and_save_results(timeschedule: list, courses: dict):
    timeschedule_treated = []
    cap_diff = []

    for schedule in timeschedule:
        
        if "CapDiff" in schedule:
            cap_diff.append(schedule)
        else:

            schedule, value = schedule.split("/")
            allocation = schedule.split("_")
            classroom_name = allocation[0]
            course_class_id = int(allocation[1])

            professor = courses[course_class_id]["professor"]
            course_id = courses[course_class_id]["course_id"]
            course_name = courses[course_class_id]["course_name"]

            day = allocation[2]
            time = allocation[3]

            result = [classroom_name, professor, course_id, course_name, day, time]

            timeschedule_treated.append(result)

    save_results_to_csv(timeschedule_treated, "classroom_assignment/results/assignment.csv")
    save_results_to_csv(cap_diff, "classroom_assignment/results/cap_diff.csv")
    
    return timeschedule_treated, cap_diff
