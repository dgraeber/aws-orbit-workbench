#!/usr/bin/env bash
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License").
#   You may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

set -ex

if [ $UID -eq 0 ]; then
  COMMAND=$0
  COMMANDARGS="$(printf " %q" "${@}")"
  exec sudo -E su jovyan -c "/usr/bin/bash -l $COMMAND $COMMANDARGS"
  exit
fi

mkdir -p /efs/"$USERNAME"
mkdir -p /efs/shared/scheduled/notebooks
mkdir -p /efs/shared/scheduled/outputs
mkdir -p /home/jovyan/tmp

ln -s /efs/"$USERNAME"/ /home/jovyan/private
ln -s /efs/shared/ /home/jovyan/shared

# Bootstrap

LOCAL_PATH="/home/jovyan/.orbit/bootstrap/scripts/"
S3_PATH="s3://${AWS_ORBIT_S3_BUCKET}/teams/${AWS_ORBIT_TEAM_SPACE}/bootstrap/"

export PATH=$PATH:/opt/conda/bin
mkdir -p $LOCAL_PATH
aws s3 cp $S3_PATH $LOCAL_PATH --recursive
for filename in $(ls $LOCAL_PATH)
do
    echo "Running ${filename}"
    sh "${LOCAL_PATH}${filename}"
done

rm -fR /home/jovyan/.aws
