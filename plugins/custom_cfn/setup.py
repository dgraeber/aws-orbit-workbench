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

from io import open

from setuptools import find_packages, setup

with open("VERSION", "r") as version_file:
    version = version_file.read().strip()

setup(
    name="aws-orbit-custom-cfn",
    version=version,
    description="Launch a CloudFormation stack for the team space",
    license="Apache License 2.0",
    packages=find_packages(include=["custom_cfn", "custom_cfn.*"]),
    python_requires=">=3.6, <3.9",
    install_requires=[
        "aws_cdk.core~=1.67.0",
    ],
    include_package_data=True,
)