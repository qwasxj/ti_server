#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import re
import unittest


class TestBankTransfer(unittest.TestCase):
    
    PD_STRING = "pingcap/pd"

    def __init__(self, db, log, func_util):
        super(TestBankTransfer, self).__init__("test_bank_transfer")
        self.db = db
        self.cursor = db.cursor()
        self.log = log
        self.base_func = func_util
        self.log.info("get db instance %s" % db)
        self.__some_pd_docker_id = ""

    def setUp(self):
        self.log.info("execute test set_up to build balance table.")
        self.cursor.execute(
            'drop table if exists ti_user1'
        )
        self.cursor.execute(
            'drop table if exists ti_user2'
        )
        # create two new balance table of two test user
        self.cursor.execute(
            'create table ti_user1(balance int, user char(20))'
        )
        self.cursor.execute(
            'create table ti_user2(balance int, user char(20))'
        )
        # set user balance, user1: 50, user2: 0
        self.log.info("balance of user1 50$ and 0 for user2")
        self.cursor.execute(
            'insert into ti_user1(balance, user) values (50, "u1")'
        )
        self.cursor.execute(
            'insert into ti_user2(balance, user) values (00, "u2")'
        )
        self.db.commit()
        self.log.info("balance table build successfully.")
        
    def tearDown(self):
        self.log.info("execute test tear_down to drop balance table.")
        self.cursor.execute('drop table ti_user1')
        self.cursor.execute('drop table ti_user2')
        self.db.commit()
        self.log.info("drop balance table successfully.")
        
    def get_some_pd_docker_id(self):
        ps_cmd = "docker ps"
        code, output = self.base_func.exe_cmd(ps_cmd)
        if code:
            self.log.info(
                "execute cmd: %s to get pd docker id failed. code: %s, error: "
                "%s" % (ps_cmd, code, output[1])
            )
            raise Exception(
                "execute cmd: %s to get pd docker id failed. code: %s, error: "
                "%s" % (ps_cmd, code, output[1])
            )
        self.log.info("output[0]: %s type: %s" % (output[0], type(output[0])))
        container_ifs = output[0].decode("utf-8").split("\n")
        for container_info in container_ifs:
            if self.PD_STRING in container_info:
                pd_container_id = re.split(r"\s+", container_info)[0]
                self.log.info("get pd container id: %s" % pd_container_id)
                return pd_container_id
        raise Exception("there is not ti pd running in docker container.")
    
    def stop_pd_docker(self, pd_container_id):
        stop_cmd = "docker stop %s" % pd_container_id
        code, output = self.base_func.exe_cmd(stop_cmd)
        if code:
            self.log.info(
                "execute cmd: %s to stop pd container: %s failed. code: %s, "
                "error: %s" % (stop_cmd, pd_container_id, code, output[1])
            )
            raise Exception(
                "execute cmd: %s to stop pd container: %s failed. code: %s, "
                "error: %s" % (stop_cmd, pd_container_id, code, output[1])
            )
        self.log.info("stop pd container: %s successfully." % pd_container_id)
        
    def start_pd_docker(self, pd_container_id):
        start_cmd = "docker start %s" % pd_container_id
        code, output = self.base_func.exe_cmd(start_cmd)
        if code:
            self.log.info(
                "execute cmd: %s to start pd container: %s failed. code: %s, "
                "error: %s" % (start_cmd, pd_container_id, code, output[1])
            )
            raise Exception(
                "execute cmd: %s to start pd container: %s failed. code: %s, "
                "error: %s" % (start_cmd, pd_container_id, code, output[1])
            )
        self.log.info("start pd container: %s successfully." % pd_container_id)

    def test_bank_transfer(self):
        # stop some pd to test tiDB stability
        self.__some_pd_docker_id = self.get_some_pd_docker_id()
        self.stop_pd_docker(self.__some_pd_docker_id)
        # transfer 30 from u1 to u2
        self.log.info("user1 transfer 30$ to user2..")
        self.cursor.execute(
            'update ti_user1 set balance = balance - 30 where user = "u1"'
        )
        self.cursor.execute(
            'update ti_user2 set balance = balance + 30 where user = "u2"'
        )
        self.db.commit()
        # judge if result expected or not
        self.cursor.execute(
            'select balance from ti_user1 where user = "u1"'
        )
        u1_balance = self.cursor.fetchall()[0][0]
        self.cursor.execute(
            'select balance from ti_user2 where user = "u2"'
        )
        u2_balance = self.cursor.fetchall()[0][0]
        self.log.info("now user1 balance is: %s and user2: %s after transfer"
                      % (u1_balance, u2_balance))
        self.assertEqual(
            u1_balance, 20, "user balance should be 20, not: %s" % u1_balance
        )
        self.assertEqual(
            u2_balance, 30, "user balance should be 20, not: %s" % u2_balance
        )
        self.log.info("bank transfer test successfully..")
        self.start_pd_docker(self.__some_pd_docker_id)
