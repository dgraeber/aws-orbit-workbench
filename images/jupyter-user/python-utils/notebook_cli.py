#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License").
#    You may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
import os
import sys
from os.path import expanduser

import boto3
import yaml

import notebook_runner as nr
import python_runner as pr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Hack to make YAML loader not auto-convert datetimes
# https://stackoverflow.com/a/52312810
NoDatesSafeLoader = yaml.SafeLoader
NoDatesSafeLoader.yaml_implicit_resolvers = {
    k: [r for r in v if r[0] != "tag:yaml.org,2002:timestamp"]
    for k, v in NoDatesSafeLoader.yaml_implicit_resolvers.items()
}


def read_yaml_file(path):
    with open(path, "r") as f:
        return yaml.load(f, Loader=NoDatesSafeLoader)


def writeOrbitYaml():
    data = dict(
        properties=dict(
            AWS_ORBIT_ENV=os.environ["AWS_ORBIT_ENV"],
            AWS_ORBIT_TEAM_SPACE=os.environ["AWS_ORBIT_TEAM_SPACE"],
        )
    )
    home = expanduser("~")
    propFilePath = f"{home}/orbit.yaml"

    with open(propFilePath, "w") as outfile:
        yaml.dump(data, outfile, default_flow_style=False)


def notifyOnTasksCompletion(subject, msg, compute):
    if "topic" not in compute["compute"].keys():
        return
    topic_name = compute["compute"]["sns.topic.name"]
    logger.info(f"sending task notification to {topic_name}...")
    try:
        sns = boto3.client("sns")
        res = sns.list_topics()["Topics"]
        for topic in res:
            if topic_name in topic["TopicArn"]:
                sns.publish(TopicArn=topic["TopicArn"], Message=msg, Subject=subject)
    finally:
        print("Unexpected error while publishing to topic:", sys.exc_info()[0])

    logger.info(f"done task notifications to {topic_name}")


def run_tasks() -> int:
    logger.debug("starting task execution with following arguments: ")
    logging.debug("ENV VARS: %s", os.environ.keys())
    env_params = ""
    for param in os.environ.keys():
        env_params += param + " = " + os.environ[param] + "\n"
    logger.debug(env_params)

    writeOrbitYaml()
    compute = yaml.load(os.environ["compute"], Loader=NoDatesSafeLoader)
    task_type = os.environ["task_type"]
    try:
        if task_type == "jupyter":
            nr.run()
        else:
            pr.run()
        logger.info("Done task execution")
        notifyOnTasksCompletion("finished executing tasks", "Tasks:\n" + os.environ["tasks"], compute)
        return 0
    except Exception as e:
        logger.exception(f"Done task execution with errors, {str(e)}")
        notifyOnTasksCompletion(
            "Error while executing tasks. Errors: \n", str(e) + "\n\n Tasks:\n" + os.environ["tasks"], compute
        )
        raise e
    finally:
        logger.info("Exiting Container Main()")


if __name__ == "__main__":
    logger.info("Starting Container Main")
    logger.info("Running tasks...")

    ret = run_tasks()
    sys.exit(ret)
