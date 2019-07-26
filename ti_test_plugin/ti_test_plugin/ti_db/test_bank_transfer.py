#! /usr/bin/env python
# -*-- coding: utf-8 -*-

import unittest

from ti_test_plugin.ti_test_plugin.common.bank_transfer import BankTransfer


class BankExchangeTest(unittest.TestCase):

    def setUp(self):
        self.bank_transfer_amount = 10

    def tearDown(self):
        pass

    def test_bank_exchange(self, ti_db):
        balance_before = ti_db.query("")
        if balance_before >= self.bank_transfer_amount:
            BankTransfer(ti_db).bank_transfer(self.bank_transfer_amount)
            balance_after = ti_db.query("")
            self.assertEqual(
                balance_after, balance_before - self.bank_transfer_amount
            )
        else:
            self.assertRaises(
                BankTransfer(ti_db).bank_transfer(self.bank_transfer_amount),
                Exception
            )
