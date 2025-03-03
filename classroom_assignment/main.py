import gurobipy as gp
from gurobipy import GRB

import settings

from utils import utils
from database.construct_sets import (
    get_classrooms_set,
    get_sections_set,
)

DEFAULT_COEFFICIENT = 10
RESPONSIBLE_INSTITUTE_COEFFICIENT = 100


class ClassroomAssignment:
    def __init__(self, classrooms, sections):
        self.classrooms = classrooms
        self.sections = sections
        self.coefficients = {}
        self.variables = {}
        self.slack_variables_capacity_diff = {}

        self.env = self.init_environment()
        self.model = gp.Model(name="ClassroomAssignment", env=self.env)

    def init_environment(self):
        if settings.APP_LICENSE_TYPE == settings.LicenseType.NAMED_USER_ACADEMIC.value:
            env = gp.Env(empty=False)

        elif settings.APP_LICENSE_TYPE == settings.LicenseType.WSL_ACADEMIC.value:
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

                    if day not in self.coefficients[classroom][section]:
                        self.coefficients[classroom][section][day] = {}

                    if (
                        self.sections[section]["responsable_institute"]
                        == self.classrooms[classroom]["responsable_institute"]
                    ):
                        self.coefficients[classroom][section][day][
                            time
                        ] = RESPONSIBLE_INSTITUTE_COEFFICIENT
                    else:
                        self.coefficients[classroom][section][day][
                            time
                        ] = DEFAULT_COEFFICIENT

                    if day not in self.variables[classroom][section]:
                        self.variables[classroom][section][day] = {}

                    self.variables[classroom][section][day][time] = self.model.addVar(
                        vtype=GRB.BINARY, name=f"{classroom}_{section}_{day}_{time}"
                    )

    def add_capacity_slack_variables(self):
        for classroom in self.classrooms:
            self.slack_variables_capacity_diff[classroom] = {}

            for section in self.sections:
                self.slack_variables_capacity_diff[classroom][section] = (
                    self.model.addVar(
                        vtype=GRB.INTEGER,
                        name=f"CapDiff_{classroom}_{section}",
                        lb=0.0,
                        ub=float("inf"),
                    )
                )

    def add_constraints(self):
        sections_days, sections_times = utils.get_possible_schedules_v2(self.sections)

        # Soft constraints
        for classroom in self.classrooms:
            for section in self.sections:
                days, times = utils.get_section_schedule(self.sections, section)

                TOLERANCE = 1e-6  # Defina uma tolerância pequena

                for day, time in zip(days, times):
                    slack_var = self.model.addVar(
                        vtype=GRB.CONTINUOUS, name=f"tolerance_slack"
                    )

                    # RF2: Garante que a sala seja alocada com a menor capacidade possível
                    self.model.addConstr(
                        self.slack_variables_capacity_diff[classroom][section]
                        <= self.classrooms[classroom][
                            "capacity"
                        ]  # TODO: testando a questão da tolerancia do erro
                        - (
                            self.variables[classroom][section][day][time]
                            * self.sections[section]["capacity"]
                        )
                        + slack_var
                    )

                    # Adicione uma restrição para garantir que a variável de folga esteja dentro da tolerância
                    self.model.addConstr(slack_var <= TOLERANCE)

        # Hard constraints
        # RN1: Um sala poderá ser alocada para no máximo 1 uma turma em um mesmo dia e horário (binário)
        for classroom in self.classrooms:
            for i in range(len(sections_days)):
                day = sections_days[i]
                time = sections_times[i]

                exact_time_sections = utils.get_courses_by_exact_day_and_time(
                    self.sections, day, time
                )

                self.model.addConstr(
                    gp.quicksum(
                        self.variables[classroom][section][day][time]
                        for section in exact_time_sections
                    )
                    <= 1,
                    name=f"RN1:Section_{section}_{classroom}_{day}_{time}",
                )

        for section in self.sections.keys():
            days, times = utils.get_section_schedule(self.sections, section)
            for day, time in zip(days, times):
                # RN2: Uma seção deverá ter somente uma sala de aula para um mesmo dia e horário
                self.model.addConstr(
                    gp.quicksum(
                        self.variables[classroom][section][day][time]
                        for classroom in self.classrooms
                    )
                    == 1,
                    name=f"RN2:Section_{section}_{classroom}_{day}_{time}",
                )

        # RN3: O tipo de sala deverá ser o mesmo requerido na alocação da disciplina
        for section in self.sections:
            days, times = utils.get_section_schedule(self.sections, section)
            classroom_types = self.sections[section]["classroom_type"].split(",")

            if len(classroom_types) == 1:
                classroom_types = [classroom_types[0]] * len(days)

            qtty_theory_classroom = classroom_types.count("Teórica")
            qtty_practical_classroom = classroom_types.count("Prática")

            self.model.addConstr(
                gp.quicksum(
                    self.variables[classroom][section][day][time]
                    for classroom in self.classrooms
                    if self.classrooms[classroom]["classroom_type"] == "Sala"
                    for day, time in zip(days, times)
                )
                == qtty_theory_classroom,
                name=f"RN3:Section_Theory_{section}",
            )

            self.model.addConstr(
                gp.quicksum(
                    self.variables[classroom][section][day][time]
                    for classroom in self.classrooms
                    if self.classrooms[classroom]["classroom_type"] == "Laboratório"
                    for day, time in zip(days, times)
                )
                == qtty_practical_classroom,
                name=f"RN3:Section_Practical_{section}",
            )

        for section in self.sections:

            # RN4: Caso a disciplina seja do primeiro período e for turma de calouro,
            # uma sala específica deverá ser ocupada para as aulas teóricas (F3014)
            if (
                self.sections[section]["term"] == 1
                and self.sections[section]["class_type"] == "Calouro"
            ):

                days, times = utils.get_section_schedule(self.sections, section)
                classroom_types = self.sections[section]["classroom_type"].split(",")
                qtty_theory_classroom = classroom_types.count("Teórica")

                if qtty_theory_classroom == len(classroom_types):
                    qtty_theory_classroom = len(times)

                classroom_new_students = "F3014"
                self.model.addConstr(
                    gp.quicksum(
                        self.variables[classroom_new_students][section][day][time]
                        for day, time in zip(days, times)
                    )
                    == qtty_theory_classroom,
                    name=f"RN4:F3014_NewStudents_{section}",
                )

            # RN5: Se a seção tiver alguma restrição de quadro, levar em consideração

            if self.sections[section]["blackboard_restriction"]:
                days, times = utils.get_section_schedule(self.sections, section)

                self.model.addConstr(
                    gp.quicksum(
                        self.variables[classroom][section][day][time]
                        for classroom in self.classrooms
                        if utils.is_blackboard(self.classrooms[classroom])
                        for day, time in zip(days, times)
                    )
                    == 0,
                    name=f"RN5:Board_Restriction_{section}_{classroom}_{day}_{time}",
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
                self.variables[classroom][section][day][time]
                * self.slack_variables_capacity_diff[classroom][section]
                for classroom in self.classrooms
                for section in self.sections.keys()
                for day, time in zip(
                    utils.get_section_schedule(self.sections, section)[0],
                    utils.get_section_schedule(self.sections, section)[1],
                )
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

        if self.model.Status == 2:
            print(f"Optimal solution found. Model return status={self.model.Status}")
        else:
            self.model.computeIIS()
            self.model.write("model.ilp")
            raise Exception(f"Model return status={self.model.Status}")

        classroom_assignement = []
        for var in self.model.getVars():
            if var.X > 0 and "tolerance_slack" not in var.VarName:
                timeschedule = f"{var.VarName}#{var.X}"
                classroom_assignement.append(timeschedule)

        model_value = self.model.ObjVal

        utils.treat_and_save_results(classroom_assignement, self.sections)

        print("========= METHOD ==========")
        print(self.model.getParamInfo("Method"))
        print(self.model.getParamInfo("ConcurrentMethod"))
        print(self.model.getParamInfo("ConcurrentMIP"))

        print(f"É MIP: {self.model.getAttr(GRB.Attr.IsMIP)}")
        print(f"É QP: {self.model.getAttr(GRB.Attr.IsQP)}")
        print(f"É QCP: {self.model.getAttr(GRB.Attr.IsQCP)}")
        print(f"É MultiObj: {self.model.getAttr(GRB.Attr.IsMultiObj)}")
        print("=============================")

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
