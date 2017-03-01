# -*- coding: UTF-8 -*-
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lvkpi.settings")
    import django
    django.setup()

    from kpi.functions import NatureChangeCheck
    from Statistics.functions import set_staff_daily_point
    
    # 生成每天的员工贡献点记录
    set_staff_daily_point()
    
    # 检查是否该触动贡献点自然增长
    NatureChangeCheck()
