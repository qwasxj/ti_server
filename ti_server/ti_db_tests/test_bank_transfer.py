#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import unittest


class TestBankTransfer(unittest.TestCase):

    def __init__(self, db, log):
        super(TestBankTransfer, self).__init__("test_bank_transfer")
        self.db = db
        self.cursor = db.cursor()
        self.log = log
        self.log.info("get db instance %s" % db)

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

    def test_bank_transfer(self):
        # transfer 30 from u1 to u2
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
        self.assertEqual(
            u1_balance, 20, "user balance should be 20, not: %s" % u1_balance
        )
        self.assertEqual(
            u2_balance, 30, "user balance should be 20, not: %s" % u2_balance
        )
        self.log.info("bank transfer test successfully..")
