# Generated Documentation with UML
Okay, here's the detailed documentation for each function, following the logical order of execution and including explanations, business logic, and potential pain points:

**1. `_get_df_service()`**

```python
def _get_df_service():
    df_service = build("dataflow", "v1b3", cache_discovery=False)
    logging.info("df service [{}]".format(df_service))
    return df_service
```

*   **Purpose:** This function initializes and returns a Google Cloud Dataflow service client.
*   **How it works:**
    *   It uses the `googleapiclient.discovery.build` function to create a Dataflow service object. The `build` function dynamically discovers the Dataflow API and creates a service object that can be used to interact with the Dataflow service.
    *   `"dataflow"` is the name of the API being used.
    *   `"v1b3"` specifies the version of the Dataflow API.
    *   `cache_discovery=False` disables caching of the API discovery document.  This is likely done because Dataflow API definitions might change, and you always want the latest.
    *   It logs the created service object for debugging purposes.
    *   It returns the Dataflow service object.
*   **Business Logic:** This function is a utility function to obtain a Dataflow service client, enabling interaction with the Dataflow API. It encapsulates the initialization process, making it reusable throughout the code.
*   **Dependencies:**
    *   It relies on the `googleapiclient.discovery.build` function.
    *   It depends on the `logging` module for logging information.
*   **Cyclomatic Complexity:** Low (1).  It's a straight-line execution path.
*   **Pain Points:**
    *   The hardcoded API version (`"v1b3"`) is a potential issue. If the API version is deprecated, the code will break. It might be better to fetch this from a configuration or environment variable.
    *   Error handling is missing. If the `build` function fails (e.g., due to network issues or authentication problems), the program will crash.
    *   The `cache_discovery=False` setting might impact performance slightly. In production, consider caching the API discovery document if Dataflow API definitions do not change frequently.

**2. `_get_impersonated_credentials(target_scopes, target_service_account)`**

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

*   **Purpose:** This function retrieves impersonated credentials for a given service account.
*   **How it works:**
    *   It obtains the default credentials using `google.auth._default.default`. This is generally the credentials of the environment the code is running in (e.g., the service account of a Compute Engine instance or Cloud Function). It also gets the project ID associated with these credentials.
    *   It creates impersonated credentials using `google.auth.impersonated_credentials.Credentials`. Impersonated credentials allow a service account to act as another service account.
        *   `source_credentials`: The default credentials obtained in the previous step.
        *   `target_principal`: The email address of the service account to impersonate.
        *   `target_scopes`: The OAuth scopes that the impersonated service account will have.
        *   `lifetime`:  The duration for which the impersonated credentials are valid (in seconds).
    *   It returns the impersonated credentials.
*   **Business Logic:** This function enables secure access to resources using service account impersonation.  This is useful in situations where the application needs to access resources with the permissions of a different service account, but doesn't want to store the private key of that service account directly.
*   **Dependencies:**
    *   `google.auth._default.default`
    *   `google.auth.impersonated_credentials.Credentials`
    *   `logging` module.
*   **Cyclomatic Complexity:** Low (1).
*   **Pain Points:**
    *   The lifetime is hardcoded to 1 hour (60 * 60 seconds). This should ideally be configurable.
    *   Error handling is limited. It doesn't handle potential exceptions from `_default.default` or `impersonated_credentials.Credentials`.
    *   It assumes the caller knows the required scopes.  A more robust approach might involve fetching these scopes from a configuration or dynamically determining them based on the resource being accessed.

**3. `_get_storage_client(target_service_account, target_project)`**

```python
def _get_storage_client(target_service_account: str, target_project: str):
    from google.cloud import storage
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    credentials = None if TEST_RUN == "true" else _get_impersonated_credentials(target_scopes,
                                                                                target_service_account)
    return storage.Client(project=target_project,
                          credentials=credentials)
```

*   **Purpose:** This function creates and returns a Google Cloud Storage client, optionally using impersonated credentials.
*   **How it works:**
    *   It defines the necessary OAuth scope for Cloud Storage (`'https://www.googleapis.com/auth/cloud-platform'`).
    *   It checks the value of `TEST_RUN`. If it's "true", it sets credentials to `None` (presumably for local testing). Otherwise, it calls `_get_impersonated_credentials` to get impersonated credentials for the specified `target_service_account`.
    *   It creates a `google.cloud.storage.Client` object, passing the `target_project` and the obtained `credentials`.
    *   It returns the Cloud Storage client.
*   **Business Logic:** This function abstracts the creation of a Cloud Storage client, handling the complexity of impersonation and testing. It allows the code to interact with Cloud Storage buckets and objects using the appropriate credentials.
*   **Dependencies:**
    *   `google.cloud.storage.Client`
    *   `_get_impersonated_credentials` (if `TEST_RUN` is not "true")
    *   The `TEST_RUN` global variable.
*   **Cyclomatic Complexity:** Low (2, due to the `if` statement).
*   **Pain Points:**
    *   The reliance on the global `TEST_RUN` variable for switching between impersonation and direct authentication is not ideal. Environment variables or configuration files would be a better approach.
    *   Error handling is missing. If `_get_impersonated_credentials` fails or the `storage.Client` cannot be created, the program will crash.
    *   The scope is hardcoded.

**4. `_is_reprocessing(**context)`**

```python
def _is_reprocessing(**context):
    reprocess_flag = context['ti'].xcom_pull(key=TASK_PARAM_REPROCESSING, task_ids=TASK_SETUP_PROCESSING)
    logging.info(f"Is reprocessing required [{reprocess_flag}]")
    return TASK_PREPARE_STAGING if not reprocess_flag else TASK_SKIP_PREPARE_STAGING
```

*   **Purpose:** This function determines whether the pipeline is in a reprocessing mode based on an XCom value.
*   **How it works:**
    *   It retrieves the value of the XCom variable with the key `TASK_PARAM_REPROCESSING` from the task instance (`ti`) of the task with ID `TASK_SETUP_PROCESSING`. XComs are a mechanism for passing information between tasks in Airflow.
    *   It logs the value of the `reprocess_flag`.
    *   If the `reprocess_flag` is `False` (or evaluates to false), it returns `TASK_PREPARE_STAGING`. Otherwise, it returns `TASK_SKIP_PREPARE_STAGING`. This suggests that the function is used to conditionally skip the staging preparation step based on whether reprocessing is required.
*   **Business Logic:**  This function implements a branching mechanism in the Airflow DAG. It allows the DAG to either prepare the staging environment (for initial processing) or skip this preparation (for reprocessing of existing data).
*   **Dependencies:**
    *   Airflow's `context` dictionary (containing `ti`).
    *   `XCom` mechanism.
    *   `TASK_PARAM_REPROCESSING`, `TASK_SETUP_PROCESSING`, `TASK_PREPARE_STAGING`, `TASK_SKIP_PREPARE_STAGING` (constants).
    *   `logging` module.
*   **Cyclomatic Complexity:** Low (2, due to the `if` statement).
*   **Pain Points:**
    *   The logic is tightly coupled with Airflow's XCom system and task IDs. It makes the function less reusable outside of Airflow.
    *   It assumes the XCom value `TASK_PARAM_REPROCESSING` is a boolean. It would be more robust to explicitly convert the value to a boolean.
    *   Error handling is missing. If the XCom value is not found, `xcom_pull` will return `None`.  The code should handle this case gracefully (e.g., by assuming a default value of `False`).

**5. `get_metric_service_client(target_service_account)`**

```python
def get_metric_service_client(target_service_account: str):
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    return monitoring_v3.MetricServiceClient()
```

*   **Purpose:** This function creates and returns a Google Cloud Monitoring API client.
*   **How it works:**
    *   It defines the necessary OAuth scope for Cloud Monitoring (`'https://www.googleapis.com/auth/cloud-platform'`).
    *   It creates a `google.cloud.monitoring_v3.MetricServiceClient` object and returns it.
*   **Business Logic:** This function provides a simple way to get a client for interacting with the Cloud Monitoring API, enabling the application to write custom metrics.
*   **Dependencies:**
    *   `google.cloud.monitoring_v3.MetricServiceClient`
*   **Cyclomatic Complexity:** Low (1).
*   **Pain Points:**
    *   The function is very simple and could be inlined.
    *   There's no error handling.  Creating the `MetricServiceClient` can fail (e.g., due to network issues or authentication problems).
    *   The `target_service_account` parameter is not used. It's vestigial. If impersonation is intended, it should be implemented.

**6. `list_jobs()`**

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

*   **Purpose:** This function lists all Dataflow jobs in a specified project and location.
*   **How it works:**
    *   It calls `_get_df_service()` to get a Dataflow service client.
    *   It uses the Dataflow service client to make a `jobs.list` API call. This call retrieves a list of Dataflow jobs.
        *   `projectId`: The ID of the Google Cloud project.
        *   `location`: The region where the Dataflow jobs are running.
    *   It extracts the list of jobs from the response (which is a JSON object) using `response["jobs"]`.
    *   It returns the list of Dataflow jobs.
*   **Business Logic:** This function provides a way to retrieve information about existing Dataflow jobs, which can be useful for monitoring, debugging, and managing Dataflow pipelines.
*   **Dependencies:**
    *   `_get_df_service()`
    *   `PIPELINE_PROJECT_ID`, `DATAFLOW_REGION` (constants)
    *   `logging` module.
*   **Cyclomatic Complexity:** Low (1).
*   **Pain Points:**
    *   Error handling is basic. If the API call fails, the program will crash. It would be better to catch exceptions and log the error.
    *   The code assumes the API response will always have a "jobs" key. It should check if the key exists before accessing it.
    *   The function lists *all* jobs. If there are many jobs, this can be slow. It might be useful to add filtering options (e.g., by job name or state).

**7. `get_job_status(job_name)`**

```python
def get_job_status(job_name):
    logging.info(job_name)
    jobs = list_jobs()
    job_status = None
    for job in jobs:
        job_nm = job["name"]
        if job_nm.startswith(job_name):
            logging.info(job["currentState"])
            job_status = job["currentState"]
            break;
        else:
            job_status= None
    return job_status
```

*   **Purpose:** This function retrieves the status of a specific Dataflow job given its name.
*   **How it works:**
    *   It calls `list_jobs()` to get a list of all Dataflow jobs.
    *   It iterates through the list of jobs.
    *   For each job, it checks if the job's name (`job["name"]`) starts with the specified `job_name`.
    *   If a matching job is found, it extracts the job's current state (`job["currentState"]`) and assigns it to `job_status`. The loop then breaks.
    *   If no matching job is found, `job_status` remains `None`.
    *   It returns the `job_status`.
*   **Business Logic:** This function allows you to check the current status of a Dataflow job, such as whether it's running, finished, or failed. This is essential for monitoring the progress of your pipelines.
*   **Dependencies:**
    *   `list_jobs()`
    *   `logging` module.
*   **Cyclomatic Complexity:** Medium (3, due to the loop and the `if` statement).
*   **Pain Points:**
    *   It relies on string prefix matching (`job_nm.startswith(job_name)`), which might not be accurate if job names are similar. Consider using an exact match or a more sophisticated matching algorithm.
    *   The function iterates through *all* jobs, even if a match is found early on. This can be inefficient if there are many jobs.
    *   The function returns `None` if no matching job is found. It might be better to raise an exception in this case, indicating that the job does not exist.
    *   There is no error handling when retrieving the job status in side the loop from `job["currentState"]`

**8. `getImpersonatedCredentials(target_scopes, target_service_account, target_project)`**

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

*   **Purpose:**  This function is similar to `_get_impersonated_credentials`, but constructs the target principal in a specific format and sets a shorter lifetime.
*   **How it works:**
    *   It retrieves the default credentials using `google.auth._default.default(scopes=target_scopes)`.
    *   It constructs the `target_principal` string by concatenating the `target_service_account`, `@`, `target_project`, and `.iam.gserviceaccount.com`. This is the standard format for a service account email address.
    *   It creates impersonated credentials using `google.auth.impersonated_credentials.Credentials` with the `source_credentials`, the constructed `target_principal`, the `target_scopes`, and a lifetime of 600 seconds (10 minutes).
    *   It returns the impersonated credentials.
*   **Business Logic:** This function creates impersonated credentials for specific service accounts within a specified project, using the standard service account email format.
*   **Dependencies:**
    *   `google.auth._default.default`
    *   `google.auth.impersonated_credentials.Credentials`
*   **Cyclomatic Complexity:** Low (1).
*   **Pain Points:**
    *   The lifetime is hardcoded to 600 seconds. This should be configurable.
    *   It assumes the caller knows the required scopes. A more robust approach might involve fetching these scopes from a configuration or dynamically determining them based on the resource being accessed.
    *   It constructs the target principal string. It's important to ensure that `target_service_account` does not include any malicious input which can lead to security breach.

**9. `_cleanup_xcom(context, session)`**

```python
def _cleanup_xcom(context, session=None):
    dag_id = context["dag"].dag_id
    session.query(XCom).filter(XCom.dag_id == dag_id).delete()
```

*   **Purpose:** This function cleans up XCom entries for a specific DAG in Airflow.
*   **How it works:**
    *   It extracts the DAG ID from the Airflow `context` dictionary.
    *   It uses the provided `session` (presumably an SQLAlchemy session connected to the Airflow metadata database) to query the `XCom` table.
    *   It filters the XCom entries to only include those with the matching `dag_id`.
    *   It deletes the filtered XCom entries.
*   **Business Logic:** This function is used to remove old XCom data, which can help to prevent the Airflow metadata database from growing too large. It's a maintenance task that can improve the performance of the Airflow web UI and scheduler.
*   **Dependencies:**
    *   Airflow's `context` dictionary (containing `dag`).
    *   Airflow's `XCom` model.
    *   SQLAlchemy (for querying the database).
*   **Cyclomatic Complexity:** Low (1).
*   **Pain Points:**
    *   It directly accesses the Airflow metadata database, which might be fragile if the database schema changes. It is recommended to use Airflow's APIs.
    *   It deletes *all* XCom entries for the DAG. It might be useful to add options for deleting XCom entries based on task ID or key.

**10. `get_bq_impersonated_client(target_service_account, target_project)`**

```python
def get_bq_impersonated_client(target_service_account: str, target_project: str):
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform',
                     'https://www.googleapis.com/auth/bigquery']
    return bigquery.Client(project=target_project, credentials=getImpersonatedCredentials(target_scopes, target_service_account, target_project))
```

*   **Purpose:** This function creates and returns a BigQuery client using impersonated credentials.
*   **How it works:**
    *   It defines the necessary OAuth scopes for BigQuery (`'https://www.googleapis.com/auth/cloud-platform'` and `'https://www.googleapis.com/auth/bigquery'`).
    *   It calls `getImpersonatedCredentials` to get impersonated credentials for the specified service account and project.
    *   It creates a `google.cloud.bigquery.Client` object, passing the `target_project` and the obtained `credentials`.
    *   It returns the BigQuery client.
*   **Business Logic:** This function simplifies the creation of a BigQuery client with impersonation. It's a reusable way to access BigQuery with the permissions of a specific service account, which can be useful for managing access control and auditing.
*   **Dependencies:**
    *   `google.cloud.bigquery.Client`
    *   `getImpersonatedCredentials`
*   **Cyclomatic Complexity:** Low (1).
*   **Pain Points:**
    *   There's no error handling. If `getImpersonatedCredentials` fails or the `bigquery.Client` cannot be created, the program will crash.
    *   The scopes are hardcoded.

**11. `create_custom_metrics(metric_type, project_id, resource_type, value_type, val)`**

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

*   **Purpose:** This function creates and writes a custom metric to Google Cloud Monitoring.
*   **How it works:**
    *   It gets a Cloud Monitoring client using `get_metric_service_client`.
    *   It constructs the project name in the format `"projects/{project_id}"`.
    *   It creates a `monitoring_v3.TimeSeries` object, which represents a time series of metric data.
        *   It sets the metric type by concatenating `CUSTOM_METRIC_DOMAIN` and the provided `metric_type`.
        *   It sets metric labels for `application_name` and `workflow_name` to `DAGID`.
        *   It sets the resource type and labels for `project_id`, `workflow_name`, and `location`.
        *   It creates a `monitoring_v3.TimeInterval` object representing the time range for the metric data.
        *   It creates a `monitoring_v3.Point` object containing the metric value. The `value_type` (e.g., `"int64_value"`, `"double_value"`) determines how the value is stored.
        *   It adds the `point` to the `series.points` list.
    *   It calls `client.create_time_series` to write the time series data to Cloud Monitoring.
    *   If any exception occurs, it logs the error.
*   **Business Logic:** This function allows you to track custom metrics specific to your application or pipeline. This is crucial for monitoring performance, identifying issues, and making data-driven decisions.
*   **Dependencies:**
    *   `get_metric_service_client`
    *   `google.cloud.monitoring_v3.TimeSeries`, `TimeInterval`, `Point`
    *   `CUSTOM_METRIC_DOMAIN`, `DAGID`, `COMPOSER_SERVICE_ACCOUNT` (constants)
    *   `logging` module.
*   **Cyclomatic Complexity:** Low (1, excluding the exception handling).
*   **Pain Points:**
    *   The function catches *all* exceptions, which might mask specific errors that should be handled differently.
    *   It relies on several global constants (`CUSTOM_METRIC_DOMAIN`, `DAGID`, `COMPOSER_SERVICE_ACCOUNT`), which makes the function less reusable.
    *   The location is hardcoded to `"us-central1"`.
    *   It is important to validate the metric_type and value_type parameters to prevent injection attacks or invalid metric data.

**12. `get_job_metrics(job_id)`**

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

*   **Purpose:** This function retrieves metrics for a specific Dataflow job.
*   **How it works:**
    *   It gets a Dataflow service client using `_get_df_service()`.
    *   It uses the Dataflow service client to make a `jobs.getMetrics` API call.
        *   `projectId`: The ID of the Google Cloud project.
        *   `location`: The region where the Dataflow job is running.
        *   `jobId`: The ID of the Dataflow job.
    *   It returns the raw API response containing the job metrics.
*   **Business Logic:** This function allows you to access detailed metrics about a Dataflow job, such as the number of records processed, CPU usage, and memory consumption. This information is essential for monitoring the performance and efficiency of your Dataflow pipelines.
*   **Dependencies:**
    *   `_get_df_service()`
    *   `PIPELINE_PROJECT_ID`, `DATAFLOW_REGION` (constants)
*   **Cyclomatic Complexity:** Low (1).
*   **Pain Points:**
    *   Error handling is missing. If the API call fails, the program will crash. It's better to catch exceptions and log the error.
    *   The function returns the raw API response. It might be useful to parse the response and return a more structured representation of the metrics.

**13. `_move_blobs(bucket_name, blob_names, destination_bucket_name, destination_prefix)`**

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

*   **Purpose:** This function moves a list of blobs from one Cloud Storage bucket to another using the `gsutil` command-line tool.
*   **How it works:**
    *   It logs the source and destination buckets and prefix.
    *   It creates a temporary file (`/tmp/pnr{SUFFIX}_file_copy_{time_millis}.txt`) to store the list of blobs to move.
    *   It writes each blob's full GCS path (`gs://{bucket_name}/{blob_name}`) to the temporary file.
    *   It constructs a `gsutil mv` command that reads the list of blobs from the temporary file and moves them to the destination bucket and prefix.
        *   It dynamically adjusts the `gsutil` path and impersonation options based on the `TEST_RUN` flag.
    *   It executes the `gsutil` command using Airflow's `BashOperator`. This ensures that the move operation is tracked by Airflow.
    *   It removes the temporary file.
*   **Business Logic:** This function provides a mechanism for moving files in Cloud Storage, which is a common operation in data pipelines for staging, archiving, and cleaning up data.
*   **Dependencies:**
    *   `os` module.
    *   `time` module.
    *   `uuid` module.
    *   Airflow's `BashOperator`.
    *   `TEST_RUN`, `DATAFLOW_SERVICE_ACCOUNT`, `SUFFIX` (constants).
*   **Cyclomatic Complexity:** Medium (2, due to the `if` statement and the loop).
*   **Pain Points:**
    *   The function relies on the `gsutil` command-line tool, which is an external dependency. It might be more robust to use the Cloud Storage client library directly.
    *   Creating a temporary file and using `cat` to pipe the file contents to `gsutil` is inefficient. Consider using `gsutil -m mv` with the blob names directly.
    *   Error handling is limited. If the `gsutil` command fails, the Airflow task will fail, but the error message might not be very informative.
    *   The logic for determining the `gsutil` path and impersonation options based on the `TEST_RUN` flag is not ideal. Environment variables or configuration files would be a better approach.
    *   There is no validation to check that the blob names exists before trying to move them.

**14. `_get_gcs_files(bucket_name, gcs_path)`**

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

*   **Purpose:** This function lists files in a Cloud Storage bucket and path using Airflow's `GCSListObjectsOperator`.
*   **How it works:**
    *   It logs the bucket and path being listed.
    *   It creates a `GCSListObjectsOperator` task:
        *   `bucket`: The name of the Cloud Storage bucket.
        *   `prefix`: The path within the bucket to list.
        *   `match_glob`: A glob pattern to match files. `**/*` matches all files recursively, and `DELIMITER` is appended.
        *   `impersonation_chain`: Sets the service account to impersonate, or `None` if `TEST_RUN == "true"`.
    *   It executes the `GCSListObjectsOperator` using `execute(context)`, which returns a list of file names that match the specified criteria.
    *   It logs the number of files found.
    *   It returns the list of files.
*   **Business Logic:** This function is used to discover files in Cloud Storage, which is a common requirement for data pipelines. The `GCSListObjectsOperator` simplifies this process by providing a dedicated Airflow operator for listing GCS objects.
*   **Dependencies:**
    *   Airflow's `GCSListObjectsOperator`.
    *   `TEST_RUN`, `DATAFLOW_SERVICE_ACCOUNT`, `DELIMITER` (constants).
*   **Cyclomatic Complexity:** Low (1).
*   **Pain Points:**
    *   The function relies on `GCSListObjectsOperator`, which is tightly coupled to Airflow.
    *   Error handling is limited. If the `GCSListObjectsOperator` fails, the Airflow task will fail, but the error message might not be very informative.
    *   The glob pattern `**/*` is very broad. This could be slow if there are many files in the bucket and path. Consider using a more specific glob pattern.
    *   Reliance on global variables `TEST_RUN`, `DATAFLOW_SERVICE_ACCOUNT`, `DELIMITER`.

**15. `_move_landing_to_staging(source_bucket, source_objects, destination_bucket, destination_path, source_path)`**

```python
def _move_landing_to_staging(source_bucket: str, source_objects: list, destination_bucket: str, destination_path: str,
                             source_path: str, **context):
    logging.info(
        f"Moving [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]...")
    _move_blobs(source_bucket, source_objects, destination_bucket, destination_path, **context)
    logging.info(
        f"Moved [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]")
```

*   **Purpose:** This function moves files from a landing bucket to a staging bucket using the
## UML Diagram
![Image](images/anotherDAG_img1.png)
## DAG FLOW
![Image](images/anotherDAG_img2.png)

