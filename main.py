"""
Questions:


    1. Complete the `MiniVenmo.create_user()` method to allow our application to create new users.

    2. Complete the `User.pay()` method to allow users to pay each other.
    Consider the following: if user A is paying user B, user's A balance should be used if
    there's enough balance to cover the whole payment,
    if not, user's A credit card should be charged instead.

    3. Venmo has the Feed functionality, that shows the payments that users have been doing in the app.
    If Bobby paid Carol $5, and then Carol paid Bobby $15, it should look something like this

    Bobby paid Carol $5.00 for Coffee
    Carol paid Bobby $15.00 for Lunch

    Implement the `User.retrieve_activity()` and `MiniVenmo.render_feed()` methods so the MiniVenmo application can render the feed.

    4. Now users should be able to add friends. Implement the `User.add_friend()` method to allow users to add friends.
    5. Now modify the methods involved in rendering the feed to also show when user's added each other as friends.
"""

"""
MiniVenmo! Imagine that your phone and wallet are trying to have a beautiful
baby. In order to make this happen, you must write a social payment app.
Implement a program that will feature users, credit cards, and payment feeds.
"""

from abc import ABC, abstractmethod
import re
import unittest
import uuid
from typing import List


class UsernameException(Exception):
    pass


class PaymentException(Exception):
    pass


class CreditCardException(Exception):
    pass


class Activity(ABC):
    @abstractmethod
    def to_string(self):
        pass


class User:
    def __init__(self, username):
        self.credit_card_number = None
        self.balance = 0.0
        self.activity: List[Activity] = []
        self.friends = []

        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException("Username not valid.")

    def retrieve_feed(self):
        return self.activity

    def add_friend(self, new_friend):
        self.friends.append(new_friend)
        self.activity.append(Friendship(self, new_friend))

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException("Only one credit card per user!")

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number

        else:
            raise CreditCardException("Invalid credit card number.")

    def pay(self, target, amount, note):
        try:
            return self.pay_with_balance(target, amount, note)
        except PaymentException:
            return self.pay_with_card(target, amount, note)

    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException("User cannot pay themselves.")

        elif amount <= 0.0:
            raise PaymentException("Amount must be a non-negative number.")

        elif self.credit_card_number is None:
            raise PaymentException("Must have a credit card to make a payment.")

        self._charge_credit_card(self.credit_card_number)

        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)
        self.activity.append(payment)

        return payment

    def pay_with_balance(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException("User cannot pay themselves.")

        elif amount <= 0.0:
            raise PaymentException("Amount must be a non-negative number.")

        elif self.balance <= 0:
            raise PaymentException("Not enough balance to pay.")

        self.balance -= amount

        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)
        self._add_activity(payment)

        return payment

    def _add_activity(self, activity: Activity):
        # this can be extended to support other types of activities, by providing an Activity base class for Payment
        self.activity.append(activity)

    @staticmethod
    def _is_valid_credit_card(credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    @staticmethod
    def _is_valid_username(username):
        return re.match("^[A-Za-z0-9_\\-]{4,15}$", username)

    @staticmethod
    def _charge_credit_card(credit_card_number):
        # magic method that charges a credit card thru the card processor
        pass


class Payment(Activity):
    def __init__(self, amount: float, actor: User, target: User, note: str):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note

    def to_string(self):
        feed = f"{self.actor.username} paid {self.target.username} ${self.amount}"
        feed += f" for {self.note}" if self.note else ""
        return feed


class Friendship(Activity):
    def __init__(self, actor: User, target: User):
        self.actor = actor
        self.target = target

    def to_string(self):
        return f"{self.actor.username} befriended {self.target.username}"


class MiniVenmo:
    @staticmethod
    def create_user(username, balance, credit_card_number):
        user = User(username)
        user.add_credit_card(credit_card_number)
        user.add_to_balance(float(balance))
        return user

    @staticmethod
    def render_feed(feed):
        for activity in feed:
            print(activity.to_string())

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")

            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")

            carol.add_friend(bobby)

        except PaymentException as e:
            print(e)

        venmo.render_feed(bobby.retrieve_feed())
        venmo.render_feed(carol.retrieve_feed())

        bobby.add_friend(carol)


class TestUser(unittest.TestCase):
    def test_this_works(self):
        with self.assertRaises(UsernameException):
            raise UsernameException()


if __name__ == "__main__":
    MiniVenmo.run()
    unittest.main()
