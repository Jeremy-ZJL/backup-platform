# coding:utf8

from lib.dbControl import dbControl
from django.http import HttpResponse
import json
from webadmins.settings import POOL
from webadmins.settings import LOGGER

# import os
# import sys
# import traceback
# from django.http import HttpResponseRedirect
# from webadmins.settings import PROJ_LIB_DIR
# sys.path.insert(0, PROJ_LIB_DIR)

try:
    from django.utils.deprecation import MiddlewareMixin
except:
    MiddlewareMixin = object


class midware_db(MiddlewareMixin):
    def process_request(self, request):
        db = dbControl(POOL)
        request.META['db'] = db
        print(db, '--process_request--')

    def process_response(self, request, response):
        db = request.META.get('db', '')
        if hasattr(db, "close"):
            db.close()
        return response


class midware_logger(MiddlewareMixin):
    def process_request(self, request):
        request.META["logger"] = LOGGER
        print(LOGGER, '--logger process request--')


class midware_force_login(MiddlewareMixin):
    def process_request(self, request):
        result = {}
        um_account = request.session.get("um_account")
        print(um_account, '--um_account--')

        path_info = request.META.get("PATH_INFO")
        if path_info == "/":  # 说明是/
            pass
        elif path_info.endswith('logout'):
            pass
        elif path_info.endswith("login"):
            pass
        else:
            if not um_account:
                result["code"] = 401
                result["message"] = "平台API未成功鉴权!"
                return HttpResponse(status=404, content=json.dumps(result))
