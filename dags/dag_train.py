from airflow import DAG
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.base import BaseSensorOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator
import os
import shutil

properties_path = '/model_training_project/data'
model_path = '/model_training_project/model'
model_file = 'model.pkl'
preprocess_file = 'preprocess.pkl'
properties_file = 'properties.csv'
properties_file_path = os.path.join(properties_path, properties_file)
model_file_path = os.path.join(model_path, model_file)
preprocess_file_path = os.path.join(model_path, preprocess_file)

file_paths = [properties_file_path, model_file_path, preprocess_file_path]


class FileSensor(BaseSensorOperator):
    def __init__(self, file_path, retries, retry_delay, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = file_path
        self.retries = retries
        self.retry_delay = retry_delay

    def poke(self, context):
        if os.path.exists(self.file_path):
            return True
        return False

def check_file_existence(file_path):
    if os.path.exists(file_path):
        return 'train_model'
    else:
        return 'send_email'

def copy_and_rename_file(original_file):
    today_date = datetime.now().strftime("%Y%m%d")
    new_file_name = os.path.basename(original_file).split('.')[0] + f'_{today_date}.csv'
    new_file_path = os.path.join(os.path.dirname(original_file), new_file_name)
    shutil.copyfile(original_file, new_file_path)

def copy_and_rename_files(file_paths, destination_dir=None):
    today_date = datetime.now().strftime("%Y%m%d")
    for original_file in file_paths:
        filename, file_extension = os.path.splitext(original_file)
        new_file_name = os.path.basename(filename) + f'_{today_date}' + file_extension
        if destination_dir:
            new_file_path = os.path.join(destination_dir, new_file_name)
        else:
            new_file_path = os.path.join(os.path.dirname(original_file), new_file_name)
        shutil.copyfile(original_file, new_file_path)

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 24),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1
}


# Define the DAG
dag = DAG(
    'train_dag',
    default_args=default_args,
    description='A simple DAG that checks if a properties.csv file is in the folder, and trains a model on it.',
    schedule_interval=None
)

# Define tasks
file_sensor_task = FileSensor(
    task_id='file_sensor',
    file_path=properties_file_path,  # Specify the file path here
    retries=3,  # Retry 3 times
    retry_delay=timedelta(minutes=1),  # Retry every minute
    mode='poke',
    dag=dag
)

branch_task = BranchPythonOperator(
    task_id='branch_task',
    python_callable=check_file_existence,
    op_kwargs={'file_path': properties_file_path},  # Specify the file path here
    dag=dag
)

train_model = BashOperator(
    task_id='train_model',
    bash_command="python /model_training_project/train.py",
    dag=dag
)

copy_and_rename_file_task = PythonOperator(
    task_id='copy_and_rename_file_task',
    python_callable=copy_and_rename_files,
    op_kwargs={'file_paths': file_paths},  # Specify the paths here
    dag=dag
)

send_email = EmailOperator(
    task_id='send_email',
    to='jens.dedeyne@gmail.com',  # Specify your email here
    subject='File not found',
    html_content='The file was not found within the specified retry attempts.',
    dag=dag
)

# Define task dependencies
file_sensor_task >> branch_task >> [train_model, send_email]
train_model >> copy_and_rename_file_task