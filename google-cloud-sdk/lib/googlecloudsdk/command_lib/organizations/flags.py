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
"""Flags for commands that deal with Organizations."""
from googlecloudsdk.calliope import base


ORGS_COLLECTION = 'cloudresourcemanager.organizations'


def OrgArg(description):
  return base.Argument(
      '--organization',
      required=False,
      metavar='ORGANIZATION_ID',
      completion_resource=ORGS_COLLECTION,
      list_command_path='organizations',
      help='ID for the organization {0}'.format(description))


def IdArg(description):
  return base.Argument(
      'id',
      metavar='ORGANIZATION_ID',
      completion_resource=ORGS_COLLECTION,
      list_command_path='organizations',
      help='ID for the organization {0}'.format(description))
