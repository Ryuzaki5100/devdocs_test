# Generated Documentation with UML
Okay, here is the detailed documentation for the provided functions, organized in a logical execution order, along with explanations, business context, and a discussion of complexity and potential pain points:

```markdown
## Function Documentation

This document details the functions in the provided code, explaining their purpose, functionality, and relationships within the overall workflow.  The functions are presented in an approximate order of execution, reflecting their dependencies.

**Function 1: `main._get_impersonated_credentials(target_scopes, target_service_account)`**

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

**Description:**

This function retrieves Google Cloud credentials using impersonation.  It obtains source credentials using the default authentication method and then creates impersonated credentials that act as the specified target service account.

**How it works:**

1.  **Default Credentials:**  It first uses `google.auth._default.default()` to obtain the default credentials. These credentials are based on the environment in which the code is running (e.g., a Compute Engine instance, a local development environment with `gcloud auth application-default login`).  The `scopes` parameter specifies the required permissions for the source credentials.
2.  **Impersonated Credentials:** It then uses `google.auth.impersonated_credentials.Credentials` to create the impersonated credentials. Key parameters include:
    *   `source_credentials`: The credentials obtained from `_default.default()`.
    *   `target_principal`:  The email address of the service account to impersonate.
    *   `target_scopes`:  The scopes (permissions) that the impersonated service account should have.
    *   `lifetime`: The duration (in seconds) for which the impersonated credentials are valid.
3.  **Return Value:** The function returns the `target_credentials`, which can then be used to authenticate with Google Cloud services as the target service account.

**Business Logic:**

Impersonation is a crucial security pattern in Google Cloud. It allows a service (or a user) with limited permissions to temporarily assume the identity of a service account with broader permissions.  This function enables the DAG to perform actions on behalf of the target service account, such as accessing data in Cloud Storage or BigQuery, without needing to store the service account's private key directly within the DAG's code.  The short lifetime is important to reduce the risk of credential compromise.

**Dependencies:** `google.auth`, `google.auth._default`, `google.auth.impersonated_credentials`, `logging`

**Function 2: `main.getImpersonatedCredentials(target_scopes, target_service_account, target_project)`**

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

**Description:**

This function is very similar to `_get_impersonated_credentials`, but it constructs the `target_principal` differently by explicitly formatting it as an email address with the `target_project` included.

**How it works:**

1.  **Default Credentials:** Same as `_get_impersonated_credentials`.
2.  **Impersonated Credentials:** It uses `google.auth.impersonated_credentials.Credentials` to create the impersonated credentials. The key difference is in the `target_principal`:
    *   `target_principal`:  It explicitly creates the email address of the service account to impersonate by combining `target_service_account`, `target_project`, and the domain `.iam.gserviceaccount.com`.
3.  **Return Value:** The function returns the `target_credentials`.

**Business Logic:**

This function provides a more explicit way to define the target service account.  It ensures that the full email address of the service account is used, which can be important in some environments or when dealing with cross-project service accounts.

**Dependencies:** `google.auth`, `google.auth._default`, `google.auth.impersonated_credentials`, `logging`

**Function 3: `main._get_storage_client(target_service_account, target_project)`**

```python
def _get_storage_client(target_service_account: str, target_project: str):
    from google.cloud import storage
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    credentials = None if TEST_RUN == "true" else _get_impersonated_credentials(target_scopes,
                                                                                target_service_account)
    return storage.Client(project=target_project,
                          credentials=credentials)
```

**Description:**

This function creates a Google Cloud Storage client, optionally using impersonated credentials.

**How it works:**

1.  **Conditional Credentials:** It checks the `TEST_RUN` environment variable. If `TEST_RUN` is "true", it sets `credentials` to `None`. Otherwise, it calls `_get_impersonated_credentials` (Function 1) to get the impersonated credentials.
2.  **Storage Client Creation:** It creates a `google.cloud.storage.Client` using the specified `target_project` and the obtained `credentials`.
3.  **Return Value:** The function returns the `storage.Client` object.

**Business Logic:**

This function provides a convenient way to obtain a Cloud Storage client.  It supports both test environments (where authentication might be disabled) and production environments (where impersonation is used for secure access).

**Dependencies:** `google.cloud.storage`, `_get_impersonated_credentials`

**Function 4: `main.get_bq_impersonated_client(target_service_account, target_project)`**

```python
def get_bq_impersonated_client(target_service_account: str, target_project: str):
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform',
                     'https://www.googleapis.com/auth/bigquery']
    return bigquery.Client(project=target_project, credentials=getImpersonatedCredentials(target_scopes, target_service_account, target_project))
```

**Description:**

This function creates a BigQuery client using impersonated credentials.

**How it works:**

1.  **Target Scopes:** Defines the necessary scopes for BigQuery access.
2.  **Impersonated Credentials:** Calls `getImpersonatedCredentials` (Function 2) to obtain the impersonated credentials.
3.  **BigQuery Client Creation:** Creates a `google.cloud.bigquery.Client` using the specified `target_project` and the obtained `credentials`.
4.  **Return Value:** Returns the `bigquery.Client` object.

**Business Logic:**

Similar to `_get_storage_client`, this function streamlines the process of obtaining a BigQuery client with impersonation. It ensures that the client is properly authenticated to perform BigQuery operations on behalf of the target service account.

**Dependencies:** `google.cloud.bigquery`, `getImpersonatedCredentials`

**Function 5: `main.get_metric_service_client(target_service_account)`**

```python
def get_metric_service_client(target_service_account: str):
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    return monitoring_v3.MetricServiceClient()
```

**Description:**

This function creates a Cloud Monitoring client.

**How it works:**

1.  **Target Scopes:** Defines the necessary scopes for Cloud Monitoring access (though it's not actually used in creating the client, which is a potential issue).
2.  **Metric Service Client Creation:** Creates a `google.cloud.monitoring_v3.MetricServiceClient`. Critically, it does *not* pass any credentials to the client.
3.  **Return Value:** Returns the `monitoring_v3.MetricServiceClient` object.

**Business Logic:**

This function is intended to provide a client for interacting with Cloud Monitoring, allowing the DAG to create and manage custom metrics.

**Dependencies:** `google.cloud.monitoring_v3`

**Function 6: `main.create_custom_metrics(metric_type, project_id, resource_type, value_type, val)`**

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

**Description:**

This function creates and inserts a custom metric into Cloud Monitoring.

**How it works:**

1.  **Metric Service Client:** Retrieves a `MetricServiceClient` using `get_metric_service_client` (Function 5).
2.  **Time Series Creation:** Constructs a `monitoring_v3.TimeSeries` object, which represents the metric data to be written.  It sets the metric type, labels (application and workflow names), resource type (e.g., `cloud_composer_environment`), resource labels (project ID, workflow name, location), and the actual data point.
3.  **Data Point Creation:** Creates a `monitoring_v3.Point` to hold the metric value. The `value_type` parameter determines the data type of the value (e.g., `int64_value`, `double_value`).
4.  **Time Interval:** Sets the time interval for the metric data point.
5.  **Metric Insertion:** Calls `client.create_time_series` to write the metric data to Cloud Monitoring.
6.  **Error Handling:** Includes a `try...except` block to catch any exceptions during the metric creation process.

**Business Logic:**

This function allows the DAG to track its performance, progress, and any other relevant metrics. By creating custom metrics, you can gain insights into the DAG's behavior and identify potential issues.

**Dependencies:** `get_metric_service_client`, `google.cloud.monitoring_v3`, `time`, `logging`

**Function 7: `main._get_default_or_from_dag_run(default_value, dag_key, dag_run_conf)`**

```python
def _get_default_or_from_dag_run(default_value: str, dag_key, dag_run_conf):
    if dag_run_conf is not None and dag_key in dag_run_conf:
        return dag_run_conf[dag_key]
    return default_value
```

**Description:**

This function retrieves a value either from the DAG run configuration or from a default value.

**How it works:**

1.  **Check DAG Run Configuration:** It checks if `dag_run_conf` is not `None` and if the specified `dag_key` exists in the `dag_run_conf` dictionary.
2.  **Return Value:** If the `dag_key` is found in the `dag_run_conf`, the corresponding value is returned. Otherwise, the `default_value` is returned.

**Business Logic:**

This function allows users to override default DAG parameters at runtime through the DAG run configuration. This provides flexibility in controlling the DAG's behavior without modifying the code.

**Dependencies:** None

**Function 8: `main._setup_processing(**context)`**

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

**Description:**

This function sets up the processing environment for the DAG.  It retrieves configuration parameters, generates a unique run ID, and pushes these parameters to XCom for use by subsequent tasks.

**How it works:**

1.  **Logging:** Logs the start of the DAG and some context information.
2.  **DAG Run Configuration:** Retrieves the `dag_run_conf` from the `context`.
3.  **Parameter Retrieval:** Uses `_get_default_or_from_dag_run` (Function 7) to retrieve various configuration parameters, such as bucket names, bucket paths, and the number of past hours to process.
4.  **Run ID Generation:** Generates a unique run ID based on the execution datetime. If a `RUN_ID` is provided in the `dag_run_conf`, it is used instead, and a `reprocessing_flag` is set to `True`.
5.  **Path Construction:** Constructs the full GCS path for the run.
6.  **Job Name Generation:** Creates a job name for the Dataflow job.
7.  **XCom Push:** Pushes the retrieved and generated parameters to XCom, making them available to downstream tasks.

**Business Logic:**

This function centralizes the configuration and setup logic for the DAG. It ensures that all subsequent tasks have access to the necessary parameters and that a consistent run ID is used throughout the workflow. The use of XCom allows for loose coupling between tasks. The DAG's overall function is to process data, likely PNR data (Passenger Name Record), ingest it, perform transformations using Dataflow, and archive it. This setup is critical for ensuring each DAG run is uniquely identifiable and properly configured.

**Dependencies:** `_get_default_or_from_dag_run`, `logging`

**Function 9: `main._is_reprocessing(**context)`**

```python
def _is_reprocessing(**context):
    reprocess_flag = context['ti'].xcom_pull(key=TASK_PARAM_REPROCESSING, task_ids=TASK_SETUP_PROCESSING)
    logging.info(f"Is reprocessing required [{reprocess_flag}]")
    return TASK_PREPARE_STAGING if not reprocess_flag else TASK_SKIP_PREPARE_STAGING
```

**Description:**

This function determines whether reprocessing is required based on the `reprocessing_flag` stored in XCom.

**How it works:**

1.  **XCom Pull:** Retrieves the `reprocessing_flag` from XCom, which was pushed by the `_setup_processing` task.
2.  **Conditional Return:** Returns either `TASK_PREPARE_STAGING` or `TASK_SKIP_PREPARE_STAGING` based on the value of `reprocess_flag`. This is used to control the DAG's execution path.

**Business Logic:**

This function enables the DAG to handle reprocessing scenarios differently. If reprocessing is required, it might skip certain tasks (e.g., preparing the staging area) and proceed directly to processing the data. This is important for handling data updates or corrections.

**Dependencies:** `logging`

**Function 10: `main._get_gcs_files(bucket_name, gcs_path, **context)`**

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

**Description:**

This function lists files in a Google Cloud Storage bucket under the specified path using the `GCSListObjectsOperator`.

**How it works:**

1.  **GCSListObjectsOperator:** Creates a `GCSListObjectsOperator` task to list the files.
    *   `bucket`: The name of the GCS bucket.
    *   `prefix`: The path within the bucket to list.
    *   `match_glob`: The glob pattern to match filenames. `**/*` matches all files and directories recursively. The `DELIMITER` constant is appended.
    * `impersonation_chain`: Configures the operator to impersonate the `DATAFLOW_SERVICE_ACCOUNT` if not in test mode.
2.  **Task Execution:** Executes the `GCSListObjectsOperator` task using the provided `context`.
3.  **Return Value:** Returns a list of filenames found in the bucket and matching the specified glob pattern.

**Business Logic:**

This function is a crucial step in the data ingestion process. It identifies the files that need to be processed by the DAG.

**Dependencies:** `GCSListObjectsOperator`, `logging`, `uuid`

**Function 11: `main._prepare_staging()`**

```python
def _prepare_staging(**context):
    ti = context['ti']
    gcs_landing_bucket_name = ti.xcom_pull(key=TASK_PARAM_LANDING_BUCKET_NAME, task_ids=TASK_SETUP_PROCESSING)
    gcs_landing_bucket_path = ti.xcom_pull(key=TASK_PARAM_LANDING_BUCKET_PATH, task_ids=TASK_SETUP_PROCESSING)
    gcs_run_bucket_name = ti.xcom_pull(key=TASK_PARAM_RUN_BUCKET_NAME, task_ids=TASK_SETUP_PROCESSING)
    gcs_run_bucket_path = ti.xcom_pull(key=TASK_PARAM_RUN_BUCKET_PATH, task_ids=TASK_SETUP_PROCESSING)
    num_past_hours = ti.xcom_pull(key=TASK_PARAM_NUM_PAST_HOURS, task_ids=TASK_SETUP_PROCESSING)

    dag_vars = get_dag_vars()
    #num_past_hours = get_dag_var_as_int(VAR_AS_NUM_PAST_HOURS, dag_vars)
    max_files = get_dag_var_as_int(VAR_AS_MAX_FILES, dag_vars)

    logging.info(f"Landing bucket name [{gcs_landing_bucket_name}]")
    logging.info(f"Landing bucket path [{gcs_landing_bucket_path}]")
    logging.info(f"Run bucket name [{gcs_run_bucket_name}]")
    logging.info(f"Run bucket path [{gcs_run_bucket_path}]")
    logging.info(f"Num past hours [{num_past_hours}]")
    logging.info(f"Max files [{max_files}]")

    logging.info(f"Getting landing files...")
    landing_files = _get_gcs_files(gcs_landing_bucket_name, gcs_landing_bucket_path, **context)
    logging.info(f"Got [{len(landing_files)}] landing files")

    all_selected_landing_files = select_files(landing_files, gcs_landing_bucket_path + "/", int(num_past_hours))
    logging.info(f"Selected [{len(all_selected_landing_files)}] landing files")
    if 0 < max_files < len(all_selected_landing_files):
        selected_landing_files = all_selected_landing_files[:max_files]
    else:
        selected_landing_files = all_selected_landing_files
    logging.info(f"Limited selected landing files to [{len(selected_landing_files)}]")
    size =len(selected_landing_files)
    if len(selected_landing_files) == 0:
        create_custom_metrics(f"pnr_input_file_count{SUFFIX}", COMPOSER_PROJECT_ID, "cloud_composer_workflow",
                              "int64_value", 0)
        logging.error(f"No files in landing [{gcs_landing_bucket_name}/{gcs_landing_bucket_path}]")
        raise AirflowFailException(f"No files in landing [{gcs_landing_bucket_name}/{gcs_landing_bucket_path}]")

    _move_landing_to_staging(gcs_landing_bucket_name, selected_landing_files, gcs_run_bucket_name, gcs_run_bucket_path,
                             gcs_landing_bucket_path, **context)
    create_custom_metrics(f"pnr_input_file_count{SUFFIX}", COMPOSER_PROJECT_ID, "cloud_composer_workflow",
                          "int64_value", size)
```

**Description:**

This function prepares the staging area by retrieving files from the landing bucket, selecting the files to be processed and moving them to the staging bucket.

**How it works:**

1.  **XCom Pull:** Retrieves parameters from XCom, including bucket names, bucket paths, and the number of past hours to process.
2.  **Get Landing Files:** Calls `_get_gcs_files` (Function 10) to retrieve a list of files from the landing bucket.
3.  **Select Files:** Calls a function named `select_files` (not provided in the code) to select the files to be processed based on a time window (`num_past_hours`).
4.  **Limit File Count:** Limits the number of selected files based on the `max_files` parameter.
5.  **Error Handling:** If no files are found, it logs an error, creates a custom metric indicating a zero file count, and raises an `AirflowFailException`, causing the DAG to fail.
6.  **Move to Staging:** Calls `_move_landing_to_staging` (Function 13) to move the selected files from the landing bucket to the staging bucket.
7.  **Create Custom Metric:** Creates a custom metric to track the number of input files processed.

**Business Logic:**

This function ensures that only the relevant files are processed by the DAG. It filters the files based on a time window and limits the number of files to prevent overloading the processing pipeline.  The explicit error handling prevents the DAG from silently failing when no data is available.

**Dependencies:** `_get_gcs_files`, `_move_landing_to_staging`, `create_custom_metrics`, `select_files`, `get_dag_vars`, `get_dag_var_as_int`

**Function 12: `main._move_blobs(bucket_name, blob_names, destination_bucket_name, destination_prefix)`**

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

**Description:**

This function moves blobs (files) from one Google Cloud Storage bucket/path to another using the `gsutil mv` command executed via the `BashOperator`.

**How it works:**

1.  **Logging:** Logs the source and destination of the move operation.
2.  **Temporary File Creation:** Creates a temporary file to store the list of blobs to be moved.
3.  **Blob List Population:** Writes the full GCS paths of each blob to the temporary file.
4.  **`gsutil` Command Construction:** Constructs the `gsutil mv` command to move the blobs.  It uses the `-m` flag for parallel execution and `-I` to read the list of blobs from the temporary file. It adds impersonation and state directory options.
5.  **BashOperator Execution:** Executes the `gsutil` command using the `BashOperator`.
6.  **Temporary File Deletion:** Deletes the temporary file.

**Business Logic:**

This function provides a reliable way to move files within Google Cloud Storage.  The use of `gsutil` with parallel execution (`-m`) improves performance for large file transfers.

**Dependencies:** `BashOperator`, `logging`, `time`, `os`, `uuid`

**Function 13: `main._move_landing_to_staging(source_bucket, source_objects, destination_bucket, destination_path, source_path)`**

```python
def _move_landing_to_staging(source_bucket: str, source_objects: list, destination_bucket: str, destination_path: str,
                             source_path: str, **context):
    logging.info(
        f"Moving [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]...")
    _move_blobs(source_bucket, source_objects, destination_bucket, destination_path, **context)
    logging.info(
        f"Moved [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]")
```

**Description:**

This function moves files from the landing bucket to the staging bucket using the `_move_blobs` function.

**How it works:**

1.  **Logging:** Logs the source and destination of the move operation.
2.  **Move Blobs:** Calls `_move_blobs` (Function 12) to perform the actual file transfer.
3.  **Logging:** Logs the completion of the move operation.

**Business Logic:**

This function encapsulates the logic for moving files from the landing area to the staging area, separating concerns. This is a standard ETL pattern.

**Dependencies:** `_move_blobs`, `logging`

**Function 14: `main._get_df_service()`**

```python
def _get_df_service():
    df_service = build("dataflow", "v1b3", cache_discovery=False)
    logging.info("df service [{}]".format(df_service))
    return df_service
```

**Description:**

This function creates a Dataflow service client.

**How it works:**

1.  **Dataflow Service Client Creation:** Uses the `googleapiclient.discovery.build` function to create a Dataflow service client. It specifies the API name (`dataflow`), the API version (`v1b3`), and disables API discovery caching.
2.  **Logging:** Logs the Dataflow service object.
3.  **Return Value:** Returns the Dataflow service client.

**Business Logic:**

This function provides a reusable way to obtain a Dataflow service client, which is needed to interact with the Dataflow API (e.g., to list jobs, get job metrics).

**Dependencies:** `googleapiclient.discovery`, `logging`

**Function 15: `main.list_jobs()`**

```python
def list_jobs():
    logging.
## UML Diagram
![Image](images/anotherDAG_img1.png)
## DAG FLOW
![Image](images/anotherDAG_img2.png)

