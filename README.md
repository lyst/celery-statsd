celery-statsd
=============

# Installation

```
pip install celery-statsd
```

# Set Up

In your `tasks.py`

```python
import celery_statsd
```

And in your settings file set `STATSD_HOST` and `STATSD_PORT`.

You will now have stats about your tasks in statsd.

By default stats will be published with a key prefix of "celery.". Change the CELERY_STATSD_PREFIX
if you want something different.
