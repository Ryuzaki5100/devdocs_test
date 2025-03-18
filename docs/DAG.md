# Generated Documentation with UML
## Function Documentation

This documentation outlines the functionality of each function in the provided code, following the order of execution implied by their dependencies and class inheritance.

**1. `BaseTask.__init__(self, task_id, python_callable)`**

*   **Purpose:** This is the constructor for the `BaseTask` class. It initializes the core attributes that are common to all task types (data tasks and compute tasks in this case).
*   **Parameters:**
    *   `task_id` (str): A unique identifier for the task. This is crucial for tracking and managing tasks within a workflow.
    *   `python_callable` (Callable): A reference to the Python function that will be executed when the task runs.  This allows different tasks to perform different operations. This is essentially a pointer or reference to a function.
*   **Functionality:**
    *   It assigns the provided `task_id` to the `self.task_id` attribute.
    *   It assigns the provided `python_callable` to the `self.python_callable` attribute.
*   **Business Logic:** The `BaseTask` class serves as a foundation for different types of tasks. The constructor sets up the basic properties required for any task within a workflow or Directed Acyclic Graph (DAG).
*   **Example:**
    ```python
    class MyTask(BaseTask):
        def __init__(self, task_id, custom_function):
            super().__init__(task_id, custom_function) #calling BaseTask.__init__ to initialize task_id and python_callable
    ```
*   **Dependencies:** `func6, func4, func2, func5, func1, func3` (implying order doesn't matter since it is used in init functions for all the classes)
*   **Cyclomatic Complexity:** 1 (simple assignment operations).
*   **Pain Points:** None identified. This constructor is straightforward and essential for setting up the base task.

**2. `DataTask.__init__(self, task_id, data)`**

*   **Purpose:** This is the constructor for the `DataTask` class, which inherits from `BaseTask`.  It initializes a task specifically designed to handle data processing.
*   **Parameters:**
    *   `task_id` (str): A unique identifier for the data task (inherited from `BaseTask`).
    *   `data` (str): The data that this task will process.
*   **Functionality:**
    *   It calls the constructor of the parent class (`BaseTask.__init__`) using `super().__init__(task_id, self.process_data)`.  This initializes the `task_id` and sets the `python_callable` to `self.process_data`.
    *   It assigns the provided `data` to the `self.data` attribute.
*   **Business Logic:** The `DataTask` class encapsulates the logic and data associated with processing a specific piece of data. This allows workflows to manage data-related tasks in a structured manner.
*   **Example:**
    ```python
    data_task = DataTask("extract_customer_data", "customer_data.csv")
    ```
*   **Dependencies:** `func6, func4, func2, func5, func1, func3` (implying order doesn't matter since it is used in init functions for all the classes)
*   **Cyclomatic Complexity:** 1 (simple assignment and `super()` call).
*   **Pain Points:** None identified. The constructor clearly sets up a data task and leverages the base class.

**3. `ComputeTask.__init__(self, task_id, operation)`**

*   **Purpose:** This is the constructor for the `ComputeTask` class, which inherits from `BaseTask`. It initializes a task that performs a specific computation.
*   **Parameters:**
    *   `task_id` (str): A unique identifier for the compute task (inherited from `BaseTask`).
    *   `operation` (str):  A string indicating the computation to be performed. This could be something like "calculate_average", "apply_model", etc.
*   **Functionality:**
    *   It calls the constructor of the parent class (`BaseTask.__init__`) using `super().__init__(task_id, self.process_compute)`.  This initializes the `task_id` and sets the `python_callable` to `self.process_compute`.
    *   It assigns the provided `operation` string to the `self.operation` attribute.
*   **Business Logic:** The `ComputeTask` class represents a unit of computation within a workflow. By encapsulating the operation details, it allows for reusable and manageable computational tasks.
*   **Example:**
    ```python
    compute_task = ComputeTask("calculate_sum", "sum_values")
    ```
*   **Dependencies:** `func6, func4, func2, func5, func1, func3` (implying order doesn't matter since it is used in init functions for all the classes)
*   **Cyclomatic Complexity:** 1 (simple assignment and `super()` call).
*   **Pain Points:** None identified. The constructor effectively sets up a compute task.

**4. `BaseTask.create_task(self, dag)`**

*   **Purpose:** This method is responsible for creating an Airflow `PythonOperator` instance that represents the task within an Airflow DAG (Directed Acyclic Graph).
*   **Parameters:**
    *   `dag` (DAG): The Airflow DAG object to which this task will be added.  A DAG represents a workflow or pipeline of tasks.
*   **Functionality:**
    *   It creates a `PythonOperator` object.
    *   It sets the `task_id` of the operator to the `self.task_id` attribute of the `BaseTask` instance.
    *   It sets the `python_callable` of the operator to the `self.python_callable` attribute of the `BaseTask` instance.  This is the function that will be executed when the Airflow task runs.
    *   It assigns the `dag` to the `dag` parameter of the `PythonOperator`.
    *   It returns the created `PythonOperator` object.
*   **Business Logic:** This method bridges the gap between the abstract `BaseTask` representation and the concrete Airflow task representation. It allows users to define tasks in a more general way and then easily integrate them into an Airflow workflow.
*   **Example:**
    ```python
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from datetime import datetime

    with DAG(
        dag_id='my_dag',
        start_date=datetime(2023, 1, 1),
        schedule_interval=None,
    ) as dag:
        my_task = MyTask("custom_task", my_python_function)
        airflow_task = my_task.create_task(dag) #creates the airflow task for the dag.
    ```
*   **Dependencies:** `func6, func4, func2, func5, func1, func3` (implying order doesn't matter since it's used across all classes).
*   **Cyclomatic Complexity:** 1 (single return statement with instantiation).
*   **Pain Points:** The tight coupling with Airflow's `PythonOperator` might make it difficult to adapt this code to other workflow management systems.  Consider using an abstraction layer for greater flexibility.

**5. `DataTask.process_data(self)`**

*   **Purpose:** This method defines the actual data processing logic for a `DataTask` instance.  It's the function that gets called by the Airflow `PythonOperator` when the data task is executed.
*   **Parameters:**
    *   `self`: Refers to the instance of the `DataTask` class.
*   **Functionality:**
    *   It prints a message to the console indicating that the data task is being processed, including the `task_id` and the `data` being processed.
*   **Business Logic:** This method represents the core functionality of the `DataTask`. In a real-world scenario, this method would contain the code to read, transform, or otherwise process the `self.data` attribute.  For example, it might read the data from a file, perform some calculations, and then store the results in a database.
*   **Example:**
    ```python
    # Imagine that this method would actually process self.data.
    def process_data(self) -> None:
        print(f"Processing data task {self.task_id} with data: {self.data}")
        # process the data here, e.g.:
        # with open(self.data, 'r') as f:
        #     content = f.read()
        #     # do something with the content
    ```
*   **Dependencies:** `func6, func4, func2, func5, func1, func3` (implying order doesn't matter since it's used across all classes).
*   **Cyclomatic Complexity:** 1 (single print statement).
*   **Pain Points:** The current implementation only prints a message.  The actual data processing logic needs to be implemented here. Additionally, there is no error handling or logging.

**6. `ComputeTask.process_compute(self)`**

*   **Purpose:** This method defines the actual computation logic for a `ComputeTask` instance. It's the function that gets called by the Airflow `PythonOperator` when the compute task is executed.
*   **Parameters:**
    *   `self`: Refers to the instance of the `ComputeTask` class.
*   **Functionality:**
    *   It prints a message to the console indicating that the compute task is being processed, including the `task_id` and the `operation` being performed.
*   **Business Logic:** This method represents the core functionality of the `ComputeTask`.  In a real-world scenario, this method would contain the code to perform the specified `self.operation`. For example, it might calculate the average of a set of numbers, train a machine learning model, or perform some other complex computation.
*   **Example:**
    ```python
    # Imagine this method would actually perform the specified operation
    def process_compute(self) -> None:
        print(f"Processing compute task {self.task_id} with operation: {self.operation}")
        # Perform computation here, e.g.:
        # if self.operation == "calculate_average":
        #     result = calculate_average(data)
    ```
*   **Dependencies:** `func6, func4, func2, func5, func1, func3` (implying order doesn't matter since it's used across all classes).
*   **Cyclomatic Complexity:** 1 (single print statement).
*   **Pain Points:** The current implementation only prints a message. The actual computation logic needs to be implemented here. Additionally, there is no error handling or logging.

In summary, the code provides a basic framework for defining and executing data and compute tasks within an Airflow workflow. It uses inheritance to create specialized task types from a base class, and it leverages Airflow's `PythonOperator` to execute the task logic.  The primary pain points are the lack of actual data processing and computation logic in the `process_data` and `process_compute` methods, as well as the absence of error handling and logging.  The tight coupling with Airflow could also be a limitation in some scenarios.

## UML Diagram
![Image](images/DAG_img1.png)
## DAG FLOW
![Image](images/DAG_img2.png)

