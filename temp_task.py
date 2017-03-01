#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lvkpi.settings")
    import django
    django.setup()

    from Statistics.functions import set_staff_daily_point
    set_staff_daily_point()