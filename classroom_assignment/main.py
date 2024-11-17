import gurobipy as gp
from gurobipy import GRB

import settings

from utils import utils
from database.construct_sets import (
    get_classrooms_set,
    get_sections_set,
)


DEFAULT_COEFFICIENT = 1
RESPONSIBLE_INSTITUTE_COEFFICIENT = 10
ZERO_COEFFICIENT = 0
WEIGHT_FACTOR_C = 1000


class ClassroomAssignment:
    def __init__(self, classrooms, sections):
        self.classrooms = classrooms
        self.sections = sections
        self.coefficients = {}
        self.variables = {}
        self.slack_variables = {}
        self.slack_variables_capacity_diff = {}

        self.env = self.init_environment()
        self.model = gp.Model(name="ClassroomAssignment", env=self.env)

    def init_environment(self):
        env = gp.Env(empty=True)
        env.setParam("LicenseID", settings.APP_LICENSE_ID)
        env.setParam("WLSAccessID", settings.APP_WLS_ACCESS_ID)
        env.setParam("WLSSecret", settings.APP_WS_SECRET)
        env.start()

        return env

    def initialize_variables_and_coefficients(self):
        for classroom in self.classrooms:
            self.coefficients[classroom] = {}
            self.variables[classroom] = {}

            for section in self.sections.keys():
                self.coefficients[classroom][section] = {}
                self.variables[classroom][section] = {}

                workload = utils.get_section_schedule(self.sections, section)
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

    def add_capacity_slack_variables(self):
        for classroom in self.classrooms:
            self.slack_variables[classroom] = self.model.addVar(
                vtype=GRB.INTEGER, name=f"PNC_{classroom}"
            )

            self.slack_variables_capacity_diff[classroom] = {}

            for section in self.sections:
                self.slack_variables_capacity_diff[classroom][section] = (
                    self.model.addVar(
                        vtype=GRB.INTEGER, name=f"CapDiff_{classroom}_{section}"
                    )
                )

    def add_constraints(self):
        sections_days, sections_times = utils.get_possible_schedules(self.sections)

        # Soft constraints
        # RF1: Garante que a sala seja alocada mesmo se exceder a capacidade da sala. Não inviabiliza o modelo.
        for classroom in self.classrooms:
            self.model.addConstr(
                gp.quicksum(
                    self.variables[classroom][section][
                        utils.get_section_schedule(self.sections, section)[0]
                    ][utils.get_section_schedule(self.sections, section)[1]]
                    * self.sections[section]["capacity"]
                    for section in self.sections.keys()
                )
                <= self.classrooms[classroom]["capacity"]
                + self.slack_variables[classroom]
            )

            # RF2: Garante que a sala seja alocada com a menor capacidade possível

            for section in self.sections:
                workload = utils.get_section_schedule(self.sections, section)
                day, time = workload


                self.model.addConstr(
                    self.slack_variables_capacity_diff[classroom][section]
                    == self.classrooms[classroom]["capacity"]
                    - self.variables[classroom][section][
                        utils.get_section_schedule(self.sections, section)[0]
                    ][utils.get_section_schedule(self.sections, section)[1]]
                    * self.sections[section]["capacity"]
                )

        # Hard constraints
        # RN1: Um sala poderá ser alocada para no máximo 1 uma turma em um mesmo dia e horário (binário)
        for classroom in self.classrooms:
            for i in range(len(sections_days)):
                day = sections_days[i]
                time = sections_times[i]
                day_sections = utils.get_section_by_day(self.sections, day)
                time_sections = utils.get_section_by_time(self.sections, time)

                common_sections = day_sections.intersection(time_sections)
                self.model.addConstr(
                    gp.quicksum(
                        self.variables[classroom][section][
                            utils.get_section_schedule(self.sections, section)[0]
                        ][utils.get_section_schedule(self.sections, section)[1]]
                        for section in common_sections
                    )
                    <= 1
                )

        # RN2: Uma seção deverá ter somente uma sala de aula
        for section in self.sections.keys():
            workload = utils.get_section_schedule(self.sections, section)
            day, time = workload
            self.model.addConstr(
                gp.quicksum(
                    self.variables[classroom][section][day][time]
                    for classroom in self.classrooms
                )
                == 1
            )

    def set_objective(self):
        self.model.setObjective(
            gp.quicksum(
                self.variables[classroom][section][day][time]
                * self.coefficients[classroom][section][day][time]
                for classroom in self.classrooms
                for section in self.sections.keys()
                for day, time in [utils.get_section_schedule(self.sections, section)]
            )
            - gp.quicksum(
                WEIGHT_FACTOR_C * self.slack_variables[classroom]
                for classroom in self.classrooms
            )
            - gp.quicksum(
                self.slack_variables_capacity_diff[classroom][section]
                for classroom in self.classrooms
                for section in self.sections
            ),
            GRB.MAXIMIZE,
        )

    def optimize(self):
        self.model.update()
        self.model.optimize()

    def generate_results(self):

        classroom_assignement = []
        for var in self.model.getVars():
            if var.X > 0:
                timeschedule = f"{var.VarName}/{var.X}"
                classroom_assignement.append(timeschedule)

        model_value = self.model.ObjVal
        print("========= RESULT ==========")
        for r in classroom_assignement:
            print(r)
        print("=============================")
        print(f"Obj: {model_value}")

        # Clean up model and environment
        self.model.dispose()
        self.env.dispose()

        return classroom_assignement, model_value


def main():
    CLASSROOMS = get_classrooms_set()

    COURSES = get_sections_set()

    timetabling = ClassroomAssignment(CLASSROOMS, COURSES)
    timetabling.initialize_variables_and_coefficients()
    timetabling.add_capacity_slack_variables()
    timetabling.add_constraints()
    timetabling.set_objective()
    timetabling.optimize()
    timetabling.generate_results()


if __name__ == "__main__":
    main()
