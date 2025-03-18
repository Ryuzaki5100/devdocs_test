# Generated Documentation with UML
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

**Function: `_get_impersonated_credentials`**

**Purpose:** This function generates impersonated credentials for a specified service account.  It's a crucial security component, allowing the Airflow DAG to act as another service account, granting it the permissions associated with that account.

**Explanation:**

1.  **Import necessary libraries:** It imports `_default` from `google.auth` to get the default credentials and `impersonated_credentials` from `google.auth` to create impersonated credentials.
2.  **Get source credentials:** It uses `_default.default(scopes=target_scopes)` to obtain the default credentials.  These are the credentials that the Airflow environment itself is using (e.g., the Compute Engine service account or the user's credentials). The `target_scopes` argument specifies the OAuth scopes required for the target service account.
3.  **Create impersonated credentials:**  It then uses `impersonated_credentials.Credentials` to create the impersonated credentials.  The key parameters are:
    *   `source_credentials`: The default credentials obtained in the previous step.
    *   `target_principal`: The email address of the service account to impersonate.
    *   `target_scopes`:  The OAuth scopes the impersonated credentials should have.
    *   `lifetime`: The duration (in seconds) for which the impersonated credentials are valid.
4.  **Return credentials:** The function returns the generated impersonated credentials.

**Business Logic:**

Impersonation is used to grant the DAG's tasks the specific permissions they need, without granting excessive permissions to the Airflow environment itself. This follows the principle of least privilege. This function is used in almost all of the helper functions

**Example:**

```python
target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
target_service_account = 'dataflow-sa'
credentials = _get_impersonated_credentials(target_scopes, target_service_account)
# Now you can use 'credentials' to create clients for Google Cloud services.
```

```python
def _get_default_or_from_dag_run(default_value: str, dag_key, dag_run_conf):
    if dag_run_conf is not None and dag_key in dag_run_conf:
        return dag_run_conf[dag_key]
    return default_value
```

**Function: `_get_default_or_from_dag_run`**

**Purpose:**  This function retrieves configuration values, prioritizing values passed in the DAG run's configuration over default values.  This allows users to override default settings when triggering a DAG run.

**Explanation:**

1.  **Check for DAG run configuration:** It checks if `dag_run_conf` is not `None` and if the specified `dag_key` exists within the `dag_run_conf` dictionary.
2.  **Return DAG run value if available:** If both conditions are true, it returns the value associated with the `dag_key` from the `dag_run_conf`.
3.  **Return default value otherwise:** If either condition is false (i.e., no DAG run config or the key is missing), it returns the `default_value`.

**Business Logic:**

This function provides flexibility. Default values are set in the DAG code, but users can override them at runtime using the DAG run configuration. This is essential for things like reprocessing data for a specific date range or pointing to a different input bucket. This function enhances configurability of the DAG.

**Example:**

```python
default_bucket = 'my-default-bucket'
dag_key = 'gcs_bucket'
dag_run_config = {'gcs_bucket': 'my-override-bucket'}

bucket_name = _get_default_or_from_dag_run(default_bucket, dag_key, dag_run_config)
# bucket_name will be 'my-override-bucket'

dag_run_config = None
bucket_name = _get_default_or_from_dag_run(default_bucket, dag_key, dag_run_config)
# bucket_name will be 'my-default-bucket'
```

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

**Function: `_setup_processing`**

**Purpose:** This function is the initial setup task for the DAG. It retrieves configuration values, determines if the DAG is reprocessing data, generates a unique run ID, and pushes these values to XCom for use by downstream tasks.

**Explanation:**

1.  **Logging and Context:** The function starts by logging information about the DAG's execution, including the DAG ID, release, and execution datetime. It extracts information from the `context` dictionary, which is passed automatically by Airflow to each task. Key elements extracted are the execution date, `task_instance`, and `dag_run`.
2.  **Retrieve Configuration Values:** It uses `_get_default_or_from_dag_run` to retrieve various configuration values, including bucket names (landing, archive, staging), bucket paths, and the number of past hours to process.  It checks the `dag_run_conf` first for overridden values, then falls back to the default values defined in the DAG.
3.  **Determine Run ID and Reprocessing Flag:**
    *   If a `DAG_PARAM_RUN_ID` is provided in the `dag_run_conf`, it's considered a reprocessing run. The function extracts the provided run ID and sets `reprocessing_flag` to `True`.
    *   If no `DAG_PARAM_RUN_ID` is provided, the function generates a new run ID based on the execution datetime.  The `reprocessing_flag` is set to `False`.
4.  **Construct GCS Run Path and Job Name:** Based on the staging bucket path and run ID, the full GCS path for the run is constructed.  The Dataflow job name is also generated.
5.  **Push Values to XCom:** Finally, the function pushes all the retrieved and generated values to XCom.  XCom (cross-communication) is a mechanism in Airflow for passing data between tasks. The function uses `task_instance.xcom_push` to store the values under specific keys (e.g., `TASK_PARAM_LANDING_BUCKET_NAME`, `TASK_PARAM_RUN_PATH_FULL`).

**Business Logic:**

This function performs critical initialization steps. It dynamically determines the configuration based on user input (through DAG run configuration) and sets up the environment for subsequent tasks. The use of XCom ensures that the downstream tasks have access to the necessary information, such as bucket names, paths, and the run ID. This function essentially orchestrates the entire workflow setup

**Example:**

```python
# Inside an Airflow task
def my_task(**context):
  _setup_processing(**context)

# In a downstream task
def another_task(**context):
  ti = context['ti']
  landing_bucket = ti.xcom_pull(key='landing_bucket_name', task_ids='setup_task')
  # Now you can use landing_bucket
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

**Function: `_get_gcs_files`**

**Purpose:** This function lists files in a Google Cloud Storage (GCS) bucket under a given path, using Airflow's `GCSListObjectsOperator`.

**Explanation:**

1.  **Logging:** It logs a message indicating that it's listing files in the specified bucket and path.
2.  **Create GCSListObjectsOperator:** It instantiates a `GCSListObjectsOperator`. This operator is an Airflow component specifically designed to interact with GCS and list objects.
    *   `task_id`: A unique ID for the task.
    *   `bucket`: The GCS bucket name.
    *   `prefix`: The GCS path prefix.
    *   `match_glob`:  A wildcard pattern to match files. `**/*` matches any file or directory recursively. The `DELIMITER` variable likely defines a suffix used to identify "files" in this context (e.g., an empty file with `.SUCCESS` suffix is used to indicate a directory has been fully processed).
    *   `impersonation_chain`: If `TEST_RUN` is not "true", it uses the `DATAFLOW_SERVICE_ACCOUNT` for impersonation. This ensures that the listing operation is performed with the permissions of the Dataflow service account.
    *   `dag`:  The Airflow DAG object.
3.  **Execute the Operator:** It calls `gcs_list_objects.execute(context)` to trigger the GCS listing operation. The `execute` method returns a list of file names that match the specified criteria.
4.  **Logging:** Logs the number of files found.
5.  **Return the List of Files:** It returns the `files` list, which contains the names of the files found in GCS.

**Business Logic:**

This function allows the Airflow DAG to dynamically discover the files that need to be processed. By using a `GCSListObjectsOperator`, Airflow handles the GCS interaction and provides a clean interface for getting the list of files. The impersonation configuration ensures the task has appropriate permissions.

**Example:**

```python
#Inside an Airflow Task
def my_task(**context):
  bucket_name = 'my-gcs-bucket'
  gcs_path = 'landing/data/'
  files = _get_gcs_files(bucket_name, gcs_path, **context)
  # Now 'files' contains a list of file names found in that location.
```

```python
def select_files(landing_files, prefix, num_past_hours):
    filtered_files = []
    now_utc = datetime.utcnow()
    for file in landing_files:
        try:
            file_modified_str = file.split(prefix)[1].split("/")[0]
            file_modified_dt = datetime.strptime(file_modified_str, '%Y%m%d%H%M%S')
            diff = now_utc - file_modified_dt
            diff_in_hours = diff.total_seconds() / 3600
            if diff_in_hours <= num_past_hours:
                filtered_files.append(file)
        except Exception as e:
            logging.info("FILENAME_ERR: skipping file {} due to error {}".format(file,str(e)))
            pass
    return filtered_files
```

**Function: `select_files`**

**Purpose:** This function filters a list of GCS file paths, selecting only those files whose modification timestamp falls within a specified time window (number of past hours).

**Explanation:**

1.  **Initialization:**
    *   `filtered_files = []`: Initializes an empty list to store the selected files.
    *   `now_utc = datetime.utcnow()`: Gets the current UTC datetime. This will be used to compare against the files' modification times.
2.  **Iterate Through Files:** Loops through each `file` in the `landing_files` list.
3.  **Extract File Modification Timestamp:**
    *   `file_modified_str = file.split(prefix)[1].split("/")[0]`: This extracts the timestamp string from the file path. It assumes the file path follows a specific structure where the timestamp is located after the `prefix` and before the first `/` after the prefix. This is a fragile assumption and a key point of failure if the naming convention changes.
    *   `file_modified_dt = datetime.strptime(file_modified_str, '%Y%m%d%H%M%S')`: Parses the extracted timestamp string into a `datetime` object, using the format `'%Y%m%d%H%M%S'`.
4.  **Calculate Time Difference:**
    *   `diff = now_utc - file_modified_dt`: Calculates the time difference between the current time and the file's modification time.
    *   `diff_in_hours = diff.total_seconds() / 3600`: Converts the time difference to hours.
5.  **Filter Files:**
    *   `if diff_in_hours <= num_past_hours:`: Checks if the time difference in hours is less than or equal to the specified `num_past_hours`. If it is, the file is considered within the time window.
    *   `filtered_files.append(file)`: If the file is within the time window, it's added to the `filtered_files` list.
6.  **Error Handling:**
    *   The `try...except` block handles potential errors during timestamp extraction or parsing. If an error occurs, the function logs the error and continues to the next file. This prevents the entire process from crashing if a malformed filename is encountered.  However, it also means that invalid filenames are silently skipped.
7.  **Return Filtered Files:**
    *   `return filtered_files`: Returns the list of files that fall within the specified time window.

**Business Logic:**

This function implements a time-based filtering mechanism. It's used to select files that have been created or modified within a certain period. This is useful for processing data in batches, where you only want to process files that have arrived since the last processing run. This function also extracts the date time from the file, so the function has tight coupling to the filename, which makes it fragile.

**Example:**

```python
landing_files = [
    "landing/data/20231026100000/file1.txt",
    "landing/data/20231026120000/file2.txt",
    "landing/data/20231025100000/file3.txt"
]
prefix = "landing/data/"
num_past_hours = 24
selected_files = select_files(landing_files, prefix, num_past_hours)
# selected_files will contain file1.txt and file2.txt
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

**Function: `_get_storage_client`**

**Purpose:** This function creates and returns a Google Cloud Storage (GCS) client. The client is configured to use either default credentials (for testing) or impersonated credentials for a specified service account.

**Explanation:**

1.  **Import the `storage` library:** It imports the `storage` module from the `google.cloud` library.
2.  **Define the required scopes:** It defines the `target_scopes` list, which specifies the OAuth scopes required for accessing GCS.
3.  **Determine the credentials to use:**
    *   It checks the value of the `TEST_RUN` variable. If `TEST_RUN` is "true", it sets `credentials` to `None`. This is likely used for local testing where you might not want to use impersonation.
    *   If `TEST_RUN` is not "true", it calls the `_get_impersonated_credentials` function to get impersonated credentials for the specified `target_service_account` and `target_scopes`. This ensures that the GCS client operates with the permissions of the impersonated service account.
4.  **Create and return the GCS client:** It creates a `storage.Client` object, passing in the `project` and `credentials`. This client object is then used to interact with GCS.

**Business Logic:**

This function provides a centralized way to obtain a GCS client with the correct credentials. It handles the logic of choosing between default and impersonated credentials based on the `TEST_RUN` flag. This simplifies the code in other functions that need to interact with GCS, as they can simply call this function to get a properly configured client. The use of impersonated credentials promotes the principle of least privilege.

**Example:**

```python
#Get a storage client
storage_client = _get_storage_client(DATAFLOW_SERVICE_ACCOUNT, PIPELINE_PROJECT_ID)

#Now you can use storage_client to interact with GCS:
bucket = storage_client.get_bucket('your-bucket-name')
blob = bucket.blob('your-file.txt')
blob.download_to_filename('/tmp/your-file.txt')
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

**Function: `_move_blobs`**

**Purpose:** This function moves multiple blobs (files) from one GCS bucket to another. It uses the `gsutil` command-line tool, invoked through Airflow's `BashOperator`, for efficient bulk moving.

**Explanation:**

1.  **Logging:** Logs a message indicating the source and destination buckets and prefix.
2.  **Create Temporary File:** Generates a temporary file path (`tmp_file`) and opens it in append mode ("a"). This file will store a list of the GCS URIs of the blobs to be moved. The filename uses a timestamp to ensure uniqueness.
3.  **Write Blob URIs to File:** Loops through the `blob_names` list and writes the GCS URI of each blob (e.g., `gs://bucket-name/blob-name`) to the temporary file, one URI per line.
4.  **Construct `gsutil` Command:** Constructs the `gsutil` command that will perform the move operation.  The command includes:
    *   `cat {tmp_file}`: Reads the list of blob URIs from the temporary file.
    *   `{gsutil_path}gsutil`: Specifies the path to the `gsutil` executable. The path is conditionally set based on the `TEST_RUN` flag.
    *   `{gsutil_state_opts}`: configures gsutil state directory to avoid any concurrency issues
    *   `{impersonation_opts}`: Adds impersonation options if `TEST_RUN` is not "true". This uses the `DATAFLOW_SERVICE_ACCOUNT` to execute `gsutil` with the correct permissions.
    *   `-m mv`: Specifies the move operation.
    *   `-I`: Tells `gsutil` to read the list of source URIs from standard input (which is being piped from `cat`).
    *   `'gs://{destination_bucket_name}/{destination_prefix}/'`: Specifies the destination bucket and prefix. The trailing `/` is important; it tells `gsutil` to treat the prefix as a directory.
5.  **Execute `gsutil` Command using `BashOperator`:**
    *   Creates a `BashOperator` to execute the constructed `bash_cmd`. The `task_id` is dynamically generated to ensure uniqueness.
    *   Executes the `BashOperator` using `file_copy_using_gsutil.execute(context)`.
6.  **Clean Up:** Deletes the temporary file using `os.remove(tmp_file)`.
7.  **Logging:** Logs a message indicating that the blobs have been moved.

**Business Logic:**

This function provides an efficient way to move large numbers of files within GCS. Instead of using the GCS client library to move files one by one, it leverages the `gsutil` command-line tool, which is optimized for bulk operations. By writing the list of files to a temporary file and then piping that file to `gsutil`, it avoids potential issues with command-line argument length limits. The impersonation options ensure the `gsutil` command runs with appropriate permissions.

**Example:**

```python
#Inside an Airflow task
def my_task(**context):
  source_bucket = "my-source-bucket"
  destination_bucket = "my-destination-bucket"
  destination_prefix = "archive/data/"
  blob_names = ["file1.txt", "file2.txt", "file3.txt"]
  _move_blobs(source_bucket, blob_names, destination_bucket, destination_prefix, **context)
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

**Function: `_move_landing_to_staging`**

**Purpose:** This function moves files from a landing GCS bucket and path to a staging GCS bucket and path. It acts as a wrapper around the `_move_blobs` function, providing a higher-level abstraction for moving landing data to staging.

**Explanation:**

1.  **Logging:** Logs a message indicating the number of files being moved and the source and destination locations.
2.  **Call `_move_blobs`:** Calls the `_move_blobs` function to perform the actual file movement. It passes the source bucket, the list of object names (filenames), the destination bucket, the destination path (prefix), and the Airflow context.
3.  **Logging:** Logs a message confirming that the files have been moved.

**Business Logic:**

This function encapsulates the logic of moving files from a landing zone to a staging area. This is a common pattern in data pipelines, where raw data is first ingested into a landing zone and then moved to a staging area for further processing. By using a dedicated function for this operation, the DAG code becomes more modular and readable.

**Example:**

```python
# Inside an Airflow task
def my_task(**context):
  landing_bucket = "my-landing-bucket"
  landing_path = "raw/data/"
  staging_bucket = "my-staging-bucket"
  staging_path = "staging/data/"
  source_objects = ["file1.txt", "file2.txt"] #List of files obtained by the _get_gcs_files()
  _move_landing_to_staging(landing_bucket, source_objects, staging_bucket, staging_path, landing_path, **context)
```

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

**Function: `_prepare_staging`**

**Purpose:** This function prepares the staging environment by retrieving configuration parameters from XCom, listing files in the landing bucket, selecting files based on a time window and a maximum file count, and moving the selected files to the staging bucket.

**Explanation:**

1.  **Retrieve Configuration from XCom:**
    *   `ti = context['ti']`: Gets the `TaskInstance` object from the Airflow context.
    *   Uses `ti.xcom_pull
## UML Diagram
![Image](images/anotherDAG_after_img1.png)
## DAG FLOW
![Image](images/anotherDAG_after_img2.png)

