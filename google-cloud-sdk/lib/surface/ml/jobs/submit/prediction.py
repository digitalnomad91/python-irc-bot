# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""ml jobs submit batch prediction command."""

from googlecloudsdk.api_lib.ml import jobs
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base


class Prediction(base.Command):
  """Start a Cloud ML batch prediction job."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    # TODO(user): move all flags definition to api_lib/ml/flags.py.
    parser.add_argument('job', help='Name of the batch prediction job.')
    parser.add_argument('--model', required=True, help='Name of the model.')
    parser.add_argument(
        '--version',
        help='Model version to be used. If unspecified, the default version '
        'of the model will be used.')
    # input location is a repeated field.
    parser.add_argument(
        '--input-paths',
        type=arg_parsers.ArgList(min_length=1),
        required=True,
        help='Google Cloud Storage paths to the instances to run prediction on.'
        ' Wildcards accepted. Multiple paths can be specified if more than one '
        'file patterns are needed. Example: '
        'gs://my-bucket-0/instances0,gs://my-bucket-1/instances1')
    parser.add_argument(
        '--data-format',
        required=True,
        choices=['TEXT', 'TF_RECORD'],
        help='Data format of the input files.')
    parser.add_argument(
        '--output-path', required=True,
        help='Google Cloud Storage path to which to save the output. '
        'Example: gs://my-bucket/output.')
    parser.add_argument(
        '--region',
        required=True,
        help='The Google Compute Engine region to run the job in.')

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    job = jobs.BuildBatchPredictionJob(
        job_name=args.job,
        model_name=args.model,
        version_name=args.version,
        input_paths=args.input_paths,
        data_format=args.data_format,
        output_path=args.output_path,
        region=args.region)
    return jobs.Create(job)
