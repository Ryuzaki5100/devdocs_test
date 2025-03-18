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

### Documentation for `_get_impersonated_credentials`

**Purpose:** This function generates Google Cloud credentials that impersonate a specified service account. This is useful for granting specific permissions to your application without directly using the service account's key, enhancing security.

**Dependencies:**  This function relies on several Google Cloud libraries and internal modules like `google.auth`, `google.auth._default`, and `google.auth.impersonated_credentials`. It implicitly depends on logging functionality.

**Functionality:**

1.  **Obtain Source Credentials:** It first retrieves the default Google Cloud credentials using `google.auth._default.default(scopes=target_scopes)`. These are the credentials the application is currently running under (e.g., the Compute Engine service account, user account via `gcloud auth`). The `scopes` argument specifies the necessary permissions for the source credentials to impersonate the target service account. `project_id` is also returned, which is associated with the default credentials.
    ```python
    from google.auth import _default
    source_credentials, project_id = _default.default(scopes=target_scopes)
    logging.info(f"Source credentials generated for project [{project_id}]")
    ```

2.  **Create Impersonated Credentials:** It then constructs `impersonated_credentials.Credentials` using the source credentials, the target service account, and the desired scopes. The `target_principal` is the email address of the service account to impersonate.  `lifetime` specifies how long the impersonated credentials are valid for (in seconds).
    ```python
    from google.auth import impersonated_credentials
    target_credentials = impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=target_service_account,
        target_scopes=target_scopes,
        lifetime=60 * 60)
    return target_credentials
    ```

**Business Logic:**

The business logic revolves around securely accessing Google Cloud resources. Impersonation allows a service (like the Airflow worker) to assume the identity of another service account with more granular permissions. This is a best practice for limiting the blast radius in case of security breaches. Instead of giving a wide range of permissions to the Airflow worker, it only needs permission to impersonate specific service accounts used by different parts of the pipeline.

**Example:**

```python
target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
target_service_account = 'my-service-account@my-project.iam.gserviceaccount.com'
credentials = _get_impersonated_credentials(target_scopes, target_service_account)

# Now you can use these credentials to access Google Cloud resources
# e.g., Construct a BigQuery client with the impersonated credentials
from google.cloud import bigquery
client = bigquery.Client(credentials=credentials, project='my-project')
```

**Cyclomatic Complexity:** Low. The function's control flow is straightforward.

**Pain Points:** Error handling is implicit through the underlying libraries. The function could benefit from explicit error handling (try-except blocks) to catch potential issues during credential retrieval or impersonation. Also, the lifetime is hardcoded to 1 hour, which can be improved by making it a configurable parameter.

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

### Documentation for `getImpersonatedCredentials`

**Purpose:** This function, similar to `_get_impersonated_credentials`, retrieves Google Cloud credentials that impersonate a given service account. However, this function constructs the target service account principal in a specific format.

**Dependencies:**  Same as `_get_impersonated_credentials`:  `google.auth`, `google.auth._default`, `google.auth.impersonated_credentials`, and implicit logging.

**Functionality:**

1.  **Obtain Source Credentials:** It retrieves the default Google Cloud credentials, analogous to `_get_impersonated_credentials`.
    ```python
    from google.auth import _default
    source_credentials, project_id = _default.default(scopes=target_scopes)
    ```

2.  **Construct Target Principal and Create Impersonated Credentials:** The crucial difference is how the `target_principal` is built.  It's constructed as `{target_service_account}@{target_project}.iam.gserviceaccount.com`. It then creates `impersonated_credentials.Credentials` using these source credentials and the formatted target principal. The `lifetime` here is set to 600 seconds (10 minutes).
    ```python
    from google.auth import impersonated_credentials
    target_credentials = impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=f'{target_service_account}@{target_project}.iam.gserviceaccount.com',
        target_scopes=target_scopes,
        lifetime=600)
    return target_credentials
    ```

**Business Logic:**

This function's logic is the same as `_get_impersonated_credentials` - securely accessing Google Cloud resources via service account impersonation.  However, by requiring `target_service_account` and `target_project` as separate arguments, it enforces a specific format for the service account principal. This format is the standard email-like naming convention for Google Cloud service accounts.

**Example:**

```python
target_scopes = ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/bigquery']
target_service_account = 'my-service-account'
target_project = 'my-project'
credentials = getImpersonatedCredentials(target_scopes, target_service_account, target_project)

# Use these credentials to construct a BigQuery client.
from google.cloud import bigquery
client = bigquery.Client(credentials=credentials, project=target_project)
```

**Cyclomatic Complexity:** Low, similar to `_get_impersonated_credentials`.

**Pain Points:**  The tight coupling to the service account principal naming convention is a potential pain point. If the naming convention changes in the future, this function will break. Hardcoding the lifetime to 600 seconds is also inflexible. Error handling could be improved.

```python
def get_metric_service_client(target_service_account: str):
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    return monitoring_v3.MetricServiceClient()
```

### Documentation for `get_metric_service_client`

**Purpose:**  This function creates and returns a Google Cloud Monitoring MetricServiceClient.

**Dependencies:** Requires the `google.cloud.monitoring_v3` library. It also seems to require `target_service_account` which is unused in the function itself but might be used in other functions.

**Functionality:**

1.  **Define Scopes:** It defines a list of scopes, specifically `https://www.googleapis.com/auth/cloud-platform`, which grants access to manage Google Cloud Platform resources.
    ```python
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    ```

2.  **Create MetricServiceClient:** It instantiates and returns a `monitoring_v3.MetricServiceClient`.
    ```python
    return monitoring_v3.MetricServiceClient()
    ```

**Business Logic:**

This function's primary business logic is to provide a client that can interact with the Google Cloud Monitoring API.  This API is used for creating, reading, and updating metrics related to your cloud resources. The seemingly unused `target_service_account` argument hints that the original intention might have been to use impersonated credentials, but it's currently not implemented.

**Example:**

```python
client = get_metric_service_client("unused_service_account@example.com")  # Service account is not used!

# Now you can use the client to interact with the Cloud Monitoring API
from google.cloud import monitoring_v3
project_name = f"projects/{project_id}"  # Assuming project_id is defined elsewhere
series = monitoring_v3.TimeSeries()
# ... (Set up the TimeSeries object) ...
client.create_time_series(name=project_name, time_series=[series])
```

**Cyclomatic Complexity:** Very low. It's a simple function with no branching.

**Pain Points:**

*   The `target_service_account` argument is misleading because it's not used. This should be removed or used for credential creation.
*   The function currently uses the default credentials. For production use with different service accounts, the code needs to be modified to use the `target_service_account` and either default Application Default Credentials or impersonated credentials.
*   There is no error handling.

```python
def _is_reprocessing(**context):
    reprocess_flag = context['ti'].xcom_pull(key=TASK_PARAM_REPROCESSING, task_ids=TASK_SETUP_PROCESSING)
    logging.info(f"Is reprocessing required [{reprocess_flag}]")
    return TASK_PREPARE_STAGING if not reprocess_flag else TASK_SKIP_PREPARE_STAGING
```

### Documentation for `_is_reprocessing`

**Purpose:** This function determines whether the Airflow DAG (Directed Acyclic Graph) is running in reprocessing mode. It checks an XCom variable to make this decision.

**Dependencies:**  Requires Airflow's context object and uses XCom (cross-communication) functionality. It also depends on `TASK_PARAM_REPROCESSING`, `TASK_SETUP_PROCESSING`, `TASK_PREPARE_STAGING`, and `TASK_SKIP_PREPARE_STAGING` which are assumed to be pre-defined constants. Implict dependency on logging.

**Functionality:**

1.  **Retrieve Reprocessing Flag from XCom:** It retrieves the value of the XCom variable with the key `TASK_PARAM_REPROCESSING` from the task instance (`ti`) associated with the task ID `TASK_SETUP_PROCESSING`.  XComs are a mechanism for tasks in an Airflow DAG to exchange information.
    ```python
    reprocess_flag = context['ti'].xcom_pull(key=TASK_PARAM_REPROCESSING, task_ids=TASK_SETUP_PROCESSING)
    logging.info(f"Is reprocessing required [{reprocess_flag}]")
    ```

2.  **Determine Next Task Based on Flag:** It then checks the value of `reprocess_flag`. If `reprocess_flag` is false (meaning reprocessing is *not* required), it returns `TASK_PREPARE_STAGING`. Otherwise (if reprocessing *is* required), it returns `TASK_SKIP_PREPARE_STAGING`.
    ```python
    return TASK_PREPARE_STAGING if not reprocess_flag else TASK_SKIP_PREPARE_STAGING
    ```

**Business Logic:**

This function implements conditional execution within an Airflow DAG.  The `reprocess_flag` indicates whether the DAG should reprocess existing data or skip the preparation step.  This is a common pattern for handling data updates or correcting errors in a previous run.

**Example:**

Assume `TASK_SETUP_PROCESSING` pushes an XCom with `TASK_PARAM_REPROCESSING` set to `True` if a user triggers a backfill of data.

```python
# Inside TASK_SETUP_PROCESSING:
task_instance.xcom_push(key=TASK_PARAM_REPROCESSING, value=True)

# Then, in a subsequent task using _is_reprocessing as a branching point:
branch_task = BranchPythonOperator(
    task_id='is_reprocessing_branch',
    python_callable=_is_reprocessing,
    dag=dag,
)

prepare_staging_task = DummyOperator(task_id=TASK_PREPARE_STAGING, dag=dag)
skip_prepare_staging_task = DummyOperator(task_id=TASK_SKIP_PREPARE_STAGING, dag=dag)

branch_task >> [prepare_staging_task, skip_prepare_staging_task]
```

If `reprocess_flag` is `True`, the DAG will branch to `skip_prepare_staging_task`. Otherwise, it will branch to `prepare_staging_task`.

**Cyclomatic Complexity:** Low (2) due to the single conditional statement.

**Pain Points:**

*   The reliance on XComs can make DAGs harder to debug and understand if the flow of XCom values isn't well-documented.
*   The function assumes the existence and correct value of the XCom variable.  It would be more robust to include error handling if the XCom variable is missing or has an unexpected value.  For instance, it should define a default value if `xcom_pull` returns None.
*   The meaning of `TASK_PREPARE_STAGING` and `TASK_SKIP_PREPARE_STAGING` is opaque without external context.  Consider using more descriptive names or adding comments.

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

### Documentation for `_get_gcs_files`

**Purpose:** This function lists files in a Google Cloud Storage (GCS) bucket under a specified path. It utilizes Airflow's `GCSListObjectsOperator` to achieve this.

**Dependencies:**  Relies heavily on Airflow, specifically the `GCSListObjectsOperator` from the `airflow.providers.google.cloud.operators.gcs` package. It also uses `uuid` for generating unique task IDs and implicit logging. It depends on global variables like `TEST_RUN`, `DATAFLOW_SERVICE_ACCOUNT`, `DELIMITER`, and `dag`.

**Functionality:**

1.  **Log Information:** It logs the bucket name and path being searched.
    ```python
    logging.info(
        f"Listing files in [{bucket_name}/{gcs_path}]...")
    ```

2.  **Create GCSListObjectsOperator:**  It instantiates a `GCSListObjectsOperator`. This operator handles the interaction with GCS to list objects.
    *   `task_id`: A unique task ID is generated using `uuid.uuid4()` to avoid naming conflicts.
    *   `bucket`:  The GCS bucket to list files from.
    *   `prefix`: The path within the bucket to list files from.
    *   `match_glob`:  A glob pattern to filter the files. Here, it matches any file that ends with the `DELIMITER`.
    *   `impersonation_chain`:  If `TEST_RUN` is "true", impersonation is disabled; otherwise, it uses the `DATAFLOW_SERVICE_ACCOUNT` for impersonation.
    *   `dag`: The Airflow DAG the operator belongs to.
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

3.  **Execute Operator and Return Files:** It executes the `GCSListObjectsOperator` using `gcs_list_objects.execute(context)`. This triggers the actual listing of files in GCS. The returned `files` variable is a list of the names of the files found.
    ```python
    files = gcs_list_objects.execute(context)
    logging.info(
        f"Found [{len(files)}] files in [{bucket_name}/{gcs_path}]")
    return files
    ```

**Business Logic:**

This function encapsulates the logic for retrieving a list of files from a GCS bucket. The `match_glob` parameter allows filtering files based on a pattern, which is crucial for selecting the right files for processing. The impersonation logic ensures the operation is performed with the correct service account credentials. The use of the `GCSListObjectsOperator` makes this an Airflow-aware function, designed to be integrated into an Airflow DAG.

**Example:**

```python
# Assuming bucket_name and gcs_path are defined
files = _get_gcs_files(bucket_name='my-bucket', gcs_path='my/path/', context=context)

if files:
    print(f"Found files: {files}")
else:
    print("No files found.")
```

**Cyclomatic Complexity:** Moderate. The conditional logic related to `TEST_RUN` adds a small amount of complexity. The main complexity lies within the `GCSListObjectsOperator` itself.

**Pain Points:**

*   The reliance on global variables like `TEST_RUN`, `DATAFLOW_SERVICE_ACCOUNT`, `DELIMITER`, and `dag` makes the function less portable and harder to test in isolation. These should ideally be passed as arguments or retrieved from a configuration object.
*   The `task_id` generation using `uuid.uuid4()` might be unnecessary if task IDs are already managed at a higher level within the Airflow DAG. It adds complexity without much benefit.
*   The `match_glob` is hardcoded to end with `DELIMITER`, limiting the function's flexibility. It should be a parameter.
*   There is no error handling. If the GCSListObjectsOperator fails, the exception will propagate, but there is no specific handling within this function.

```python
def get_bq_impersonated_client(target_service_account: str, target_project: str):
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform',
                     'https://www.googleapis.com/auth/bigquery']
    return bigquery.Client(project=target_project, credentials=getImpersonatedCredentials(target_scopes, target_service_account, target_project))
```

### Documentation for `get_bq_impersonated_client`

**Purpose:**  This function creates a BigQuery client that uses impersonated credentials.

**Dependencies:** Depends on `google.cloud.bigquery` and `getImpersonatedCredentials`.

**Functionality:**

1.  **Define Scopes:** Defines the necessary scopes for BigQuery access: `https://www.googleapis.com/auth/cloud-platform` and `https://www.googleapis.com/auth/bigquery`.
    ```python
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform',
                     'https://www.googleapis.com/auth/bigquery']
    ```

2.  **Get Impersonated Credentials:** Calls `getImpersonatedCredentials` with the defined scopes, target service account, and target project to retrieve impersonated credentials.
    ```python
    credentials = getImpersonatedCredentials(target_scopes, target_service_account, target_project)
    ```

3.  **Create BigQuery Client:** Instantiates a `bigquery.Client` using the obtained impersonated credentials and the target project.
    ```python
    return bigquery.Client(project=target_project, credentials=credentials)
    ```

**Business Logic:**

This function allows secure access to BigQuery resources using service account impersonation. By using impersonation, the application doesn't need to store or manage service account keys directly. Instead, it leverages existing credentials (e.g., the Compute Engine service account) to assume the identity of another service account with BigQuery access permissions.

**Example:**

```python
target_service_account = "my-dataflow-sa"
target_project = "my-project"
bq_client = get_bq_impersonated_client(target_service_account, target_project)

# Now you can use bq_client to interact with BigQuery
query = "SELECT * FROM `my-project.my_dataset.my_table` LIMIT 10"
query_job = bq_client.query(query)
results = query_job.result()
for row in results:
    print(row)
```

**Cyclomatic Complexity:** Low. The function's control flow is simple and linear.

**Pain Points:**

*   The function relies on `getImpersonatedCredentials`, inheriting any potential issues or limitations from that function (e.g., hardcoded lifetime).
*   Error handling is minimal. It should include try-except blocks to handle potential exceptions during credential retrieval or BigQuery client creation.

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

### Documentation for `create_custom_metrics`

**Purpose:** This function creates and inserts a custom metric into Google Cloud Monitoring.

**Dependencies:** Relies on `get_metric_service_client`, `google.cloud.monitoring_v3`, and the `time` module. It also depends on global variables like `COMPOSER_SERVICE_ACCOUNT`, `CUSTOM_METRIC_DOMAIN`, and `DAGID`.

**Functionality:**

1.  **Get Metric Service Client:** Retrieves a MetricServiceClient using `get_metric_service_client`.
    ```python
    client = get_metric_service_client(COMPOSER_SERVICE_ACCOUNT)
    ```

2.  **Construct TimeSeries Object:** Creates a `monitoring_v3.TimeSeries` object, which represents the metric data to be written.
    *   `series.metric.type`:  Sets the metric type by combining `CUSTOM_METRIC_DOMAIN` and the provided `metric_type`.
    *   `series.metric.labels`:  Adds labels to the metric for identification and filtering.
    *   `series.resource.type`: Sets the resource type the metric is associated with.
    *   `series.resource.labels`: Adds labels to the resource, including project ID, workflow name, and location.
    *   `interval`:  Creates a `monitoring_v3.TimeInterval` representing the time range for the metric.
    *   `point`: Creates a `monitoring_v3.Point` representing the actual metric value. The value type is determined by the `value_type` parameter (e.g., "int64_value", "double_value").
    ```python
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
    ```

3.  **Create Time Series:** Calls `client.create_time_series` to insert the metric data into Cloud Monitoring.
    ```python
    client.create_time_series(name=project_name, time_series=[series])
    ```

4.  **Error Handling:** Includes a try-except block to catch potential exceptions during metric creation and logs any errors.
    ```python
    except Exception as ex:
        logging.error("Error [{}] occurred while inserting/creating custom metric".format(str(ex)))
    ```

**Business Logic:**

This function is crucial for monitoring the performance and health of the data pipeline. By creating custom metrics, you can track key indicators such as the number of processed files, processing time, error rates, and other relevant metrics. This data can then be used to identify bottlenecks, optimize performance, and ensure the pipeline is running smoothly.

**Example:**

```python
metric_type = "pnr_processed_file_count"
project_id = "my-project"
resource_type = "cloud_composer_workflow"
value_type = "int64_value"
val = 123

create_custom_metrics(metric_type, project_id, resource_type, value_type, val)
```

**Cyclomatic Complexity:** Moderate. The try-except block and the construction of the TimeSeries object add to the complexity.

**Pain Points:**

*   The reliance on global variables (`COMPOSER_SERVICE_ACCOUNT`, `CUSTOM_METRIC_DOMAIN`, `DAGID`) reduces the function's reusability and testability.
*   The location ("us-central1") is hardcoded. This should be configurable.
*   The function assumes the metric type already exists. It would be better if it could create the metric definition if it doesn't exist.
*   The time interval is only capturing the end time. Consider adding the start time as well.
*   The error handling only logs the error. It might be helpful to re-raise the exception or take other actions, depending on the specific needs.

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

### Documentation for `_move_blobs`

**Purpose:** This function moves multiple blobs (files) from one GCS bucket to another using the `gsutil mv` command. It uses an Airflow `BashOperator` to execute the `gsutil` command.

**Dependencies:**  Relies on Airflow's `BashOperator`, the `os` and `time` modules, and `uuid` for generating unique task IDs.  It also has implicit dependencies on global variables like `TEST_RUN`, `DATAFLOW_SERVICE_ACCOUNT`, and `SUFFIX`.

**Functionality:**

1.  **Log Information:** Logs the source and destination buckets and path.
    ```python
    logging.info(f"Moving blobs from [{bucket_name}] to [{destination_bucket_name}/{destination_prefix}]")
    ```

2.  **Create Temporary File:** Creates a temporary file to store the list of blobs to move.
    ```python
    num_blobs = len(blob_names)
    time_millis = round(time.time() * 1000)
    tmp_file = f"/tmp/pnr{SUFFIX}_file_copy_{time_millis}.txt"
    with open(tmp_file, "a") as f:
        for i, blob_name in enumerate(blob_names):
            logging.info(
                f"[{i + 1}/{num_blobs}] Adding blob [{bucket_name}/{blob_name}]...")
            f.writelines(f"gs://{bucket_name}/{blob_name}\n")
    ```

3.  **Construct `gsutil` Command:** Builds the `gsutil mv` command to move the blobs.
    *   It adds impersonation options based on the `TEST_RUN` flag and `DATAFLOW_SERVICE_ACCOUNT`.
    *   It includes options to set the `gsutil` state directory.
    *   The command reads the list of blobs from the temporary file and moves them to the destination bucket and path.
    ```python
    impersonation_opts = "" if TEST_RUN == "true" else f"-i {DATAFLOW_SERVICE_ACCOUNT}"
    gsutil_path = "/google-cloud-sdk/bin/" if TEST_RUN == "true" else ""
    gsutil_state_opts = f"-o 'GSUtil:state_dir=/tmp/pnr{SUFFIX}_gsutil_state_{time_millis}'"
    bash_cmd = f"cat {tmp_file} | {gsutil_path}gsutil {gsutil_state_opts} {impersonation_opts} -m mv -I 'gs://{destination_bucket_name}/{destination_prefix}/'"
    logging.info(f"Executing Bash command [{bash_cmd}]")
    ```

4.  **Execute `gsutil` Command using `BashOperator`:** Creates a `BashOperator` to execute the constructed `gsutil` command. It then executes the operator.
    ```python
    file_copy_using_gsutil = BashOperator(
        task_id="file_copy_using_gsutil" + str(uuid.uuid4()),
        bash_command=bash_cmd
    )
    file_copy_using_gsutil.execute(context)
    ```

5.  **Remove Temporary File:** Deletes the temporary file after the move operation is complete.
    ```python
    os.remove(tmp_file)

    logging.info(f"Moved blobs from file [{tmp_file}] to [{destination_bucket_name}/{destination_prefix}]")
    ```

**Business Logic:**

This function provides a way to move a large number of files between GCS buckets efficiently using `gsutil`. It leverages the `-m` flag for parallel operations, improving performance. The impersonation logic ensures the move operation is performed with the correct service account credentials.

**Example:**

```python
source_bucket = "my-source-bucket"
destination_bucket = "my-destination-bucket"
destination_path = "archive/2024/01/01/"
blob_names = ["file1.txt", "file2.txt", "file3.txt"]

_move_blobs(source_bucket, blob_names, destination_bucket, destination_path, context=context)
```

**Cyclomatic Complexity:** Moderate. The conditional logic related to `TEST_RUN` adds some complexity.

**Pain Points:**

*   The reliance on global variables (`TEST_RUN`, `DATAFLOW_SERVICE_ACCOUNT`, `SUFFIX`) makes the function less portable and harder to test.
*   Using a temporary file to pass the list of blobs to `gsutil` can be inefficient for a very large number of files. Consider using `gsutil -m mv gs://bucket/{file1,file2,file3} dest`.
*   There is no error handling for the `BashOperator`. If the `gsutil` command fails, the exception will propagate, but there is no specific handling within this function.
*   The function assumes `gsutil` is installed and available on the system. It should include a check to verify this.
*   Generating a unique task ID with UUID might be redundant if Airflow already manages task IDs.

```python
def _move_to_archive(**context):
    ti = context['ti']
    gcs_archive_bucket_name = ti.xcom_pull(key=TASK_PARAM_ARCHIVE_BUCKET_NAME, task_ids=TASK_SETUP_PROCESSING)
    gcs_archive_bucket_path = ti.xcom_pull(key=TASK_PARAM_ARCHIVE_BUCKET_PATH, task_ids
## UML Diagram
![Image](images/anotherDAG_img1.png)
## DAG FLOW
![Image](images/anotherDAG_img2.png)

