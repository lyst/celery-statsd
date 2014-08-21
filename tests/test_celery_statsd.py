from __future__ import absolute_import

import mock

import celery

import pytest

import celery_statsd


celery.current_app.conf.CELERY_ALWAYS_EAGER = True


@celery.task
def _stub_task(arg):
    return arg


@pytest.fixture
def mock_client(monkeypatch):
    mock_client = mock.Mock()

    def _get_mock_client(app):
        return mock_client

    monkeypatch.setattr(celery_statsd, "get_client", _get_mock_client)

    return mock_client


def test_run(mock_client):
    assert _stub_task.delay(1)

    mock_client.timing.assert_called_with(
        "celery.tests.test_celery_statsd._stub_task.run", mock.ANY)
    mock_client.incr.assert_called_with(
        "celery.tests.test_celery_statsd._stub_task.success")
