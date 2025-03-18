# Generated Documentation with UML
## Function Documentation

This documentation outlines the functions and their dependencies, providing explanations for each function's purpose, functionality, and business logic, adhering to the specified execution order.

**1. `BaseTask.__init__(self, task_id, python_callable)`**

```python
 def __init__(self, task_id: str, python_callable: Callable) -> None:
        self.task_id = task_id
        self.python_callable = python_callable
```

*   **Purpose:** This is the constructor (initializer) for the `BaseTask` class. It's responsible for setting up the fundamental attributes that every task will possess.

*   **Functionality:**
    *   It takes `task_id` (a string representing the unique identifier for the task) and `python_callable` (a callable object, which is a function to be executed when the task runs) as input.
    *   It assigns the provided `task_id` to the `self.task_id` attribute.
    *   It assigns the provided `python_callable` to the `self.python_callable` attribute.

*   **Business Logic:**  The `BaseTask` serves as an abstract representation of a generic task. The `task_id` allows the task to be uniquely identified within a larger workflow (like an Airflow DAG). The `python_callable` attribute stores the *actual* piece of code (a function) that the task is supposed to execute. This promotes a separation of concerns: the `BaseTask` handles the *management* of a task, while the `python_callable` defines the *work* the task performs.

*   **Example:**

    ```python
    def my_function():
        print("Hello from my_function!")

    base_task = BaseTask(task_id="my_task", python_callable=my_function)
    print(base_task.task_id)  # Output: my_task
    ```

**2. `DataTask.__init__(self, task_id, data)`**

```python
 def __init__(self, task_id: str, data: str) -> None:
        super().__init__(task_id, self.process_data)
        self.data = data
```

*   **Purpose:** This is the constructor for the `DataTask` class, which inherits from `BaseTask`. It initializes a task that specifically deals with data processing.

*   **Functionality:**
    *   It calls the `BaseTask`'s constructor using `super().__init__(task_id, self.process_data)`. This initializes the `task_id` and, crucially, sets the `python_callable` of the base class to `self.process_data`. This means when this task is executed it will call `self.process_data` function
    *   It takes `data` (a string representing the data to be processed) as input.
    *   It assigns the provided `data` to the `self.data` attribute.

*   **Business Logic:** The `DataTask` specializes the `BaseTask` for tasks that operate on data.  The `data` attribute stores the data that the task needs to work with. By passing `self.process_data` to the `BaseTask`'s constructor, we're telling the task to execute the `process_data` method when it's run. This ties the task's behavior to the specific logic defined in `process_data`.

*   **Example:**

    ```python
    data_task = DataTask(task_id="process_my_data", data="some_data.csv")
    print(data_task.data)  # Output: some_data.csv
    ```

**3. `ComputeTask.__init__(self, task_id, operation)`**

```python
    def __init__(self, task_id: str, operation: str) -> None:
        super().__init__(task_id, self.process_compute)
        self.operation = operation
```

*   **Purpose:** This is the constructor for the `ComputeTask` class, inheriting from `BaseTask`. It initializes a task designed for performing computational operations.

*   **Functionality:**
    *   It calls the `BaseTask` constructor using `super().__init__(task_id, self.process_compute)`.  This initializes the `task_id` and sets the `python_callable` to `self.process_compute`. This means when this task is executed it will call `self.process_compute` function
    *   It takes `operation` (a string representing the computational operation to be performed) as input.
    *   It assigns the provided `operation` to the `self.operation` attribute.

*   **Business Logic:** The `ComputeTask` provides a specialized version of `BaseTask` focused on computations. The `operation` attribute describes the computation the task needs to perform.  By setting the `python_callable` to `self.process_compute`, we ensure that the `process_compute` method is executed when the task is run.

*   **Example:**

    ```python
    compute_task = ComputeTask(task_id="calculate_sum", operation="a + b")
    print(compute_task.operation)  # Output: a + b
    ```

**4. `DataTask.process_data(self)`**

```python
    def process_data(self) -> None:
        print(f" Processing data tas k {self.task_id} with data: {self.data}")
```

*   **Purpose:** This method defines the data processing logic for the `DataTask`.

*   **Functionality:**
    *   It prints a message to the console indicating that the data processing task is being executed, including the `task_id` and the `data` being processed.

*   **Business Logic:** This method represents the core action of the `DataTask`.  In a real-world scenario, this method would contain the actual code to process the data, such as reading from a file, transforming the data, or writing the data to a database. The current implementation is a placeholder for this logic.

*   **Example:**

    ```python
    data_task = DataTask(task_id="process_data", data="my_file.txt")
    data_task.process_data()  # Output: Processing data task process_data with data: my_file.txt
    ```

**5. `ComputeTask.process_compute(self)`**

```python
    def process_compute(self) -> None:
        print(f"Processing compute task {self.task_id} with operation: {self.operation}")
```

*   **Purpose:** This method defines the computational logic for the `ComputeTask`.

*   **Functionality:**
    *   It prints a message to the console indicating that the compute task is being executed, including the `task_id` and the `operation` being performed.

*   **Business Logic:** This method represents the central action of the `ComputeTask`. In a realistic application, this method would contain the actual code to perform the computation described by the `operation` attribute. The current implementation is a simple placeholder.

*   **Example:**

    ```python
    compute_task = ComputeTask(task_id="calculate", operation="10 + 5")
    compute_task.process_compute() # Output: Processing compute task calculate with operation: 10 + 5
    ```

**6. `BaseTask.create_task(self, dag)`**

```python
    def create_task(self, dag: DAG) -> PythonOperator:
        return PythonOperator(
            task_id=self.task_id,
            python_callable=self.python_callable,
            dag=dag,
        )
```

*   **Purpose:** This method is responsible for creating an Airflow `PythonOperator` object that represents the task within an Airflow DAG (Directed Acyclic Graph).

*   **Functionality:**
    *   It takes an Airflow `DAG` object as input.
    *   It creates a `PythonOperator` object.
    *   It sets the `task_id` of the `PythonOperator` to the `task_id` of the `BaseTask`.
    *   It sets the `python_callable` of the `PythonOperator` to the `python_callable` of the `BaseTask`.  This is the crucial step that connects the task's logic (the function to execute) to the Airflow operator.
    *   It associates the `PythonOperator` with the provided `DAG`.
    *   It returns the created `PythonOperator` object.

*   **Business Logic:** This method bridges the gap between the abstract `BaseTask` (and its subclasses) and the Airflow framework. It takes the information defined in the `BaseTask` (task ID and the function to execute) and uses it to create a concrete Airflow task that can be scheduled and executed within a DAG. This enables the task to become part of an automated workflow managed by Airflow.

*   **Example:**

    ```python
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from datetime import datetime

    with DAG(dag_id="my_dag", start_date=datetime(2023, 1, 1), schedule_interval=None) as dag:
        def my_function():
            print("Task executed!")

        base_task = BaseTask(task_id="my_airflow_task", python_callable=my_function)
        airflow_task = base_task.create_task(dag)
        # airflow_task is now a PythonOperator that will execute my_function when the DAG runs.
    ```

### Mapping
* func1 maps to BaseTask.create_task
* func2 maps to BaseTask.__init__
* func3 maps to ComputeTask.process_compute
* func4 maps to DataTask.process_data
* func5 maps to DataTask.__init__
* func6 maps to ComputeTask.__init__

### Cyclomatic Complexity and Pain Points

*   **Cyclomatic Complexity:** The cyclomatic complexity of these functions is generally low. Each function has a single execution path (except for the `__init__` methods which always call the super class's init, it's complexity is still low).  This means the code is easy to understand and test.
*   **Pain Points:**
    *   **Limited Functionality:** The `process_data` and `process_compute` methods currently only print messages.  In a real application, they would need to contain the actual data processing or computation logic.  This is a major area for expansion.
    *   **String-Based Operations:** The `operation` attribute in `ComputeTask` is a string. This might require using `eval()` or other potentially unsafe methods to execute the operation, or building a more robust expression parser. This design choice could be a security risk and a maintenance headache. A better approach would be to use function objects or a more structured representation of the computation.
    *   **Error Handling:**  The code lacks error handling.  For example, what happens if the `python_callable` raises an exception?  Error handling mechanisms should be added to make the code more robust.
    *   **Lack of Abstraction:** The base class and inherited classes `DataTask` and `ComputeTask` are simple but lack advanced abstraction. The `python_callable` works to provide a basic level of function. But there is no support for logging, monitoring or other utilities in the base class.

## UML Diagram
![Image](images/DAG_img1.png)
## DAG FLOW
![Image](images/DAG_img2.png)

