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

import json
import logging
import os
import subprocess
import time
from copy import deepcopy
from typing import Any, Dict

from kubernetes import config as k8_config
from kubernetes.client import CoreV1Api, V1ConfigMap
from kubernetes.client.exceptions import ApiException

ORBIT_API_VERSION = "v1"
ORBIT_API_GROUP = "orbit.aws"
ORBIT_SYSTEM_NAMESPACE = "orbit-system"

DEBUG_LOGGING_FORMAT = "[%(asctime)s][%(filename)-13s:%(lineno)3d][%(levelname)s] %(message)s"


def _get_logger() -> logging.Logger:
    debug = os.environ.get("ADMISSION_CONTROLLER_DEBUG", "False").lower() in ["true", "yes", "1"]
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format=DEBUG_LOGGING_FORMAT)
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(level)
    if debug:
        logging.getLogger("kubernetes").setLevel(logging.ERROR)
    return logger


def get_admission_controller_state() -> V1ConfigMap:
    try:
        config_map: V1ConfigMap = CoreV1Api().read_namespaced_config_map(
            name="admission-controller-state", namespace=ORBIT_SYSTEM_NAMESPACE
        )

        logger.debug("admission-controller-state: %s", config_map.to_dict())
        return config_map
    except ApiException as e:
        if e.status == 404:
            logger.info(
                "The admission-controller-state ConfigMap was not found in the %s Namespace", ORBIT_SYSTEM_NAMESPACE
            )
            return initialize_admission_controller_state()
        else:
            logger.exception("Error fetching admission-controller-state ConfigMap")
            raise e
    except Exception:
        logger.exception("Error fetching admission-controller-state ConfigMap")
        raise


def initialize_admission_controller_state() -> V1ConfigMap:
    try:
        logger.info("Initializing admission-controller-state ConfigMap in the %s Namesapce", ORBIT_SYSTEM_NAMESPACE)
        return CoreV1Api().create_namespaced_config_map(
            namespace=ORBIT_SYSTEM_NAMESPACE,
            body={
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {"name": "admission-controller-state"},
                "data": {},
            },
        )
    except Exception:
        logger.exception("Error putting admission-controller-state ConfigMap")
        raise


def get_module_state(module: str) -> Dict[str, Any]:
    config_map = get_admission_controller_state()
    config_map_data = config_map.data if config_map.data is not None else {}
    data = {k: json.loads(v) for k, v in config_map_data.items()} if config_map is not None else {}

    return data.get(module, {})


def put_module_state(module: str, state: Dict[str, Any]) -> None:
    try:
        body = {"data": {module: json.dumps({k: v for k, v in state.items()})}}
        logger.debug("Patching admission-controller-state in Namespace %s with %s", ORBIT_SYSTEM_NAMESPACE, body)
        CoreV1Api().patch_namespaced_config_map(
            name="admission-controller-state", namespace=ORBIT_SYSTEM_NAMESPACE, body=body
        )
    except Exception:
        logger.exception("Error patching admission-controller-state ConfigMap")
        raise


def maintain_module_state(module: str, state: Dict[str, Any], sleep_time: int = 1) -> None:
    last_state = None
    while True:
        state_copy = deepcopy(state)
        if state_copy != last_state:
            put_module_state(module=module, state=state)
        last_state = state_copy
        time.sleep(sleep_time)


def load_config(in_cluster: bool = True) -> None:
    in_cluster_env = os.environ.get("IN_CLUSTER_DEPLOYMENT", None)
    in_cluster = in_cluster_env.lower() in ["yes", "true", "1"] if in_cluster_env is not None else in_cluster
    if in_cluster:
        logger.debug("Loading In-Cluster Config")
        k8_config.load_incluster_config()
    else:
        logger.debug("Loading Off-Cluster Config")
        k8_config.load_kube_config()


def run_command(cmd: str) -> str:
    """ Module to run shell commands. """
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, timeout=29, universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        logger.debug("Command failed with exit code {}, stderr: {}".format(exc.returncode, exc.output))
        raise Exception(exc.output)
    return output


logger = _get_logger()