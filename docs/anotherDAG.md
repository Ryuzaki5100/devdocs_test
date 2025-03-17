# Generated Documentation with UML
Okay, here's the detailed documentation of the functions, following their likely execution order based on dependencies, along with explanations, business logic insights, cyclomatic complexity considerations, and potential pain points.

**Assumptions:**

*   I'm assuming `main` refers to a module or a class where these functions are defined.
*   I'm assuming certain global variables like `DAGID`, `RELEASE_RAW`, `GCS_LANDING_BUCKET_NAME`, etc., are defined elsewhere in the code.
*   I'm using placeholders for `func1`, `func2`, etc., and will map them to the corresponding function names as I go through the documentation.

**Dependencies Mapping**
* `func1` is `_cleanup_xcom`
* `func2` is `_get_impersonated_credentials`
* `func3` is `_get_default_or_from_dag_run`
* `func4` is `_setup_processing`
* `func5` is `_get_gcs_files`
* `func6` is `get_metric_service_client`
* `func7` is `_move_blobs`
* `func8` is `_get_storage_client`
* `func9` is `getImpersonatedCredentials`
* `func10` is `create_custom_metrics`
* `func11` is `_is_reprocessing`
* `func12` is `_get_df_service`
* `func13` is `get_job_metrics`
* `func14` is `list_jobs`
* `func15` is `_move_to_archive`
* `func16` is `get_bq_impersonated_client`
* `func17` is `get_job_id`
* `func18` is `_move_landing_to_staging`
* `func19` is `_prepare_staging`
* `func20` is `get_time_diff_between_processed_tm_vs_current_time`
* `func21` is `get_job_status`
* `func22` is `get_valid_record_count`
* `func23` is `_process_staging`

**Function Documentation:**

1.  **`_get_default_or_from_dag_run(default_value, dag_key, dag_run_conf)`**

    *   **Purpose:** This function retrieves a configuration value, prioritizing values passed in the Airflow DAG run configuration (`dag_run_conf`). If the `dag_key` is found in the DAG run configuration, its value is returned. Otherwise, the `default_value` is returned.
    *   **How it works:** It checks if `dag_run_conf` is not `None` and if the `dag_key` exists within it. If both conditions are true, it returns the value associated with that key from the configuration. Otherwise, it falls back to the provided `default_value`.
    *   **Business Logic:** This function allows for flexibility in DAG execution. It enables users to override default configuration parameters at runtime through the Airflow UI or API, without modifying the DAG code itself.  This is especially useful for things like bucket names, paths, and processing parameters that might change between executions.
    *   **Cyclomatic Complexity:** Low (2).  It's a simple conditional.
    *   **Potential Pain Points:** None anticipated, its simple and straight forward

2.  **`_setup_processing(**context)`**

    *   **Purpose:** This function is responsible for setting up the processing environment for the DAG run.  This includes extracting configuration values, generating a unique run ID, and pushing these values into Airflow's XCom (cross-communication) system for use by downstream tasks.
    *   **How it works:**
        *   It first logs the start of the DAG and the execution datetime.
        *   It retrieves the DAG run configuration (`dag_run.conf`) from the Airflow context.
        *   It calls `_get_default_or_from_dag_run` to get values for various parameters like landing/archive/staging bucket names and paths, and the number of past hours to process. These values can come from defaults or be overridden by the DAG run configuration.
        *   It generates a unique `run_id` based on the execution datetime, unless a `run_id` is already provided in the DAG run configuration (in which case, it's considered a reprocessing scenario).
        *   It constructs the full GCS path for the run (`gcs_run_full_path`).
        *   It generates a job name (`job_name`) for the Dataflow job.
        *   It uses `task_instance.xcom_push` to push all these parameters (bucket names, paths, `run_id`, `reprocessing_flag`, `job_name`, `num_past_hours`) into XCom.  These values become available to other tasks in the DAG.
    *   **Business Logic:** This function acts as the initialization step of the DAG. It ensures all necessary configuration and parameters are correctly set up and shared between tasks. The `run_id` generation and handling of reprocessing scenarios are key aspects of managing data processing runs.
    *   **Cyclomatic Complexity:** Moderate.  There are multiple `if` statements, especially around reading from the `dag_run_conf`.
    *   **Potential Pain Points:**
        *   **XCom limitations:**  XCom is suitable for small to medium-sized data.  If the configuration data becomes very large, consider alternative storage mechanisms (e.g., storing the configuration in GCS and passing the GCS path via XCom).
        *   **Configuration management:**  The current approach relies on a combination of default values and DAG run configuration.  For more complex scenarios, consider using a dedicated configuration management system (e.g., a configuration file in GCS or a database) to improve maintainability and scalability.
        *   **Error handling:**  More robust error handling could be added to handle cases where required configuration values are missing.

3.  **`_get_impersonated_credentials(target_scopes: list, target_service_account: str)`**

    *   **Purpose:** This function obtains Google Cloud credentials that are impersonated for a specific service account. Impersonation allows a different service account to act on behalf of the specified `target_service_account`.
    *   **How it works:**
        *   It uses `google.auth._default.default()` to get the default credentials and project ID from the environment. These are the credentials that the Airflow worker is running under.
        *   It then uses `google.auth.impersonated_credentials.Credentials()` to create impersonated credentials.  It passes the source credentials, the target service account, the required scopes, and a lifetime (60 minutes).
        *   It returns the impersonated credentials object.
    *   **Business Logic:** In a secure Google Cloud environment, service account impersonation is often used to grant specific permissions to tasks. Instead of granting broad permissions to the Airflow worker service account, each task can impersonate a service account with the minimum required privileges. This enhances security and reduces the risk of unauthorized access.
    *   **Cyclomatic Complexity:** Low.  It primarily involves calling Google Cloud library functions.
    *   **Potential Pain Points:**
        *   **Impersonation configuration:**  Properly configuring service account impersonation requires careful attention to IAM roles and permissions.  The Airflow worker service account must have the `roles/iam.serviceAccountTokenCreator` role on the `target_service_account`.  Misconfiguration can lead to permission errors.
        *   **Scope management:**  Selecting the correct scopes is crucial. The scopes define the level of access granted by the impersonated credentials.  Overly broad scopes can increase security risks.

4.  **`_get_storage_client(target_service_account: str, target_project: str)`**

    *   **Purpose:** This function creates a Google Cloud Storage client, optionally using impersonated credentials if running outside of a test environment.
    *   **How it works:**
        *   It imports `google.cloud.storage`.
        *   It defines the required scopes for Cloud Storage access.
        *   If `TEST_RUN` is "true", it creates a client using the default credentials.
        *   Otherwise, it calls `_get_impersonated_credentials` to get impersonated credentials for the `target_service_account`.
        *   It creates a `storage.Client` object, passing in the `target_project` and the credentials (either the default credentials or the impersonated credentials).
        *   It returns the `storage.Client` object.
    *   **Business Logic:** Provides access to Google Cloud Storage. The ability to use impersonated credentials allows the DAG to access storage resources with the specific permissions of the `target_service_account`, improving security.
    *   **Cyclomatic Complexity:** Low (2).  Conditional logic based on `TEST_RUN`.
    *   **Potential Pain Points:**
        *   Relies on `_get_impersonated_credentials` which has the above mentioned pain points.

5.  **`_get_gcs_files(bucket_name: str, gcs_path: str, **context)`**

    *   **Purpose:** This function lists files in a Google Cloud Storage bucket under a specified path (prefix).
    *   **How it works:**
        *   It uses the `GCSListObjectsOperator` from the Airflow GCP provider.  This operator is designed to efficiently list objects in GCS.
        *   The operator is configured with the `bucket`, `prefix`, and `match_glob` parameters.  The `match_glob` parameter is set to `**/*` + `DELIMITER` to match files that end with the `DELIMITER` which is used for uniquely identifying the file
        *   The `impersonation_chain` is set to `DATAFLOW_SERVICE_ACCOUNT` unless `TEST_RUN` is "true". This ensures that the listing operation is performed using the specified service account's credentials.
        *   The `execute()` method of the operator is called to perform the listing.
        *   The function returns the list of files found.
    *   **Business Logic:** This function is a crucial part of the data ingestion pipeline. It identifies the files in the landing zone that need to be processed.
    *   **Cyclomatic Complexity:** Low. Relies on the complexity of `GCSListObjectsOperator`.
    *   **Potential Pain Points:**
        *   **Performance:** Listing a very large number of objects in GCS can be slow. If performance becomes an issue, consider using pagination or other optimization techniques.
        *   **Permissions:** The `DATAFLOW_SERVICE_ACCOUNT` needs to have the appropriate permissions (e.g., `storage.objects.list`) on the specified bucket and path.

6.  **`select_files(landing_files, gcs_landing_bucket_path + "/", int(num_past_hours))`**

    *   **Purpose:** This function selects files from a list of landing files based on their timestamp and the number of past hours to consider.
    *   **How it works:**
        *   TODO: Provide the body for the function
    *   **Business Logic:** TODO: Provide the business logic for the function
    *   **Cyclomatic Complexity:** TODO: Provide the complexity for the function
    *   **Potential Pain Points:** TODO: Provide pain points if any

7.  **`create_custom_metrics(metric_type: str, project_id: str, resource_type: str, value_type: str, val)`**

    *   **Purpose:** This function creates and publishes custom metrics to Google Cloud Monitoring.
    *   **How it works:**
        *   It gets a MetricServiceClient instance by calling `get_metric_service_client`.
        *   It constructs the project name in the format `projects/{project_id}`.
        *   It creates a `monitoring_v3.TimeSeries` object. This object represents the metric data to be published.
            *   It sets the metric type to `CUSTOM_METRIC_DOMAIN` + "/" + `metric_type`.
            *   It adds labels to the metric, including the `application_name` (set to `DAGID`), `workflow_name` (also `DAGID`).
            *   It sets the resource type and labels, including the `project_id`, `workflow_name`, and `location`.
            *   It creates a `monitoring_v3.TimeInterval` object to specify the time range for the metric data.
            *   It creates a `monitoring_v3.Point` object to represent the metric value at the specified time.
            *   It assigns the `point` to the `series.points` list.
        *   It calls `client.create_time_series` to publish the metric data to Cloud Monitoring.
        *   It catches any exceptions that occur during the process and logs an error message.
    *   **Business Logic:** This function provides a way to track the performance and health of the DAG. Custom metrics can be used to monitor things like the number of files processed, the data processing latency, and any errors that occur.
    *   **Cyclomatic Complexity:** Moderate (try/except block, object creation).
    *   **Potential Pain Points:**
        *   **Error handling:** The `try...except` block catches all exceptions. It might be helpful to catch specific exceptions and handle them differently.
        *   **Metric granularity:** Consider the granularity of the metrics being published. Publishing too many metrics or metrics with high cardinality can increase costs and impact performance.
        *   **Permissions:** The `COMPOSER_SERVICE_ACCOUNT` must have the `monitoring.metricDescriptors.create` and `monitoring.timeSeries.create` permissions on the project.

8.  **`_move_landing_to_staging(source_bucket: str, source_objects: list, destination_bucket: str, destination_path: str, source_path: str, **context)`**

    *   **Purpose:** This function moves files from the landing zone to the staging area in GCS.
    *   **How it works:**
        *   It logs the number of files to be moved and the source and destination locations.
        *   It calls the `_move_blobs` function to perform the actual file movement.
    *   **Business Logic:** Moves files from the initial landing zone (where they are first ingested) to the staging area, which is a dedicated location for files that are ready to be processed by the Dataflow job.
    *   **Cyclomatic Complexity:** Low. Primarily a wrapper around `_move_blobs`.
    *   **Potential Pain Points:** Relies on `_move_blobs` which has the mentioned pain points below

9.  **`_move_blobs(bucket_name: str, blob_names: list, destination_bucket_name: str, destination_prefix: str, **context)`**

    *   **Purpose:** This function moves multiple blobs (files) from one GCS location to another using the `gsutil` command-line tool.
    *   **How it works:**
        *   It logs the source and destination locations.
        *   It creates a temporary file (`tmp_file`) to store the list of source GCS paths.
        *   It writes the GCS paths of all blobs to be moved into the temporary file, one path per line.
        *   It constructs a `bash_cmd` that uses `gsutil -m mv -I` to move the files. The `-I` option tells `gsutil` to read the list of source paths from the temporary file. The `-m` option enables parallel moving of the files to improve performance.
        *   It creates a `BashOperator` from Airflow to execute the `bash_cmd`.
        *   It calls `file_copy_using_gsutil.execute(context)` to execute the bash command.
        *   It removes the temporary file.
    *   **Business Logic:** Moves files between GCS locations. This is a fundamental operation for data pipelines, enabling the movement of data from landing zones to staging areas, and from staging areas to archive locations. Using `gsutil -m` provides parallelization for faster file transfers.
    *   **Cyclomatic Complexity:** Moderate. Involves file I/O, string formatting, and calling a bash command.
    *   **Potential Pain Points:**
        *   **Temporary file management:**  Ensure the temporary file is properly cleaned up after use (the code already does this with `os.remove(tmp_file)`).
        *   **`gsutil` dependency:**  The function relies on the `gsutil` command-line tool being available on the Airflow worker nodes.
        *   **Error handling:**  The `BashOperator` will raise an exception if the `gsutil` command fails. However, more granular error handling might be needed to capture specific `gsutil` errors and retry the operation.
        *   **Security:** Running arbitrary bash commands can introduce security risks. Ensure that the `bash_cmd` is constructed carefully to prevent command injection vulnerabilities.
        *   **File size limitations**: When the number of files is very large, the command might fail because the generated command line is too long. You might need to chunk the files and move it iteratively

10. **`_prepare_staging(**context)`**

    *   **Purpose:** This function orchestrates the process of preparing the staging area by selecting files from the landing zone and moving them to the staging area.
    *   **How it works:**
        *   It retrieves the necessary parameters (landing bucket name/path, run bucket name/path, number of past hours) from XCom.
        *   It retrieves `max_files` from dag variables.
        *   It calls `_get_gcs_files` to list the files in the landing zone.
        *   It calls `select_files` to select the files to be processed based on the timestamp and number of past hours.
        *   It limits the number of selected landing files to `max_files` if defined.
        *   It calls `_move_landing_to_staging` to move the selected files from the landing zone to the staging area.
        *   It raises `AirflowFailException` if no files are found in the landing zone.
        *   It records custom metrics
    *   **Business Logic:** This function implements the core logic for selecting and preparing data for processing. The selection logic based on timestamp and number of past hours allows for incremental data processing.
    *   **Cyclomatic Complexity:** Moderate. It has multiple calls to external functions, conditional logic (limiting number of files).
    *   **Potential Pain Points:**
        *   Relies on `select_files` to have well defined logic.
        *   The XCom values need to be set up correctly in the `_setup_processing` function.

11. **`_is_reprocessing(**context)`**

    *   **Purpose:** This function determines whether the current DAG run is a reprocessing run based on the `reprocessing_flag` stored in XCom.
    *   **How it works:**
        *   It retrieves the `reprocess_flag` from XCom using `context['ti'].xcom_pull`.
        *   It logs the value of the flag.
        *   It returns `TASK_PREPARE_STAGING` if `reprocess_flag` is `False` (meaning it's a normal run), and `TASK_SKIP_PREPARE_STAGING` if `reprocess_flag` is `True` (meaning it's a reprocessing run).
    *   **Business Logic:** This function controls the execution flow of the DAG based on whether it's a normal run or a reprocessing run. In a reprocessing run, the `_prepare_staging` task might be skipped to avoid duplicating data.
    *   **Cyclomatic Complexity:** Low (conditional statement).
    *   **Potential Pain Points:**
        *   The `reprocess_flag` must be correctly set in the `_setup_processing` function for this function to work correctly.
        *   Ensure correct task ID dependency in `xcom_pull`.

12. **`_get_df_service()`**

    *   **Purpose:** This function creates and returns a Google Cloud Dataflow service object.
    *   **How it works:**
        *   It uses the `build` function from the `googleapiclient.discovery` module to create a Dataflow service object.
        *   The `build` function takes the service name ("dataflow"), the API version ("v1b3"), and a `cache_discovery=False` argument.
        *   The function logs the service object.
        *   It returns the Dataflow service object.
    *   **Business Logic:** This function encapsulates the creation of the Dataflow service object, which is used to interact with the Dataflow API.
    *   **Cyclomatic Complexity:** Low.
    *   **Potential Pain Points:**
        *   If there are issues with the Google API client library or the Dataflow API itself, this function might fail.
        *   The `cache_discovery=False` argument disables API discovery caching. While this might be useful for development, it can impact performance in production. Consider enabling caching for production deployments.

13. **`get_job_status(job_name)`**

    *   **Purpose:** This function retrieves the status of a Dataflow job by its name.
    *   **How it works:**
        *   It logs the `job_name`.
        *   It calls the `list_jobs()` function to retrieve a list of all Dataflow jobs.
        *   It iterates over the list of jobs and checks if the job name starts with the given `job_name`.
        *   If a matching job is found, it retrieves the `currentState` of the job and returns it.
        *   If no matching job is found, it returns `None`.
    *   **Business Logic:** This function allows the DAG to monitor the status of the Dataflow job and take appropriate actions based on its status.
    *   **Cyclomatic Complexity:** Moderate. It involves iterating over a list and checking for a match.
    *   **Potential Pain Points:**
        *   If there are many Dataflow jobs in the project, the `list_jobs()` function can be slow.
        *   The function only checks if the job name *starts with* the given `job_name`. This might not be sufficient if there are multiple jobs with similar names.
        *   The function returns the first matching job status that matches the name and could be inaccurate.

14. **`list_jobs()`**

    *   **Purpose:** Lists all Dataflow jobs in a project and location.
    *   **How it works:**
        *   It calls `_get_df_service()` to get the Dataflow service object.
        *   It uses the Dataflow service object to call the `projects().locations().jobs().list()` API method to list all jobs in the specified project and location.
        *   It extracts the list of jobs from the response and returns it.
    *   **Business Logic:** Provides a way to retrieve information about all Dataflow jobs in a project. This is useful for monitoring, auditing, and troubleshooting.
    *   **Cyclomatic Complexity:** Low. Primarily a wrapper around the Dataflow API.
    *   **Potential Pain Points:**
        *   Listing all jobs can be slow if there are many jobs in the project.
        *   The function does not handle pagination. If there are more jobs than the API's default page size, it will only return the first page of results.

15. **`get_job_id(job_name)`**

    *   **Purpose:** Retrieves the ID of a completed Dataflow job with a given name.
    *   **How it works:**
        *   Calls `list_jobs()` to get a list of Dataflow jobs.
        *   Iterates through the jobs, comparing the job's name to the given `job_name`. It checks `job["name"]` starts with `job_name` and the job's `currentState` is `JOB_STATE_DONE`.
        *   If a match is found, the job's ID is returned.
        *   If no matching job is found that is in the state of `JOB_STATE_DONE`, `None` is returned.
    *   **Business Logic:**  Finds the Dataflow job ID which can be used to get additional metrics from the job.
    *   **Cyclomatic Complexity:** Moderate, involves iteration and conditional logic.
    *   **Potential Pain Points:**
        *   Relies on `list_jobs()` which can be slow for many jobs.
        *   It only selects jobs in `JOB_STATE_DONE` which may not be the desired behavior for finding current jobs, or failed jobs
        *   It only returns the first job ID which is matched.

16. **`get_job_metrics(job_id)`**

    *   **Purpose:** Retrieves metrics for a specific Dataflow job.
    *   **How it works:**
        *   It calls `_get_df_service()` to get the Dataflow service object.
        *   It uses the Dataflow service object to call the `projects().locations().jobs().getMetrics()` API method to retrieve the metrics for the specified job ID.
        *   It returns the raw response containing the metrics.
    *   **Business Logic:** Provides access to detailed performance and operational metrics for a Dataflow job. This is crucial for monitoring the job's progress, identifying bottlenecks, and optimizing its performance.
    *   **Cyclomatic Complexity:** Low. It primarily calls the Dataflow API.
    *   **Potential Pain Points:**
        *   If the Dataflow job does not exist or if the API call fails, this function will raise an exception.
        *   The raw response from the API might need to be parsed and processed to extract the desired metrics.

17. **`get_valid_record_count(job_name, metrics_names)`**

    *   **Purpose:** This function retrieves the count of valid records processed by a Dataflow job based on a given job name and a list of metrics names.
    *   **How it works:**
        *   It first calls the `get_job_id` function to retrieve the job ID corresponding to the given `job_name`.
        *   If a `job_id` is found, it calls the `get_job_metrics` function to retrieve the metrics for that job.
        *   If job metrics are found, it iterates through the metrics and checks if the metric name matches any of the names in `metrics_names`
        *   If it finds a matching metric, it extracts the scalar value and returns it
        *   If no matching metrics or no job id is found, the function returns 0
    *   **Business Logic:** This function is meant to extract specific metric data from a Dataflow job execution, which is typically used to confirm correct output volume.
    *   **Cyclomatic Complexity:** High, involves conditional logic, looping, and potentially error conditions.
    *   **Potential Pain Points:**
        *   Relies on `get_job_metrics()` and `get_job_id()` functions, which are prone to issues.
        *   It assumes the desired metric is a scalar value. This might not be the case for all metrics.
        *   If the `get_job_metrics` function returns `None` or if the `metrics` list is empty, the function will not return the valid record count.

18. **`_process_staging(**context)`**

    *   **Purpose:** This function starts a Dataflow job from a template, passing in the staged data location and other configuration parameters.
    *   **How it works:**
        *   Retrieves the job name and run path from XCom.
        *   Retrieves Dataflow worker configuration (number of workers, max workers, machine type) from dag variables
        *   Uses `DataflowTemplatedJobStartOperator` to launch the Dataflow job. Key parameters include:
            *   `template`: Specifies the GCS location of the Dataflow template.
            *   `job_name`: The name of the Dataflow job.
            *   `parameters`:  Includes the `runPath` parameter, which tells the Dataflow job where to find the input data in GCS.
            *   `dataflow_default_options`: Specifies default options for the Dataflow job, such as the temp location, number of workers, max workers, and machine type.
        *   The function retries in a loop to handle HttpError's thrown by the job.
        *   It pushes the "JOB\_STATE\_DONE" status to xcom
        *   After the Dataflow job has started, the function gets the `pnr_processed_file_count` from the Dataflow job
        *   It get's the lag time in minutes between processed timestamp and current time
        *   It records some custom metrics related to the job
    *   **Business Logic:** This function encapsulates the starting of the Dataflow processing step in the DAG. It uses the Dataflow template to define the data processing logic and provides the necessary parameters to the Dataflow job.
    *   **Cyclomatic Complexity:** High. There's a `while` loop for retries, calls to external functions, and exception handling.
    *   **Potential Pain Points:**
        *   **Template management:** Ensuring the Dataflow template is correctly configured and deployed is critical.
        *   **Error handling:** The `try...except` block catches a broad exception, it might be more selective to handle specific expected exceptions.
        *   **Parameter passing:** Ensuring the correct parameters are passed to the Dataflow job is crucial. Any misconfiguration can lead to processing errors.
        *   **Retries**: The use of a max retry loop may cause issues and may not be ideal as it may flood the server with request. exponential backoff would be a better solution.

19. **`getImpersonatedCredentials(target_scopes, target_service_account, target_project)`**

    *   **Purpose:** Gets impersonated credentials for a target service account using the Google Cloud IAM API.
    *   **How it works:**
        *   Uses `google.auth._default.default()` to get the default credentials and project ID from the environment.
        *   Creates `impersonated_credentials.Credentials` using:
            *   The default (source) credentials.
            *   The target service account email address (constructed from `target_service_account` and `target_project`).
            *   The required scopes.
            *   A lifetime of 600 seconds.
    *   **Business Logic:** Allows a service (like Airflow) to assume the identity of another service account with specific permissions. This is important for security and access control.
    *   **Cyclomatic Complexity:** Low.
    *   **Potential Pain Points:**
        *   Requires the Airflow worker service account to have the correct IAM permissions to impersonate the `target_service_account`.
        *   The lifetime of the credentials is fixed at 600 seconds. This might not be suitable for all use cases.

20. **`get_bq_impersonated_client(target_service_account, target_project)`**

    *   **Purpose:** Creates a BigQuery client that uses impersonated credentials.
    *   **How it works:**
        *   Defines the necessary scopes for BigQuery access.
        *   Calls `getImpersonatedCredentials` to obtain impersonated credentials for the specified service account and project.
        *   Creates a `bigquery.Client` object using the impersonated credentials.
    *   **Business Logic:** Allows the DAG to interact with BigQuery using the permissions of a specific service account, rather than the default credentials of the Airflow worker. This improves security and allows for fine-grained access control.
    *   **Cyclomatic Complexity:** Low.
    *   **Potential Pain Points:**
        *   Depends on `getImpersonatedCredentials`, which has its own potential pain points.
        *   Requires the correct IAM permissions to allow impersonation.

21. **`get_time_diff_between_processed_tm_vs_current_time()`**

    *   **Purpose:** Retrieves the time difference in minutes between the maximum `ingest_ts` (ingestion timestamp) from a BigQuery table and the current timestamp. This is used to check data freshness.
    *   **How it works:**
        *   Constructs a SQL query to:
            *   Find the maximum `ingest_ts` from the specified BigQuery table (`FRESHNESS_CHECK_DATASET_NAME.FRESHNESS_CHECK_TABLE_NAME`).
            *   Get the current timestamp (`CURRENT_TIMESTAMP()`).
            *   Calculate the difference in minutes between the current timestamp and the maximum `ingest_ts` using `TIMESTAMP_DIFF`.
        *   Calls `get_bq_impersonated_client` to get a BigQuery client with impersonated credentials.
        *   Executes the SQL query using the BigQuery client.
        *   Extracts the `max_ingest_ts`, `current_ts`, and `diff_in_mins` from the query results.
        *   Returns the `diff_in_mins`.
    *   **Business Logic:** This function is designed to measure the freshness of data in the BigQuery table. The time difference indicates how long ago the latest data was ingested. This is a key metric for monitoring the health and reliability of the data pipeline.
    *   **Cyclomatic Complexity:** Moderate. Involves constructing a SQL query, executing it, and processing the results. The `try...except` block adds to the complexity.
    *   **Potential Pain Points:**
        *   The SQL query is hardcoded. Any changes to the table structure or data types will require modifying the query.
        *   The function only retrieves the *maximum* `ingest_ts`. This might not be representative of the overall data freshness if there are only a few recent records.
        *   Relies on `get_bq_impersonated_client`, which has its own potential pain points.
        *   The `try...except` block catches all exceptions. More specific error handling would be better.
        *   No handling when the ingestion timestamp is null.

22. **`get_metric_service_client(target_service_account)`**

    *   **Purpose:** Gets a Google Cloud Monitoring MetricServiceClient.
    *   **How it works:**
        *   Defines the necessary scopes for Cloud Monitoring access (`https://www.googleapis.com/auth/cloud-platform`).
        *   Creates and returns a `monitoring_v3.MetricServiceClient()`
    *   **Business Logic:** Provides a way to interact with the Google Cloud Monitoring API to create and manage metrics.
    *   **Cyclomatic Complexity:** Low.
    *   **Potential Pain Points:**
        *   Doesn't use the `target_service_account` parameter. Potentially needs to use the `_get_impersonated_credentials` function to use specified service account credentials
23.  **Main DAG Flow**
    * The DAG will start with the `_setup_processing` function to extract all the configuration variables.
    * The next function will be `_is_reprocessing` which will determine whether the DAG run is for a reprocessing run.
    * If `_is_reprocessing` is false, it will run `_prepare_staging` that extracts the files to be processed, from the landing bucket to a staging bucket.
    * After the files have been staged, the DAG will run the dataflow job, with the function `_process_staging`.
    * If the dataflow job runs without errors, `_move_to_archive` is run which moves all the files from the staging bucket to the archive bucket.
    * Once the files have been moved to the archive bucket, the `_cleanup_xcom` is run to remove all the XCom artifacts that were generated by this DAG run.

24.  **`_cleanup_xcom(context, session)`**

    *   **Purpose:** Cleans up XCom entries associated with the current DAG run to prevent clutter and potential data leakage.
    *   **How it works:**
        *   Extracts the DAG ID from the Airflow `context`.
        *   Queries the XCom table using the provided `session` (Airflow database session).
        *   Filters the XCom entries to delete only those associated with the current DAG ID.
        *   Deletes the filtered XCom entries.
    *   **Business Logic:** Maintains a clean Airflow
## UML Diagram
![Image](images/anotherDAG_img1.png)
## DAG FLOW
![Image](images/anotherDAG_img2.png)

