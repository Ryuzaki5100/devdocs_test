import os
import time
import uuid

import pendulum
from airflow import DAG
from googleapiclient.discovery import build
from airflow.exceptions import AirflowFailException
from airflow.models import XCom
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.google.cloud.operators.dataflow import DataflowTemplatedJobStartOperator
from airflow.providers.google.cloud.operators.gcs import GCSListObjectsOperator
from airflow.utils.db import provide_session
from airflow.utils.trigger_rule import TriggerRule
from googleapiclient.errors import HttpError
from google.cloud import monitoring_v3
from pnr_dag_vars import *
from pnr_vars import *
from dag_utils import group_partitions_per_hour, select_files
from google.cloud import bigquery

DAGID = f"pnr{SUFFIX}"
DAG_SCHEDULE = "*/30 * * * *"

TAG_RELEASE = RELEASE_RAW
TAG_APP = "pnr"

DAG_PARAM_GCS_LANDING_BUCKET_NAME = "gcs_landing_bucket_name"
DAG_PARAM_GCS_LANDING_BUCKET_PATH = "gcs_landing_bucket_path"
DAG_PARAM_GCS_ARCHIVE_BUCKET_NAME = "gcs_archive_bucket_name"
DAG_PARAM_GCS_ARCHIVE_BUCKET_PATH = "gcs_archive_bucket_path"
DAG_PARAM_GCS_STAGING_BUCKET_NAME = "gcs_staging_bucket_name"
DAG_PARAM_GCS_STAGING_BUCKET_PATH = "gcs_staging_bucket_path"
DAG_PARAM_NUM_PAST_HOURS = "num_past_hours"
DAG_PARAM_RUN_ID = "run_id"

TASK_PARAM_JOB_NAME = "job_name"
TASK_PARAM_STAGING_BUCKET_NAME = "staging_bucket_name"
TASK_PARAM_STAGING_BUCKET_PATH = "staging_bucket_path"
TASK_PARAM_ARCHIVE_BUCKET_NAME = "archive_bucket_name"
TASK_PARAM_ARCHIVE_BUCKET_PATH = "archive_bucket_path"
TASK_PARAM_LANDING_BUCKET_NAME = "landing_bucket_name"
TASK_PARAM_LANDING_BUCKET_PATH = "landing_bucket_path"
TASK_PARAM_RUN_BUCKET_NAME = "run_bucket_name"
TASK_PARAM_RUN_BUCKET_PATH = "run_bucket_path"
TASK_PARAM_RUN_PATH_FULL = "run_path"
TASK_PARAM_REPROCESSING = "is_reprocessing"
TASK_PARAM_NUM_PAST_HOURS = "num_past_hours"

TASK_PARAM_RUN_DIR = "run_dir"

TASK_SETUP_PROCESSING = "setup_processing"
TASK_PREPARE_STAGING = "prepare_staging"
TASK_PROCESS_STAGING = "process_staging"
TASK_MOVE_TO_ARCHIVE = "move_to_archive"
TASK_CLEAN_STAGING = "clean_staging"
TASK_SKIP_PREPARE_STAGING = "skip_prepare_staging"
TASK_TRIGGER_DF_JOB = "trigger_df_job"

DEFAULT_TIMEZONE = "America/Chicago"
DEFAULT_NUM_HOURS = "10"
DATAFLOW_REGION = 'us-central1'

# START_DATE = pendulum.now(DEFAULT_TIMEZONE).subtract(minutes=20)
# PREV_HOUR = pendulum.now(DEFAULT_TIMEZONE).subtract(hours=1)
# START_DATE = PREV_HOUR.at(PREV_HOUR.hour, 0, 0)
START_DATE = pendulum.now(DEFAULT_TIMEZONE).subtract(hours=1)

DELIMITER = ".avro"

MAX_RETRIES = 3

service_account_name = DATAFLOW_SERVICE_ACCOUNT.split('@')[0]
billing_label = f"pnr-data-ingestion{SUFFIX}"

# For manual run
# {
#     "run_id": "",
# }
CUSTOM_METRIC_DOMAIN = "custom.googleapis.com"
def _get_df_service():
    df_service = build("dataflow", "v1b3", cache_discovery=False)
    logging.info("df service [{}]".format(df_service))
    return df_service

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


def _get_default_or_from_dag_run(default_value: str, dag_key, dag_run_conf):
    if dag_run_conf is not None and dag_key in dag_run_conf:
        return dag_run_conf[dag_key]
    return default_value

def get_metric_service_client(target_service_account: str):
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    return monitoring_v3.MetricServiceClient()

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


def get_bq_impersonated_client(target_service_account: str, target_project: str):
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform',
                     'https://www.googleapis.com/auth/bigquery']
    return bigquery.Client(project=target_project, credentials=getImpersonatedCredentials(target_scopes, target_service_account, target_project))


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


def _get_storage_client(target_service_account: str, target_project: str):
    from google.cloud import storage
    target_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    credentials = None if TEST_RUN == "true" else _get_impersonated_credentials(target_scopes,
                                                                                target_service_account)
    return storage.Client(project=target_project,
                          credentials=credentials)


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


def _is_reprocessing(**context):
    reprocess_flag = context['ti'].xcom_pull(key=TASK_PARAM_REPROCESSING, task_ids=TASK_SETUP_PROCESSING)
    logging.info(f"Is reprocessing required [{reprocess_flag}]")
    return TASK_PREPARE_STAGING if not reprocess_flag else TASK_SKIP_PREPARE_STAGING


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


def _move_landing_to_staging(source_bucket: str, source_objects: list, destination_bucket: str, destination_path: str,
                             source_path: str, **context):
    logging.info(
        f"Moving [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]...")
    _move_blobs(source_bucket, source_objects, destination_bucket, destination_path, **context)
    logging.info(
        f"Moved [{len(source_objects)}] landing files from [{source_bucket}/{source_path}] to staging [{destination_bucket}/{destination_path}]")


def _move_to_archive(**context):
    ti = context['ti']
    gcs_archive_bucket_name = ti.xcom_pull(key=TASK_PARAM_ARCHIVE_BUCKET_NAME, task_ids=TASK_SETUP_PROCESSING)
    gcs_archive_bucket_path = ti.xcom_pull(key=TASK_PARAM_ARCHIVE_BUCKET_PATH, task_ids=TASK_SETUP_PROCESSING)
    gcs_run_bucket_name = ti.xcom_pull(key=TASK_PARAM_RUN_BUCKET_NAME, task_ids=TASK_SETUP_PROCESSING)
    gcs_run_bucket_path = ti.xcom_pull(key=TASK_PARAM_RUN_BUCKET_PATH, task_ids=TASK_SETUP_PROCESSING)

    logging.info(f"Archive bucket name [{gcs_archive_bucket_name}]")
    logging.info(f"Archive bucket path [{gcs_archive_bucket_path}]")
    logging.info(f"Run bucket name [{gcs_run_bucket_name}]")
    logging.info(f"Run bucket path [{gcs_run_bucket_path}]")

    logging.info(
        f"Archiving files from [{gcs_run_bucket_name}/{gcs_run_bucket_path}] to [{gcs_archive_bucket_name}/{gcs_archive_bucket_path}]")

    processed_files = _get_gcs_files(gcs_run_bucket_name, gcs_run_bucket_path, **context)
    logging.info(f"Found [{len(processed_files)}] processed files in [{gcs_run_bucket_name}/{gcs_run_bucket_path}]")

    if len(processed_files) == 0:
        logging.error(f"No files in run path [{gcs_run_bucket_name}/{gcs_run_bucket_path}]")
        raise AirflowFailException(f"No files in run path [{gcs_run_bucket_name}/{gcs_run_bucket_path}]")

    per_hour_grouping = group_partitions_per_hour(processed_files, gcs_run_bucket_path + "/")

    for partition in per_hour_grouping:
        files_per_partition = per_hour_grouping[partition]
        logging.info(
            f"Moving files from partition [{partition}] to [{gcs_archive_bucket_name}/{gcs_archive_bucket_path}/{partition}/]")
        _move_blobs(gcs_run_bucket_name, files_per_partition, gcs_archive_bucket_name,
                    f"{gcs_archive_bucket_path}/{partition}", **context)
    logging.info(f"Processed [{len(per_hour_grouping)}] partitions")


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


def _process_staging(**context):
    logging.info(f"Preparing Dataflow job...")
    dag = context["dag"]
    ti = context['ti']
    job_name = ti.xcom_pull(key=TASK_PARAM_JOB_NAME, task_ids=TASK_SETUP_PROCESSING)
    run_path = ti.xcom_pull(key=TASK_PARAM_RUN_PATH_FULL, task_ids=TASK_SETUP_PROCESSING)

    dag_vars = get_dag_vars()
    num_workers = get_dag_var_as_int(VAR_AS_DF_NUM_WORKERS, dag_vars)
    max_workers = get_dag_var_as_int(VAR_AS_DF_MAX_WORKERS, dag_vars)
    machine_type = get_dag_var_as_string(VAR_AS_DF_MACHINE_TYPE, dag_vars)

    logging.info(f"Num workers [{num_workers}]")
    logging.info(f"Max workers [{max_workers}]")
    logging.info(f"Machine type [{machine_type}]")

    df_job = DataflowTemplatedJobStartOperator(
        task_id=TASK_TRIGGER_DF_JOB,
        template=DATAFLOW_TEMPLATE_LOCATION,
        project_id=PIPELINE_PROJECT_ID,
        job_name=job_name,
        location=DATAFLOW_REGION,
        environment={
            "serviceAccountEmail": DATAFLOW_SERVICE_ACCOUNT,
            "additionalUserLabels": USER_LABELS
        },
        parameters={
            "runPath": f"gs://{run_path}/*{DELIMITER}"
        },
        dataflow_default_options={
            "tempLocation": DATAFLOW_TEMP_LOCATION,
            "numWorkers": num_workers,
            "maxWorkers": max_workers,
            "machineType": machine_type
        },
        dag=dag
    )
    retry_option = 0
    while retry_option < MAX_RETRIES:
        try:
            retry_option += 1
            logging.info(f"Try [{retry_option}/{MAX_RETRIES}]")
            logging.info(f"Starting Dataflow job [{job_name}]...")
            df_job.execute(context)
            break
        except (Exception,HttpError) as err:
            logging.error(
                f"DataflowTemplatedJobStartOperator got HttpError exception while running DF job [{err}]")
            create_custom_metrics(f"pnr_processed_file_count{SUFFIX}", COMPOSER_PROJECT_ID, "cloud_composer_workflow",
                                  "int64_value", 0)
            raise AirflowFailException(f"Unable to start Dataflow job after [{MAX_RETRIES}]")
            time.sleep(5)

            continue
        break
    logging.info(f"Finished Dataflow job [{job_name}]")
    ti.xcom_push("job_status", value="JOB_STATE_DONE")
    pnr_processed_file_count = get_valid_record_count(job_name, "pnr_valid_records")
    logging.info(f"pnr_processed_file_count [{pnr_processed_file_count}]")
    create_custom_metrics(f"pnr_processed_file_count{SUFFIX}", COMPOSER_PROJECT_ID, "cloud_composer_workflow",
                              "int64_value", pnr_processed_file_count)
    diff_in_mins = get_time_diff_between_processed_tm_vs_current_time()
    logging.info(f"Time difference between processed_dt and current time is [{diff_in_mins}]")
    create_custom_metrics(f"pnr_processed_time_lag_in_mins{SUFFIX}", COMPOSER_PROJECT_ID, "cloud_composer_workflow",
                              "int64_value", diff_in_mins)


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

@provide_session
def _cleanup_xcom(context, session=None):
    dag_id = context["dag"].dag_id
    session.query(XCom).filter(XCom.dag_id == dag_id).delete()


# Default args
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': DAG_EMAIL_LIST,
    'email_on_failure': True if ENABLE_EMAIL_ALERTS == "true" else False,
    'email_on_retry': False,
    'retries': 0
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=1)
}

# DAG definition
dag = DAG(
    dag_id=DAGID,
    default_args=default_args,
    description="pnr",
    schedule_interval=None if TEST_RUN == "true" else DAG_SCHEDULE,
    start_date=START_DATE,
    catchup=False,
    max_active_runs=3,
    tags=[TAG_APP, TAG_RELEASE]  # ,
    # on_success_callback=_cleanup_xcom,
    # on_failure_callback=_cleanup_xcom
)

setup_processing_task = PythonOperator(
    task_id=TASK_SETUP_PROCESSING,
    python_callable=_setup_processing,
    dag=dag
)

prepare_staging_task = PythonOperator(
    task_id=TASK_PREPARE_STAGING,
    python_callable=_prepare_staging,
    dag=dag
)

is_reprocessing_task = BranchPythonOperator(
    task_id='is_reprocessing_branch',
    trigger_rule=TriggerRule.ALL_DONE,
    python_callable=_is_reprocessing,
    dag=dag
)

process_staging_task = PythonOperator(
    task_id=TASK_PROCESS_STAGING,
    python_callable=_process_staging,
    trigger_rule=TriggerRule.NONE_FAILED_OR_SKIPPED,
    dag=dag
)

move_to_archive_task = PythonOperator(
    task_id=TASK_MOVE_TO_ARCHIVE,
    python_callable=_move_to_archive,
    dag=dag
)



skip_prepare_staging_task = EmptyOperator(
    task_id=TASK_SKIP_PREPARE_STAGING,
    dag=dag,
)

# Pipeline
setup_processing_task >> is_reprocessing_task >> [prepare_staging_task,
                                                  skip_prepare_staging_task] >> process_staging_task >> move_to_archive_task