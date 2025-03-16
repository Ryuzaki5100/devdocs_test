from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from typing import Callable

# Base class for tasks
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

# Derived class for data processing tasks
class DataTask(BaseTask):
    def __init__(self, task_id: str, data: str) -> None:
        super().__init__(task_id, self.process_data)
        self.data = data

    def process_data(self) -> None:
        print(f" Processing data tas k {self.task_id} with data: {self.data}")

# Derived class for compute tasks
class ComputeTask(BaseTask):
    def __init__(self, task_id: str, operation: str) -> None:
        super().__init__(task_id, self.process_compute)
        self.operation = operation

    def process_compute(self) -> None:
        print(f"Processing compute task {self.task_id} with operation: {self.operation}")

# Define the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'example_dag',
    default_args=default_args,
    description='A simple example DAG',
    schedule_interval=timedelta(days=1),
)

# Create tasks
data_task1 = DataTask(task_id="data_task_1", data="Data 1")
data_task2 = DataTask(task_id="data_task_2", data="Data 2")
compute_task = ComputeTask(task_id="compute_task", operation="Addition")

# Add tasks to the DAG
data_task1_op = data_task1.create_task(dag)
data_task2_op = data_task2.create_task(dag)
compute_task_op = compute_task.create_task(dag)

# Define task dependencies
data_task1_op >> compute_task_op
data_task2_op >> compute_task_op
