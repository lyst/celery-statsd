from __future__ import absolute_import

import threading
import time

import celery
import celery.signals

import statsd

_state = threading.local()


def task_key(task):
    prefix = getattr(celery.current_app.conf,
                     "CELERY_STATSD_PREFIX", "celery.")

    if isinstance(task, str):
        return prefix + task
    else:
        return prefix + task.name


def get_client(celery_app):
    try:
        client = _state.clients[celery_app]
    except AttributeError:
        client = statsd.StatsClient(
            celery_app.conf.STATSD_HOST,
            celery_app.conf.STATSD_PORT
        )

        _state.clients = {celery_app: client}
    except KeyError:
        client = statsd.StatsClient(
            celery_app.conf.STATSD_HOST,
            celery_app.conf.STATSD_PORT
        )

        _state.clients[celery_app] = client

    return client


def start_timer(name, group, instance):
    try:
        assert (name, group, instance) not in _state.timers
        _state.timers[(name, group, instance)] = time.time()
    except AttributeError:
        _state.timers = {(name, group, instance): time.time()}


def stop_timer(name, group, instance):
    total = time.time() - _state.timers.pop((name, group, instance))

    get_client(celery.current_app).timing(
        "{0}.{1}".format(group, name),
        total * 1000
    )


def inc_counter(name, group):
    get_client(celery.current_app).incr("{0}.{1}".format(group, name))


@celery.signals.before_task_publish.connect
def statsd_before_task_publish(sender, body, **kwargs):
    start_timer("enqueue", task_key(sender), body['id'])


@celery.signals.after_task_publish.connect
def statsd_after_task_publish(sender, body, **kwargs):
    stop_timer("enqueue", task_key(sender), body['id'])


@celery.signals.task_prerun.connect
def statsd_task_prerun(sender, task_id, **kwargs):
    start_timer("run", task_key(sender), task_id)


@celery.signals.task_postrun.connect
def statsd_task_postrun(sender, task_id, **kwargs):
    stop_timer("run", task_key(sender), task_id)


@celery.signals.task_retry.connect
def statsd_task_retry(sender, **kwargs):
    inc_counter("retry", task_key(sender))


@celery.signals.task_success.connect
def statsd_task_success(sender, **kwargs):
    inc_counter("success", task_key(sender))


@celery.signals.task_failure.connect
def statsd_task_failure(sender, **kwargs):
    inc_counter("failure", task_key(sender))


@celery.signals.task_revoked.connect
def statsd_task_revoked(sender, **kwargs):
    inc_counter("revoked", task_key(sender))
