# coding:utf8

from util import *
import os
import traceback
from logger import log

# from lib.sshConn import controlHost
logger = log().getLogger()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJ_CONFIG_FILE = os.path.join(os.path.join(BASE_DIR, 'config'), 'config.cfg')
PROJ_CONFIG_OBJ = readConfig(PROJ_CONFIG_FILE)
BACKUP_AGENT_CONFIG = PROJ_CONFIG_OBJ.read_config("backup-agent")


class backup_agent_install:
    pkg_path = os.path.join(BASE_DIR, 'package')

    def __init__(self, sshObj):
        self.sshObj = sshObj
        self.result = u'主机%s正在部署备份代理:\n' % self.sshObj.host

    def __check_rsync(self):
        try:
            output = self.sshObj.exeCommand('/usr/local/rsync --help', timeout=5)
            if output["exit_code"] != 0:
                self.result += u'\trsync未安装!\n'
                return False
            else:
                self.result += u'\trsync已安装!\n'
                logger.info("rsync已安装")
                return True
        except Exception as e:
            traceback.print_exc()
            logger.warn(str(e))
            return False

    def __install_rsync(self):
        try:
            rsync_pkg = os.path.join(backup_agent_install.pkg_path, BACKUP_AGENT_CONFIG['rsync'])
            # print(rsync_pkg)
            tmp_dir = '/usr/local/src'
            # print(tmp_dir, 'tmp_dir')
            dst_mkdir = self.sshObj.exeCommand("mkdir -p %s" % tmp_dir)
            # print(dst_mkdir,  'dst_mkdir')
            dst_sftp_file = self.sshObj.sftpFile('%s.tar.gz' % rsync_pkg,
                                                 '/usr/local/src/%s.tar.gz' % BACKUP_AGENT_CONFIG['rsync'],
                                                 'push')  # 将安装包推送到目标主机
            # print(dst_sftp_file, 'dst_sftp_file')
            un_zip = self.sshObj.exeCommand("cd /usr/local/src; tar -zxf %s.tar.gz"
                                            % BACKUP_AGENT_CONFIG['rsync'])  # 解压包
            # print(un_zip, 'unzip')
            make_install = self.sshObj.exeCommand(
                "cd /usr/local/src/{rsync}; ./configure --prefix=/usr/local/{rsync}; make && make install".format(
                    rsync=BACKUP_AGENT_CONFIG['rsync']
                )
            )
            # print(make_install, 'make_install')
            dst_ln = self.sshObj.exeCommand(
                "ln -s /usr/local/{rsync}/bin/rsync /usr/local/rsync".format(rsync=BACKUP_AGENT_CONFIG['rsync'])
            )
            # print(dst_ln, 'dst_ln')
            self.result += u'\trsync已安装!\n'
            if all([dst_mkdir["status"], dst_sftp_file["status"], un_zip["status"], make_install["status"],
                    dst_ln["status"]]):
                logger.info(self.result)
                return True
            else:
                logger.warn("rsync安装失败")
                return False
        except:
            traceback.print_exc()
            logger.warn("rsync安装失败")
            return False

    def __check_sersync(self):
        try:
            output = self.sshObj.exeCommand("/usr/local/sersync/sersync2 -h", timeout=3)
            if output["exit_code"] != 0:
                self.result += u'\tsersync未安装!\n'
                return False
            else:
                self.result += u'\tsersync已安装!\n'
                logger.info("sersync已安装")
                return True
        except Exception as e:
            traceback.print_exc()
            logger.warn(str(e))
            return False

    def __install_sersync(self):
        try:
            sersync_pkg = os.path.join(backup_agent_install.pkg_path, BACKUP_AGENT_CONFIG['sersync'])
            tmp_dir = '/usr/local/src'
            dst_mkdir = self.sshObj.exeCommand("mkdir -p %s" % tmp_dir)
            # print(dst_mkdir, 'dst_mkdir')
            dst_sftp = self.sshObj.sftpFile('%s.tar.gz' % sersync_pkg,
                                            '/usr/local/src/%s.tar.gz' % BACKUP_AGENT_CONFIG['sersync'], 'push')
            # print(dst_sftp, 'dst_sftp')
            un_zip = self.sshObj.exeCommand('cd /usr/local/src; tar -zxvf %s.tar.gz' % BACKUP_AGENT_CONFIG['sersync'])
            # print(un_zip, 'un_zip')
            dst_ln = self.sshObj.exeCommand('ln -s /usr/local/src/GNU-Linux-x86/ /usr/local/sersync')
            # print(dst_ln, 'dst_ln')
            self.result += u'\tsersync已安装!\n'
            if all([dst_mkdir["status"], dst_sftp["status"], un_zip["status"], dst_ln["status"]]):
                logger.info(self.result)
                return True
            else:
                logger.warn("sersync安装失败")
                return False
        except:
            traceback.print_exc()
            logger.warn("sersync安装失败")
            return False

    def __check_xtrabackup(self):
        try:
            output = self.sshObj.exeCommand('/usr/local/percona-xtrabackup/bin/innobackupex --version', timeout=5)
            if output['exit_code'] != 0:
                self.result += '\txtrabackup未安装\n'
                return False
            else:
                self.result += '\txtrabackup已安装\n'
                logger.info("xtrabackup已安装")
                return True
        except Exception as e:
            traceback.print_exc()
            logger.warn(str(e))
            return False

    def __install_xtrabackup(self):
        try:
            xtrabackup_pkg = os.path.join(backup_agent_install.pkg_path, BACKUP_AGENT_CONFIG['xtrabackup'])
            tmp_dir = '/usr/local/src'
            # print(tmp_dir)
            dst_mkdir = self.sshObj.exeCommand("mkdir -p %s" % tmp_dir)
            # print(dst_mkdir, 'dst_mkdir')
            dst_sftp_file = self.sshObj.sftpFile('%s.tar.gz' % xtrabackup_pkg,
                                                 '/usr/local/src/%s.tar.gz' % BACKUP_AGENT_CONFIG['xtrabackup'], 'push')
            # print(dst_sftp_file, 'dst_sftp_file')
            un_zip = self.sshObj.exeCommand(
                "cd /usr/local/src; tar -zxvf %s.tar.gz" % BACKUP_AGENT_CONFIG['xtrabackup']
            )
            # print(un_zip, 'unzip')
            dst_ln = self.sshObj.exeCommand(
                'ln -s /usr/local/src/%s/  /usr/local/percona-xtrabackup' % BACKUP_AGENT_CONFIG['xtrabackup']
            )
            # print(dst_ln, 'dst_ln')
            self.result += '\txtrabackup已安装!'
            if all([dst_mkdir["status"], dst_sftp_file["status"], un_zip["status"], dst_ln["status"]]):
                logger.info(self.result)
                return True
            else:
                logger.warn("xtrabackup安装失败")
                return False
        except:
            traceback.print_exc()
            logger.warn("xtrabackup安装失败")
            return False

    def fs_backup_agent(self):
        if not self.__check_rsync():
            rsync = self.__install_rsync()
        else:
            rsync = True

        if not self.__check_sersync():
            sersync = self.__install_sersync()
        else:
            sersync = True

        result = {'rsync': rsync, 'sersync': sersync, 'msg': self.result}
        return result

    def db_backup_agent(self):
        if not self.__check_xtrabackup():
            print('wsgiaa')
            xtrabackup = self.__install_xtrabackup()
            print('222r')
        else:
            xtrabackup = True
        result = {'xtrabackup': xtrabackup, 'msg': self.result}
        return result


if __name__ == '__main__':
    pass
    # sshObj = controlHost('192.168.1.11', 'root', '123456', 22)
    # print(sshObj)
    # res = backup_agent_install(sshObj)

    # print(res.check_rsync())
    # print(res.install_rsync())

    # print(res.check_xtrabackup())
    # print(res.install_xtrabackup())

    # print(res.check_sersync())
    # print(res.install_sersync())

    # print(res.fs_backup_agent())
    # print(res.db_backup_agent())
    # print(res.result)
