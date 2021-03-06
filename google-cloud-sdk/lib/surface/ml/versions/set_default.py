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
"""ml versions set-default command."""

from googlecloudsdk.api_lib.ml import versions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ml import flags


class BetaSetDefault(base.DescribeCommand):
  """Sets an existing Cloud ML version as the default for its model.

     *{command}* sets an existing Cloud ML version as the default for its model.
     Only one version may be the default for a given version.
  """

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.GetModelName(positional=False, required=True).AddToParser(parser)
    flags.VERSION_NAME.AddToParser(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    return versions.SetDefault(args.model, args.version)
