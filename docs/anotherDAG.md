# Generated Documentation with UML
```python
def _get_default_or_from_dag_run(default_value: str, dag_key, dag_run_conf):
    if dag_run_conf is not None and dag_key in dag_run_conf:
        return dag_run_conf[dag_key]
    return default_value
```

**Documentation:**

`_get_default_or_from_dag_run(default_value, dag_key, dag_run_conf)`

**Purpose:**

This function retrieves configuration values, prioritizing values passed via the Airflow DAG run's configuration. If a specific configuration parameter isn't provided in the DAG run, it falls back to a predefined default value.

**How it Works:**

1.  **Check for DAG Run Configuration:** It first checks if a `dag_run_conf` dictionary is available (meaning the DAG was triggered with a configuration).
2.  **Check for Key in Configuration:** If a configuration exists, it checks if the `dag_key` (the configuration parameter name) is present in the `dag_run_conf` dictionary.
3.  **Return Value:**
    *   If the `dag_key` is found in the `dag_run_conf`, its corresponding value is returned.
    *   Otherwise, the `default_value` passed to the function is returned.

**Business Logic:**

This function implements a common pattern in Airflow DAGs: allowing users to override default pipeline behavior through the DAG run configuration. This makes the DAG more flexible and reusable, as users can customize it without modifying the DAG's code directly.  For example, a user could specify a different landing bucket or path for a specific execution.

**Example:**

```python
default_bucket = "default-landing-bucket"
dag_config = {"landing_bucket": "override-bucket"} # example of Dag run config

# Scenario 1: Key present in dag_config
bucket_name = _get_default_or_from_dag_run(default_bucket, "landing_bucket", dag_config)
print(bucket_name) # Output: override-bucket

# Scenario 2: Key not present in dag_config
bucket_name = _get_default_or_from_dag_run(default_bucket, "another_key", dag_config)
print(bucket_name) # Output: default-landing-bucket
```

**Cyclomatic Complexity:**

The cyclomatic complexity is low (2), due to the simple `if-else` structure.

**Pain Points:**

The function is straightforward and doesn't inherently have significant pain points. However, a potential improvement could be adding type validation to ensure that the value retrieved from the `dag_run_conf` matches the expected type.

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

**Documentation:**

`_setup_processing(**context)`

**Purpose:**

This function initializes the data processing pipeline by extracting configuration parameters, determining the run ID, and pushing these parameters to XComs (cross-communication mechanism in Airflow) for use by downstream tasks. It essentially sets up the environment and parameters for the current pipeline run.

**How it Works:**

1.  **Logging:** It starts by logging basic information about the DAG and the current execution context.
2.  **Extracting Context Information:** Retrieves the execution datetime (`logical_date`), the `TaskInstance`, and the `DagRun` object from the `context`.
3.  **Retrieving Configuration Parameters:**  It calls `_get_default_or_from_dag_run` to retrieve various configuration parameters such as:
    *   GCS bucket names and paths for landing, archive, and staging.
    *   The number of past hours to consider for data selection.  It retrieves these values either from the DAG run's configuration or from default values.
4.  **Determining the Run ID:**  It checks if a `RUN_ID` is provided in the DAG run configuration.
    *   If a `RUN_ID` is provided, it uses that and sets a `reprocessing_flag` to `True` (indicating a reprocessing run).
    *   If not, it generates a new `RUN_ID` based on the execution datetime and sets `reprocessing_flag` to `False`.
5.  **Constructing Paths:**  It constructs the full GCS path for the current run based on the staging bucket and the run ID.
6.  **Constructing Job Name:** Creates a job name for the Dataflow job based on a prefix and the run ID.
7.  **Pushing to XCom:**  Finally, it pushes all the retrieved and constructed parameters to XCom using `task_instance.xcom_push`. These parameters include bucket names, paths, the `reprocessing_flag`, the job name, and the number of past hours.

**Business Logic:**

This function orchestrates the initial setup of the pipeline.  It handles the following key aspects:

*   **Configuration Management:**  It centralizes the retrieval of configuration parameters, allowing users to customize the pipeline through DAG run configurations.
*   **Run Identification:**  It manages the generation or retrieval of a unique run ID, ensuring that each pipeline execution is properly tracked and isolated.
*   **Parameter Sharing:** It uses XCom to pass the necessary parameters to downstream tasks, enabling communication and coordination between different parts of the DAG.
*   **Reprocessing Logic:** The logic surrounding the `reprocessing_flag` provides a mechanism to rerun the pipeline for a specific time range, which is useful for handling data errors or backfilling missing data.

**Example:**

```python
# Example DAG Run configuration
dag_run_config = {
    "gcs_landing_bucket_name": "my-landing-bucket",
    "num_past_hours": "24",
    "run_id": "user-specified-run-id"
}

# Inside the _setup_processing function:
# ...
# gcs_landing_bucket_name will be "my-landing-bucket" (taken from dag_run_config)
# num_past_hours will be "24" (taken from dag_run_config)
# reprocessing_flag will be True (because run_id is provided)
```

**Cyclomatic Complexity:**

The cyclomatic complexity is moderate (4). The decision points are: checking for `dag_run`, `dag_run_conf is not None and DAG_PARAM_RUN_ID in dag_run_conf`.

**Pain Points:**

*   **Stringly-typed configuration:** The function uses strings for configuration values.  It could benefit from using more specific data types and validation.
*   **XCom Dependence:**  The heavy reliance on XCom can make debugging more difficult, as it's harder to trace the flow of data.
*   **Lack of Error Handling:** There is limited error handling. If a required parameter is missing, the pipeline might fail in a later task. Adding checks for the existence of essential parameters would improve robustness.
*   **Hardcoded Keys:** The keys for the XComs (`TASK_PARAM_LANDING_BUCKET_NAME`, etc.) are likely defined elsewhere as constants. Ensuring consistency and avoiding typos is crucial.

```python
def _is_reprocessing(**context):
    reprocess_flag = context['ti'].xcom_pull(key=TASK_PARAM_REPROCESSING, task_ids=TASK_SETUP_PROCESSING)
    logging.info(f"Is reprocessing required [{reprocess_flag}]")
    return TASK_PREPARE_STAGING if not reprocess_flag else TASK_SKIP_PREPARE_STAGING
```

**Documentation:**

`_is_reprocessing(**context)`

**Purpose:**

This function determines whether the current pipeline run is a reprocessing run based on a flag retrieved from XCom.  It then returns the ID of the next task to be executed, effectively controlling the flow of the DAG.

**How it Works:**

1.  **Retrieve Reprocessing Flag from XCom:** It retrieves the value of the `TASK_PARAM_REPROCESSING` key from XCom, specifically from the task with ID `TASK_SETUP_PROCESSING`. The `ti` object (Task Instance) from the context is used to pull the value.
2.  **Logging:** It logs whether reprocessing is required based on the retrieved flag.
3.  **Conditional Task Routing:** It returns either `TASK_PREPARE_STAGING` or `TASK_SKIP_PREPARE_STAGING` based on the value of the `reprocess_flag`. If `reprocess_flag` is `False` (meaning it's *not* a reprocessing run), it returns `TASK_PREPARE_STAGING`. Otherwise, it returns `TASK_SKIP_PREPARE_STAGING`.

**Business Logic:**

This function implements conditional execution in the DAG. The business logic is to avoid unnecessary steps (presumably the "prepare staging" step) if the pipeline is being rerun for a specific time range. This can save time and resources. The function acts as a branching point in the DAG based on the reprocessing flag.

**Example:**

```python
# Assuming TASK_SETUP_PROCESSING has pushed reprocess_flag = True to XCom

# Inside the _is_reprocessing function:
# reprocess_flag will be True (retrieved from XCom)
# The function will return TASK_SKIP_PREPARE_STAGING
```

**Cyclomatic Complexity:**

The cyclomatic complexity is low (2) due to the simple `if-else` structure.

**Pain Points:**

*   **Magic Strings:** The task IDs (`TASK_SETUP_PROCESSING`, `TASK_PREPARE_STAGING`, `TASK_SKIP_PREPARE_STAGING`) and the XCom key (`TASK_PARAM_REPROCESSING`) are likely defined as constants elsewhere.  A typo in these strings could lead to unexpected behavior.
*   **Implicit Dependency:** The function has an implicit dependency on the `TASK_SETUP_PROCESSING` task having successfully pushed the `reprocessing_flag` to XCom. If that task fails or doesn't push the flag, this function will error.
*   **Boolean Blindness:**  The use of a bare boolean `reprocess_flag` can be less readable than using a named constant (e.g., `IS_REPROCESSING`).

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

**Documentation:**

`_get_gcs_files(bucket_name, gcs_path, **context)`

**Purpose:**

This function retrieves a list of files from a Google Cloud Storage (GCS) bucket based on a given path and a file-matching pattern. It uses the `GCSListObjectsOperator` from Airflow's Google Cloud provider.

**How it Works:**

1.  **Logging:** Logs the bucket and path from which files are being listed.
2.  **GCSListObjectsOperator:**
    *   It creates a `GCSListObjectsOperator` object.
    *   `task_id`:  A unique task ID is generated using `uuid.uuid4()` to avoid conflicts if the task is used multiple times in the DAG.
    *   `bucket`:  The GCS bucket to list files from.
    *   `prefix`: The path within the bucket to list files from.
    *   `match_glob`:  A glob pattern to match files.  `"**/*" + DELIMITER` means to match any file with any name, in any subdirectory, that ends with the `DELIMITER` (presumably a file extension or suffix).
    *   `impersonation_chain`: It sets the service account to use for authentication when listing GCS objects, unless it is a test run. If `TEST_RUN` is "true", impersonation is disabled. Otherwise, it uses `DATAFLOW_SERVICE_ACCOUNT`.
    *   `dag`: The Airflow DAG object.
3.  **Execute the Operator:** It executes the `GCSListObjectsOperator` using `gcs_list_objects.execute(context)`. This triggers the actual listing of files in GCS.
4.  **Logging:** Logs the number of files found.
5.  **Return Files:** Returns the list of files retrieved from GCS.

**Business Logic:**

This function is a utility for interacting with GCS. It abstracts the details of listing files in a bucket, providing a simple interface for other tasks in the DAG.  The `match_glob` parameter allows for filtering files based on a pattern, which is useful for selecting specific data files for processing.

**Example:**

```python
# Assuming gcs_bucket = "my-data-bucket" and gcs_prefix = "raw/data/"
# And DELIMITER = ".csv"

# Inside the _get_gcs_files function:
# The GCSListObjectsOperator will list all files in "my-data-bucket/raw/data/"
# that end with ".csv".
# The function will return a list of filenames like ["raw/data/file1.csv", "raw/data/file2.csv"]
```

**Cyclomatic Complexity:**

The cyclomatic complexity is low (2) because of the conditional `impersonation_chain`.

**Pain Points:**

*   **Dependency on `GCSListObjectsOperator`:**  The function is tightly coupled to the `GCSListObjectsOperator`. If the operator's behavior changes, this function might need to be updated.
*   **Error Handling:** There's no explicit error handling. If the GCS listing fails (e.g., due to permission errors or network issues), the function will likely raise an exception, but it's not handled gracefully.
*   **`uuid.uuid4()` in `task_id`:** While generating a unique `task_id` is good practice, constantly generating new task IDs can make it harder to monitor and debug the DAG, especially if you want to track the history of a specific listing operation.  Consider using a more descriptive and consistent base task ID.
*   **`TEST_RUN` Conditional:** The `TEST_RUN` conditional suggests that the function's behavior changes during testing. This can make it harder to reason about the code and ensure that it behaves correctly in all environments.

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

**Documentation:**

`_prepare_staging(**context)`

**Purpose:**

This function prepares the staging environment by retrieving files from the landing zone, selecting a subset of those files based on time and a maximum file limit, and then moving the selected files to the staging area.

**How it Works:**

1.  **Retrieve Parameters from XCom:** It retrieves various parameters from XCom using `ti.xcom_pull`. These parameters include:
    *   GCS bucket names and paths for landing and staging areas.
    *   The number of past hours to consider for file selection.
2.  **Retrieve DAG Variables:** Retrieves DAG variables using `get_dag_vars()`, specifically `VAR_AS_MAX_FILES` to determine the maximum number of files to process.
3.  **Logging:** Logs the retrieved parameters.
4.  **List Landing Files:** Calls `_get_gcs_files` to retrieve a list of files from the landing zone.
5.  **Select Files:** Calls a `select_files` function (not provided in the code snippet, but presumably selects files based on their timestamp and the `num_past_hours`).
6.  **Limit File Count:** If a `max_files` value is specified and the number of selected files exceeds this limit, it truncates the list of selected files to the specified maximum.
7.  **Error Handling:** Checks if any files were selected. If no files were selected, raises an `AirflowFailException` to stop the DAG and logs a custom metric with a file count of 0.
8.  **Move Files to Staging:** Calls `_move_landing_to_staging` to move the selected files from the landing zone to the staging area.
9.  **Create Metric:** Creates a custom metric `pnr_input_file_count` with the size of the files moved.

**Business Logic:**

This function is responsible for preparing the data for processing. It ensures that only the necessary files are processed, based on time window and maximum file limits. The file selection and limiting logic prevent the pipeline from processing too much data, which could lead to performance issues or increased costs. The function separates data ingestion from the actual processing.

**Example:**

```python
# Example:
# gcs_landing_bucket_name = "my-landing-bucket"
# gcs_landing_bucket_path = "raw/data/"
# num_past_hours = 24
# max_files = 10

# The function will:
# 1. List all files in "my-landing-bucket/raw/data/".
# 2. Select files from the last 24 hours.
# 3. If more than 10 files were selected, it will keep only the first 10.
# 4. Move the selected files to the staging area.
```

**Cyclomatic Complexity:**

The cyclomatic complexity is moderate (4) due to `if 0 < max_files < len(all_selected_landing_files)` and `if len(selected_landing_files) == 0` conditions.

**Pain Points:**

*   **Dependency on `select_files`:** The function depends on the `select_files` function, whose implementation is not provided. It's crucial to understand how `select_files` works to fully understand the behavior of `_prepare_staging`.
*   **Error Handling:** Error handling is limited to checking for the case where no files are selected. It does not handle potential errors during file listing or moving.
*   **Tight Coupling to XCom:**  Relies heavily on XCom for parameter passing, making the function less modular and harder to test in isolation.
*   **Logging Volume:** The logging volume might be high depending on the number of files and the level of detail in the `select_files` function.

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

**Documentation:**

`_move_blobs(bucket_name, blob_names, destination_bucket_name, destination_prefix, **context)`

**Purpose:**

This function moves multiple blobs (files) from one Google Cloud Storage (GCS) bucket to another, using the `gsutil mv` command executed via a BashOperator in Airflow. It constructs a temporary file containing the list of blobs to move and then uses `gsutil` to move them in bulk.

**How it Works:**

1.  **Logging:** Logs the source and destination buckets/prefix.
2.  **Create Temporary File:**
    *   Generates a unique temporary file name in the `/tmp` directory.
    *   Opens the temporary file in append mode (`"a"`).
    *   Iterates through the list of `blob_names`.
    *   For each blob, it constructs the full GCS path (`gs://{bucket_name}/{blob_name}`) and writes it to the temporary file, followed by a newline.
3.  **Construct Bash Command:**
    *   Builds the `gsutil mv` command to move the blobs.
    *   `impersonation_opts`: Sets impersonation options using the `DATAFLOW_SERVICE_ACCOUNT` unless it's a test run.
    *   `gsutil_path`: Sets the path to the `gsutil` executable, depending on whether it's a test run or not.
    *   `gsutil_state_opts`: Creates state directory to avoid concurrency issues.
    *   The core of the command is: `cat {tmp_file} | {gsutil_path}gsutil ... -m mv -I 'gs://{destination_bucket_name}/{destination_prefix}/'`. This pipes the contents of the temporary file (the list of blobs) to `gsutil mv -I`, which reads the list of sources from stdin and moves them to the specified destination.
4.  **Execute Bash Command with BashOperator:**
    *   Creates a `BashOperator` to execute the `gsutil mv` command.
    *   `task_id`:  A unique task ID is generated using `uuid.uuid4()`.
    *   `bash_command`: The constructed `gsutil mv` command.
    *   Executes the `BashOperator` using `file_copy_using_gsutil.execute(context)`.
5.  **Clean Up:**
    *   Removes the temporary file using `os.remove(tmp_file)`.
6.  **Logging:** Logs that the blobs have been moved.

**Business Logic:**

This function provides an efficient way to move multiple files between GCS buckets. It leverages the `gsutil mv` command's ability to read a list of files from stdin, allowing for bulk file movement. This is more efficient than moving files one at a time. The use of a temporary file avoids command-line length limitations.

**Example:**

```python
# Example:
# bucket_name = "my-source-bucket"
# blob_names = ["data/file1.csv", "data/file2.csv"]
# destination_bucket_name = "my-destination-bucket"
# destination_prefix = "staging/"

# The function will:
# 1. Create a temporary file with the following contents:
#    gs://my-source-bucket/data/file1.csv
#    gs://my-source-bucket/data/file2.csv
# 2. Execute the following gsutil command:
#    cat /tmp/pnr_file_copy_1678886400000.txt | gsutil -m mv -I 'gs://my-destination-bucket/staging/'
# 3. Remove the temporary file.
```

**Cyclomatic Complexity:**

The cyclomatic complexity is low (2) due to the conditional `impersonation_opts` and `gsutil_path`.

**Pain Points:**

*   **Temporary File Management:**  Creating and deleting temporary files in `/tmp` can be problematic if the system has limited disk space or if the process doesn't have sufficient permissions to write to `/tmp`.  Consider using `tempfile.NamedTemporaryFile` for safer temporary file handling.
*   **Security:** Executing arbitrary bash commands through `BashOperator` can introduce security risks if the input parameters (especially `bucket_name`, `blob_names`, `destination_bucket_name`, `destination_prefix`) are not properly sanitized.
*   **Error Handling:** The function relies on the `BashOperator` to raise an exception if the `gsutil` command fails. More robust error handling could be added to check the return code of the `gsutil` command and log more detailed error messages. Consider catching exceptions during file creation/deletion.
*   **`gsutil` Dependency:** The function is tightly coupled to the `gsutil` command-line tool. If `gsutil` is not installed or configured correctly, the function will fail. Consider using the Google Cloud Storage client library directly for more robust and portable code.
*   **Testability:**  The use of `BashOperator` makes it harder to test the function in isolation. Consider mocking the `BashOperator` or using a different approach that doesn't rely on external commands.
*   **Performance:**  For very large numbers of files, creating a single temporary file with all the filenames might become a bottleneck. Consider splitting the list of files into smaller chunks and executing multiple `gsutil mv` commands in parallel.

```python
def _move_landing_to_staging(source_bucket: str, source_objects: list, destination_bucket: str, destination_path: str,
                             source_path: str, **context):
    logging.info(
        f"Moving [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]...")
    _move_blobs(source_bucket, source_objects, destination_bucket, destination_path, **context)
    logging.info(
        f"Moved [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]")
```

**Documentation:**

`_move_landing_to_staging(source_bucket, source_objects, destination_bucket, destination_path, source_path, **
## UML Diagram
![Image](images/anotherDAG_img1.png)
## DAG FLOW
![Image](images/anotherDAG_img2.png)

