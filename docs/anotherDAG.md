# Generated Documentation with UML
```markdown
## Function Documentation

This document details the functions involved in a data pipeline, explaining their purpose, functionality, and dependencies. The functions are presented in an order that reflects the potential execution flow within the pipeline.

### 1. `main.get_metric_service_client(target_service_account)`

**Purpose:** This function creates and returns a Google Cloud Monitoring MetricServiceClient. This client is used to interact with the Cloud Monitoring API, enabling the pipeline to create and manage custom metrics.

**Functionality:**

1.  **Define Target Scopes:** It defines the necessary OAuth 2.0 scopes required for accessing Cloud Monitoring resources. In this case, it specifies `https://www.googleapis.com/auth/cloud-platform`, granting access to all Cloud Platform services.

    ```python
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    ```

2.  **Instantiate MetricServiceClient:** It instantiates a `monitoring_v3.MetricServiceClient` object.  This object handles communication with the Cloud Monitoring API.

    ```python
    return monitoring_v3.MetricServiceClient()
    ```

**Business Logic:** This function abstracts the creation of the Cloud Monitoring client. This simplifies metric creation and keeps the configuration (scopes) centralized.

### 2. `main.create_custom_metrics(metric_type, project_id, resource_type, value_type, val)`

**Purpose:** This function creates and pushes custom metrics to Google Cloud Monitoring. These metrics can be used to track the performance, progress, and health of the data pipeline.

**Functionality:**

1.  **Obtain MetricServiceClient:** It calls `get_metric_service_client()` to retrieve a Cloud Monitoring client.

    ```python
    client = get_metric_service_client(COMPOSER_SERVICE_ACCOUNT)
    ```

2.  **Construct Metric Time Series:** It constructs a `monitoring_v3.TimeSeries` object, which represents a sequence of data points for a specific metric.
    *   It sets the metric type by concatenating `CUSTOM_METRIC_DOMAIN` with the provided `metric_type`.
    *   It adds labels to the metric for `application_name` and `workflow_name`, using `DAGID` as the value.
    *   It sets the resource type and labels, including `project_id`, `workflow_name` (using `DAGID`), and `location`.

    ```python
    series = monitoring_v3.TimeSeries()
    series.metric.type = CUSTOM_METRIC_DOMAIN + "/" + metric_type
    series.metric.labels['application_name'] = DAGID
    series.resource.type = resource_type
    series.resource.labels["project_id"] = project_id
    series.resource.labels["workflow_name"] = DAGID
    series.resource.labels["location"] = "us-central1"
    ```

3.  **Create Data Point:** It creates a `monitoring_v3.Point` object, which represents a single data point in the time series.
    *   It sets the time interval for the point, using the current time.
    *   It sets the value of the point, using the provided `value_type` and `val`.

    ```python
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10 ** 9)
    interval = monitoring_v3.TimeInterval(
        {"end_time": {"seconds": seconds, "nanos": nanos}}
    )
    point = monitoring_v3.Point({"interval": interval, "value": {value_type: val}})
    series.points = [point]
    ```

4.  **Create Time Series in Cloud Monitoring:** It calls the `create_time_series` method of the `MetricServiceClient` to create the time series in Cloud Monitoring.

    ```python
    client.create_time_series(name=project_name, time_series=[series])
    ```

5.  **Error Handling:** It includes a `try...except` block to catch any exceptions that occur during the metric creation process. If an exception is caught, it logs an error message.

    ```python
    except Exception as ex:
        logging.error("Error [{}] occurred while inserting/creating custom metric".format(str(ex)))
    ```

**Business Logic:**  This function allows the pipeline to report its status and performance in a standardized way. This reporting can then be visualized and used for alerting.

### 3. `main._get_gcs_files(bucket_name, gcs_path)`

**Purpose:** This function lists files in a Google Cloud Storage (GCS) bucket under a specified path.  It leverages the `GCSListObjectsOperator` from Apache Airflow.

**Functionality:**

1.  **Log Information:** Logs the bucket name and GCS path to indicate which directory is being scanned.

    ```python
    logging.info(
        f"Listing files in [{bucket_name}/{gcs_path}]...")
    ```

2.  **GCSListObjectsOperator:** It creates a `GCSListObjectsOperator` to list files within the specified bucket and path.

    *   `task_id`: A unique identifier for the task.
    *   `bucket`: The name of the GCS bucket.
    *   `prefix`: The path within the bucket to list files from.
    *   `match_glob`: Uses a glob pattern to filter files.  Here, it matches files ending with the `DELIMITER`.
    *   `impersonation_chain`: Specifies a service account to impersonate when accessing GCS. It uses `DATAFLOW_SERVICE_ACCOUNT` unless `TEST_RUN` is set to "true".

    ```python
    gcs_list_objects = GCSListObjectsOperator(
        task_id='list_gcs_files' + str(uuid.uuid4()),
        bucket=bucket_name,
        prefix=gcs_path,
        match_glob="**/*" + DELIMITER,
        impersonation_chain=None if TEST_RUN == "true" else DATAFLOW_SERVICE_ACCOUNT,
        dag=dag
    )
    ```

3.  **Execute Operator:** Executes the Airflow operator to retrieve the list of files.

    ```python
    files = gcs_list_objects.execute(context)
    ```

4.  **Log Information:** Logs the number of files found in the specified location.

    ```python
    logging.info(
        f"Found [{len(files)}] files in [{bucket_name}/{gcs_path}]")
    ```

5.  **Return Files:** Returns a list of file names (objects) found in GCS.

    ```python
    return files
    ```

**Business Logic:** This function is crucial for discovering the data that needs to be processed by the pipeline. The `match_glob` parameter allows for flexible filtering of files based on naming conventions or extensions.

### 4. `main._is_reprocessing()`

**Purpose:** This function determines whether the current pipeline run is a reprocessing run or a regular run.  It checks for a flag set by a previous task.

**Functionality:**

1.  **Pull XCom Value:** It retrieves the value of an XCom (cross-communication) variable named `TASK_PARAM_REPROCESSING` from the task `TASK_SETUP_PROCESSING`. XComs are used for passing data between Airflow tasks.

    ```python
    reprocess_flag = context['ti'].xcom_pull(key=TASK_PARAM_REPROCESSING, task_ids=TASK_SETUP_PROCESSING)
    ```

2.  **Log Information:** Logs the value of the reprocessing flag.

    ```python
    logging.info(f"Is reprocessing required [{reprocess_flag}]")
    ```

3.  **Conditional Return:** It returns a different task ID based on the value of `reprocess_flag`. If `reprocess_flag` is false, it returns `TASK_PREPARE_STAGING`; otherwise, it returns `TASK_SKIP_PREPARE_STAGING`.

    ```python
    return TASK_PREPARE_STAGING if not reprocess_flag else TASK_SKIP_PREPARE_STAGING
    ```

**Business Logic:** This function allows the pipeline to handle reprocessing scenarios differently from regular runs. For example, it might skip certain data preparation steps if the data has already been prepared.

### 5. `main.getImpersonatedCredentials(target_scopes, target_service_account, target_project)`

**Purpose:** This function generates impersonated credentials for a target service account, allowing the pipeline to access resources as if it were that service account.

**Functionality:**

1.  **Get Default Credentials:** It retrieves the default credentials for the current environment using `google.auth._default.default()`.

    ```python
    source_credentials, project_id = _default.default(scopes=target_scopes)
    ```

2.  **Create Impersonated Credentials:** It creates impersonated credentials using `google.auth.impersonated_credentials.Credentials`.
    *   `source_credentials`: The credentials of the account initiating the impersonation.
    *   `target_principal`: The email address of the service account to impersonate.
    *   `target_scopes`: The OAuth 2.0 scopes required for accessing resources as the target service account.
    *   `lifetime`: The lifetime of the impersonated credentials in seconds.

    ```python
    target_credentials = impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=f'{target_service_account}@{target_project}.iam.gserviceaccount.com',
        target_scopes=target_scopes,
        lifetime=600)
    ```

3.  **Return Credentials:** Returns the impersonated credentials.

    ```python
    return target_credentials
    ```

**Business Logic:** This function is used to implement the principle of least privilege. Instead of granting broad access to the main service account running the pipeline, it uses impersonation to grant specific access to specific resources only when needed.

### 6. `main._get_default_or_from_dag_run(default_value, dag_key, dag_run_conf)`

**Purpose:** This function retrieves a configuration value, prioritizing values passed in the Airflow DAG run configuration. If the value is not found in the DAG run configuration, it returns a default value.

**Functionality:**

1.  **Check DAG Run Configuration:** It checks if the `dag_run_conf` dictionary is not None and if the `dag_key` exists in the dictionary.

    ```python
    if dag_run_conf is not None and dag_key in dag_run_conf:
        return dag_run_conf[dag_key]
    ```

2.  **Return Default Value:** If the `dag_key` is not found in the `dag_run_conf`, it returns the `default_value`.

    ```python
    return default_value
    ```

**Business Logic:** This function allows users to override default configuration values for the pipeline at runtime. This provides flexibility and allows users to customize the pipeline's behavior without modifying the code.

### 7. `main._get_df_service()`

**Purpose:** This function creates and returns a Google Cloud Dataflow service client. This client is used to interact with the Dataflow API, enabling the pipeline to manage Dataflow jobs.

**Functionality:**

1.  **Build Dataflow Service:** It uses the `googleapiclient.discovery.build()` function to create a Dataflow service client.

    ```python
    df_service = build("dataflow", "v1b3", cache_discovery=False)
    ```

2.  **Log Information:** Logs the Dataflow service object.

    ```python
    logging.info("df service [{}]".format(df_service))
    ```

3.  **Return Dataflow Service:** Returns the Dataflow service client.

    ```python
    return df_service
    ```

**Business Logic:** This function centralizes the creation of the Dataflow client, ensuring that all interactions with the Dataflow API use the same client configuration.

### 8. `main._setup_processing()`

**Purpose:** This function sets up the processing environment for a pipeline run. It retrieves configuration values, generates a unique run ID, and pushes these values to XComs for use by subsequent tasks.

**Functionality:**

1.  **Log Information:** Logs the DAG ID and release version.

    ```python
    logging.info(f"Starting DAG [{DAGID}-{RELEASE_RAW}]")
    ```

2.  **Retrieve Context Information:** Retrieves information from the Airflow context, including the execution date, task instance, and DAG run.

    ```python
    execution_dt_utc = context["logical_date"]
    task_instance = context["task_instance"]
    dag_run = context["dag_run"]
    dag_run_conf = dag_run.conf if dag_run else None
    ```

3.  **Retrieve Configuration Values:** Retrieves configuration values from either the DAG run configuration or default values using `_get_default_or_from_dag_run()`.  These values include bucket names, bucket paths, and the number of past hours to process.

    ```python
    gcs_landing_bucket_name = _get_default_or_from_dag_run(GCS_LANDING_BUCKET_NAME, DAG_PARAM_GCS_LANDING_BUCKET_NAME,
                                                           dag_run_conf)
    ```

4.  **Generate Run ID:** Generates a unique run ID based on the execution date, unless a run ID is provided in the DAG run configuration. It also sets a `reprocessing_flag` based on whether a run ID was provided.

    ```python
    if dag_run_conf is not None and DAG_PARAM_RUN_ID in dag_run_conf:
        run_id = dag_run_conf[DAG_PARAM_RUN_ID]
        reprocessing_flag = True
    else:
        run_id = f"{execution_dt_utc.year:04}{execution_dt_utc.month:02}{execution_dt_utc.day:02}{execution_dt_utc.hour:02}{execution_dt_utc.minute:02}"
        reprocessing_flag = False
    ```

5.  **Construct GCS Run Path:** Constructs the full GCS path for the run.

    ```python
    gcs_run_path = f"{gcs_staging_bucket_path}/{run_id}"
    gcs_run_full_path = f"{gcs_staging_bucket_name}/{gcs_run_path}"
    ```

6.  **Construct Job Name:** Constructs the Dataflow job name.

    ```python
    job_name = f"{DF_JOB_NAME}-{run_id}"
    ```

7.  **Push Values to XComs:** Pushes configuration values and the run ID to XComs for use by subsequent tasks.

    ```python
    task_instance.xcom_push(key=TASK_PARAM_LANDING_BUCKET_NAME, value=gcs_landing_bucket_name)
    ```

**Business Logic:** This function is the central configuration point for the pipeline. It ensures that all subsequent tasks have access to the necessary configuration values and metadata.

### 9. `main._cleanup_xcom(context, session)`

**Purpose:** This function cleans up XCom entries associated with a specific DAG ID from the Airflow metadata database.

**Functionality:**

1.  **Get DAG ID:** Retrieves the DAG ID from the Airflow context.

    ```python
    dag_id = context["dag"].dag_id
    ```

2.  **Delete XCom Entries:**  Queries the XCom table in the Airflow metadata database and deletes all entries associated with the DAG ID.

    ```python
    session.query(XCom).filter(XCom.dag_id == dag_id).delete()
    ```

**Business Logic:** This function prevents the XCom table from growing indefinitely, which can impact Airflow performance. It's a maintenance task to keep the Airflow environment clean.

### 10. `main.get_job_metrics(job_id)`

**Purpose:** This function retrieves metrics for a Dataflow job using the Dataflow API.

**Functionality:**

1.  **Get Dataflow Service:** Retrieves the Dataflow service client using `_get_df_service()`.

    ```python
    df_service = _get_df_service()
    ```

2.  **Get Job Metrics:** Calls the `getMetrics` method of the Dataflow service to retrieve metrics for the specified `job_id`.

    ```python
    response = (
        df_service.projects()
        .locations()
        .jobs()
        .getMetrics(projectId=PIPELINE_PROJECT_ID, location=DATAFLOW_REGION, jobId=job_id)
        .execute()
    )
    ```

3.  **Return Metrics:** Returns the retrieved metrics.

    ```python
    metrics = response
    return metrics
    ```

**Business Logic:** This function allows the pipeline to monitor the performance of Dataflow jobs. The retrieved metrics can be used to track resource usage, processing time, and error rates.

### 11. `main._get_impersonated_credentials(target_scopes, target_service_account)`

**Purpose:** This function generates impersonated credentials for a target service account. It's similar to `getImpersonatedCredentials` but without the explicit project ID parameter.

**Functionality:**

1.  **Get Default Credentials:** Retrieves the default credentials for the current environment using `google.auth._default.default()`.

    ```python
    source_credentials, project_id = _default.default(scopes=target_scopes)
    logging.info(f"Source credentials generated for project [{project_id}]")
    ```

2.  **Create Impersonated Credentials:** Creates impersonated credentials using `google.auth.impersonated_credentials.Credentials`.

    ```python
    target_credentials = impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=target_service_account,
        target_scopes=target_scopes,
        lifetime=60 * 60)
    ```

3.  **Return Credentials:** Returns the impersonated credentials.

    ```python
    return target_credentials
    ```

**Business Logic:**  Similar to `getImpersonatedCredentials`, this function is used to grant specific access to resources to the Dataflow pipeline without granting excessive permissions to the primary service account.

### 12. `main._move_blobs(bucket_name, blob_names, destination_bucket_name, destination_prefix)`

**Purpose:** This function moves blobs (files) from one GCS bucket to another, using the `gsutil mv` command.

**Functionality:**

1.  **Log Information:** Logs the source and destination buckets and paths.

    ```python
    logging.info(f"Moving blobs from [{bucket_name}] to [{destination_bucket_name}/{destination_prefix}]")
    ```

2.  **Create Temporary File:** Creates a temporary file to store the list of blobs to move.

    ```python
    time_millis = round(time.time() * 1000)
    tmp_file = f"/tmp/pnr{SUFFIX}_file_copy_{time_millis}.txt"
    with open(tmp_file, "a") as f:
        for i, blob_name in enumerate(blob_names):
            logging.info(
                f"[{i + 1}/{num_blobs}] Adding blob [{bucket_name}/{blob_name}]...")
            f.writelines(f"gs://{bucket_name}/{blob_name}\n")
    ```

3.  **Construct gsutil Command:** Constructs the `gsutil mv` command. This command reads the list of blobs from the temporary file and moves them to the destination bucket and prefix.

    ```python
    impersonation_opts = "" if TEST_RUN == "true" else f"-i {DATAFLOW_SERVICE_ACCOUNT}"
    gsutil_path = "/google-cloud-sdk/bin/" if TEST_RUN == "true" else ""
    gsutil_state_opts = f"-o 'GSUtil:state_dir=/tmp/pnr{SUFFIX}_gsutil_state_{time_millis}'"
    bash_cmd = f"cat {tmp_file} | {gsutil_path}gsutil {gsutil_state_opts} {impersonation_opts} -m mv -I 'gs://{destination_bucket_name}/{destination_prefix}/'"
    ```

4.  **Execute gsutil Command:** Executes the `gsutil mv` command using the `BashOperator`.

    ```python
    file_copy_using_gsutil = BashOperator(
        task_id="file_copy_using_gsutil" + str(uuid.uuid4()),
        bash_command=bash_cmd
    )
    file_copy_using_gsutil.execute(context)
    ```

5.  **Remove Temporary File:** Removes the temporary file.

    ```python
    os.remove(tmp_file)
    ```

**Business Logic:** This function is used to move data between different stages of the pipeline. This is often necessary for organizing data, archiving processed data, or preparing data for further processing.  It is essential in the prepare staging and move to archive functions.

### 13. `main._move_to_archive()`

**Purpose:** This function moves processed files from a staging GCS bucket to an archive GCS bucket.

**Functionality:**

1.  **Pull XCom Values:** Retrieves the archive bucket name, archive bucket path, run bucket name, and run bucket path from XComs.

    ```python
    ti = context['ti']
    gcs_archive_bucket_name = ti.xcom_pull(key=TASK_PARAM_ARCHIVE_BUCKET_NAME, task_ids=TASK_SETUP_PROCESSING)
    gcs_archive_bucket_path = ti.xcom_pull(key=TASK_PARAM_ARCHIVE_BUCKET_PATH, task_ids=TASK_SETUP_PROCESSING)
    ```

2.  **List Processed Files:** Calls `_get_gcs_files()` to list the files in the run bucket.

    ```python
    processed_files = _get_gcs_files(gcs_run_bucket_name, gcs_run_bucket_path, **context)
    ```

3.  **Error Handling:** Checks if any files were found in the run bucket. If not, it raises an `AirflowFailException`.

    ```python
    if len(processed_files) == 0:
        logging.error(f"No files in run path [{gcs_run_bucket_name}/{gcs_run_bucket_path}]")
        raise AirflowFailException(f"No files in run path [{gcs_run_bucket_name}/{gcs_run_bucket_path}]")
    ```

4.  **Group Partitions per Hour:** Groups the processed files by hour using the `group_partitions_per_hour` function (not provided in the code snippet).

    ```python
    per_hour_grouping = group_partitions_per_hour(processed_files, gcs_run_bucket_path + "/")
    ```

5.  **Move Blobs:** Iterates over the grouped partitions and calls `_move_blobs()` to move the files to the archive bucket, organized by partition.

    ```python
    for partition in per_hour_grouping:
        files_per_partition = per_hour_grouping[partition]
        _move_blobs(gcs_run_bucket_name, files_per_partition, gcs_archive_bucket_name,
                    f"{gcs_archive_bucket_path}/{partition}", **context)
    ```

**Business Logic:** This function ensures that processed data is archived for long-term storage and compliance purposes. Organizing the data by hour facilitates efficient retrieval and analysis of historical data.

### 14. `main._get_storage_client(target_service_account, target_project)`

**Purpose:** This function creates and returns a Google Cloud Storage client.

**Functionality:**

1.  **Define Target Scopes:** Defines the necessary OAuth 2.0 scopes required for accessing Cloud Storage resources.

    ```python
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    ```

2.  **Get Impersonated Credentials:** Retrieves impersonated credentials using `_get_impersonated_credentials()` if `TEST_RUN` is not "true".

    ```python
    credentials = None if TEST_RUN == "true" else _get_impersonated_credentials(target_scopes,
                                                                                target_service_account)
    ```

3.  **Create Storage Client:** Creates a `google.cloud.storage.Client` object, using the provided `target_project` and `credentials`.

    ```python
    return storage.Client(project=target_project,
                          credentials=credentials)
    ```

**Business Logic:** This function centralizes the creation of the Cloud Storage client, allowing easy management of authentication and authorization for accessing GCS resources.

### 15. `main.get_bq_impersonated_client(target_service_account, target_project)`

**Purpose:** This function creates and returns a BigQuery client that is impersonated as the service account that is passed to it.

**Functionality:**

1.  **Target Scopes:** Defines the OAuth scopes that would be used in the impersonation of the account

    ```python
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform',
                     'https://www.googleapis.com/auth/bigquery']
    ```

2.  **Credentials:** Gets the impersonated credentials to be passed to Big Query client

    ```python
    return bigquery.Client(project=target_project, credentials=getImpersonatedCredentials(target_scopes, target_service_account, target_project))
    ```

**Business Logic:** This function gets the big query client by impersonating, which is essential in accessing the tables in data warehouse.

### 16. `main._move_landing_to_staging(source_bucket, source_objects, destination_bucket, destination_path, source_path)`

**Purpose:** This function moves files from a landing GCS bucket to a staging GCS bucket.

**Functionality:**

1.  **Log Information:** Logs the source and destination buckets and paths.

    ```python
    logging.info(
        f"Moving [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]...")
    ```

2.  **Move Blobs:** Calls `_move_blobs()` to move the files from the source bucket to the destination bucket and path.

    ```python
    _move_blobs(source_bucket, source_objects, destination_bucket, destination_path, **context)
    ```

**Business Logic:** This function is used to prepare data for processing by moving it from a landing area (where it is initially ingested) to a staging area (where it is prepared for analysis).

### 17. `main._prepare_staging()`

**Purpose:** This function prepares the staging environment for the data pipeline. It selects files from the landing bucket, moves them to the staging bucket, and creates a custom metric to track the number of input files.

**Functionality:**

1.  **Pull XCom Values:** Retrieves the landing bucket name, landing bucket path, run bucket name, run bucket path, and number of past hours from XComs.

    ```python
    ti = context['ti']
    gcs_landing_bucket_name = ti.xcom_pull(key=TASK_PARAM_LANDING_BUCKET_NAME, task_ids=TASK_SETUP_PROCESSING)
    gcs_landing_bucket_path = ti.xcom_pull(key=TASK_PARAM_LANDING_BUCKET_PATH, task_ids=TASK_SETUP_PROCESSING)
    ```

2.  **Get DAG Variables:** Retrieves DAG variables (not fully shown in the provided code).

    ```python
    dag_vars = get_dag_vars()
    max_files = get_dag_var_as_int(VAR_AS_MAX_FILES, dag_vars)
    ```

3.  **List Landing Files:** Calls `_get_gcs_files()` to list the files in the landing bucket.

    ```python
    landing_files = _get_gcs_files(gcs_landing_bucket_name, gcs_landing_bucket_path, **context)
    ```

4.  **Select Files:** Calls `select_files()` to select files from the landing bucket based on the number of past hours.

    ```python
    all_selected_landing_files = select_files(landing_files, gcs_landing_bucket_path + "/", int(num_past_hours))
    ```

5.  **Limit Selected Files:** Limits the number of selected files to a maximum value, if specified by the `max_files` DAG variable.

    ```python
    if 0 < max_files < len(all_selected_landing_files):
        selected_landing_files = all_selected_landing_files[:max_files]
    else:
        selected_landing_files = all_selected_landing_files
    ```

6.  **Error Handling:** Checks if any files were selected. If not, it creates a custom metric with the count of 0 and raises an `AirflowFailException`.

    ```python
    if len(selected_landing_files) == 0:
        create_custom_metrics(f"pnr_input_file_count{SUFFIX}", COMPOSER_PROJECT_ID, "cloud_composer_workflow",
                              "int64_value", 0)
        logging.error(f"No files in landing [{gcs_landing_bucket_name}/{gcs_landing_bucket_path}]")
        raise AirflowFailException(f"No files in landing [{gcs_landing_bucket_name}/{gcs_landing_bucket_path}]")
    ```

7.  **Move Landing Files to Staging:** Calls `_move_landing_to_staging()` to move the selected files from the landing bucket to the staging bucket.

    ```python
    _move_landing_to_staging(gcs_landing_bucket_name, selected_landing_files, gcs_run_bucket_name, gcs_run_bucket_path,
                             gcs_landing_bucket_path, **context)
    ```

8.  **Create Custom Metric:** Creates a custom metric to track the number of input files.

    ```python
    create_custom_metrics(f"pnr_input_file_count{SUFFIX}", COMPOSER_PROJECT_ID, "cloud_composer_workflow",
                          "int64_value", size)
    ```

**Business Logic:** This function prepares the data for processing by selecting the relevant files from the landing area, moving them to a staging area, and tracking the number of input files.

### 18. `main.get_time_diff_between_processed_tm_vs_current_time()`

**Purpose:** This function calculates the time difference in minutes between the maximum `ingest_ts` (ingestion timestamp) in a BigQuery table and the current timestamp. This determines the freshness of the data being processed.

**Functionality:**

1.  **Get BigQuery Client:** Obtains the BigQuery client with impersonation using the service account.

    ```python
    client = get_bq_impersonated_client(service_account_name, PIPELINE_PROJECT_ID)
    ```

2.  **Construct and Execute Query:** Constructs a SQL query to fetch the maximum `ingest_ts`, current timestamp, and the difference between them in minutes. Executes the query using the BigQuery client.

    ```python
    time_difference = """
                        SELECT
                            MAX(ingest_ts) max_ingest_ts,
                            CURRENT_TIMESTAMP() AS current_ts,
                            TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(ingest_ts), MINUTE) diff_in_mins
                        FROM
                          {0}.{1}.{2}  WHERE ingest_ts is not null
                        """.format(PIPELINE_PROJECT_ID, FRESHNESS_CHECK_DATASET_NAME, FRESHNESS_CHECK_TABLE_NAME)

    query_job = client.query(time_difference, job_config=bigquery.QueryJobConfig(
        labels={"pnr-data-ingestion-label": billing_label}), job_id_prefix=billing_label)
    query_job.result()
    ```

3.  **Extract Results:** Extracts the `max_ingest_ts`, `current_ts`, and `diff_in_mins` from the query results.

    ```python
    records_dict = [dict(row) for row in query_job]
    max_ingest_ts_in_batch = records_dict[0]['max_ingest_ts']
    current_ts = records_dict[0]['current_ts']
    diff_in_mins = records_dict[0]['diff_in_mins']
    ```

4.  **Error Handling:** Includes a `try...except` block to handle any exceptions that occur during the query execution.

    ```python
    except Exception as e:
        return logging.info('Error: {}'.format(str(e)))
    ```

5.  **Return Time Difference:** Returns the calculated time difference in minutes.

    ```python
    return diff_in_mins
    ```

**Business Logic:** This function is critical for monitoring data freshness. By comparing the most recent ingestion timestamp with the current time, the pipeline can ensure that it's processing up-to-date data.

### 19. `main.list_jobs()`

**Purpose:** This function lists all Dataflow jobs in a specified project and region.

**Functionality:**

1.  **Get Dataflow Service:** Retrieves the Dataflow service client using `_get_df_service()`.

    ```python
    df_service = _get_df_service()
    ```

2.  **List Dataflow Jobs:** Calls the `list` method of the Dataflow service to retrieve a list of Dataflow jobs.

    ```python
    response = (
        df_service.projects()
        .locations()
        .jobs()
        .list(projectId=PIPELINE_PROJECT_ID, location=DATAFLOW_REGION)
        .execute()
    )
    ```

3.  **Extract Jobs:** Extracts the list of jobs from the response.

    ```python
    jobs = response["jobs"]
    return jobs
    ```

**Business Logic:** This function is used to monitor and manage Dataflow jobs. It can be used to check the status of jobs, identify errors, and track resource usage.

### 20. `main.get_job_id(job_name)`

**Purpose:** This function retrieves the job ID of a Dataflow job, searching by job name and filtering by `JOB_STATE_DONE`.

**Functionality:**

1.  **Log Information:** Logs the Dataflow Job name.

    ```python
    logging.info(job_name)
    ```

2.  **List Jobs:** Calls `list_jobs()` to retrieve a list of all Dataflow jobs.

    ```python
    jobs = list_jobs()
    ```

3.  **Iterate and Find Job ID:** Iterates over the list of jobs and searches for a job with a name that starts with the specified `job_name` and whose current state is "JOB\_STATE\_DONE".

    ```python
    for job in jobs:
        job_nm = job["name"]
        if job_nm.startswith(job_name) and job["currentState"] == "JOB_STATE_DONE":
            job_id = job["id"]
            break;
        else:
            job_id= None
    ```

4.  **Return Job ID:** Returns the job ID
## UML Diagram
![Image](images/anotherDAG_img1.png)
## DAG FLOW
![Image](images/anotherDAG_img2.png)

