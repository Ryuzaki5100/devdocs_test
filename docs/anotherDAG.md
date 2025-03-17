# Generated Documentation with UML
```text
## Function Documentation

This document provides detailed documentation for each function in the provided code, following the logical order of execution and dependencies. It also includes explanations of the business logic, potential improvements, and addresses cyclomatic complexity.

**1. `_get_impersonated_credentials(target_scopes, target_service_account)`**

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

*   **Purpose:** This function obtains Google Cloud credentials that are impersonated from a target service account. Impersonation allows a principal (e.g., the Airflow worker) to act as another service account, granting access to resources that the target service account has permissions for.
*   **Parameters:**
    *   `target_scopes` (list): A list of OAuth scopes that the impersonated credentials should have. Scopes define the level of access granted (e.g., read-only, read-write) to Google Cloud services.
    *   `target_service_account` (str): The email address of the service account to impersonate.
*   **Logic:**
    1.  It first retrieves the default credentials using `google.auth._default.default()`. These are the credentials that the environment (e.g., the Airflow worker) is already authenticated with.
    2.  Then, it creates `google.auth.impersonated_credentials.Credentials` object. This object wraps the source credentials and configures them to act as the `target_service_account`.
    3.  It sets a lifetime for the impersonated credentials. In this case, it is set to 1 hour (60 * 60 seconds).
*   **Return Value:** `target_credentials` (google.auth.credentials.Credentials): The impersonated credentials object.
*   **Business Logic:** This function enables secure access to Google Cloud resources by using the principle of least privilege. Instead of granting broad permissions to the Airflow worker, it uses impersonation to temporarily assume the identity of a service account with specific, limited permissions.
*   **Dependencies:** `google.auth`, `google.auth.impersonated_credentials`.
*   **Potential Improvements:**
    *   The lifetime of the credentials could be configurable via an environment variable or DAG parameter.
    *   Error handling and retry logic could be added to handle cases where the impersonation fails.
*   **Cyclomatic Complexity:** Low. The function has a straightforward control flow with no complex branching.
*   **Pain Points:** No immediate pain points are apparent in the code itself. However, the security configuration related to service account permissions and scope management can be a complex area.

**2. `getImpersonatedCredentials(target_scopes, target_service_account, target_project)`**

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

*   **Purpose:** Similar to `_get_impersonated_credentials`, this function obtains impersonated Google Cloud credentials.  However, it constructs the `target_principal` differently.
*   **Parameters:**
    *   `target_scopes` (list): A list of OAuth scopes for the impersonated credentials.
    *   `target_service_account` (str): The name of the service account to impersonate (without the full email address).
    *   `target_project` (str): The project ID where the service account resides.
*   **Logic:**
    1.  Retrieves default credentials and the project ID.
    2.  Constructs the fully qualified service account email address by combining `target_service_account`, `target_project`, and the `iam.gserviceaccount.com` domain.
    3.  Creates `impersonated_credentials.Credentials` using the source credentials, fully qualified target principal, and specified scopes.
    4.  Sets a lifetime of 600 seconds (10 minutes) for the credentials.
*   **Return Value:** `target_credentials` (google.auth.credentials.Credentials): The impersonated credentials object.
*   **Business Logic:**  This function simplifies the construction of the `target_principal` by taking the service account name and project ID as separate parameters. It's useful when the caller knows the service account name and project ID but doesn't want to manually construct the full email address.
*   **Dependencies:** `google.auth`, `google.auth.impersonated_credentials`.
*   **Potential Improvements:**
    *   Consistent lifetime across impersonation functions (consider using a shared constant or configuration).
    *   Error handling and retry logic.
*   **Cyclomatic Complexity:** Low.
*   **Pain Points:** Potential for confusion if the caller provides an incorrect service account name or project ID, leading to failed impersonation.  Input validation could help.

**3. `_get_df_service()`**

```python
def _get_df_service():
    df_service = build("dataflow", "v1b3", cache_discovery=False)
    logging.info("df service [{}]".format(df_service))
    return df_service
```

*   **Purpose:** Creates and returns a Google Cloud Dataflow service client.
*   **Parameters:** None
*   **Logic:**
    1.  Uses the `googleapiclient.discovery.build()` function to create a Dataflow service client.  Specifies the API name ("dataflow"), API version ("v1b3"), and disables API discovery caching (`cache_discovery=False`).
    2.  Logs the created service client object.
*   **Return Value:** `df_service` (googleapiclient.discovery.Resource): The Dataflow service client.
*   **Business Logic:** This function encapsulates the creation of the Dataflow service client, making it easier to interact with the Dataflow API. Disabling API discovery caching ensures that the client uses the latest API definition.
*   **Dependencies:** `googleapiclient.discovery.build`.
*   **Potential Improvements:**
    *   Consider adding retry logic in case the `build()` function fails.
    *   The API version could be configurable via an environment variable.
*   **Cyclomatic Complexity:** Low.
*   **Pain Points:** No apparent pain points.

**4. `get_job_metrics(job_id)`**

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

*   **Purpose:** Retrieves metrics for a specific Dataflow job.
*   **Parameters:**
    *   `job_id` (str): The ID of the Dataflow job.
*   **Logic:**
    1.  Calls `_get_df_service()` to obtain a Dataflow service client.
    2.  Uses the client to call the `projects.locations.jobs.getMetrics` API method, providing the project ID, region, and job ID.
    3.  Executes the API call and stores the response.
*   **Return Value:** `metrics` (dict): A dictionary containing the job metrics. The structure of the dictionary depends on the Dataflow API response.
*   **Business Logic:** This function allows monitoring of Dataflow job performance and resource utilization by retrieving metrics such as CPU usage, memory consumption, and data processed.
*   **Dependencies:** `_get_df_service()`, `PIPELINE_PROJECT_ID`, `DATAFLOW_REGION`.
*   **Potential Improvements:**
    *   Error handling (e.g., handling cases where the job ID is invalid or the API call fails).
    *   Consider adding pagination to handle cases where the number of metrics is very large.
*   **Cyclomatic Complexity:** Low.
*   **Pain Points:** No apparent pain points.

**5. `_move_blobs(bucket_name, blob_names, destination_bucket_name, destination_prefix)`**

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

*   **Purpose:** Moves multiple blobs (files) from one Google Cloud Storage (GCS) location to another using the `gsutil` command-line tool. This function creates a temporary file with a list of the files to move, then uses `gsutil mv -I` to move them in bulk.
*   **Parameters:**
    *   `bucket_name` (str): The name of the GCS bucket where the blobs are currently located.
    *   `blob_names` (list): A list of blob names (filenames) to move.
    *   `destination_bucket_name` (str): The name of the GCS bucket to move the blobs to.
    *   `destination_prefix` (str): The prefix (directory path) within the destination bucket where the blobs should be moved.
    *   `context` (dict):  Airflow context dictionary, used to execute the `BashOperator`.
*   **Logic:**
    1.  Logs the source and destination locations.
    2.  Creates a temporary file with a list of the GCS URIs (e.g., `gs://bucket/path/to/file`) of the blobs to move.
    3.  Constructs a `gsutil` command to move the blobs.
        *   It conditionally adds impersonation options (`-i DATAFLOW_SERVICE_ACCOUNT`) if `TEST_RUN` is not "true".
        *   It uses `gsutil mv -I` to read the list of blobs to move from the temporary file.  `-m` enables multi-threading.
        *   It also uses `gsutil_state_opts` to make gsutil store the state file in a directory.
    4.  Creates an Airflow `BashOperator` to execute the `gsutil` command.
    5.  Executes the `BashOperator`.
    6.  Removes the temporary file.
*   **Return Value:** None
*   **Business Logic:** This function provides an efficient way to move multiple blobs within GCS. Using `gsutil mv -I` and multithreading (`-m`) allows for parallel transfer of files, improving performance compared to moving files one by one.
*   **Dependencies:** `gsutil`, `BashOperator`, `uuid`, `os`, `time`, `logging`, `SUFFIX`, `TEST_RUN`, `DATAFLOW_SERVICE_ACCOUNT`.
*   **Potential Improvements:**
    *   Implement error handling and retry logic for the `gsutil` command.
    *   Consider using the Google Cloud Storage client library directly instead of relying on the `gsutil` command-line tool, which reduces the dependency on external tools.
    *   Implement a maximum size limit for the temporary file to prevent issues with very large lists of blobs.
    *   Consider using `tempfile.NamedTemporaryFile` with `delete=False` to create the temporary file, which is more secure and handles cleanup better.
*   **Cyclomatic Complexity:** Moderate.  The conditional logic for impersonation increases the complexity slightly.
*   **Pain Points:**
    *   Relying on `gsutil` introduces a dependency on an external tool and its configuration.
    *   The temporary file approach can be inefficient for extremely large numbers of blobs.
    *   Lack of robust error handling.

**6. `_move_landing_to_staging(source_bucket, source_objects, destination_bucket, destination_path, source_path)`**

```python
def _move_landing_to_staging(source_bucket: str, source_objects: list, destination_bucket: str, destination_path: str,
                             source_path: str, **context):
    logging.info(
        f"Moving [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]...")
    _move_blobs(source_bucket, source_objects, destination_bucket, destination_path, **context)
    logging.info(
        f"Moved [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]")
```

*   **Purpose:**  Moves files from a "landing" GCS location to a "staging" GCS location. It acts as a wrapper around `_move_blobs`.
*   **Parameters:**
    *   `source_bucket` (str): The name of the source GCS bucket.
    *   `source_objects` (list): A list of blob names in the source bucket to move.
    *   `destination_bucket` (str): The name of the destination GCS bucket.
    *   `destination_path` (str): The prefix (directory path) within the destination bucket to move the files to.
    *   `source_path` (str):  The prefix (directory path) within the source bucket where the files are located.
    *   `context` (dict): Airflow context dictionary.
*   **Logic:**
    1.  Logs the source and destination locations.
    2.  Calls `_move_blobs` to perform the actual file movement.
    3.  Logs the completion of the file movement.
*   **Return Value:** None
*   **Business Logic:**  This function implements a common data pipeline pattern: moving data from a raw landing zone to a staging area where it can be pre-processed or validated before further processing.
*   **Dependencies:** `_move_blobs`.
*   **Potential Improvements:**
    *   Consider adding input validation to ensure that the `source_objects` list is not empty.
*   **Cyclomatic Complexity:** Low.
*   **Pain Points:**  The function is very simple and doesn't introduce any new pain points beyond those of `_move_blobs`.

**7. `get_metric_service_client(target_service_account)`**

```python
def get_metric_service_client(target_service_account: str):
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    return monitoring_v3.MetricServiceClient()
```

*   **Purpose:** Creates and returns a Google Cloud Monitoring service client.
*   **Parameters:**
    *   `target_service_account` (str):  This parameter is present but not actually used. It might be intended for future use to create an impersonated client.
*   **Logic:**
    1.  Defines a list of OAuth scopes required for the Monitoring API.
    2.  Creates a `monitoring_v3.MetricServiceClient` object directly.
*   **Return Value:** `monitoring_v3.MetricServiceClient`: The Monitoring service client.
*   **Business Logic:**  This function provides a centralized way to obtain a Monitoring service client for publishing custom metrics.
*   **Dependencies:** `monitoring_v3.MetricServiceClient`.
*   **Potential Improvements:**
    *   Implement impersonation using the `target_service_account` and the scopes to create the client.  This would improve security by allowing the client to run with the specific permissions of the service account.
    *   Add error handling and retry logic.
*   **Cyclomatic Complexity:** Low.
*   **Pain Points:** The `target_service_account` parameter is misleading as it's not currently used.

**8. `_get_gcs_files(bucket_name, gcs_path)`**

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

*   **Purpose:** Lists files in a Google Cloud Storage (GCS) bucket and path using Airflow's `GCSListObjectsOperator`.
*   **Parameters:**
    *   `bucket_name` (str): The name of the GCS bucket.
    *   `gcs_path` (str): The path (prefix) within the bucket to list files from.
    *   `context` (dict): Airflow context dictionary.
*   **Logic:**
    1.  Logs the bucket and path being listed.
    2.  Creates a `GCSListObjectsOperator` task.
        *   `task_id` is dynamically generated using `uuid.uuid4()`.
        *   `bucket` and `prefix` are set to the provided values.
        *   `match_glob` uses the `DELIMITER` to match only the directories and not specific files.
        *   `impersonation_chain` uses the `DATAFLOW_SERVICE_ACCOUNT` for impersonation, if `TEST_RUN` is not "true".
    3.  Executes the `GCSListObjectsOperator` using the provided `context`.
    4.  Logs the number of files found.
*   **Return Value:** `files` (list): A list of strings, where each string is the name of a file found in the specified GCS location.
*   **Business Logic:** This function provides a way to programmatically discover files in GCS, which is a common requirement in data pipelines for tasks such as processing newly arrived data.  The `match_glob` parameter allows for filtering the files based on a pattern.
*   **Dependencies:** `GCSListObjectsOperator`, `uuid`, `DELIMITER`, `TEST_RUN`, `DATAFLOW_SERVICE_ACCOUNT`, `dag`.
*   **Potential Improvements:**
    *   Add error handling for cases where the GCSListObjectsOperator fails (e.g., due to invalid credentials or permissions).
    *   Allow the `match_glob` to be configurable via a parameter.
*   **Cyclomatic Complexity:** Low.
*   **Pain Points:**  The function depends on Airflow's `GCSListObjectsOperator`, which might not be suitable for all use cases. Direct usage of the Google Cloud Storage client library could provide more flexibility.

**9. `list_jobs()`**

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

*   **Purpose:** Lists all Dataflow jobs in a specified project and region.
*   **Parameters:** None
*   **Logic:**
    1.  Logs a message indicating that it's listing Dataflow jobs.
    2.  Obtains a Dataflow service client using `_get_df_service()`.
    3.  Uses the client to call the `projects.locations.jobs.list` API method, providing the project ID and region.
    4.  Executes the API call and extracts the "jobs" list from the response.
*   **Return Value:** `jobs` (list): A list of dictionaries, where each dictionary represents a Dataflow job. The structure of the dictionary depends on the Dataflow API response.
*   **Business Logic:** This function is used to retrieve information about existing Dataflow jobs, such as their status, ID, and creation time.
*   **Dependencies:** `_get_df_service()`, `PIPELINE_PROJECT_ID`, `DATAFLOW_REGION`.
*   **Potential Improvements:**
    *   Add error handling for API call failures.
    *   Consider adding pagination to handle cases where the number of jobs is very large.
*   **Cyclomatic Complexity:** Low.
*   **Pain Points:** No apparent pain points.

**10. `_cleanup_xcom(context, session)`**

```python
def _cleanup_xcom(context, session=None):
    dag_id = context["dag"].dag_id
    session.query(XCom).filter(XCom.dag_id == dag_id).delete()
```

*   **Purpose:** Cleans up XCom (cross-communication) entries in the Airflow metadata database for a specific DAG (Directed Acyclic Graph). XComs are used to pass data between tasks in an Airflow DAG.
*   **Parameters:**
    *   `context` (dict): Airflow context dictionary.
    *   `session` (sqlalchemy.orm.session.Session): SQLAlchemy session object used to interact with the Airflow metadata database. Defaults to `None`.
*   **Logic:**
    1.  Extracts the DAG ID from the Airflow context.
    2.  Uses the provided SQLAlchemy `session` to query the `XCom` table, filters for entries associated with the DAG ID, and deletes those entries.
*   **Return Value:** None
*   **Business Logic:** This function is used to prevent the XCom table from growing too large, which can impact Airflow performance. It's typically called at the end of a DAG run to remove XCom entries that are no longer needed.
*   **Dependencies:** `XCom` (Airflow model), `sqlalchemy.orm.session.Session`.
*   **Potential Improvements:**
    *   Add error handling in case the database connection fails or the XCom table cannot be accessed.
    *   Consider adding a retention policy to only delete XCom entries older than a certain age.
*   **Cyclomatic Complexity:** Low.
*   **Pain Points:** The function directly interacts with the Airflow metadata database, which requires a good understanding of Airflow's internal data model.

**11. `get_bq_impersonated_client(target_service_account, target_project)`**

```python
def get_bq_impersonated_client(target_service_account: str, target_project: str):
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform',
                     'https://www.googleapis.com/auth/bigquery']
    return bigquery.Client(project=target_project, credentials=getImpersonatedCredentials(target_scopes, target_service_account, target_project))
```

*   **Purpose:** Creates and returns a Google Cloud BigQuery client with impersonated credentials.
*   **Parameters:**
    *   `target_service_account` (str): The name of the service account to impersonate.
    *   `target_project` (str): The ID of the project where BigQuery operations will be performed.
*   **Logic:**
    1.  Defines the required OAuth scopes for BigQuery access.
    2.  Calls `getImpersonatedCredentials` to obtain impersonated credentials for the target service account and project.
    3.  Creates a `bigquery.Client` object, passing in the `target_project` and the impersonated `credentials`.
*   **Return Value:** `bigquery.Client`: A BigQuery client object configured to use impersonated credentials.
*   **Business Logic:**  This function allows secure access to BigQuery resources by using impersonation. The client will perform BigQuery operations as the specified service account, granting access to datasets and tables that the service account has permissions for.
*   **Dependencies:** `bigquery.Client`, `getImpersonatedCredentials`.
*   **Potential Improvements:**
    *   Add error handling in case the impersonation fails or the BigQuery client cannot be created.
*   **Cyclomatic Complexity:** Low.
*   **Pain Points:** No apparent pain points.

**12. `get_time_diff_between_processed_tm_vs_current_time()`**

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
                                """.format(PIPELINE_PROJECT_ID, FRESHNESS_CHECK_DATASET_NAME, FRESHNESS_CHECK_TABLE_NAME)

        logging.info(f"time_difference query: {time_difference}")
        query_job = client.query(time_difference, job_config=bigquery.QueryJobConfig(
            labels={"pnr-data-ingestion-label": billing_label}), job_id_prefix=billing_label)
        query_job.result()
        records_dict = [dict(row) for row in query_job]
        max_ingest_ts_in_batch = records_dict[0]['max_ingest_ts']
        current_ts = records_dict[0]['current_ts']
        diff_in_mins = records_dict[0]['diff_in_mins']
        logging.info(f"max_ingest_ts_in_batch: {max_ingest_ts_in_batch}")
        logging.info(f"current_ts: {current_ts}")
        logging.info(f"diff_in_mins: {diff_in_mins}")

    except Exception as e:
        return logging.info('Error: {}'.format(str(e)))

    return diff_in_mins
```

*   **Purpose:** Calculates the time difference (in minutes) between the most recent `ingest_ts` value in a BigQuery table and the current timestamp. This is used to monitor data freshness.
*   **Parameters:** None
*   **Logic:**
    1.  Obtains a BigQuery client with impersonated credentials using `get_bq_impersonated_client`.
    2.  Constructs a SQL query that:
        *   Finds the maximum `ingest_ts` value in the specified BigQuery table.
        *   Gets the current timestamp.
        *   Calculates the difference between the current timestamp and the maximum `ingest_ts` in minutes using `TIMESTAMP_DIFF`.
    3.  Executes the query using the BigQuery client.
    4.  Retrieves the results and extracts the `max_ingest_ts`, `current_ts`, and `diff_in_mins` values.
    5.  Logs these values.
*   **Return Value:** `diff_in_mins` (int): The time difference in minutes. If an error occurs, it returns `None` implicitly after logging the error (because there is a return statement in the `except` block)
*   **Business Logic:** This function is critical for monitoring data freshness in a data pipeline. By comparing the timestamp of the most recently ingested data with the current time, it can detect delays or failures in the data ingestion process.
*   **Dependencies:** `get_bq_impersonated_client`, `PIPELINE_PROJECT_ID`, `FRESHNESS_CHECK_DATASET_NAME`, `FRESHNESS_CHECK_TABLE_NAME`, `service_account_name`, `billing_label`.
*   **Potential Improvements:**
    *   The `try...except` block's `return` statement logs error info and returns `None` implicitly. Better to raise Exception instead or return some sentinel value indicating the failure.
    *   Implement more robust error handling, including retries and logging of specific error codes.
    *   Add validation to ensure that the query returns a single row with the expected columns.
*   **Cyclomatic Complexity:** Moderate due to the `try...except` block.
*   **Pain Points:**
    *   The SQL query is hardcoded, making it difficult to adapt to different table schemas or freshness requirements.
    *   The error handling is basic and doesn't provide much information about the cause of the error.
    *   Implicit return of `None` could be problematic.

**13. `_is_reprocessing()`**

```python
def _is_reprocessing(**context):
    reprocess_flag = context['ti'].xcom_pull(key=TASK_PARAM_REPROCESSING, task_ids=TASK_SETUP_PROCESSING)
    logging.info(f"Is reprocessing required [{reprocess_flag}]")
    return TASK_PREPARE_STAGING if not reprocess_flag else TASK_SKIP_PREPARE_STAGING
```

*   **Purpose:** Determines whether data reprocessing is required based on an XCom value. This function is typically used in an Airflow DAG to conditionally execute tasks based on whether a previous task has indicated that reprocessing is necessary.
*   **Parameters:**
    *   `context` (dict): Airflow context dictionary.
*   **Logic:**
    1.  Retrieves the value of the `TASK_PARAM_REPROCESSING` XCom variable from the task instance (`ti`) of the `TASK_SETUP_PROCESSING` task.
    2.  Logs whether reprocessing is required based on the value of the `reprocess_flag`.
    3.  Returns either `TASK_PREPARE_STAGING` if reprocessing is not required (reprocess_flag is False), or `TASK_SKIP_PREPARE_STAGING` if reprocessing is required (reprocess_flag is True). These return values are likely task IDs that determine the next task to be executed.
*   **Return Value:** str: Either `TASK_PREPARE_STAGING` or `TASK_SKIP_PREPARE_STAGING`, depending on the value of the `reprocess_flag`.
*   **Business Logic:** This function allows for conditional execution of tasks in a data pipeline. If reprocessing is required (e.g., due to a data quality issue or a change in the processing logic), the pipeline can skip certain steps or execute alternative tasks.
*   **Dependencies:** `TASK_PARAM_REPROCESSING`, `TASK_SETUP_PROCESSING`, `TASK_PREPARE_STAGING`, `TASK_SKIP_PREPARE_STAGING`.
*   **Potential Improvements:**
    *   Add error handling for cases where the XCom value is not found or is of an unexpected type.
    *   Consider using a more descriptive name for the return values (e.g., `PREPARE_STAGING_TASK_ID` and `SKIP_PREPARE_STAGING_TASK_ID`).
*   **Cyclomatic Complexity:** Low.
*   **Pain Points:** The function relies on specific XCom keys and task IDs, which can make the DAG harder to maintain if these values change.

**14. `get_job_id(job_name)`**

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

*   **Purpose:** Retrieves the ID of a Dataflow job with a name that starts with a given `job_name` and has a `JOB_STATE_DONE` state.
*   **Parameters:**
    *   `job_name` (str): The name (or prefix) of the Dataflow job to search for.
*   **Logic:**
    1.  Logs the provided `job_name`.
    2.  Retrieves a list of Dataflow jobs using `list_jobs()`.
    3.  Iterates through the list of jobs:
        *   For each job, it checks if the job's name starts with the provided `job_name` and if the job's current state is `JOB_STATE_DONE`.
        *   If both conditions are met, it extracts the job's ID and logs it, then breaks out of the loop.
        *   If the conditions are not met, it sets the job_id to None in the else block
    4.  Returns the job ID.
*   **Return Value:** `job_id` (str): The ID of the matching Dataflow job, or `None` if no matching job is found.
*   **Business Logic:** This function is used to find the ID of a specific Dataflow job based on its name and state. This is often necessary to perform further operations on the job, such as retrieving its metrics
## UML Diagram
![Image](images/anotherDAG_img1.png)
## DAG FLOW
![Image](images/anotherDAG_img2.png)

