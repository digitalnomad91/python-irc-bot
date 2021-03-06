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
"""Command group for ml versions."""

from googlecloudsdk.calliope import base


class Versions(base.Group):
  """Cloud ML Versions commands.

     A version is an implementation of a model. Each version is a trained
     TensorFlow graph that solves the problem posed by the model. You use
     version identifiers to track iterations of your model.

     When you communicate with Cloud ML services, you use the combination of
     the model, version, and currently project to identify a specific model
     implementation that is deployed in the cloud.
  """
  pass
