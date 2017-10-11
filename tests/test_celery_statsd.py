from __future__ import absolute_import

import celery

import mock

import celery_statsd

import pytest


celery.current_app.conf.CELERY_ALWAYS_EAGER = True


@celery.task
def _stub_task(arg):
    return arg


@celery.task(bind=True, max_retries=2)
def _stub_task_with_retries(self, arg):
    self.retry()


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


def test_run_with_retry(mock_client, monkeypatch):
    task = _stub_task_with_retries
    task.apply_async = mock.Mock(wraps=_stub_task_with_retries.apply_async)

    get_timer_mock = mock.Mock(wraps=celery_statsd._get_timer)

    monkeypatch.setattr('celery_statsd._get_timer', get_timer_mock)

    task.delay(1)

    # Only one call to the timing (the last task)
    assert mock_client.timing.call_count == 1

    # The name of the metric does not change among retried tasks
    mock_client.timing.assert_called_with(
        "celery.tests.test_celery_statsd._stub_task_with_retries.run",
        mock.ANY)

    # We get the timer 3 times
    assert get_timer_mock.call_count == 3
