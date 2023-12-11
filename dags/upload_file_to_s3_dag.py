from datetime import datetime

from airflow.decorators import task
from airflow.models.dag import DAG
from airflow.providers.amazon.aws.operators.ecs import EcsCreateClusterOperator, EcsRegisterTaskDefinitionOperator, EcsRunTaskOperator


CLUSTER_NAME = "<your-cluster-name>"
REGION_NAME = "<your-region-name>"
AWS_CONN_ID = "<airflow-connection-name>"
TASK_DEFINITION_NAME = "<task-definition-name>"

with DAG(
    dag_id="ecs_fargate_sample",
    schedule=None,
    start_date=datetime(2023, 11, 20),
    tags=["ECS"],
    catchup=False,
) as dag:
    create_cluster = EcsCreateClusterOperator(
        task_id="create_ecs_cluster",
        aws_conn_id=AWS_CONN_ID,
        region=REGION_NAME,
        cluster_name=CLUSTER_NAME,
        create_cluster_kwargs={
            "tags": [
                {
                    "key": "isSample",
                    "value": "true"
                }
            ],
            "capacityProviders": [
                "FARGATE",  # DO NOT CHANGE THIS LINE
            ],
            "settings": [
                {
                    "name": "containerInsights",
                    "value": "enabled"
                },
            ],
            "configuration": {
                "executeCommandConfiguration": {
                    "logging": "OVERRIDE",
                    "logConfiguration": {
                        "cloudWatchLogGroupName": "ECSCloudWatchLogGroupName",
                        "cloudWatchEncryptionEnabled": False
                    }
                }
            }
        },
        wait_for_completion=True,
        waiter_delay=15,
        waiter_max_attempts=60,
    )

    register_task = EcsRegisterTaskDefinitionOperator(
        task_id="register_task",
        family=TASK_DEFINITION_NAME,
        aws_conn_id=AWS_CONN_ID,
        region=REGION_NAME,
        container_definitions=[
            {
                "name": "s3_poc_airflow",
                "image": "mostafaghadimi/s3_poc_airflow:v5",
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {
                        "awslogs-group": "ecs-aws-s3-poc_airflow-log-group",
                        "awslogs-region": REGION_NAME,
                        "awslogs-create-group": "true",
                        "awslogs-stream-prefix": "ecs",
                    },
                },
            },
        ],
        register_task_kwargs={
            "cpu": "1024",
            "memory": "2048",
            "networkMode": "awsvpc",
            "requiresCompatibilities": [
                "FARGATE"
            ],
            "executionRoleArn": "<assigned-role>",
            "taskRoleArn": "<assigned-role>",
        },
    )

    run_task = EcsRunTaskOperator(
        task_id="run_task",
        aws_conn_id=AWS_CONN_ID,
        region=REGION_NAME,
        cluster=CLUSTER_NAME,
        task_definition=TASK_DEFINITION_NAME,
        launch_type="FARGATE",
        overrides={
            "containerOverrides": [],
        },
        network_configuration={
            "awsvpcConfiguration": {
                "subnets": [
                    "<replace-this-with-your-subnet>",
                ],
                "securityGroups": [
                    "<replace-this-with-your-security-group>",
                ],
                "assignPublicIp": "ENABLED",
            },
        },
    )
        
    create_cluster >> register_task >> run_task
