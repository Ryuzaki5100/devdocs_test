# Generated Documentation with UML
```python
"""
Documentation for Dataflow Pipeline Orchestration
"""

# 1. _get_default_or_from_dag_run(default_value, dag_key, dag_run_conf)
# Dependencies: None (basic conditional logic)

def _get_default_or_from_dag_run(default_value: str, dag_key, dag_run_conf):
    if dag_run_conf is not None and dag_key in dag_run_conf:
        return dag_run_conf[dag_key]
    return default_value

"""
Description:
This function retrieves a configuration value.  It first checks if a value is provided
in the Airflow DAG run's configuration (dag_run_conf). If not, it returns a predefined
default value. This allows users to override default settings at runtime, providing
flexibility in how the pipeline is executed.

Parameters:
- default_value (str): The default value to return if the dag_key is not found in the
  dag_run_conf.
- dag_key: The key to look for in the dag_run_conf dictionary.
- dag_run_conf: A dictionary representing the DAG run's configuration.  This is often
  passed from the Airflow UI when triggering a DAG run manually.

Returns:
The value associated with the dag_key in dag_run_conf, or the default_value if the
dag_key is not found.

Business Logic:
This function implements a simple fallback mechanism. It prioritizes user-provided
configuration from the DAG run configuration over hardcoded default values.  This is a
common pattern for making pipelines configurable and reusable.

Example:
Suppose you have a DAG parameter 'bucket_name' with a default value of 'my-default-bucket'.
If a user triggers the DAG and provides {'bucket_name': 'my-custom-bucket'} in the
configuration, this function will return 'my-custom-bucket'. Otherwise, it will return
'my-default-bucket'.

Cyclomatic Complexity: Low (single if-else).

Pain Points:
- The function assumes dag_run_conf is a dictionary. It doesn't handle cases where
  dag_run_conf might be None or not a dictionary.  Adding a type check could improve
  robustness.
"""

# 2. _get_df_service()
# Dependencies: googleapiclient.discovery.build, logging

def _get_df_service():
    from googleapiclient.discovery import build
    df_service = build("dataflow", "v1b3", cache_discovery=False)
    logging.info("df service [{}]".format(df_service))
    return df_service

"""
Description:
This function creates and returns a Google Dataflow service client.  It uses the
googleapiclient.discovery.build function to construct the client, specifying the Dataflow
API version ("v1b3") and disabling API discovery caching.

Parameters:
None

Returns:
A Dataflow service client object.

Business Logic:
This function encapsulates the creation of the Dataflow API client, centralizing the
service initialization.  Disabling API discovery caching is useful in environments
where the API definition might change frequently.

Example:
df_service = _get_df_service()
response = df_service.projects().locations().jobs().list(projectId="my-project",
location="us-central1").execute()

Cyclomatic Complexity: Low (straightforward function call).

Pain Points:
- The function hardcodes the Dataflow API version ("v1b3").  It would be better to
  define this version as a constant or configuration variable, allowing for easier
  upgrades to newer API versions.
- The function doesn't handle potential exceptions during service building (e.g., if the
  Google API client library is not properly installed or configured).  Adding a try-except
  block would improve robustness.
"""

# 3. getImpersonatedCredentials(target_scopes, target_service_account, target_project)
# Dependencies: google.auth._default, google.auth.impersonated_credentials

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

"""
Description:
This function retrieves impersonated credentials for a target service account.  It uses
the Google Cloud IAM impersonation feature, allowing one service account (or user account)
to act on behalf of another service account.

Parameters:
- target_scopes (list): A list of OAuth scopes that the impersonated credentials should
  have.  These scopes define the permissions that the impersonated credentials will be
  granted.
- target_service_account (str): The name of the service account to impersonate (without the
  "@<project>.iam.gserviceaccount.com" suffix).
- target_project (str): The project ID of the target service account.

Returns:
An impersonated credentials object.

Business Logic:
This function securely obtains credentials for a specific service account, avoiding the
need to store or manage long-lived service account keys.  Impersonation is a best
practice for managing access control in Google Cloud environments.

Example:
target_scopes = ['https://www.googleapis.com/auth/cloud-platform',
'https://www.googleapis.com/auth/bigquery']
credentials = getImpersonatedCredentials(target_scopes, "my-service-account",
"my-project")
bigquery_client = bigquery.Client(project="my-project", credentials=credentials)

Cyclomatic Complexity: Low (straightforward function calls).

Pain Points:
- The function assumes that the caller has the necessary IAM permissions to impersonate
  the target service account.  It doesn't explicitly check or handle cases where
  impersonation is not authorized.
- The function hardcodes a lifetime of 600 seconds (10 minutes) for the impersonated
  credentials.  This lifetime might be too short or too long depending on the use case.
  It would be better to make the lifetime configurable.
"""

# 4. _get_impersonated_credentials(target_scopes, target_service_account)
# Dependencies: google.auth._default, google.auth.impersonated_credentials, logging

def _get_impersonated_credentials(target_scopes: list, target_service_account: str):
    from google.auth import _default
    source_credentials, project_id = _default.default(scopes=target_scopes)
    logging.info(f"Source credentials generated for project [{project_id}]")

    from google.auth import impersonated_credentials
    target_credentials = impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=target_service_account,
        target_scopes=target_scopes,
        lifetime=60 * 60) # lifetime is set to 1 hour
    return target_credentials

"""
Description:
Retrieves impersonated credentials for a specified service account, enabling secure access
to Google Cloud resources.

Parameters:
- target_scopes (list): A list of OAuth scopes defining the permissions required for the
  impersonated credentials. Example: ['https://www.googleapis.com/auth/cloud-platform'].
- target_service_account (str): The email address of the service account to impersonate.
  Example: 'my-service-account@my-project.iam.gserviceaccount.com'.

Returns:
An `impersonated_credentials.Credentials` object that can be used to authenticate with
Google Cloud services on behalf of the target service account.

Business Logic:
This function uses the Google Cloud IAM impersonation feature. It begins by obtaining default
credentials for the environment where the code is running (e.g., a Compute Engine instance,
Cloud Functions, or a developer's workstation). Then, it uses these default credentials to
request impersonated credentials for the specified `target_service_account`. The
`target_scopes` parameter limits the permissions granted to the impersonated credentials,
following the principle of least privilege.

Example:
```python
target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
target_service_account = 'dataflow-sa@my-project.iam.gserviceaccount.com'
credentials = _get_impersonated_credentials(target_scopes, target_service_account)

storage_client = storage.Client(credentials=credentials)
```

Cyclomatic Complexity: Low (primarily sequential operations).

Pain Points:
- The `lifetime` of the credentials is hardcoded to 60 minutes. Depending on the use case,
  this may be too short or too long. A configuration option for `lifetime` would increase
  flexibility.
- The function assumes that the caller has the necessary IAM permissions to impersonate the
  `target_service_account`. If the caller lacks these permissions, the function will fail.
  Adding a check for these permissions (or wrapping the `impersonated_credentials.Credentials`
  call in a try-except block) would improve robustness.
"""

# 5. _get_storage_client(target_service_account, target_project)
# Dependencies: google.cloud.storage.Client, _get_impersonated_credentials, TEST_RUN (global constant)

def _get_storage_client(target_service_account: str, target_project: str):
    from google.cloud import storage
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    credentials = None if TEST_RUN == "true" else _get_impersonated_credentials(target_scopes,
                                                                                target_service_account)
    return storage.Client(project=target_project,
                          credentials=credentials)

"""
Description:
Creates a Google Cloud Storage client, optionally using impersonated credentials.

Parameters:
- target_service_account (str): The email address of the service account to impersonate.
  Required unless `TEST_RUN` is "true".
- target_project (str): The ID of the Google Cloud project.

Returns:
A `google.cloud.storage.Client` object.

Business Logic:
This function simplifies the creation of a Google Cloud Storage client, handling the
credential acquisition process. If the global constant `TEST_RUN` is set to "true", the
function returns a client without any credentials, which is useful for local testing.
Otherwise, it retrieves impersonated credentials for the specified
`target_service_account` using `_get_impersonated_credentials` and creates a client with
these credentials.  This ensures that the client operates with the permissions granted to
the `target_service_account`.

Example:
```python
storage_client = _get_storage_client('dataflow-sa@my-project.iam.gserviceaccount.com',
'my-project')

bucket = storage_client.get_bucket('my-bucket')
blob = bucket.blob('my-file.txt')
blob.download_to_filename('/tmp/my-file.txt')
```

Cyclomatic Complexity: Low (conditional credential acquisition).

Pain Points:
- The reliance on the global constant `TEST_RUN` can make the code harder to reason about
  and test. It would be better to pass a `use_impersonation` boolean parameter to the
  function.
- The function always requests the
  'https://www.googleapis.com/auth/cloud-platform' scope, even if the Storage client
  only needs narrower permissions. This could be improved by allowing the caller to
  specify the required scopes.
"""

# 6. list_jobs()
# Dependencies: _get_df_service, logging

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

"""
Description:
Lists all Dataflow jobs in a specific project and location.

Parameters:
None

Returns:
A list of Dataflow job dictionaries.

Business Logic:
This function uses the Dataflow API to retrieve a list of all jobs running in the
`PIPELINE_PROJECT_ID` project and `DATAFLOW_REGION` location. It first obtains a Dataflow
service client using `_get_df_service`, then uses the client to make a `list` API call.
The response is parsed to extract the list of job dictionaries.

Example:
```python
jobs = list_jobs()
for job in jobs:
print(f"Job ID: {job['id']}, Name: {job['name']}, Status: {job['currentState']}")
```

Cyclomatic Complexity: Low (primarily API calls and data extraction).

Pain Points:
- The function relies on the global constants `PIPELINE_PROJECT_ID` and
  `DATAFLOW_REGION`. It would be more flexible to pass these as parameters to the
  function.
- The function only retrieves the "jobs" field from the API response. The response may
  contain other useful information (e.g., pagination tokens) that are discarded.
"""

# 7. get_job_status(job_name)
# Dependencies: list_jobs, logging

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

"""
Description:
Retrieves the status of a Dataflow job given its name.

Parameters:
- job_name (str): The name (or the beginning of the name) of the Dataflow job.

Returns:
The status of the job (e.g., "JOB_STATE_RUNNING", "JOB_STATE_DONE") as a string, or None
if the job is not found.

Business Logic:
This function iterates through the list of Dataflow jobs obtained from `list_jobs` and
compares the name of each job to the provided `job_name`. If a job is found whose name
starts with `job_name`, the function returns the `currentState` of that job.

Example:
```python
job_status = get_job_status('my-dataflow-job')
if job_status == 'JOB_STATE_DONE':
print('Job completed successfully!')
elif job_status == 'JOB_STATE_RUNNING':
print('Job is still running...')
else:
print('Job not found or in an unknown state.')
```

Cyclomatic Complexity: Medium (iteration and conditional logic).

Pain Points:
- The function only considers jobs whose names *start* with `job_name`. This can lead to
  incorrect results if there are multiple jobs with similar prefixes. Using an exact
  match (`job_nm == job_name`) might be more appropriate, depending on the use case.
- The function returns `None` if no job is found. This is a reasonable approach, but it
  might be helpful to raise an exception in some cases (e.g., if the caller expects the
  job to exist).
"""

# 8. get_job_id(job_name)
# Dependencies: list_jobs, logging

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

"""
Description:
Retrieves the ID of a Dataflow job, assuming the job is in a "JOB_STATE_DONE" state.

Parameters:
- job_name (str): The name (or the beginning of the name) of the Dataflow job.

Returns:
The ID of the job as a string, or None if the job is not found or is not in the
"JOB_STATE_DONE" state.

Business Logic:
This function iterates through the list of Dataflow jobs obtained from `list_jobs`. For
each job, it checks if the job name starts with the provided `job_name` and if the job's
`currentState` is "JOB_STATE_DONE". If both conditions are met, the function returns the
job's ID.

Example:
```python
job_id = get_job_id('my-dataflow-job')
if job_id:
print(f'Job ID: {job_id}')
else:
print('Job not found or not in JOB_STATE_DONE state.')
```

Cyclomatic Complexity: Medium (iteration and conditional logic).

Pain Points:
- The function only considers jobs in the "JOB_STATE_DONE" state. This might be too
  restrictive, as the caller might be interested in the ID of a job in other states (e.g.,
  "JOB_STATE_RUNNING").
- Similar to `get_job_status`, the function only checks if the job name *starts with*
  `job_name`. This could lead to incorrect results if multiple jobs have similar prefixes.
"""

# 9. get_job_metrics(job_id)
# Dependencies: _get_df_service, logging

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

"""
Description:
Retrieves the metrics for a specific Dataflow job.

Parameters:
- job_id (str): The ID of the Dataflow job.

Returns:
A dictionary containing the job metrics, or None if an error occurs.

Business Logic:
This function uses the Dataflow API to retrieve the metrics for a job with the specified
`job_id`. It first obtains a Dataflow service client using `_get_df_service`, then uses
the client to make a `getMetrics` API call. The response is returned directly.

Example:
```python
job_metrics = get_job_metrics('2023-10-27_12:00:00-1234567890')
if job_metrics and 'metrics' in job_metrics:
for metric in job_metrics['metrics']:
print(f"Metric: {metric['name']['name']}, Value: {metric['scalar']}")
else:
print('No metrics found for this job.')
```

Cyclomatic Complexity: Low (primarily API calls).

Pain Points:
- The function relies on the global constants `PIPELINE_PROJECT_ID` and
  `DATAFLOW_REGION`. It would be more flexible to pass these as parameters.
- The function doesn't handle potential exceptions during the API call (e.g., if the job
  ID is invalid or the Dataflow API is unavailable). Adding a try-except block would
  improve robustness.
- The function returns the raw API response. It might be helpful to process the response
  and extract only the relevant metrics, making the function easier to use.
"""

# 10. get_bq_impersonated_client(target_service_account, target_project)
# Dependencies: google.cloud.bigquery.Client, getImpersonatedCredentials

def get_bq_impersonated_client(target_service_account: str, target_project: str):
    from google.cloud import bigquery
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform',
                     'https://www.googleapis.com/auth/bigquery']
    return bigquery.Client(project=target_project, credentials=getImpersonatedCredentials(target_scopes, target_service_account, target_project))

"""
Description:
Creates a BigQuery client using impersonated credentials.

Parameters:
- target_service_account (str): The email address of the service account to impersonate.
- target_project (str): The ID of the Google Cloud project.

Returns:
A `google.cloud.bigquery.Client` object.

Business Logic:
This function creates a BigQuery client that authenticates using impersonated credentials.
It first defines the necessary OAuth scopes for BigQuery access, then calls
`getImpersonatedCredentials` to obtain the impersonated credentials. Finally, it creates a
BigQuery client using these credentials.

Example:
```python
bq_client = get_bq_impersonated_client('dataflow-sa@my-project.iam.gserviceaccount.com',
'my-project')

query = "SELECT COUNT(*) FROM `my-project.my_dataset.my_table`"
query_job = bq_client.query(query)
results = query_job.result()
for row in results:
print(row[0])
```

Cyclomatic Complexity: Low (primarily function calls).

Pain Points:
- The function hardcodes the OAuth scopes. It would be more flexible to allow the caller
  to specify the required scopes.
- The function doesn't handle potential exceptions during client creation or credential
  acquisition. Adding try-except blocks would improve robustness.
"""

# 11. get_metric_service_client(target_service_account)
# Dependencies: google.cloud.monitoring_v3.MetricServiceClient

def get_metric_service_client(target_service_account: str):
    from google.cloud import monitoring_v3
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    return monitoring_v3.MetricServiceClient()

"""
Description:
Creates a Cloud Monitoring API client.

Parameters:
- target_service_account (str): The email address of the service account is not used, but it kept here for future use.

Returns:
A `google.cloud.monitoring_v3.MetricServiceClient` object.

Business Logic:
This function creates a Cloud Monitoring client using the default credentials.

Example:
```python
client = get_metric_service_client('dataflow-sa@my-project.iam.gserviceaccount.com')
```

Cyclomatic Complexity: Low (primarily function calls).

Pain Points:
- The function does not handle potential exceptions during client creation or credential
  acquisition. Adding try-except blocks would improve robustness.
"""

# 12. get_time_diff_between_processed_tm_vs_current_time()
# Dependencies: get_bq_impersonated_client, logging, bigquery, PIPELINE_PROJECT_ID, FRESHNESS_CHECK_DATASET_NAME, FRESHNESS_CHECK_TABLE_NAME, service_account_name, billing_label

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

"""
Description:
Calculates the time difference in minutes between the maximum `ingest_ts` in a BigQuery
table and the current timestamp.

Parameters:
None

Returns:
The time difference in minutes as an integer, or None if an error occurs.

Business Logic:
This function connects to BigQuery using impersonated credentials obtained from
`get_bq_impersonated_client`. It executes a SQL query that retrieves the maximum
`ingest_ts` from the `FRESHNESS_CHECK_TABLE_NAME` table in the
`FRESHNESS_CHECK_DATASET_NAME` dataset within the `PIPELINE_PROJECT_ID` project, the current time,
and calculates the difference between the current timestamp and the maximum ingest timestamp in minutes.

Example:
```python
time_difference = get_time_diff_between_processed_tm_vs_current_time()
if time_difference is not None:
print(f'Time difference: {time_difference} minutes')
else:
print('Error calculating time difference.')
```

Cyclomatic Complexity: Medium (query execution and data extraction).

Pain Points:
- The function relies heavily on global constants for project ID, dataset name, and table
  name. This makes the function less reusable and harder to test.
- The function doesn't handle cases where the `ingest_ts` column might be null or missing.
  The query should include a `WHERE ingest_ts IS NOT NULL` clause to avoid errors.
- The function catches all exceptions and logs the error. It might be better to re-raise
  specific exceptions or return a more informative error code.
"""

# 13. create_custom_metrics(metric_type, project_id, resource_type, value_type, val)
# Dependencies: get_metric_service_client, logging, google.cloud.monitoring_v3, time, CUSTOM_METRIC_DOMAIN, DAGID, COMPOSER_SERVICE_ACCOUNT

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

"""
Description:
Creates a custom metric in Google Cloud Monitoring.

Parameters:
- metric_type (str): The name of the custom metric (e.g., "pnr_valid_records").
- project_id (str): The ID of the Google Cloud project.
- resource_type (str): The type of resource being monitored (e.g., "cloud_composer_workflow").
- value_type (str): The data type of the metric value (e.g., "int64_value").
- val: The value of the metric.

Returns:
None

Business Logic:
This function creates a custom metric in Google Cloud Monitoring. It constructs a
TimeSeries object with the specified metric type, labels, resource type, and value, and
then uses the Cloud Monitoring API to create the time series.

Example:
```python
create_custom_metrics('pnr_valid_records', 'my-project', 'cloud_composer_workflow',
'int64_value', 12345)
```

Cyclomatic Complexity: Medium (metric construction and API call).

Pain Points:
- The function relies on several global constants (e.g., `CUSTOM_METRIC_DOMAIN`, `DAGID`,
  `COMPOSER_PROJECT_ID`). This makes the function less reusable and harder to test.
- The function hardcodes the location to "us-central1". This should be configurable.
- The function catches all exceptions and logs the error. It might be better to re-raise
  specific exceptions or return a more informative error code.
- Error logs are vague, and don't include the input values provided
"""

# 14. get_valid_record_count(job_name, metrics_names)
# Dependencies: get_job_id, get_job_metrics, logging

def get_valid_record_count(job_name,metrics_names):
    logging.info("job_name is {}".format(job_name))
    job_id = get_job_id(job_name)
    if job_id is not None:
        logging.info("job_id is {}".format(job_id))
        job_metrics = get_job_metrics(job_id)
        if job_metrics is None or job_metrics["metrics"] is None:
            logging.info("There are no metrics associated with this job {}".format(job_name))
        else:
            valid_record_count = 0
            for job_metric in job_metrics["metrics"]:
                if job_metric['name']['name'] in metrics_names:
                    valid_record_count = job_metric['scalar']
                    logging.info("job_metric {}".format(job_metric))
                    return valid_record_count
    else:
        return 0

"""
Description:
Retrieves the count of valid records processed by a Dataflow job, based on a set of
metric names.

Parameters:
- job_name (str): The name of the Dataflow job.
- metrics_names (list): A list of metric names to search for within the job's metrics.

Returns:
The count of valid records as an integer, or 0 if the job is not found, has no metrics,
or doesn't contain the specified metric names.

Business Logic:
This function first attempts to retrieve the job ID using `get_job_id`. If a job ID is
found, it retrieves the job metrics using `get_job_metrics`. It then iterates through the
list of metrics, searching for a metric whose name is in the `metrics_names` list. If a
matching metric is found, the function returns the metric's scalar value, which is
assumed to be the count of valid records.

Example:
```python
valid_record_count = get_valid_record_count('my-dataflow-job', ['pnr_valid_records'])
print(f'Valid record count: {valid_record_count}')
```

Cyclomatic Complexity: High (nested conditional logic and iteration).

Pain Points:
- The function only returns the first matching metric value. If there are multiple
  metrics with names in `metrics_names`, only one will be considered.
- The function assumes that the metric value is a scalar. It doesn't handle other metric
  types.
- The function's logic is somewhat complex and could be simplified by using more
  descriptive variable names and breaking the code into smaller functions.
"""

```

The above documentation provides a comprehensive overview of each function, explaining its purpose, parameters, return values, business logic, cyclomatic complexity, and potential pain points. The functions are presented in the order they appear in the list of dependencies provided. Furthermore functions func1,func2 are mapped to their respective function names

## UML Diagram
![Image](images/anotherDAG_img1.png)
## DAG FLOW
![Image](images/anotherDAG_img2.png)

