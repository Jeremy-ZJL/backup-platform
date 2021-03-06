from django.conf import settings
from lib.sshConn import controlHost
from lib.db_backup_tools import db_xtrabackup
from lib.backup_agent_install import backup_agent_install
from lib.dbControl import dbControl
from lib.fs_backup_tools import distribute_filesystem_backup
from lib.util import *
import traceback
import pymysql
import os

# import time
# import sys
# PROJ_LIB_DIR = settings.PROJ_LIB_DIR
# sys.path.insert(0, PROJ_LIB_DIR)


app = settings.CELERY
logger = settings.LOGGER
PROJ_DB_CONFIG = settings.PROJ_DB_CONFIG
POOL = settings.POOL


class MyTask(app.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        db = dbControl(POOL)
        try:
            db.select_database(PROJ_DB_CONFIG["database"]).select_table("backup_task_history")\
                .set({"message": pymysql.escape_string(str(einfo))}).where({"task_id": task_id}).update()
        except Exception as e:
            logger.warn(str(e))
        finally:
            db.close()

    def on_success(self, retval, task_id, args, kwargs):
        db = dbControl(POOL)
        try:
            db.select_database(PROJ_DB_CONFIG["database"]).select_table("backup_task_history")\
                .where({"task_id": task_id})\
                .set({"task_status": 1, "message": pymysql.escape_string(str(retval))}).update()
        except Exception as e:
            traceback.print_exc()
            logger.warn(str(e))
        finally:
            db.close()


@app.task(base=MyTask)
def celery_database_full_backup(cmdb_host_info, db_conn_info, backup_to_local_path, timestamp):
    sshObj = controlHost(cmdb_host_info["source_addr"],
                         cmdb_host_info["host_user"],
                         cmdb_host_info["host_passwd"],
                         cmdb_host_info["host_port"])
    db_info = {}
    db_info.update(db_conn_info)
    db_info["my_files"] = db_conn_info["db_conf"]
    db_info["db_host"] = db_conn_info["source_addr"]
    xObj = db_xtrabackup(sshObj, db_info)
    result = xObj.xtrabackup_full_backup(backup_to_local_path, timestamp)  # 此处备份失败会raise一个错误出来!
    sshObj.close()
    return result


@app.task(base=MyTask)
def celery_filesystem_agent_install(cmdb_host_info, svc_type):
    result = ''
    db = dbControl(POOL)
    sshObj = controlHost(cmdb_host_info["source_addr"],
                         cmdb_host_info["host_user"],
                         cmdb_host_info["host_passwd"],
                         cmdb_host_info["host_port"],)
    if svc_type == 'fs':
        data = {"rsync_status": 1, "sersync_status": 1}
        fs_agent_install = backup_agent_install(sshObj)  # celery
        res = fs_agent_install.fs_backup_agent()
        result += res["msg"]

    elif svc_type == 'db':
        data = {"xtrabackup_status": 1}
        db_agent_install = backup_agent_install(sshObj)  # celery
        res = db_agent_install.db_backup_agent()
        result += res["msg"]

    elif svc_type == "all":
        data = {"rsync_status": 1, "sersync_status": 1, "xtrabackup_status": 1}
        fs_agent_install = backup_agent_install(sshObj)  # celery
        res1 = fs_agent_install.fs_backup_agent()
        result += res1["msg"]

        db_agent_install = backup_agent_install(sshObj)  # celery
        res2 = db_agent_install.db_backup_agent()
        result += res2["msg"]
    else:
        data = {}
    try:
        db.select_database(PROJ_DB_CONFIG["database"]).select_table("backup_host_manager")\
            .where({"source_addr": cmdb_host_info["source_addr"]}).set(data).update()
    except Exception as e:
        logger.warn(str(e))
    finally:
        if hasattr(sshObj, "close"):
            sshObj.close()
    return result


@app.task(base=MyTask)
def celery_filesystem_full_backup(cmdb_host_info, backup_path, backup_to_local_path, action):
    result = ''
    db = dbControl(POOL)
    sshObj = controlHost(cmdb_host_info["source_addr"],
                         cmdb_host_info["host_user"],
                         cmdb_host_info["host_passwd"],
                         cmdb_host_info["host_port"])
    d = distribute_filesystem_backup(sshObj,
                                     cmdb_host_info["source_addr"],
                                     backup_path,
                                     backup_to_local_path)
    if action == "start":
        data = {"backup_status": 2}
        db.select_database(PROJ_DB_CONFIG["database"]).select_table("filesystem_backup_task")\
            .where({"source_addr": cmdb_host_info["source_addr"],
                    "backup_path": backup_path,
                   "backup_to_local_path": backup_to_local_path}).set(data).update()
        result = d.fs_backup_start()  # celery
        data = {"backup_status": 1}
        db.select_database(PROJ_DB_CONFIG["database"]).select_table("filesystem_backup_task")\
            .where({"source_addr": cmdb_host_info["source_addr"],
                    "backup_path": backup_path,
                   "backup_to_local_path": backup_to_local_path}).set(data).update()

    elif action == "stop":
        result = d.fs_backup_stop()
        data = {"backup_status": 0}
        db.select_database(PROJ_DB_CONFIG["database"]).select_table("filesystem_backup_task")\
            .where({"source_addr": cmdb_host_info["source_addr"],
                    "backup_path": backup_path,
                   "backup_to_local_path": backup_to_local_path}).set(data).update()

    elif action == "fs_full_backup":
        today = ControlTime.date_today(_format="%Y%m%d%H%M%S")[0]
        fs_full_backup_path = list(backup_to_local_path.partition(cmdb_host_info["source_addr"]))
        fs_full_backup_path[1] = os.path.join(fs_full_backup_path[1], 'filesystem_full_backup')
        fs_full_backup_path.append('/%s' % today)
        fs_full_backup_path = ''.join(fs_full_backup_path)
        task_id = celery_filesystem_full_backup.request.id
        db.select_database(PROJ_DB_CONFIG["database"]).select_table("backup_task_history").where({"task_id": task_id})\
            .set({"backup_path": backup_to_local_path,
                  "backup_to_local_path": fs_full_backup_path}).update()

        result = d.fs_full_backup(backup_to_local_path, fs_full_backup_path)  # celery

    if hasattr(sshObj, "close"):
        sshObj.close()
    return result
