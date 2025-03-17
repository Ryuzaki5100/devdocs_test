# Generated Documentation with UML
## Function Documentation

This documentation outlines the provided functions, their dependencies, and their roles in defining and processing tasks. The functions are presented in an order that reflects their logical dependencies and potential execution flow.

**1. `BaseTask.__init__(self, task_id, python_callable)`**

*   **Purpose:** This is the constructor for the `BaseTask` class. It initializes the core attributes common to all tasks.
*   **Parameters:**
    *   `task_id` (str): A unique identifier for the task. This is crucial for tracking and managing tasks within a larger workflow or DAG (Directed Acyclic Graph).
    *   `python_callable` (Callable): A reference to the Python function that will be executed when the task is run.  This allows the `BaseTask` to be generic and execute different actions depending on the provided callable.
*   **Functionality:**
    *   Assigns the `task_id` to the `self.task_id` attribute.
    *   Assigns the `python_callable` to the `self.python_callable` attribute.
*   **Business Logic:** The `BaseTask` class serves as an abstract representation of a unit of work. It provides a standardized way to define tasks and associate them with specific functions to be executed.
*   **Cyclomatic Complexity:** 1 (Simple assignment operations)
*   **Pain Points:** None obvious. It's a standard constructor.
*   **Example:**

    ```python
    class BaseTask:
        def __init__(self, task_id: str, python_callable: Callable) -> None:
            self.task_id = task_id
            self.python_callable = python_callable

    def my_function():
        print("Hello from my_function!")

    task = BaseTask("my_task", my_function)
    print(task.task_id)  # Output: my_task
    ```

**2. `DataTask.__init__(self, task_id, data)`**

*   **Purpose:** This is the constructor for the `DataTask` class, which inherits from `BaseTask`.  It initializes a task specifically designed to work with data.
*   **Parameters:**
    *   `task_id` (str): A unique identifier for the task (inherited from `BaseTask`).
    *   `data` (str): The data that the task will process.  In a real-world scenario, this could be a file path, a database query, or any other relevant data source.
*   **Functionality:**
    *   Calls the `BaseTask` constructor using `super().__init__(task_id, self.process_data)`. This sets the `task_id` and assigns the `process_data` method of the `DataTask` class as the `python_callable`.
    *   Assigns the `data` to the `self.data` attribute.
*   **Business Logic:** The `DataTask` specializes the `BaseTask` to handle data-related operations. It encapsulates the data and the processing logic (the `process_data` method) into a single unit.
*   **Cyclomatic Complexity:** 1 (Simple inheritance and assignment)
*   **Pain Points:** The `data` parameter is currently a string.  In a more robust system, it might need to support different data types or a more structured data representation.
*   **Example:**

    ```python
    class DataTask(BaseTask):
        def __init__(self, task_id: str, data: str) -> None:
            super().__init__(task_id, self.process_data)
            self.data = data

        def process_data(self):
            print(f"Processing data: {self.data}")

    data_task = DataTask("process_file", "my_file.txt")
    print(data_task.task_id) #output: process_file
    ```

**3. `ComputeTask.__init__(self, task_id, operation)`**

*   **Purpose:** This is the constructor for the `ComputeTask` class, inheriting from `BaseTask`. It initializes a task designed for computational operations.
*   **Parameters:**
    *   `task_id` (str): A unique identifier for the task (inherited from `BaseTask`).
    *   `operation` (str): A string representing the computational operation to be performed. This could be something like "addition", "multiplication", or a more complex algorithm name.
*   **Functionality:**
    *   Calls the `BaseTask` constructor using `super().__init__(task_id, self.process_compute)`. This sets the `task_id` and assigns the `process_compute` method of the `ComputeTask` class as the `python_callable`.
    *   Assigns the `operation` to the `self.operation` attribute.
*   **Business Logic:** The `ComputeTask` class specializes the `BaseTask` to handle computational tasks. It holds information about the desired operation and uses the `process_compute` method to execute it.
*   **Cyclomatic Complexity:** 1 (Simple inheritance and assignment)
*   **Pain Points:** The `operation` parameter is currently a string, which is limiting.  A more advanced system would likely use a function pointer, an enum, or a more structured representation of the operation to be performed.  There's no actual computation performed here yet.
*   **Example:**

    ```python
    class ComputeTask(BaseTask):
        def __init__(self, task_id: str, operation: str) -> None:
            super().__init__(task_id, self.process_compute)
            self.operation = operation

        def process_compute(self):
           print(f"Running {self.operation}")

    compute_task = ComputeTask("add_numbers", "addition")
    print(compute_task.task_id)  #output: add_numbers
    ```

**4. `DataTask.process_data(self)`**

*   **Purpose:** This method defines the action performed by a `DataTask`. It prints a message indicating that the data is being processed.
*   **Parameters:**
    *   `self`:  A reference to the `DataTask` instance.
*   **Functionality:**
    *   Prints a formatted string to the console, indicating the task ID and the data being processed.
*   **Business Logic:** This method is a placeholder for the actual data processing logic. In a real application, this method would contain the code to read, transform, or otherwise manipulate the `self.data`.
*   **Cyclomatic Complexity:** 1 (Simple print statement)
*   **Pain Points:** This is just a placeholder.  It doesn't do any actual data processing. In a real application, error handling, data validation, and robust processing logic would be required.
*   **Example:**
    ```python
    class DataTask(BaseTask):
        def __init__(self, task_id: str, data: str) -> None:
            super().__init__(task_id, self.process_data)
            self.data = data

        def process_data(self):
           print(f" Processing data tas k {self.task_id} with data: {self.data}")

    data_task = DataTask("process_file", "my_file.txt")
    data_task.process_data() # Output:  Processing data tas k process_file with data: my_file.txt
    ```

**5. `ComputeTask.process_compute(self)`**

*   **Purpose:** This method defines the action performed by a `ComputeTask`. It prints a message indicating the computation being performed.
*   **Parameters:**
    *   `self`: A reference to the `ComputeTask` instance.
*   **Functionality:**
    *   Prints a formatted string to the console, indicating the task ID and the operation being performed.
*   **Business Logic:** This is a placeholder for the actual computational logic.  In a real application, this method would contain the code to perform the specified operation using the `self.operation` string as a guide (or ideally, using a more robust representation of the operation).
*   **Cyclomatic Complexity:** 1 (Simple print statement)
*   **Pain Points:** Similar to `DataTask.process_data`, this is a placeholder. It doesn't perform any real computation.  The `operation` string is also not very useful in its current form; a better design would be required to map the string to actual computation logic.
*   **Example:**

    ```python
    class ComputeTask(BaseTask):
        def __init__(self, task_id: str, operation: str) -> None:
            super().__init__(task_id, self.process_compute)
            self.operation = operation

        def process_compute(self):
           print(f"Processing compute task {self.task_id} with operation: {self.operation}")

    compute_task = ComputeTask("add_numbers", "addition")
    compute_task.process_compute() # Output: Processing compute task add_numbers with operation: addition
    ```

**6. `BaseTask.create_task(self, dag)`**

*   **Purpose:** This method creates an Airflow `PythonOperator` from the `BaseTask` instance. It connects the task to an Airflow DAG (Directed Acyclic Graph) for execution.
*   **Parameters:**
    *   `self`: A reference to the `BaseTask` instance.
    *   `dag` (DAG): The Airflow DAG to which the task will be added.
*   **Functionality:**
    *   Creates a `PythonOperator` with the following properties:
        *   `task_id`: Set to the `self.task_id` of the `BaseTask`.
        *   `python_callable`: Set to the `self.python_callable` of the `BaseTask`. This ensures that the correct function (e.g., `process_data` or `process_compute`) is executed when the task runs.
        *   `dag`: Set to the provided `dag` parameter, linking the task to the Airflow DAG.
*   **Business Logic:** This method integrates the custom task definitions with the Airflow framework. It allows users to define their tasks using the `BaseTask`, `DataTask`, and `ComputeTask` classes and then easily incorporate them into an Airflow workflow.
*   **Cyclomatic Complexity:** 1 (Simple operator creation)
*   **Pain Points:** Requires familiarity with Airflow's `PythonOperator`. Error handling for potential exceptions during operator creation (e.g., invalid task_id) might be beneficial.
*   **Example:**

    ```python
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from datetime import datetime

    class BaseTask:
        def __init__(self, task_id: str, python_callable: Callable) -> None:
            self.task_id = task_id
            self.python_callable = python_callable

        def create_task(self, dag: DAG) -> PythonOperator:
            return PythonOperator(
                task_id=self.task_id,
                python_callable=self.python_callable,
                dag=dag,
            )


    def my_function():
        print("Hello from my_function!")

    with DAG("my_dag", start_date=datetime(2023, 1, 1)) as dag:
        task = BaseTask("my_task", my_function)
        airflow_task = task.create_task(dag)
    ```

**Mapping of `func1` to `func6` to function names:**

*   `func1`: `BaseTask.__init__`
*   `func2`: `DataTask.__init__`
*   `func3`: `ComputeTask.__init__`
*   `func4`: `DataTask.process_data`
*   `func5`: `ComputeTask.process_compute`
*   `func6`: `BaseTask.create_task`

This mapping reflects the order in which these functions might be called when constructing and using these tasks within an Airflow DAG. `BaseTask.__init__` initializes the base class, followed by specialized initializers for `DataTask` and `ComputeTask`. The `process_data` and `process_compute` methods define the task logic, and `BaseTask.create_task` converts the task into an Airflow operator.

## UML Diagram
![Image](images/DAG_img1.png)
## DAG FLOW
![Image](images/DAG_img2.png)

