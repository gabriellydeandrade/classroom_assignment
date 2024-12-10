     for classroom in self.classrooms:

            for section in self.sections:
                days, times = utils.get_section_schedule(self.sections, section)
                classroom_types = self.sections[section]["classroom_type"].split(",")

                if len(classroom_types) == 1:
                    classroom_types = [classroom_types[0]] * len(days)

                # RN3: O tipo de sala deverá ser o mesmo requerido na alocação da disciplina
                # for classroom in self.classrooms:
                    # if self.classrooms[classroom]["classroom_type"] in classroom_types:
                assigned_types = gp.quicksum(
                    self.variables[classroom][section][day][time]
                    for day, time in zip(days, times)
                )
                type_qtty = classroom_types.count(self.classrooms[classroom]["classroom_type"])
                self.model.addConstr(
                    assigned_types == type_qtty
                )
                # else:
                #     for day, time in zip(days, times):
                #         self.model.addConstr(
                #             self.variables[classroom][section][day][time] == 0
                #         )

        # for section in self.sections:
        #     days, times = utils.get_section_schedule(self.sections, section)
        #     classroom_types = self.sections[section]["classroom_type"].split(",")

        #     if len(classroom_types) == 1:
        #         classroom_types = [classroom_types[0]] * len(days)

        #     # RN3: O tipo de sala deverá ser o mesmo requerido na alocação da disciplina
        #     if self.classrooms[classroom]["classroom_type"] in classroom_types:

        #         self.model.addConstr(
        #             gp.quicksum(
        #                 self.variables[classroom][section][days[i]][times[i]]
        #                 for i in range(len(days))
        #             )
        #             == sum(
        #                 [
        #                     1
        #                     for x in classroom_types
        #                     if x == self.classrooms[classroom]["classroom_type"]
        #                 ]
        #             )
        #         )
        #         # for day, time in zip(days, times):
        #         #     self.model.addConstr(
        #         #         self.variables[classroom][section][day][time] <= 1
        #         #     )
        #     else:
        #         for day, time in zip(days, times):
        #             self.model.addConstr(
        #                 self.variables[classroom][section][day][time] == 0
        #             )

            # RN4: Caso a disciplina seja do primeiro período, uma sala específica deverá ser ocupada para as aulas teóricas (F3014)
            # for section in self.sections:
            # days, times = utils.get_section_schedule(self.sections, section)
            # classroom_types = self.sections[section]["classroom_type"].split(",")

            # if (
            #     self.sections[section]["term"] == 1
            #     and self.sections[section]["class_type"] == "Calouro"
            # ):
            #     classroom_new_students = "F3014"

            #     self.model.addConstr(
            #         gp.quicksum(
            #             self.variables[classroom_new_students][section][days[i]][
            #                 times[i]
            #             ]
            #             for i in range(len(days))
            #         )
            #         == len(classroom_types)
            # sum(
            #     [
            #         1
            #         for x in classroom_types
            #         if x
            #         == self.classrooms[classroom_new_students]["classroom_type"]
            #     ]
            # )
            # )

            # # # RN4: Caso a disciplina seja do primeiro período, uma sala específica deverá ser ocupada para as aulas teóricas (F3014)
            # if (
            #     self.sections[section]["term"] == 1
            #     and self.sections[section]["class_type"] == "Calouro"
            # ):
            #     classroom_new_students = "F3014"
            #     self.model.addConstr(
            #         gp.quicksum(
            #             self.variables[classroom_new_students][section][days[i]][
            #                 times[i]
            #             ]
            #             for i in range(len(days))
            #         )
            #         == sum(
            #             [
            #                 1
            #                 for x in classroom_types
            #                 if x
            #                 == self.classrooms[classroom_new_students]["classroom_type"]
            #             ]
            #         )
            #     )