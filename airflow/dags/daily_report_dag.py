import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.email_operator import EmailOperator
local_tz = pendulum.timezone("Asia/Seoul")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='daily_report_dag',
    default_args=default_args,
    description='매일 새벽 1시에 Spark를 이용해 뉴스 리포트 생성',
    schedule_interval='0 1 * * *',
    start_date=datetime(2025, 5, 1, tzinfo=local_tz),
    catchup=False,
    tags=['daily', 'report', 'spark']
) as dag:

    # 키워드 분석
    submit_spark_job = SparkSubmitOperator(
        task_id='spark_daily_report',
        application='/opt/airflow/dags/scripts/spark_daily_report.py',
        conn_id='spark_default',
        application_args=['--date', '{{ ds }}'],
    )
    
    notify_report_generated = BashOperator(
        task_id='notify_report_generated',
        bash_command=(
            'echo "리포트가 생성되었습니다: {{ ds }} 날짜의 이메일 보내기 "'
        )
    )

    # 분석 결과 이메일 전송
    send_email = EmailOperator(
        task_id='send_email',
        to='shrbqor1104@gmail.com',
        subject='Daily Report',
        html_content='''
        <h3>일일 뉴스 키워드 분석 리포트</h3>
        <p>분석 대상 날짜: {{ macros.ds_add(ds, -1) }}</p>
        <img src="/opt/airflow/data/keyword_frequency_{{ macros.ds_add(ds, -1) }}.png" alt="Daily Report">
        ''',
        files=['/opt/airflow/data/keyword_frequency_{{ macros.ds_add(ds, -1) }}.png']
    )

  
    # submit_spark_job >> notify_report_generated
    submit_spark_job >> notify_report_generated >> send_email