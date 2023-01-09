# libraries
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator, PythonOperator, ZipOperator, UnzipOperator
from airflow.utils.dates import days_ago
import pandas as pd

### Defining DAG Arguments
default_args = {
    'owner': 'Shehroz',
    'start_date': datetime(2021, 1, 1),
    'email': ['shehroz@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

### Define the DAG
dag = DAG(
    'ETL_toll_data',
    default_args=default_args,
    description='Apache Airflow Final Assignment',
    schedule_interval=timedelta(days=1))

### Define the Tasks

# 1.Task to Unzip Data
unzip_task = UnzipOperator(
    task_id='unzip_data',
    path_to_zip_file="/home/project/airflow/dags/finalassignment/tolldata.tgz",
    path_to_unzip_contents="/home/project/airflow/dags/finalassignment/",
    dag=dag)

# 2.Extract Data from csv File
extract_csv_task = PythonOperator(
    task_id='extract_data_from_csv',
    python_callable= csv_extraction
    )
    
def csv_extraction():
    df = pd.read_csv('/home/project/airflow/dags/finalassignment/vehicle-data.csv', header= 'infer')
    df = df.iloc[:, 0:4]
    df.columns = ['Rowid', 'Timestamp', 'Anonymized Vehicle number',  'Vehicle type']    
    df.to_csv('/home/project/airflow/dags/finalassignment/csv_data.csv')

# 3. extract_data_from_tsv
extract_tsv_task = PythonOperator(
    task_id='extract_data_from_tsv',
    python_callable= tsv_extraction
    )
    
def tsv_extraction():
    df = pd.read_csv('/home/project/airflow/dags/finalassignment/tollplaza-data.tsv', header= 'infer', sep='\t')
    df = df.iloc[:, 5:8]
    df.columns = ['Number of axles', 'Tollplaza id', 'Tollplaza code']     
    df.to_csv('/home/project/airflow/dags/finalassignment/tsv_data.csv')

# 4. extract_data_from_fixed_width
extract_txt_task = PythonOperator(
    task_id='extract_data_from_fixed_width',
    python_callable= txt_extraction
    )
    
def txt_extraction():
    df = pd.DataFrame(columns = ['Type of Payment code',  'Vehicle Code'])   
    
    lines = []
    with open('/home/project/airflow/dags/finalassignment/payment-data.txt') as f:
        lines = f.readlines()

    for line in lines:
        line = line[::-1]
        line = line.split(' ', 2)[0:2]
        line[0]=line[0].replace('\n','')
        line[0],line[1] = line[1],line[0]       
        to_append = line
        df_length = len(df)
        df.loc[df_length] = to_append 
        
    df.to_csv('/home/project/airflow/dags/finalassignment/fixed_width_data.csv')


# 5. Consolidate_Data
consolidate_task = PythonOperator(
    task_id='consolidate_data',
    python_callable= consolidate
    )

def consolidate():
    df1 = pd.read_csv('/home/project/airflow/dags/finalassignment/csv_data.csv', header= None)
    df2 = pd.read_csv('/home/project/airflow/dags/finalassignment/tsv_data.csv', header= None)
    df3 = pd.read_csv('/home/project/airflow/dags/finalassignment/fixed_width_data.csv', header= None)
    df = pd.concat([df1, df2, df3], axis=1, join="inner")    

    df.to_csv('/home/project/airflow/dags/finalassignment/extracted_data.csv')

# 6. Transform_Data
transform_task = PythonOperator(
    task_id='transform_data',
    python_callable= transform
    )

def transform():
    df = pd.read_csv('/home/project/airflow/dags/finalassignment/extracted_data.csv', header= None) 
    df['Vehicle type'] = df['Vehicle type'].map(lambda name: name.upper())
    df.to_csv('/home/project/airflow/dags/finalassignment/staging/transform_data.csv')

# 7. Task Pipeline
unzip_task >> extract_csv_task >> extract_tsv_task >> extract_txt_task >> transform_task