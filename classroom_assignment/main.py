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

                days, times = utils.get_section_schedule(self.sections, section)

                for day, time in zip(days, times):

                    self.coefficients[classroom][section][day] = {}

                    if (
                        self.classrooms[classroom]["classroom_type"]
                        and self.classrooms[classroom]["classroom_type"]
                        in self.sections[section]["classroom_type"]
                        and self.sections[section]["responsable_institute"]
                        == self.classrooms[classroom]["responsable_institute"]
                    ):
                        self.coefficients[classroom][section][day][
                            time
                        ] = RESPONSIBLE_INSTITUTE_COEFFICIENT
                    elif (
                        self.classrooms[classroom]["classroom_type"]
                        and self.classrooms[classroom]["classroom_type"]
                        in self.sections[section]["classroom_type"]
                    ):
                        self.coefficients[classroom][section][day][
                            time
                        ] = DEFAULT_COEFFICIENT
                    else:
                        self.coefficients[classroom][section][day][
                            time
                        ] = ZERO_COEFFICIENT

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
                    self.variables[classroom][section][day][time]
                    * self.sections[section]["capacity"]
                    for section in self.sections.keys()
                    for day, time in zip(
                        utils.get_section_schedule(self.sections, section)[0],
                        utils.get_section_schedule(self.sections, section)[1],
                    )
                )
                <= self.classrooms[classroom]["capacity"]
                + self.slack_variables[classroom]
            )

            # RF2: Garante que a sala seja alocada com a menor capacidade possível

            for section in self.sections:
                days, times = utils.get_section_schedule(self.sections, section)
                for day, time in zip(days, times):
                    self.model.addConstr(
                        self.slack_variables_capacity_diff[classroom][section]
                        == self.classrooms[classroom]["capacity"]
                        - self.variables[classroom][section][day][time]
                        * self.sections[section]["capacity"]
                    )

        # Hard constraints
        for classroom in self.classrooms:

            # RN1: Um sala poderá ser alocada para no máximo 1 uma turma em um mesmo dia e horário (binário)
            for i in range(len(sections_days)):
                day = sections_days[i]
                time = sections_times[i]
                day_sections = utils.get_section_by_day(self.sections, day)
                time_sections = utils.get_section_by_time(self.sections, time)

                common_sections = day_sections.intersection(time_sections)
                self.model.addConstr(
                    gp.quicksum(
                        self.variables[classroom][section][day][time]
                        for section in common_sections
                        for day, time in zip(
                            utils.get_section_schedule(self.sections, section)[0],
                            utils.get_section_schedule(self.sections, section)[1],
                        )
                    )
                    <= 1
                )

        for section in self.sections.keys():
            days, times = utils.get_section_schedule(self.sections, section)
            for day, time in zip(days, times):
                # RN2: Uma seção deverá ter somente uma sala de aula
                self.model.addConstr(
                    gp.quicksum(
                        self.variables[classroom][section][day][time]
                        for classroom in self.classrooms
                    )
                    == 1
                )

                # RN3: Caso a disciplina seja do primeiro período, uma sala específica deverá ser ocupada para as aulas teóricas (F3014)
                # if (
                #     self.sections[section]["term"] == 1
                #     and self.sections[section]["class_type"] == "Calouro"
                # ):
                #     classroom = "F3014"
                #     # TODO considerar que eu posso ter um OU. Ou aloca em um horário/tempo ou em outro
                #     self.model.addConstr(
                #         self.variables[classroom][section][day][time] == 1
                #     )

        # RN4: O tipo de sala deverá ser o mesmo requerido na alocação da disciplina

        for section in self.sections:
            days, times = utils.get_section_schedule(self.sections, section)
            classroom_types = self.sections[section]["classroom_type"].split(",")

            if len(classroom_types) > 1:

                # Garante que seja alocada a quantidade de sala de um tipo determinado solicitada na alocação
                for i in range(len(classroom_types)):
                    if (
                        self.classrooms[classroom]["classroom_type"]
                        == classroom_types[i]
                    ):
                        self.model.addConstr(
                            gp.quicksum(
                                self.variables[classroom][section][days[j]][times[j]]
                                for classroom in self.classrooms
                                for j in range(len(days))
                                if self.classrooms[classroom]["classroom_type"]
                                == classroom_types[i]
                            )
                            == sum(
                                [1 for x in classroom_types if x == classroom_types[i]]
                            )
                        )

                # TODO: avaliar necessidade e remover se for o caso
                # Garante que não seja alocada mais de uma sala de um tipo determinado solicitada na alocação
                # for classroom in self.classrooms:
                #     if self.classrooms[classroom]["classroom_type"] in classroom_types:
                #         self.model.addConstr(
                #             gp.quicksum(
                #                 self.variables[classroom][section][days[i]][times[i]]
                #                 for i in range(len(days))
                #             )
                #             <= 1
                #         )

                if (
                    self.sections[section]["term"] == 1
                    and self.sections[section]["class_type"] == "Calouro"
                ):
                    classroom_new_students = "F3014"
                    self.model.addConstr(
                        gp.quicksum(
                            self.variables[classroom_new_students][section][days[i]][
                                times[i]
                            ]
                            for i in range(len(days))
                        )
                        == sum(
                            [
                                1
                                for x in classroom_types
                                if x
                                == self.classrooms[classroom_new_students][
                                    "classroom_type"
                                ]
                            ]
                        )
                    )
            else:
                if (
                    self.sections[section]["term"] == 1
                    and self.sections[section]["class_type"] == "Calouro"
                ):
                    # FIXME: não está funcionando e está inviabilizando o modelo
                    classroom_new_students = "F3014"
                    self.model.addConstr(
                        gp.quicksum(
                            self.variables[classroom_new_students][section][
                                days[i]
                            ][times[i]]
                            for i in range(len(days))
                        )
                        == len(days)
                    )
                else:
                    for day, time in zip(days, times):
                        if (
                            self.classrooms[classroom]["classroom_type"]
                            in classroom_types
                        ):
                            self.model.addConstr(
                                self.variables[classroom][section][day][time] <= 1
                            )
                        else:
                            self.model.addConstr(
                                self.variables[classroom][section][day][time] == 0
                            )

    def set_objective(self):
        self.model.setObjective(
            gp.quicksum(
                self.variables[classroom][section][day][time]
                * self.coefficients[classroom][section][day][time]
                for classroom in self.classrooms
                for section in self.sections.keys()
                for day, time in zip(
                    utils.get_section_schedule(self.sections, section)[0],
                    utils.get_section_schedule(self.sections, section)[1],
                )
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

    def clean_model(self):
        self.model.dispose()
        self.env.dispose()

    def generate_results(self):

        classroom_assignement = []
        for var in self.model.getVars():
            if var.X > 0:
                timeschedule = f"{var.VarName}#{var.X}"
                classroom_assignement.append(timeschedule)

        model_value = self.model.ObjVal

        utils.treat_and_save_results(classroom_assignement, self.sections)

        print("========= RESULT ==========")
        print("Result was saved in results/*")
        print("=============================")
        print(f"Obj: {model_value}")

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
    timetabling.clean_model()


if __name__ == "__main__":
    main()
