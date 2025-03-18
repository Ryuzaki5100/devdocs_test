# Generated Documentation with UML
```text
## Function Documentation

Here's the detailed documentation for each function, following their execution order and dependencies:

**1. `main._get_df_service()`**

```python
def _get_df_service():
    df_service = build("dataflow", "v1b3", cache_discovery=False)
    logging.info("df service [{}]".format(df_service))
    return df_service
```

**Description:** This function is responsible for creating and returning a Dataflow service client. It utilizes the `googleapiclient.discovery.build` function to construct the client, specifying the Dataflow API version ("v1b3") and disabling cache discovery. Disabling cache discovery is useful when running in environments where the API definition might change frequently.

**Business Logic:** This function establishes the connection to the Dataflow service, enabling the application to interact with Dataflow jobs, such as listing, creating, and monitoring them.

**Dependencies:** googleapiclient library is used here

**Cyclomatic Complexity:** Low. The function has a single path of execution.

**Pain Points:**
*   Error Handling: The function lacks explicit error handling. If the `build` function fails, the application might crash. A try-except block should be added to handle potential exceptions.
*   Version Hardcoding: The Dataflow API version "v1b3" is hardcoded. Consider using a configuration variable to allow for easier updates.

**Example Usage:**

```python
df_service = _get_df_service()
# Now you can use df_service to interact with Dataflow
```

**2. `main.get_metric_service_client(target_service_account)`**

```python
def get_metric_service_client(target_service_account: str):
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    return monitoring_v3.MetricServiceClient()
```

**Description:**  This function creates and returns a Google Cloud Monitoring service client. It instantiates `monitoring_v3.MetricServiceClient()` without explicitly using the `target_service_account`.
The `target_scopes` variable defines the authorization scopes needed to access Cloud Monitoring.
It appears that the `target_service_account` is not being correctly applied for authorization which might result in authentication issues.

**Business Logic:** This function helps to interact with Cloud Monitoring service that allows the application to create and manage custom metrics.
**Dependencies:** google cloud monitoring library is used here.

**Cyclomatic Complexity:** Low

**Pain Points:**
*   The target service account is not utilized, which might cause authentication errors
*   Version Hardcoding: The Monitoring API version "v3" is implicitly used by importing `monitoring_v3`. Consider using a configuration variable to allow for easier updates.

**Example Usage:**

```python
metric_client = get_metric_service_client("service_account@example.com")
# Now use metric_client to create or manage metrics
```

**3. `main._get_default_or_from_dag_run(default_value, dag_key, dag_run_conf)`**

```python
def _get_default_or_from_dag_run(default_value: str, dag_key, dag_run_conf):
    if dag_run_conf is not None and dag_key in dag_run_conf:
        return dag_run_conf[dag_key]
    return default_value
```

**Description:** This function retrieves a value either from the `dag_run_conf` (DAG run configuration) if it exists, or falls back to a `default_value`. This is a common pattern in Airflow DAGs to allow users to override default parameters when triggering a DAG run.

**Business Logic:** The function provides a way to prioritize user-provided configurations over default settings, making the DAG more flexible and configurable.

**Dependencies:** None.

**Cyclomatic Complexity:** Low. The function has a simple conditional structure.

**Pain Points:** None. The function is straightforward and well-defined.

**Example Usage:**

```python
default_bucket = "my-default-bucket"
dag_run_config = {"bucket_name": "user-provided-bucket"}
bucket_name = _get_default_or_from_dag_run(default_bucket, "bucket_name", dag_run_config)
# bucket_name will be "user-provided-bucket"

dag_run_config = None
bucket_name = _get_default_or_from_dag_run(default_bucket, "bucket_name", dag_run_config)
# bucket_name will be "my-default-bucket"
```

**4. `main.create_custom_metrics(metric_type, project_id, resource_type, value_type, val)`**

```python
def create_custom_metrics(metric_type: str, project_id: str, resource_type: str, value_type: str, val):
    try:
        client = get_metric_service_client(COMPOSER_SERVICE_ACCOUNT)
        project_name = f"projects/{project_id}"
        series = monitoring_v3.TimeSeries()
        series.metric.type = CUSTOM_METRIC_DOMAIN + "/" + metric_type
        series.metric.labels['application_name'] = DAGID
        series.metric.labels['workflow_name'] = DAGID
        series.resource.type = resource_type
        series.resource.labels["project_id"] = project_id
        series.resource.labels["workflow_name"] = DAGID
        series.resource.labels["location"] = "us-central1"
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10 ** 9)
        interval = monitoring_v3.TimeInterval(
            {"end_time": {"seconds": seconds, "nanos": nanos}}
        )
        point = monitoring_v3.Point({"interval": interval, "value": {value_type: val}})
        series.points = [point]
        client.create_time_series(name=project_name, time_series=[series])
    except Exception as ex:
        logging.error("Error [{}] occurred while inserting/creating custom metric".format(str(ex)))
```

**Description:** This function creates and publishes custom metrics to Google Cloud Monitoring. It constructs a `TimeSeries` object, which represents a series of data points for a specific metric. The metric type, project ID, resource type, value type, and value are provided as input. The function utilizes `get_metric_service_client` to obtain a Monitoring service client.

**Business Logic:** This function allows for tracking custom performance indicators and events within the DAG, providing valuable insights into its behavior and performance.

**Dependencies:**

*   `get_metric_service_client`
*   `google.cloud.monitoring_v3`
*   `time`

**Cyclomatic Complexity:** Moderate. The function has a `try-except` block, increasing complexity slightly.

**Pain Points:**

*   Hardcoded Location: The `location` resource label is hardcoded to "us-central1". This should be configurable.
*   Limited Value Types: The function only supports a single `value_type`. It could be extended to handle different value types (e.g., `int64_value`, `double_value`, `string_value`) more dynamically.
*   Inconsistent Metric Labels: Labels could be more descriptive and configurable.

**Example Usage:**

```python
create_custom_metrics(
    metric_type="my_custom_metric",
    project_id="my-gcp-project",
    resource_type="cloud_composer_environment",
    value_type="int64_value",
    val=123
)
```

**5. `main._get_impersonated_credentials(target_scopes, target_service_account)`**

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

**Description:** This function obtains impersonated credentials for a given `target_service_account`. It first retrieves the default credentials using `google.auth._default.default` and then uses these credentials to create impersonated credentials using `google.auth.impersonated_credentials.Credentials`. Impersonation allows the application to act as the specified service account.

**Business Logic:** Impersonation is often used to grant specific permissions to a service account, limiting the application's access to only the necessary resources.

**Dependencies:**

*   `google.auth`

**Cyclomatic Complexity:** Low. The function has a single path of execution.

**Pain Points:**

*   Hardcoded Lifetime: The credential lifetime is hardcoded to 60 minutes (60 * 60 seconds). Consider making this configurable.
*   Error Handling: The function lacks explicit error handling. Exceptions during credential retrieval or impersonation should be handled gracefully.

**Example Usage:**

```python
target_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
target_service_account = "my-service-account@my-project.iam.gserviceaccount.com"
credentials = _get_impersonated_credentials(target_scopes, target_service_account)
# Use the credentials to authenticate with other Google Cloud services
```

**6. `main.getImpersonatedCredentials(target_scopes, target_service_account, target_project)`**

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

**Description:**  This function also retrieves impersonated credentials for a specified `target_service_account`, but it explicitly constructs the target principal using the `target_project`.

**Business Logic:** It also performs service account impersonation for a specific project.

**Dependencies:**

*   `google.auth`

**Cyclomatic Complexity:** Low

**Pain Points:**
*   Hardcoded Lifetime: Credential lifetime is hardcoded to 10 minutes (600 seconds). Make this configurable.
*   Error Handling: Lack of error handling

**Example Usage:**

```python
target_scopes = ["https://www.googleapis.com/auth/bigquery"]
target_service_account = "my-service-account"
target_project = "my-gcp-project"
credentials = getImpersonatedCredentials(target_scopes, target_service_account, target_project)
# Now use the credentials to access BigQuery
```

**7. `main._setup_processing(**context)`**

```python
def _setup_processing(**context):
    logging.info(f"Starting DAG [{DAGID}-{RELEASE_RAW}]")
    logging.info("Preparing partition")
    logging.info(f"Context [{context}]")
    execution_dt_utc = context["logical_date"]
    logging.info(f"Execution datetime [{execution_dt_utc}] UTC")

    task_instance = context["task_instance"]
    dag_run = context["dag_run"]
    dag_run_conf = dag_run.conf if dag_run else None

    gcs_landing_bucket_name = _get_default_or_from_dag_run(GCS_LANDING_BUCKET_NAME, DAG_PARAM_GCS_LANDING_BUCKET_NAME,
                                                           dag_run_conf)
    gcs_landing_bucket_path = _get_default_or_from_dag_run(GCS_LANDING_BUCKET_PATH, DAG_PARAM_GCS_LANDING_BUCKET_PATH,
                                                           dag_run_conf)
    gcs_archive_bucket_name = _get_default_or_from_dag_run(GCS_ARCHIVE_BUCKET_NAME, DAG_PARAM_GCS_ARCHIVE_BUCKET_NAME,
                                                           dag_run_conf)
    gcs_archive_bucket_path = _get_default_or_from_dag_run(GCS_ARCHIVE_BUCKET_PATH, DAG_PARAM_GCS_ARCHIVE_BUCKET_PATH,
                                                           dag_run_conf)
    gcs_staging_bucket_name = _get_default_or_from_dag_run(GCS_STAGING_BUCKET_NAME, DAG_PARAM_GCS_STAGING_BUCKET_NAME,
                                                           dag_run_conf)
    gcs_staging_bucket_path = _get_default_or_from_dag_run(GCS_STAGING_BUCKET_PATH, DAG_PARAM_GCS_STAGING_BUCKET_PATH,
                                                           dag_run_conf)
    num_past_hours = _get_default_or_from_dag_run(DEFAULT_NUM_HOURS, DAG_PARAM_NUM_PAST_HOURS, dag_run_conf)


    logging.info(f"Landing bucket name [{gcs_landing_bucket_name}]")
    logging.info(f"Landing bucket path [{gcs_landing_bucket_path}]")
    logging.info(f"Staging bucket name [{gcs_staging_bucket_name}]")
    logging.info(f"Staging bucket path [{gcs_staging_bucket_path}]")
    logging.info(f"Archive bucket name [{gcs_archive_bucket_name}]")
    logging.info(f"Archive bucket path [{gcs_archive_bucket_path}]")
    logging.info(f"Num past hours [{num_past_hours}]")

    if dag_run_conf is not None and DAG_PARAM_RUN_ID in dag_run_conf:
        run_id = dag_run_conf[DAG_PARAM_RUN_ID]
        reprocessing_flag = True
        logging.info(f"Using RUN ID from user [{run_id}]")
    else:
        run_id = f"{execution_dt_utc.year:04}{execution_dt_utc.month:02}{execution_dt_utc.day:02}{execution_dt_utc.hour:02}{execution_dt_utc.minute:02}"
        reprocessing_flag = False
        logging.info(f"Creating new RUN ID [{run_id}]")

    gcs_run_path = f"{gcs_staging_bucket_path}/{run_id}"
    gcs_run_full_path = f"{gcs_staging_bucket_name}/{gcs_run_path}"
    logging.info(f"Full RUN path on GCS [{gcs_run_full_path}]")

    job_name = f"{DF_JOB_NAME}-{run_id}"
    logging.info(f"Job name [{job_name}]")

    task_instance.xcom_push(key=TASK_PARAM_LANDING_BUCKET_NAME, value=gcs_landing_bucket_name)
    task_instance.xcom_push(key=TASK_PARAM_LANDING_BUCKET_PATH, value=gcs_landing_bucket_path)
    task_instance.xcom_push(key=TASK_PARAM_ARCHIVE_BUCKET_NAME, value=gcs_archive_bucket_name)
    task_instance.xcom_push(key=TASK_PARAM_ARCHIVE_BUCKET_PATH, value=gcs_archive_bucket_path)
    task_instance.xcom_push(key=TASK_PARAM_RUN_BUCKET_NAME, value=gcs_staging_bucket_name)
    task_instance.xcom_push(key=TASK_PARAM_RUN_BUCKET_PATH, value=gcs_run_path)
    task_instance.xcom_push(key=TASK_PARAM_RUN_PATH_FULL, value=gcs_run_full_path)
    task_instance.xcom_push(key=TASK_PARAM_REPROCESSING, value=reprocessing_flag)
    task_instance.xcom_push(key=TASK_PARAM_JOB_NAME, value=job_name)
    task_instance.xcom_push(key=TASK_PARAM_NUM_PAST_HOURS, value=num_past_hours)
```

**Description:** This function sets up the processing environment for the DAG. It retrieves configuration parameters from the DAG run configuration or uses default values. It generates a unique `run_id`, determines whether reprocessing is required, and constructs the full GCS path for the current run. Finally, it pushes these parameters to XCom for use by downstream tasks.

**Business Logic:** This function centralizes the initialization of processing parameters, ensuring consistency and configurability across the DAG.

**Dependencies:**

*   `_get_default_or_from_dag_run`
*   Airflow context (provided via `**context`)
*   XCom

**Cyclomatic Complexity:** Moderate. The function has conditional logic for handling DAG run configurations and determining the `run_id`.

**Pain Points:**

*   Hardcoded Constants: Many constants (e.g., `GCS_LANDING_BUCKET_NAME`, `DAG_PARAM_GCS_LANDING_BUCKET_NAME`) are hardcoded. These should be defined in a configuration file or environment variables.
*   Excessive XCom Pushes: Pushing so many parameters to XCom can lead to performance issues, especially in complex DAGs. Consider grouping related parameters into a single XCom value or using a more efficient data storage mechanism.

**Example Usage:**

```python
# This function is typically called from an Airflow PythonOperator
# The context is automatically passed by Airflow
_setup_processing(**context)
```

**8. `main._is_reprocessing(**context)`**

```python
def _is_reprocessing(**context):
    reprocess_flag = context['ti'].xcom_pull(key=TASK_PARAM_REPROCESSING, task_ids=TASK_SETUP_PROCESSING)
    logging.info(f"Is reprocessing required [{reprocess_flag}]")
    return TASK_PREPARE_STAGING if not reprocess_flag else TASK_SKIP_PREPARE_STAGING
```

**Description:** This function determines whether reprocessing is required based on the value of the `TASK_PARAM_REPROCESSING` XCom variable, which was set by `_setup_processing`. It returns the task ID of the next task to be executed, depending on the `reprocess_flag`.

**Business Logic:** This function implements a conditional execution path within the DAG, allowing it to either prepare the staging area or skip this step if reprocessing is not needed.

**Dependencies:**

*   Airflow context (provided via `**context`)
*   XCom

**Cyclomatic Complexity:** Low. The function has a simple conditional structure.

**Pain Points:**

*   Reliance on XCom: The function relies heavily on XCom for inter-task communication. This can make the DAG harder to understand and debug.

**Example Usage:**

```python
# This function is typically called from an Airflow BranchPythonOperator
# The context is automatically passed by Airflow
next_task = _is_reprocessing(**context)
# The DAG will then execute the task specified by next_task
```

**9. `main._cleanup_xcom(context, session)`**

```python
def _cleanup_xcom(context, session=None):
    dag_id = context["dag"].dag_id
    session.query(XCom).filter(XCom.dag_id == dag_id).delete()
```

**Description:** This function cleans up XCom entries associated with the current DAG. It retrieves the DAG ID from the context and then deletes all XCom entries with that DAG ID from the Airflow metadata database.

**Business Logic:** Cleaning up XCom is important to prevent the XCom table from growing excessively, which can negatively impact Airflow performance.

**Dependencies:**

*   Airflow context (provided via `context`)
*   Airflow `XCom` model
*   SQLAlchemy session

**Cyclomatic Complexity:** Low.

**Pain Points:**

*   Direct Database Access: The function directly accesses the Airflow metadata database. This can be risky, as changes to the database schema could break the function. It is generally recommended to use the Airflow API for interacting with the metadata database.
*   Lack of Error Handling: The function lacks error handling. If the database operation fails, the function might crash.

**Example Usage:**

```python
# This function needs to be called with a session object, typically from an Airflow operator
# session = settings.Session()
# _cleanup_xcom(context, session=session)
# session.close()
```

**10. `main._move_blobs(bucket_name, blob_names, destination_bucket_name, destination_prefix, **context)`**

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

**Description:** This function moves blobs (files) from one GCS bucket/path to another. It constructs a `gsutil` command to perform the move operation, utilizing a temporary file to pass the list of blobs to `gsutil`. The `gsutil` command is executed using an Airflow `BashOperator`.

**Business Logic:** This function provides a mechanism for moving data between different GCS locations, such as from a landing zone to a staging area or from a staging area to an archive.

**Dependencies:**

*   `BashOperator`
*   `gsutil` command-line tool
*   `uuid`
*   `time`
*   `os`

**Cyclomatic Complexity:** Moderate. The function involves file I/O, string manipulation, and execution of an external command.

**Pain Points:**

*   Temporary File: Using a temporary file to pass the list of blobs to `gsutil` is inefficient and can be problematic if the number of blobs is very large. Consider using `gsutil rsync` or a custom Python implementation for moving blobs.
*   BashOperator: The function relies on a `BashOperator`, which can be less reliable and harder to debug than a native Python implementation.
*   gsutil dependency: It requires gsutil to be installed.
*   Error Handling: The function lacks robust error handling. The `BashOperator` might fail, but the function doesn't explicitly handle this case.
*   Impersonation Logic: The logic for handling impersonation using `-i` option is conditional.
*   Temporary file clean up: `os.remove(tmp_file)` might fail because of permission issues.

**Example Usage:**

```python
source_bucket = "my-source-bucket"
blob_names = ["file1.txt", "file2.csv"]
destination_bucket = "my-destination-bucket"
destination_prefix = "archive"
_move_blobs(source_bucket, blob_names, destination_bucket, destination_prefix, **context)
```

**11. `main._get_gcs_files(bucket_name, gcs_path, **context)`**

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

**Description:** This function lists files within a specified GCS bucket and path. It utilizes the Airflow `GCSListObjectsOperator` to perform the listing operation. The `match_glob` parameter is used to filter the files based on a pattern.

**Business Logic:** This function allows the DAG to discover files in GCS, which is often a necessary step before processing them.

**Dependencies:**

*   `GCSListObjectsOperator`
*   `uuid`

**Cyclomatic Complexity:** Low. The function primarily involves instantiating and executing an Airflow operator.

**Pain Points:**

*   Reliance on Airflow Operator: Similar to `_move_blobs`, relying on a custom Python implementation provides better control and error handling.
*   Error Handling: The function doesn't explicitly handle potential exceptions during file listing.
*   Impersonation Logic: The function uses conditional logic to handle impersonation.

**Example Usage:**

```python
bucket_name = "my-bucket"
gcs_path = "data/landing"
files = _get_gcs_files(bucket_name, gcs_path, **context)
# files will be a list of file names in the specified bucket and path
```

**12. `main._move_landing_to_staging(source_bucket, source_objects, destination_bucket, destination_path, source_path, **context)`**

```python
def _move_landing_to_staging(source_bucket: str, source_objects: list, destination_bucket: str, destination_path: str,
                             source_path: str, **context):
    logging.info(
        f"Moving [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]...")
    _move_blobs(source_bucket, source_objects, destination_bucket, destination_path, **context)
    logging.info(
        f"Moved [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]")
```

**Description:**  This function acts as a wrapper around `_move_blobs` to specifically move files from a landing area to a staging area in GCS.

**Business Logic:**  It moves files from the landing bucket to the staging bucket.

**Dependencies:**

*   `_move_blobs`

**Cyclomatic Complexity:** Low

**Pain Points:**
*   It tightly coupled with moving to landing to staging
*   It depends on the `_move_blobs` with all its issues.

**Example Usage:**

```python
source_bucket = "my-landing-bucket"
source_objects = ["file1.txt", "file2.csv"]
destination_bucket = "my-staging-bucket"
destination_path = "staging/run1"
source_path = "landing"
_move_landing_to_staging(source_bucket, source_objects, destination_bucket, destination_path, source_path, **context)
```

**13. `main.get_job_metrics(job_id)`**

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

**Description:** This function retrieves metrics for a specific Dataflow job using the Dataflow API. It utilizes the `_get_df_service` function to obtain a Dataflow service client.

**Business Logic:**  This function allows monitoring the performance and progress of Dataflow jobs.

**Dependencies:**

*   `_get_df_service`

**Cyclomatic Complexity:** Low. The function involves a single API call.

**Pain Points:**

*   Error Handling: Lack of error handling

**Example Usage:**

```python
job_id = "1234567890"
metrics = get_job_metrics(job_id)
# metrics will be a dictionary containing the Dataflow job metrics
```

**14. `main.get_bq_impersonated_client(target_service_account, target_project)`**

```python
def get_bq_impersonated_client(target_service_account: str, target_project: str):
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform',
                     'https://www.googleapis.com/auth/bigquery']
    return bigquery.Client(project=target_project, credentials=getImpersonatedCredentials(target_scopes, target_service_account, target_project))
```

**Description:** This function obtains a BigQuery client with impersonated credentials. It utilizes `getImpersonatedCredentials` to obtain the credentials and then creates a `bigquery.Client` object using these credentials.

**Business Logic:**  This function allows the DAG to interact with BigQuery using the identity of the specified service account, ensuring proper authorization.

**Dependencies:**

*   `getImpersonatedCredentials`
*   `google.cloud.bigquery`

**Cyclomatic Complexity:** Low.

**Pain Points:**
*   The dependency on  `getImpersonatedCredentials`
*   Error Handling: Lack of error handling

**Example Usage:**

```python
target_service_account = "my-service-account"
target_project = "my-gcp-project"
bq_client = get_bq_impersonated_client(target_service_account, target_project)
# Now use bq_client to interact with BigQuery
```

**15. `main.list_jobs()`**

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

**Description:** This function lists all Dataflow jobs in a specific project and region. It retrieves the Dataflow service client using `_get_df_service` and then calls the `jobs().list()` API method.

**Business Logic:**  This function is used to discover existing Dataflow jobs, which can be useful for monitoring, management, or coordination between DAGs.

**Dependencies:**

*   `_get_df_service`

**Cyclomatic Complexity:** Low.

**Pain Points:**
*   Error Handling: Lack of error handling

**Example Usage:**

```python
jobs = list_jobs()
# jobs will be a list of Dataflow job dictionaries
```

**16. `main._get_storage_client(target_service_account, target_project)`**

```python
def _get_storage_client(target_service_account: str, target_project: str):
    from google.cloud import storage
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    credentials = None if TEST_RUN == "true" else _get_impersonated_credentials(target_scopes,
                                                                                target_service_account)
    return storage.Client(project=target_project,
                          credentials=credentials)
```

**Description:** This function retrieves a Google Cloud Storage client, optionally with impersonated credentials. If `TEST_RUN` is "true", it returns a client with default credentials; otherwise, it retrieves impersonated credentials using `_get_impersonated_credentials` and creates a client with those credentials.

**Business Logic:** It helps to interact with cloud storage with/without impersonation.

**Dependencies:**

*   `_get_impersonated_credentials` (conditionally)
*   `google.cloud.storage`

**Cyclomatic Complexity:** Low.

**Pain Points:**

*   Conditional Logic: Conditional logic based on a global `TEST_RUN`.
*   Error Handling: Lack of error handling

**Example Usage:**

```python
target_service_account = "my-service-account"
target_project = "my-gcp-project"
storage_client = _get_storage_client(target_service_account, target_project)
# Now use storage_client to interact with GCS
```

**17. `main.get_time_diff_between_processed_tm_vs_current_time()`**

```python
def get_time_diff_between_processed_tm_vs_current_time():
    client = get_bq_impersonated_client(service_account_name, PIPELINE_PROJECT_ID)
    try:
        time_difference = """
                                SELECT
                                    MAX(ingest_ts) max_ingest_ts,
                                    CURRENT_TIMESTAMP() AS current_ts,
                                    TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(ingest_ts), MINUTE) diff_in_mins
                                FROM
                                  {0}.{1}.{2}  WHERE ingest_ts is not null
                                """.format(PIPELINE_PROJECT_ID, FRESHNESS_CHECK_DATASET_NAME, FRESHNESS_CHECK_TABLE
## UML Diagram
![Image](images/anotherDAG_after_img1.png)
## DAG FLOW
![Image](images/anotherDAG_after_img2.png)

