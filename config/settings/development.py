from .base import *  # noqa: F403,F401

DEBUG = True
if ENABLE_DEMO_UI:
    INSTALLED_APPS += ["apps.demo"]  # noqa: F405
