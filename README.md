# Classroom Timetabling


This project is a classroom timetabling system that uses a mathematical model to optimize the allocation of classrooms to sections. The optimization method is based on mixed-integer quadratic programming (MIQP) using the Gurobi solver. The case study is applied to the Institute of Computing at UFRJ, as part of my undergraduate thesis.

> The latest result of the model, pointing to the main branch, can be viewed at the following URL: [https://classroom-assignment-ufrj.streamlit.app](https://classroom-assignment-ufrj.streamlit.app)

### Phase 2: Allocate Professors to Courses
This project is part 2 of 2. The first phase, which is available in [course_timetabling](https://github.com/gabriellydeandrade/course_timetabling), will focus on the allocation of professors to courses. This phase will use the results of the previous model to continue the optimization process.


## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- pipenv (requirements)
- Virtual environment (recommended)

### Steps

1. **Clone the repository:**

    ```sh
    git clone https://github.com/gabriellydeandrade/classroom_assignment.git
    ```

2. **Create a virtual environment inside the project (recommended):**

    ```sh
    cd classroom_assignment
    python -m venv .venv
    ```

3. **Activate the virtual environment (recommended):**

    - On macOS/Linux:

        ```sh
        source .venv/bin/activate
        ```

    - On Windows:

        ```sh
        .venv\Scripts\activate
        ```

4. **Install the required packages:**

    ```sh
    pip install pipenv
    pipenv install
    ```

## Running the Code

### Running the Optimization Model

To run the optimization model and generate the timetabling results, execute the following command:

```sh
python classroom_assignment/main.py
```

Two .csv files will be updated into the `results` folder.

## Viewing the Results

To view the results using Streamlit, run the following command:

```sh
streamlit run classroom_assignment/results/generate_assignment.py
```

This will start a local Streamlit server. Open your web browser and navigate to the URL provided in the terminal (usually http://localhost:8501).

## Project Structure

```
classroom_assignment/
├── cache/
├── classroom_assignment/
├── ├── database/
├── │   ├── construct_sets.py
├── │   ├── service_google_sheet.py
├── │   ├── transform_data.py
├── ├── results/
├── │   ├── generate_assignment.py
├── │   ├── cap_diff.csv
├── │   ├── classroom_allocation.csv
├── │   ├── pnc.csv
├── ├── tests/
├── ├── utils/
├── ├── main.py
├── ├── settings.py
├── Pipfile
├── Pipfile.lock
├── README.md
```

## Mathematical Formulation

See the [classrrom_assignment.ipynb](classrrom_assignment.ipynb) file.

## Implementation Steps

1. **Model Initialization:** Create an instance of the `ClassroomAssignment` class, which takes input data: classrooms and sections. These parameters are the sets read from the spreadsheet.

    ```python
    timetabling = ClassroomAssignment(
        CLASSROOMS,
        SECTIONS,
    )
    ```

    During class initialization, the Gurobi environment is configured and the model is defined.

    ```python
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
            env = gp.Env(empty=True)
            env.setParam("LicenseID", settings.APP_LICENSE_ID)
            env.setParam("WLSAccessID", settings.APP_WLS_ACCESS_ID)
            env.setParam("WLSSecret", settings.APP_WLS_SECRET)
            env.start()
            return env
    ```

2. **Variable and Coefficient Initialization:** Define decision variables and coefficients. The decision variable is binary and represented by an array combining classroom, section, day, and time. A separate method initializes slack variables, which correspond to the difference between the minimum required capacity and the actual allocated capacity for each classroom.

    ```python
    # Decision variable definition
    self.variables[classroom][section][day][time] = self.model.addVar(
        vtype=GRB.BINARY, name=f"{classroom}_{section}_{day}_{time}"
    )

    # Initialize variables and coefficients
    timetabling.initialize_variables_and_coefficients()

    # Initialize slack variables
    timetabling.add_capacity_slack_variables()
    ```

3. **Constraints and Objective Function Definition:** Add constraints to the model to ensure valid allocation, such as the constraint that each section must be allocated to a single classroom per day and time. Then, set the objective function to maximize the utilization of classrooms using the defined coefficients.

    ```python
    timetabling.add_constraints()
    timetabling.set_objective()
    ```

4. **Model Execution, Results, and Finalization:** Run the Gurobi solver to find the optimal solution, considering all decision variables, the objective function, and constraints. Extract and present the model results, including detailed allocation of classrooms to sections, schedules, and days. Finally, clean up the model to free resources and prepare the environment for future runs.

    ```python
    timetabling.optimize()
    timetabling.generate_results()
    timetabling.clean_model()
    ```