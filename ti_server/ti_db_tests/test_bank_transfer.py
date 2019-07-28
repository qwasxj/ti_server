#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import unittest

from ti_server.service_api.ti_db_api import TiDBService


class TestBankTransfer(unittest.TestCase):

    def __int__(self):
        super(TestBankTransfer, self).__init__("bank_transfer")
        self.db = None

    def setUp(self):
        self.db = TiDBService().ti_db
        # create two new balance table of two test user
        self.db.cursor("create table ti_user1(balance int, user char(20)")
        self.db.cursor("create table ti_user2(balance int, user char(20))")
        # set user balance, user1: 50, user2: 0
        self.db.cursor("insert into ti_user1(balance, user) values (50, u1)")
        self.db.cursor("insert into ti_user2(balance, user) values (00, u2)")

    def tearDown(self):
        self.db.cursor("drop table ti_user1")
        self.db.cursor("drop table ti_user2")
        self.db.close()

    def test_bank_transfer(self):
        # transfer 30 from u1 to u2
        self.db.cursor(
            "update ti_user1 set balance = balance - 30 where user = u1"
        )
        self.db.cursor(
            "update ti_user2 set balance = balance + 30 where user = u2"
        )
        # judge if result expected or not
        u1_balance = \
            self.db.cursor("select balance from ti_user1 where user = u1")
        u2_balance = \
            self.db.cursor("select balance from ti_user1 where user = u2")
        self.assertEqual(
            u1_balance, 20, "user balance should be 20, not: %s" % u1_balance
        )
        self.assertEqual(
            u2_balance, 30, "user balance should be 20, not: %s" % u1_balance
        )
