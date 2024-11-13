import gurobipy as gp
from gurobipy import GRB

import settings

from utils import utils
from database.construct_sets import (
    get_courses_set,
    get_manual_allocation_set,
    get_professors_set,
)


DEFAULT_COEFFICIENT = 1
RESPONSIBLE_INSTITUTE_COEFFICIENT = 10

ZERO_COEFFICIENT = 0
WEIGHT_FACTOR_C = 1000


class ClassroomAssignment:
    def __init__(
        self,
        classrooms,
        sections,
        professors,
    ):
        self.classrroms = classrooms
        self.sections = sections
        self.classrooms = professors
        self.coefficients = {}
        self.variables = {}
        self.slack_variables = {}

        self.env = self.init_environment()
        self.model = gp.Model(name="ClassroomAssignment", env=self.env)

    def init_environment(self):
        env = gp.Env(empty=True)
        env.setParam("LicenseID", settings.APP_LICENSE_ID)
        env.setParam("WLSAccessID", settings.APP_WLS_ACCESS_ID)
        env.setParam("WLSSecret", settings.APP_WS_SECRET)
        env.start()

        return env

    def set_courses(self, courses):
        self.sections = courses

    def initialize_variables_and_coefficients(self):
        for classroom in self.classrooms:
            self.coefficients[classroom] = {}
            self.variables[classroom] = {}

            for section in self.sections.keys():
                self.coefficients[classroom][section] = {}
                self.variables[classroom][section] = {}

                workload = utils.get_course_schedule(self.sections, section)
                day, time = workload

                self.coefficients[classroom][section][day] = {}

                if (
                    self.sections[section]["classroom_type"]
                    == self.classrooms[classroom]["classroom_type"]
                    and self.sections[section]["responsable_institute"]
                    == self.classrooms[classroom]["responsable_institute"]
                ):
                    self.coefficients[classroom][section][day][
                        time
                    ] = RESPONSIBLE_INSTITUTE_COEFFICIENT
                elif (
                    self.sections[section]["classroom_type"]
                    == self.classrooms[classroom]["classroom_type"]
                ):
                    self.coefficients[classroom][section][day][
                        time
                    ] = DEFAULT_COEFFICIENT
                else:
                    self.coefficients[classroom][section][day][time] = ZERO_COEFFICIENT

                self.variables[classroom][section][day] = {}
                self.variables[classroom][section][day][time] = self.model.addVar(
                    vtype=GRB.BINARY, name=f"{classroom}_{section}_{day}_{time}"
                )

    def add_credit_slack_variables(self):
        for professor in self.permanent_professors:
            self.slack_variables[professor] = self.model.addVar(
                vtype=GRB.INTEGER, name=f"PNC_{professor}"
            )

    def add_constraints(self):
        course_days, course_times = utils.get_possible_schedules(self.sections)

        # Manual
        # RH1: Alocar manualmente os professores
        for course_class_id in self.manual_allocation.keys():
            professor = self.manual_allocation[course_class_id]["professor"]
            day = self.manual_allocation[course_class_id]["day"]
            time = self.manual_allocation[course_class_id]["time"]

            self.model.addConstr(
                self.variables[professor][course_class_id][day][time] == 1
            )

        # Soft constraints
        # RF1: Garante que o professor seja alocado com a quantidade de créditos sujerida pela coordenação se possível. Não inviabiliza o modelo caso não seja atingido.
        for professor in self.permanent_professors:
            self.model.addConstr(
                gp.quicksum(
                    self.variables[professor][course][
                        utils.get_course_schedule(self.sections, course)[0]
                    ][utils.get_course_schedule(self.sections, course)[1]]
                    * self.sections[course]["credits"]
                    for course in self.sections.keys()
                )
                == MIN_CREDITS_PERMANENT - self.slack_variables[professor]
            )

        # Hard constraints
        # RH1: Um sala poderá ser alocada para no máximo 1 uma turma em um mesmo dia e horário (binário)
        for professor in self.classrooms:
            if professor == DUMMY_PROFESSOR:
                continue
            for i in range(len(course_days)):
                day = course_days[i]
                time = course_times[i]
                day_courses = utils.get_courses_by_day(self.sections, day)
                time_courses = utils.get_courses_by_time(self.sections, time)
                common_courses = day_courses.intersection(time_courses)
                self.model.addConstr(
                    gp.quicksum(
                        self.variables[professor][course][
                            utils.get_course_schedule(self.sections, course)[0]
                        ][utils.get_course_schedule(self.sections, course)[1]]
                        for course in common_courses
                    )
                    <= 1
                )

    def set_objective(self):
        self.model.setObjective(
            gp.quicksum(
                self.variables[professor][course][day][time]
                * self.coefficients[professor][course][day][time]
                for professor in self.classrooms
                for course in self.sections.keys()
                for day, time in [utils.get_course_schedule(self.sections, course)]
            )
            - gp.quicksum(
                WEIGHT_FACTOR_C * self.slack_variables[professor]
                for professor in self.permanent_professors
            ),
            GRB.MAXIMIZE,
        )

    def optimize(self):
        self.model.update()
        self.model.optimize()

    def generate_results(self):

        professor_timeschedule = []
        for var in self.model.getVars():
            if var.X > 0:
                timeschedule = f"{var.VarName}/{var.X}"
                professor_timeschedule.append(timeschedule)

        model_value = self.model.ObjVal
        print("========= RESULT ==========")
        for r in professor_timeschedule:
            print(r)
        print("=============================")
        print(f"Obj: {model_value}")

        # Clean up model and environment
        self.model.dispose()
        self.env.dispose()

        return professor_timeschedule, model_value


def main():
    MANUAL_ALLOCATION = get_manual_allocation_set()

    professors_permanent_set, professors_substitute_set, professor_dummy = (
        get_professors_set()
    )
    professors_set = (
        professors_permanent_set | professors_substitute_set | professor_dummy
    )
    PROFESSORS = professors_set
    PERMANENT_PROFESSORS = professors_permanent_set
    SUBSTITUTE_PROFESSORS = professors_substitute_set

    COURSES = get_courses_set(MANUAL_ALLOCATION)

    timetabling = ClassroomAssignment(
        PROFESSORS,
        PERMANENT_PROFESSORS,
        SUBSTITUTE_PROFESSORS,
        COURSES,
        MANUAL_ALLOCATION,
    )
    timetabling.initialize_variables_and_coefficients()
    timetabling.add_credit_slack_variables()
    timetabling.add_constraints()
    timetabling.set_objective()
    timetabling.optimize()
    timetabling.generate_results()


if __name__ == "__main__":
    main()
