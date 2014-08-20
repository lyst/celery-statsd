celery-statsd
=============

In your `tasks.py`

```python
import celery_statsd
```

And in your settings file set `STATSD_HOST` and `STATSD_PORT`.

You will now have stats about your tasks in statsd.
