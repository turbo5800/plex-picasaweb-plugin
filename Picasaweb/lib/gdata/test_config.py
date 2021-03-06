#!/usr/bin/env python

# Copyright (C) 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import gdata.test_config_template
import atom.mock_http_core


"""Loads configuration for tests which connect to Google servers.

The test_config_template.py is an example of the settings used in the tests.
Copy the test_config_template and insert your own values if you want to run
the tests which communicate with the servers. Change the import above and 
settings assignment below to use your own test configuration.
"""


settings = gdata.test_config_template


def configure_client(client, config, case_name):
  """Sets up a mock client which will reuse a saved session.

  Should be called during setUp of each unit test.

  Handles authentication to allow the GDClient to make requests which
  require an auth header.

  Args:
    client: a gdata.GDClient whose http_client member should be replaced
            with a atom.mock_http_core.MockHttpClient so that repeated
            executions can used cached responses instead of contacting
            the server.
    config: a dict of test specific settings from the gdata.test_config
            module. Examples can be found in gdata.test_config_template
            look at BloggerConfig and ContactsConfig.
    case_name: str The name of the test case class. Examples: 'BloggerTest',
               'ContactsTest'. Used to save a session
               for the ClientLogin auth token request, so the case_name
               should be reused if and only if the same username, password,
               and service are being used.
  """
  # Use a mock HTTP client which will record and replay the HTTP traffic
  # from these tests.
  client.http_client = atom.mock_http_core.MockHttpClient()
  client.http_client.cache_case_name = case_name
  # Getting the auth token only needs to be done once in the course of test
  # runs.
  if config.auth_token is None:
    client.http_client.cache_test_name = 'client_login'
    cache_name = client.http_client.get_cache_file_name()
    if settings.CLEAR_CACHE:
      client.http_client.delete_session(cache_name)
    client.http_client.use_cached_session(cache_name)
    config.auth_token = client.request_client_login_token(
        config.email(), config.password(), config.service, case_name)
    client.http_client.close_session()
  client.auth_token = config.auth_token


def configure_cache(client, test_name):
  """Loads or begins a cached session to record HTTP traffic.

  Should be called at the beginning of each test method.

  Args:
    client: a gdata.GDClient whose http_client member has been replaced
            with a atom.mock_http_core.MockHttpClient so that repeated
            executions can used cached responses instead of contacting
            the server.
    test_name: str The name of this test method. Examples: 
               'TestClass.test_x_works', 'TestClass.test_crud_operations'.
               This is used to name the recording of the HTTP requests and
               responses, so it should be unique to each test method in the
               test case.
  """
  # Auth token is obtained in configure_client which is called as part of
  # setUp.
  client.http_client.cache_test_name = test_name
  cache_name = client.http_client.get_cache_file_name()
  if settings.CLEAR_CACHE:
    client.http_client.delete_session(cache_name)
  client.http_client.use_cached_session(cache_name)


def close_client(client):
  """Saves the recoded responses to a temp file if the config file allows.
  
  This should be called in the unit test's tearDown method.

  Checks to see if settings.CACHE_RESPONSES is True, to make sure we only
  save sessions to repeat if the user desires.
  """
  if client and settings.CACHE_RESPONSES:
    # If this was a live request, save the recording.
    client.http_client.close_session()


def configure_service(service, config, case_name):
  """Sets up a mock GDataService v1 client to reuse recorded sessions.
  
  Should be called during setUp of each unit test. This is a duplicate of
  configure_client, modified to handle old v1 service classes.
  """
  service.http_client.v2_http_client = atom.mock_http_core.MockHttpClient()
  service.http_client.v2_http_client.cache_case_name = case_name
  # Getting the auth token only needs to be done once in the course of test
  # runs.
  if config.auth_token is None:
    service.http_client.v2_http_client.cache_test_name = 'client_login'
    cache_name = service.http_client.v2_http_client.get_cache_file_name()
    if settings.CLEAR_CACHE:
      service.http_client.v2_http_client.delete_session(cache_name)
    service.http_client.v2_http_client.use_cached_session(cache_name)
    service.ClientLogin(config.email(), config.password(), 
                        service=config.service, source=case_name)
    config.auth_token = service.GetClientLoginToken()
    service.http_client.v2_http_client.close_session()
  if isinstance(config.auth_token, gdata.gauth.ClientLoginToken):
    service.SetClientLoginToken(config.auth_token.token_string)
  else:
    service.SetClientLoginToken(config.auth_token)


def configure_service_cache(service, test_name):
  """Loads or starts a session recording for a v1 Service object.
  
  Duplicates the behavior of configure_cache, but the target for this
  function is a v1 Service object instead of a v2 Client.
  """
  service.http_client.v2_http_client.cache_test_name = test_name
  cache_name = service.http_client.v2_http_client.get_cache_file_name()
  if settings.CLEAR_CACHE:
    service.http_client.v2_http_client.delete_session(cache_name)
  service.http_client.v2_http_client.use_cached_session(cache_name)


def close_service(service):
  if service and settings.CACHE_RESPONSES:
    # If this was a live request, save the recording.
    service.http_client.v2_http_client.close_session()

