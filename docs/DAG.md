# Generated Documentation with UML
```python
from typing import Callable
from airflow import DAG
from airflow.operators.python import PythonOperator
```

### BaseTask.__init__(self, task_id, python_callable)

**Purpose:** This is the constructor for the `BaseTask` class. It initializes the basic attributes that are common to all tasks.

**Explanation:**

-   `self.task_id`: Stores the unique identifier for the task. This `task_id` is used by Airflow to track and manage the task within the DAG.
-   `self.python_callable`: Stores a reference to the Python function that this task will execute. This function defines the core logic of the task.

**Business Logic:**

The `BaseTask` class serves as the foundation for creating different types of tasks within an Airflow DAG. The `__init__` method sets up the fundamental properties needed for any task to function correctly within the Airflow environment.

**Example:**

```python
class BaseTask:
    def __init__(self, task_id: str, python_callable: Callable) -> None:
        self.task_id = task_id
        self.python_callable = python_callable
```

**Cyclomatic Complexity:** 1. The function contains a simple sequence of assignments with no branching or looping.

**Pain Points:** None identified at this level of abstraction.

### DataTask.__init__(self, task_id, data)

**Purpose:**  This is the constructor for the `DataTask` class, which inherits from `BaseTask`. It initializes a task that processes data.

**Explanation:**

-   `super().__init__(task_id, self.process_data)`: Calls the constructor of the parent class (`BaseTask`) to initialize the `task_id` and sets the `python_callable` to `self.process_data`.  This means when the Airflow operator executes this task, it will call the `process_data` method of the `DataTask` instance.
-   `self.data`: Stores the data that the task will process.

**Business Logic:**

The `DataTask` is designed to handle data-related operations. By inheriting from `BaseTask`, it reuses the basic task structure and adds the `data` attribute, allowing it to operate on specific data inputs.

**Example:**

```python
class DataTask(BaseTask):
    def __init__(self, task_id: str, data: str) -> None:
        super().__init__(task_id, self.process_data)
        self.data = data
```

**Cyclomatic Complexity:** 1. The function contains a simple call to the superclass constructor and an assignment, with no branching or looping.

**Pain Points:** None identified.

### ComputeTask.__init__(self, task_id, operation)

**Purpose:** This is the constructor for the `ComputeTask` class, which inherits from `BaseTask`. It initializes a task that performs a computation.

**Explanation:**

-   `super().__init__(task_id, self.process_compute)`: Calls the constructor of the parent class (`BaseTask`) to initialize the `task_id` and sets the `python_callable` to `self.process_compute`.  This ensures that when the Airflow operator executes this task, it will call the `process_compute` method of the `ComputeTask` instance.
-   `self.operation`: Stores the operation that the task will perform.

**Business Logic:**

The `ComputeTask` is designed for computation-related tasks.  It inherits from `BaseTask` and adds the `operation` attribute.

**Example:**

```python
class ComputeTask(BaseTask):
    def __init__(self, task_id: str, operation: str) -> None:
        super().__init__(task_id, self.process_compute)
        self.operation = operation
```

**Cyclomatic Complexity:** 1.  The function contains a simple call to the superclass constructor and an assignment, with no branching or looping.

**Pain Points:** None identified.

### BaseTask.create_task(self, dag)

**Purpose:** This method creates an Airflow `PythonOperator` instance from the `BaseTask` object.

**Explanation:**

-   `PythonOperator(...)`: Creates a `PythonOperator` instance, which is the Airflow operator responsible for executing Python callables.
    -   `task_id=self.task_id`:  Assigns the task ID from the `BaseTask` instance to the `PythonOperator`.
    -   `python_callable=self.python_callable`: Assigns the Python callable (the function to be executed) from the `BaseTask` instance to the `PythonOperator`.
    -   `dag=dag`:  Associates the `PythonOperator` with the given Airflow DAG.

**Business Logic:**

This method bridges the gap between the task definitions (represented by `BaseTask` and its subclasses) and the Airflow framework.  It creates an Airflow-compatible operator that can be scheduled and executed as part of a DAG.

**Example:**

```python
class BaseTask:
    # ... (previous code)

    def create_task(self, dag: DAG) -> PythonOperator:
        return PythonOperator(
            task_id=self.task_id,
            python_callable=self.python_callable,
            dag=dag,
        )
```

**Cyclomatic Complexity:** 1. This function consists of a single return statement that constructs a `PythonOperator` object. There are no conditional branches or loops.

**Pain Points:** None identified.

### DataTask.process_data(self)

**Purpose:** This method defines the data processing logic for a `DataTask`.

**Explanation:**

-   `print(f" Processing data task {self.task_id} with data: {self.data}")`: Prints a message to the console indicating that the data processing task is running, along with the task ID and the data being processed.  In a real-world scenario, this would be replaced by actual data processing logic (e.g., cleaning, transforming, loading data).

**Business Logic:**

This method represents the core data processing operation performed by the `DataTask`. It's a placeholder for more complex data manipulation.

**Example:**

```python
class DataTask(BaseTask):
    # ... (previous code)

    def process_data(self) -> None:
        print(f" Processing data task {self.task_id} with data: {self.data}")
```

**Cyclomatic Complexity:** 1. This function contains only a print statement, so there are no branching or looping structures.

**Pain Points:**

-   The current implementation only prints a message.  In a real application, this should be replaced with meaningful data processing logic.  It lacks error handling and more robust operations.

### ComputeTask.process_compute(self)

**Purpose:** This method defines the computation logic for a `ComputeTask`.

**Explanation:**

-   `print(f"Processing compute task {self.task_id} with operation: {self.operation}")`: Prints a message to the console indicating that the compute task is running, along with the task ID and the operation being performed.  In a real-world scenario, this would be replaced by actual computation logic (e.g., mathematical calculations, simulations).

**Business Logic:**

This method represents the core computation operation performed by the `ComputeTask`. It serves as a placeholder for more complex computations.

**Example:**

```python
class ComputeTask(BaseTask):
    # ... (previous code)

    def process_compute(self) -> None:
        print(f"Processing compute task {self.task_id} with operation: {self.operation}")
```

**Cyclomatic Complexity:** 1.  This function contains only a print statement, so there are no branching or looping structures.

**Pain Points:**

-   The current implementation only prints a message.  This should be replaced with actual computation logic. The lack of error handling and specific computation operations are limitations.
```

## UML Diagram
![Image](images/DAG_img1.png)
## DAG FLOW
![Image](images/DAG_img2.png)

