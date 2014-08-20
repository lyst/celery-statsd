from __future__ import absolute_import

import mock

import celery

import pytest

import celery_statsd


@celery.task
def _stub_task(arg):
    return arg


celery.current_app.conf.CELERY_ALWAYS_EAGER = True

def test_enqueue(monkeypatch):
    mock_client = mock.Mock()

    def _get_mock_client(app):
        return mock_client

    monkeypatch.setattr(celery_statsd, "get_client", _get_mock_client)
    result = _stub_task.delay(1)

    print mock_client.incr.mock_calls
    print mock_client.timing.mock_calls

    mock_client.timing.assertCalledWith("tests.test_celery_statsd._stub_task.enqueue")
    mock_client.incr.assertCalledWith("tests.test_celery_statsd._stub_task.success")



def test_run(monkeypatch):
    pass
