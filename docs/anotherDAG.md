# Generated Documentation with UML
```python
def _get_default_or_from_dag_run(default_value: str, dag_key, dag_run_conf):
    if dag_run_conf is not None and dag_key in dag_run_conf:
        return dag_run_conf[dag_key]
    return default_value
```

### Function: `_get_default_or_from_dag_run`

**Purpose:** This function retrieves a configuration value.  It prioritizes values passed in via the Airflow DAG run's configuration (`dag_run_conf`). If a value for the specified key (`dag_key`) is not found in the DAG run configuration, it falls back to a default value (`default_value`).

**Business Logic:**  Airflow DAGs often need configurable parameters. This function provides a mechanism to override default parameter values at runtime via the DAG run's configuration, making the DAG more flexible and reusable.  It supports use cases where specific runs need to behave differently without modifying the underlying DAG code. This mechanism is especially helpful for ad-hoc adjustments or retries with modified settings.

**Parameters:**

*   `default_value` (str): The default value to return if the `dag_key` is not found in the `dag_run_conf`.
*   `dag_key`: The key to look for in the `dag_run_conf` dictionary. This identifies the specific configuration parameter.
*   `dag_run_conf`: A dictionary containing configuration parameters passed to the DAG run. This can be `None` if no configuration is provided.

**Return Value:**

*   The value associated with `dag_key` in `dag_run_conf` if it exists; otherwise, `default_value`.

**Example:**

```python
default_bucket = "my-default-bucket"
dag_config = {"bucket_name": "override-bucket"}

# Example 1: Key exists in dag_config
bucket_name = _get_default_or_from_dag_run(default_bucket, "bucket_name", dag_config)
print(bucket_name)  # Output: override-bucket

# Example 2: Key does not exist in dag_config
region = _get_default_or_from_dag_run("us-central1", "region", dag_config)
print(region)  # Output: us-central1

# Example 3: dag_config is None
database = _get_default_or_from_dag_run("my_database", "database", None)
print(database) #Output: my_database
```

```python
def _get_impersonated_credentials(target_scopes: list, target_service_account: str):
    from google.auth import _default
    source_credentials, project_id = _default.default(scopes=target_scopes)
    logging.info(f"Source credentials generated for project [{project_id}]")

    from google.auth import impersonated_credentials
    target_credentials = impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=target_service_account,
        target_scopes=target_scopes,
        lifetime=60 * 60)
    return target_credentials
```

### Function: `_get_impersonated_credentials`

**Purpose:** This function obtains Google Cloud credentials that are impersonated from a target service account. It leverages the `google-auth` library to create credentials that act as if they were directly obtained by the specified service account.

**Business Logic:** Impersonation is a crucial security practice in cloud environments. It allows a service (in this case, the Airflow worker) to assume the identity of another service account to perform actions on its behalf. This limits the permissions of the Airflow worker itself, adhering to the principle of least privilege and improving security.  This function centralizes the credential creation process, making it easier to manage and reuse impersonation logic throughout the DAG.

**Parameters:**

*   `target_scopes` (list): A list of OAuth scopes that the impersonated credentials should have. These scopes define the permissions granted to the impersonated service account.
*   `target_service_account` (str): The email address of the service account to impersonate. This is the identity that the credentials will assume.

**Return Value:**

*   An `impersonated_credentials.Credentials` object representing the impersonated credentials. This object can then be used to authenticate with Google Cloud services.

**Example:**

```python
# Example usage
target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
target_service_account = 'my-dataflow-sa@my-project.iam.gserviceaccount.com'

credentials = _get_impersonated_credentials(target_scopes, target_service_account)

# Now you can use the 'credentials' object to authenticate with Google Cloud services,
# acting as the 'my-dataflow-sa' service account.
# For example, to create a storage client:
# from google.cloud import storage
# storage_client = storage.Client(credentials=credentials)
```

```python
def _get_storage_client(target_service_account: str, target_project: str):
    from google.cloud import storage
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    credentials = None if TEST_RUN == "true" else _get_impersonated_credentials(target_scopes,
                                                                                target_service_account)
    return storage.Client(project=target_project,
                          credentials=credentials)
```

### Function: `_get_storage_client`

**Purpose:** This function creates a Google Cloud Storage client, optionally using impersonated credentials.

**Business Logic:** This function simplifies the process of creating a GCS client for interacting with Google Cloud Storage.  It encapsulates the logic for determining whether to use impersonated credentials based on the `TEST_RUN` environment variable. This allows for easy switching between using the default credentials (for local testing) and impersonated credentials (for production deployments). By using impersonated credentials, it enforces the principle of least privilege, granting only the necessary permissions to the service account used by the Dataflow job.

**Parameters:**

*   `target_service_account` (str): The email address of the service account to impersonate.  Used only when `TEST_RUN` is not "true".
*   `target_project` (str): The Google Cloud project ID.

**Return Value:**

*   A `google.cloud.storage.Client` object, authenticated either with default or impersonated credentials, ready to interact with Google Cloud Storage.

**Example:**

```python
# Example usage:
target_service_account = 'my-dataflow-sa@my-project.iam.gserviceaccount.com'
target_project = 'my-project'

storage_client = _get_storage_client(target_service_account, target_project)

# Now you can use the 'storage_client' to interact with Google Cloud Storage.
# For example, to list buckets:
# for bucket in storage_client.list_buckets():
#     print(bucket.name)
```

```python
def _get_df_service():
    df_service = build("dataflow", "v1b3", cache_discovery=False)
    logging.info("df service [{}]".format(df_service))
    return df_service
```

### Function: `_get_df_service`

**Purpose:** This function creates and returns a Google Cloud Dataflow service client using the `googleapiclient.discovery.build` function.

**Business Logic:** The Dataflow service client is the primary interface for interacting with the Dataflow API. This function encapsulates the creation of this client, ensuring that it's configured correctly for use within the DAG. Setting `cache_discovery=False` is important in Airflow environments, as it prevents caching issues that can arise from long-running processes.

**Parameters:**

*   None

**Return Value:**

*   A Dataflow service client object (built using `googleapiclient.discovery.build`).

**Example:**

```python
# Example usage:
df_service = _get_df_service()

# Now you can use the 'df_service' to interact with the Dataflow API.
# For example, to list jobs:
# response = df_service.projects().locations().jobs().list(
#     projectId=PIPELINE_PROJECT_ID, location=DATAFLOW_REGION).execute()
```

```python
def list_jobs():
    logging.info(f"Listing Dataflow jobs")
    df_service = _get_df_service()
    response = (
        df_service.projects()
        .locations()
        .jobs()
        .list(projectId=PIPELINE_PROJECT_ID, location=DATAFLOW_REGION)
        .execute()
    )
    jobs = response["jobs"]
    return jobs
```

### Function: `list_jobs`

**Purpose:** This function lists Dataflow jobs in a specific project and location using the Dataflow API.

**Business Logic:** This function retrieves a list of Dataflow jobs, which is essential for monitoring, debugging, and managing Dataflow pipelines. The retrieved list can be used to check the status of running jobs, identify completed jobs, or gather information about job execution.

**Parameters:**

*   None

**Return Value:**

*   A list of Dataflow job dictionaries. Each dictionary represents a Dataflow job and contains information about the job, such as its ID, name, status, and creation time.

**Example:**

```python
# Example usage:
jobs = list_jobs()

# Now you can iterate through the 'jobs' list and access information about each job.
# for job in jobs:
#     print(f"Job ID: {job['id']}, Name: {job['name']}, State: {job['currentState']}")
```

```python
def _is_reprocessing(**context):
    reprocess_flag = context['ti'].xcom_pull(key=TASK_PARAM_REPROCESSING, task_ids=TASK_SETUP_PROCESSING)
    logging.info(f"Is reprocessing required [{reprocess_flag}]")
    return TASK_PREPARE_STAGING if not reprocess_flag else TASK_SKIP_PREPARE_STAGING
```

### Function: `_is_reprocessing`

**Purpose:** This function determines whether the current DAG run is a reprocessing run based on an XCom value. It pulls the `TASK_PARAM_REPROCESSING` key from the XCom of the `TASK_SETUP_PROCESSING` task.

**Business Logic:** This function enables conditional execution within the DAG based on whether a reprocessing flag is set.  Reprocessing might involve skipping certain steps (like preparing the staging area) if the data is already staged from a previous run. It promotes efficiency by avoiding redundant operations when reprocessing data.

**Parameters:**

*   `**context`: The Airflow context dictionary, which provides access to various objects, including the task instance (`ti`).

**Return Value:**

*   `TASK_PREPARE_STAGING` if `reprocess_flag` is False (meaning it's *not* a reprocessing run).
*   `TASK_SKIP_PREPARE_STAGING` if `reprocess_flag` is True (meaning it *is* a reprocessing run).

**Example:**

```python
# Example usage (within an Airflow task):
# Assuming TASK_SETUP_PROCESSING has pushed 'reprocessing_flag' to XCom

def my_task(**context):
    next_task = _is_reprocessing(**context)
    logging.info(f"Next task will be: {next_task}")
    # Use BranchPythonOperator to route to the appropriate task based on next_task

# In the DAG definition:
# my_branch_task = BranchPythonOperator(
#     task_id='my_branch_task',
#     python_callable=my_task,
#     provide_context=True,
#     dag=dag,
# )
```

```python
def _cleanup_xcom(context, session=None):
    dag_id = context["dag"].dag_id
    session.query(XCom).filter(XCom.dag_id == dag_id).delete()
```

### Function: `_cleanup_xcom`

**Purpose:** This function cleans up XCom entries associated with the current DAG. It removes all XCom entries for the DAG from the Airflow metadata database.

**Business Logic:** XComs (cross-communication) are used to pass data between tasks in an Airflow DAG. Over time, these XCom entries can accumulate and potentially impact Airflow's performance. This function provides a way to periodically clear out these entries, maintaining a clean Airflow metadata database. This is especially important for long-running DAGs or DAGs that generate a large number of XCom entries.

**Parameters:**

*   `context`: The Airflow context dictionary. This provides access to the DAG object and other relevant information.
*   `session`: An optional database session object. If not provided, the function will likely obtain a session from the Airflow environment.

**Return Value:**

*   None

**Example:**

```python
# Example usage (within an Airflow task):
def cleanup_task(**context):
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    hook = PostgresHook(postgres_conn_id='airflow_db')
    session = hook.get_session()
    _cleanup_xcom(context, session)
    session.close()

# In the DAG definition:
# cleanup_xcom_task = PythonOperator(
#     task_id='cleanup_xcom_task',
#     python_callable=cleanup_task,
#     provide_context=True,
#     dag=dag,
# )
```

```python
def get_job_metrics(job_id):
    df_service = _get_df_service()
    response = (
        df_service.projects()
        .locations()
        .jobs()
        .getMetrics(projectId=PIPELINE_PROJECT_ID, location=DATAFLOW_REGION, jobId=job_id)
        .execute()
    )
    metrics = response
    return metrics
```

### Function: `get_job_metrics`

**Purpose:** This function retrieves metrics for a specific Dataflow job using the Dataflow API.

**Business Logic:** This function is critical for monitoring the performance and progress of Dataflow jobs. The metrics retrieved can include information about the number of records processed, the amount of data read and written, and the CPU and memory usage of the workers. This information can be used to identify bottlenecks, optimize job performance, and troubleshoot issues.

**Parameters:**

*   `job_id` (str): The ID of the Dataflow job for which to retrieve metrics.

**Return Value:**

*   A dictionary containing the metrics for the specified Dataflow job. The structure of this dictionary is defined by the Dataflow API. It will contain a `metrics` key that is a list of metric objects.

**Example:**

```python
# Example usage:
job_id = "2023-10-27_12-00-00-1234567890" # Replace with an actual Dataflow job ID
metrics = get_job_metrics(job_id)

# Now you can access the metrics in the 'metrics' dictionary.
# if metrics and 'metrics' in metrics:
#     for metric in metrics['metrics']:
#         print(f"Metric Name: {metric['name']['name']}, Value: {metric['scalar']}")
```

```python
def _get_gcs_files(bucket_name: str, gcs_path: str, **context):
    logging.info(
        f"Listing files in [{bucket_name}/{gcs_path}]...")
    gcs_list_objects = GCSListObjectsOperator(
        task_id='list_gcs_files' + str(uuid.uuid4()),
        bucket=bucket_name,
        prefix=gcs_path,
        match_glob="**/*" + DELIMITER,
        impersonation_chain=None if TEST_RUN == "true" else DATAFLOW_SERVICE_ACCOUNT,
        dag=dag
    )
    files = gcs_list_objects.execute(context)
    logging.info(
        f"Found [{len(files)}] files in [{bucket_name}/{gcs_path}]")
    return files
```

### Function: `_get_gcs_files`

**Purpose:** This function lists files in a Google Cloud Storage (GCS) bucket under a specified path using the `GCSListObjectsOperator`.

**Business Logic:** This function provides a convenient way to retrieve a list of files from GCS. The returned list is used as an input to other tasks, such as moving files, processing data, or archiving data. The `match_glob` parameter allows filtering files based on a pattern, which can be useful for selecting specific types of files. The use of `impersonation_chain` is important for security, ensuring that the listing operation is performed with the appropriate service account credentials. Adding `uuid.uuid4()` helps ensure the task_id is unique.

**Parameters:**

*   `bucket_name` (str): The name of the GCS bucket.
*   `gcs_path` (str): The path within the GCS bucket to list files from.
*   `**context`: The Airflow context dictionary, which is required by the `GCSListObjectsOperator`.

**Return Value:**

*   A list of strings, where each string represents the name of a file found in the specified GCS bucket and path.

**Example:**

```python
# Example usage:
bucket_name = "my-data-bucket"
gcs_path = "landing/raw_data"

# Assuming 'dag' is defined elsewhere in your DAG file.
def my_task(**context):
    files = _get_gcs_files(bucket_name, gcs_path, **context)
    logging.info(f"Files found: {files}")

# In the DAG definition:
# my_task_instance = PythonOperator(
#     task_id='my_task',
#     python_callable=my_task,
#     provide_context=True,
#     dag=dag,
# )
```

```python
def _move_blobs(bucket_name: str, blob_names: list, destination_bucket_name: str,
                destination_prefix: str, **context):
    logging.info(f"Moving blobs from [{bucket_name}] to [{destination_bucket_name}/{destination_prefix}]")
    num_blobs = len(blob_names)
    time_millis = round(time.time() * 1000)
    tmp_file = f"/tmp/pnr{SUFFIX}_file_copy_{time_millis}.txt"
    with open(tmp_file, "a") as f:
        for i, blob_name in enumerate(blob_names):
            logging.info(
                f"[{i + 1}/{num_blobs}] Adding blob [{bucket_name}/{blob_name}]...")
            f.writelines(f"gs://{bucket_name}/{blob_name}\n")

    impersonation_opts = "" if TEST_RUN == "true" else f"-i {DATAFLOW_SERVICE_ACCOUNT}"
    gsutil_path = "/google-cloud-sdk/bin/" if TEST_RUN == "true" else ""
    gsutil_state_opts = f"-o 'GSUtil:state_dir=/tmp/pnr{SUFFIX}_gsutil_state_{time_millis}'"
    bash_cmd = f"cat {tmp_file} | {gsutil_path}gsutil {gsutil_state_opts} {impersonation_opts} -m mv -I 'gs://{destination_bucket_name}/{destination_prefix}/'"
    logging.info(f"Executing Bash command [{bash_cmd}]")
    file_copy_using_gsutil = BashOperator(
        task_id="file_copy_using_gsutil" + str(uuid.uuid4()),
        bash_command=bash_cmd
    )
    file_copy_using_gsutil.execute(context)
    os.remove(tmp_file)

    logging.info(f"Moved blobs from file [{tmp_file}] to [{destination_bucket_name}/{destination_prefix}]")
```

### Function: `_move_blobs`

**Purpose:** This function moves blobs (files) from one GCS bucket and path to another using the `gsutil mv` command executed via a `BashOperator`.

**Business Logic:**  This function efficiently moves multiple files in GCS. Instead of moving files one-by-one, it constructs a `gsutil mv` command that reads a list of files from a temporary file and moves them in parallel.  This approach significantly improves performance when dealing with a large number of files.  The function also handles impersonation using the `DATAFLOW_SERVICE_ACCOUNT` if the `TEST_RUN` variable is not set to "true". It uses a temporary file to store the list of files to move, which is then passed to the `gsutil mv` command. The `gsutil_state_opts` is configured to prevent concurrency and state related errors from the `gsutil` command. Adds a `uuid.uuid4` to the task_id to ensure uniqueness.

**Parameters:**

*   `bucket_name` (str): The name of the source GCS bucket.
*   `blob_names` (list): A list of blob names (file names) to move from the source bucket.
*   `destination_bucket_name` (str): The name of the destination GCS bucket.
*   `destination_prefix` (str): The prefix (path) in the destination bucket where the blobs should be moved.
*   `**context`: The Airflow context dictionary, which is required by the `BashOperator`.

**Return Value:**

*   None

**Example:**

```python
# Example usage:
source_bucket = "my-source-bucket"
blob_names = ["file1.txt", "file2.csv", "data/file3.json"]
destination_bucket = "my-destination-bucket"
destination_prefix = "archive/2023-10-27"

# Assuming 'dag' is defined elsewhere in your DAG file.
def my_task(**context):
    _move_blobs(source_bucket, blob_names, destination_bucket, destination_prefix, **context)

# In the DAG definition:
# my_task_instance = PythonOperator(
#     task_id='my_task',
#     python_callable=my_task,
#     provide_context=True,
#     dag=dag,
# )
```

```python
def _move_to_archive(**context):
    ti = context['ti']
    gcs_archive_bucket_name = ti.xcom_pull(key=TASK_PARAM_ARCHIVE_BUCKET_NAME, task_ids=TASK_SETUP_PROCESSING)
    gcs_archive_bucket_path = ti.xcom_pull(key=TASK_PARAM_ARCHIVE_BUCKET_PATH, task_ids=TASK_SETUP_PROCESSING)
    gcs_run_bucket_name = ti.xcom_pull(key=TASK_PARAM_RUN_BUCKET_NAME, task_ids=TASK_SETUP_PROCESSING)
    gcs_run_bucket_path = ti.xcom_pull(key=TASK_PARAM_RUN_BUCKET_PATH, task_ids=TASK_SETUP_PROCESSING)

    logging.info(f"Archive bucket name [{gcs_archive_bucket_name}]")
    logging.info(f"Archive bucket path [{gcs_archive_bucket_path}]")
    logging.info(f"Run bucket name [{gcs_run_bucket_name}]")
    logging.info(f"Run bucket path [{gcs_run_bucket_path}]")

    logging.info(
        f"Archiving files from [{gcs_run_bucket_name}/{gcs_run_bucket_path}] to [{gcs_archive_bucket_name}/{gcs_archive_bucket_path}]")

    processed_files = _get_gcs_files(gcs_run_bucket_name, gcs_run_bucket_path, **context)
    logging.info(f"Found [{len(processed_files)}] processed files in [{gcs_run_bucket_name}/{gcs_run_bucket_path}]")

    if len(processed_files) == 0:
        logging.error(f"No files in run path [{gcs_run_bucket_name}/{gcs_run_bucket_path}]")
        raise AirflowFailException(f"No files in run path [{gcs_run_bucket_name}/{gcs_run_bucket_path}]")

    per_hour_grouping = group_partitions_per_hour(processed_files, gcs_run_bucket_path + "/")

    for partition in per_hour_grouping:
        files_per_partition = per_hour_grouping[partition]
        logging.info(
            f"Moving files from partition [{partition}] to [{gcs_archive_bucket_name}/{gcs_archive_bucket_path}/{partition}/]")
        _move_blobs(gcs_run_bucket_name, files_per_partition, gcs_archive_bucket_name,
                    f"{gcs_archive_bucket_path}/{partition}", **context)
    logging.info(f"Processed [{len(per_hour_grouping)}] partitions")
```

### Function: `_move_to_archive`

**Purpose:** This function moves processed files from a "run" GCS bucket to an archive GCS bucket, organizing them into hourly partitions.

**Business Logic:** Archiving processed data is a common practice for data pipelines. This function automates this process, ensuring that data is stored for long-term retention and analysis. Grouping the files into hourly partitions makes it easier to manage and query the archived data. The function first retrieves the necessary bucket and path information from XComs, lists the files in the run path, and then moves the files to the archive bucket, organizing them by hour. The check for empty files ensures that an exception is thrown to prevent the archive task from completing when there are no files to process.

**Parameters:**

*   `**context`: The Airflow context dictionary, providing access to XComs and other relevant information.

**Return Value:**

*   None

**Example:**

```python
# Assuming 'dag' is defined elsewhere in your DAG file and that the XComs
# TASK_PARAM_ARCHIVE_BUCKET_NAME, TASK_PARAM_ARCHIVE_BUCKET_PATH,
# TASK_PARAM_RUN_BUCKET_NAME, and TASK_PARAM_RUN_BUCKET_PATH are set by a
# previous task.
def my_task(**context):
    _move_to_archive(**context)

# In the DAG definition:
# my_task_instance = PythonOperator(
#     task_id='my_task',
#     python_callable=my_task,
#     provide_context=True,
#     dag=dag,
# )
```

```python
def get_job_id(job_name):
    logging.info(job_name)
    jobs = list_jobs()
    logging.info("Jobs retrieved from dataflow are [{}]".format(jobs))
    job_id = None
    for job in jobs:
        job_nm = job["name"]
        if job_nm.startswith(job_name) and job["currentState"] == "JOB_STATE_DONE":
            job_id = job["id"]
            logging.info("job_id {} for current job {}".format(job_id, job_name))
            break;
        else:
            job_id= None
    return job_id
```

### Function: `get_job_id`

**Purpose:** This function retrieves the ID of a Dataflow job based on its name.

**Business Logic:** This function enables the DAG to identify a specific Dataflow job among all jobs in the project. It retrieves the Dataflow job name from the `list_jobs` function and verifies that it `startswith` the provided `job_name` and checks that the `currentState` is "JOB_STATE_DONE". It's used to find completed jobs for further processing or analysis. The function iterates through the list of jobs, comparing the job names and state, and returns the corresponding job ID.

**Parameters:**

*   `job_name` (str): The name (or the beginning of the name) of the Dataflow job to find.

**Return Value:**

*   The ID of the Dataflow job if found and `currentState` is "JOB_STATE_DONE".
*   `None` if no matching Dataflow job is found with the state `JOB_STATE_DONE`.

**Example:**

```python
# Example usage:
job_name_prefix = "my-dataflow-job"
job_id = get_job_id(job_name_prefix)

if job_id:
    print(f"Found Dataflow job with ID: {job_id}")
else:
    print(f"No Dataflow job found with name starting with: {job_name_prefix} and status JOB_STATE_DONE")
```

```python
def get_metric_service_client(target_service_account):
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    return monitoring_v3.MetricServiceClient()
```

### Function: `get_metric_service_client`

**Purpose:** This function creates and returns a Google Cloud Monitoring API client.

**Business Logic:** The Monitoring API client is used to interact with Google Cloud Monitoring, allowing you to create, read, and manage metrics.  This function centralizes the creation of the client, ensuring consistent configuration and simplifying metric-related operations within the DAG.

**Parameters:**

*   `target_service_account` (str): The target service account, though not explicitly used, suggests intent for future impersonation implementations. It's present likely for consistency with other `get_*_client` functions.

**Return Value:**

*   A `monitoring_v3.MetricServiceClient` object, ready to interact with the Google Cloud Monitoring API.

**Example:**

```python
# Example usage:
metric_client = get_metric_service_client(COMPOSER_SERVICE_ACCOUNT)

# Now you can use the 'metric_client' to interact with the Google Cloud Monitoring API.
# For example, to create a custom metric:
# from google.cloud import monitoring_v3
# project_name = f"projects/{PROJECT_ID}"
# series = monitoring_v3.TimeSeries()
# ...
# metric_client.create_time_series(name=project_name, time_series=[series])
```

```python
def _move_landing_to_staging(source_bucket: str, source_objects: list, destination_bucket: str, destination_path: str,
                             source_path: str, **context):
    logging.info(
        f"Moving [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]...")
    _move_blobs(source_bucket, source_objects, destination_bucket, destination_path, **context)
    logging.info(
        f"Moved [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]")
```

### Function: `_move_landing_to_staging`

**Purpose:** This function moves files from a landing GCS bucket to a staging GCS bucket.

**Business Logic:** This function implements a common pattern in data pipelines: moving data from a raw "landing" area to a "staging" area where it can be prepared for processing. This separation provides a clear boundary between raw and processed data. It reuses the `_move_blobs` function to perform the actual file movement.

**Parameters:**

*   `source_bucket` (str): The name of the GCS bucket where the landing files are located.
*   `source_objects` (list): A list of the names of the files to move from the landing bucket.
*   `destination_bucket` (str): The name of the GCS bucket where the staging files will be located.
*   `destination_path` (str): The path within the staging bucket where the files will be moved.
*   `source_path` (str): The path within the source bucket where the files are located.
*   `**context`: The Airflow context dictionary, which is required by the `_move_blobs` function.

**Return Value:**

*   None

**Example:**

```python
# Example usage:
source_bucket = "my-landing-bucket"
source_objects = ["data/file1.csv", "data/file2.json"]
destination_bucket = "my-staging-bucket"
destination_path = "raw/2023-10-27"
source_path = "data"

# Assuming 'dag' is defined elsewhere in your DAG file.
def my_task(**context):
    _move_landing_to_staging(source_bucket, source_objects, destination_bucket, destination_path, source_path, **context)

# In the DAG definition:
# my_task_instance = PythonOperator(
#     task_id='my_task',
#     python_callable=my_task,
#     provide_context=True,
#     dag=dag,
# )
```

```python
def getImpersonatedCredentials(target_scopes: list, target_service_account: str, target_project: str):
    from google.auth import _default
    source_credentials, project_id = _default.default(scopes=target_scopes)

    from google.auth import impersonated_credentials
    target_credentials = impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=f'{target_service_account}@{target_project}.iam.gserviceaccount.com',
        target_scopes=target_scopes,
        lifetime=600)
    return target_credentials
```

### Function: `getImpersonatedCredentials`

**Purpose:** This function generates Google Cloud credentials that impersonate a target service account. It is similar to `_get_impersonated_credentials` but formats the `target_principal` differently.

**Business Logic:** This function provides a way to obtain credentials that act as if they were directly obtained by the specified service account. Impersonation is essential for security, as it allows a service to assume the identity of another service account to perform actions on its behalf, adhering to the principle of least privilege. The function constructs the `target_principal` string using the format expected by the `impersonated_credentials.Credentials` class.

**Parameters:**

*   `target_scopes` (list): A list of OAuth scopes that the impersonated credentials should have.
*   `target_service_account` (str): The email address of the service account to impersonate (without the `@<project>.iam.gserviceaccount.com` suffix).
*   `target_project` (str): The Google Cloud project ID.

**Return Value:**

*   An `impersonated_credentials.Credentials` object representing the impersonated credentials.

**Example:**

```python
# Example usage:
target_scopes = ['https://www.googleapis.com/auth/bigquery']
target_service_account = 'my-bq-sa'
target_project = 'my-project'

credentials = getImpersonatedCredentials(target_scopes, target_service_account, target_project)

# Now you can use the 'credentials' object to authenticate with Google Cloud services,
# acting as the 'my-bq-sa@my-project.iam.gserviceaccount.com' service account.
# For example, to create a BigQuery client:
# from google.cloud import bigquery
# client = bigquery.
## UML Diagram
![Image](images/anotherDAG_img1.png)
## DAG FLOW
![Image](images/anotherDAG_img2.png)

