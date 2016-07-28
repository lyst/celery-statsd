import os
from setuptools import setup, find_packages


base_dir = os.path.dirname(__file__)

about = {}
with open(os.path.join(base_dir, 'celery_statsd', '__about__.py')) as f:
    exec(f.read(), about)


setup(
    name=about['__title__'],
    version=about['__version__'],

    description=about['__summary__'],
    license=about['__license__'],
    url=about['__uri__'],
    author=about['__author__'],
    author_email=about['__email__'],

    packages=find_packages(exclude=['tests']),
    zip_safe=False,
)
