import typing as tp
from decimal import Decimal

from .exceptions import SplitViseException
from .models import User, Expense, Trip, Debt, Event, Summary
from .models.base import Session

MoneyType = Decimal


# type: ignore

def create_user(
        username: str,
        *,
        session: Session
) -> User:
    """
    Create new User; validate user exists
    :param username: username to create
    :param session: active session to perform operations with
    :return: orm User object
    :exception: username already taken
    """
    existing_user = session.query(User).filter(User.username == username).first()  # type: ignore
    if existing_user:
        raise SplitViseException("Username already taken")

    new_user = User(username=username)
    session.add(new_user)
    session.commit()

    return new_user


def create_event(
        trip_id: int,
        people_debt: tp.Mapping[int, MoneyType],
        people_payment: tp.Mapping[int, MoneyType],
        title: str,
        *,
        session: Session
) -> Event:
    """
    Create Event in database, automatically creates Debts and Expenses; validates sum
    :param trip_id: Trip.trip_id from the database
    :param people_debt: mapping of User.user_id to theirs debt in that event
    :param people_payment: mapping of User.user_id to theirs payments in that event
    :param title: title of the event
    :param session: active session to perform operations with
    :return: orm Event object
    :exception: Trip not found by id, Can not create debt for user not in trip,
                Can not create payment for user not in trip, Sum of debts and sum of payments are not equal
    """
    trip = session.query(Trip).filter_by(trip_id=trip_id).first()
    if not trip:
        raise SplitViseException("Trip not found by id")

    users_in_trip = [user.user_id for user in trip.users]
    for user_id in people_payment.keys():
        if user_id not in users_in_trip:
            raise SplitViseException("Can not create payment for user not in trip")

    for user_id in people_debt.keys():
        if user_id not in users_in_trip:
            raise SplitViseException("Can not create debt for user not in trip")

    event = Event(trip_id=trip_id, title=title)
    session.add(event)
    session.flush()

    for debtor_id, value in people_debt.items():
        debt = Debt(event_id=event.event_id, debtor_id=debtor_id, value=value)
        session.add(debt)

    for payer_id, value in people_payment.items():
        expense = Expense(event_id=event.event_id, payer_id=payer_id, value=value)
        session.add(expense)

    sum_debts = sum(people_debt.values())
    sum_payments = sum(people_payment.values())
    if sum_debts != sum_payments:
        raise SplitViseException("Sum of debts and sum of payments are not equal")

    session.commit()
    return event


def create_trip(
        creator_id: int,
        title: str,
        description: str,
        *,
        session: Session
) -> Trip:
    """
    Create Trip. Automatically add creator to the trip. Validate input: the title should not be empty and the creator
    should exist in the users table
    :param creator_id: User.user_id from the database to create trip by
    :param title: Title of the trip
    :param description: Long (or not so long) description of the trip
    :param session: active session to perform operations with
    :return: orm Trip object
    :exception: Title of a trip should not be empty, User not found by id
    """
    if not title:
        raise SplitViseException("Title of a trip should not be empty")

    creator = session.query(User).filter(User.user_id == creator_id).first()
    if not creator:
        raise SplitViseException("User not found by id")
    new_trip = Trip(title=title, description=description)
    new_trip.users.append(creator)
    session.add(new_trip)
    session.commit()

    return new_trip


def add_user_to_trip(
        guest_id: int,
        trip_id: int,
        *,
        session: Session
) -> None:
    """
    Mark that the user with guest_id takes part in the trip. Check that the user and the trip do exist and the user has
    not been added to the trip yet.
    :param guest_id: User.user_id from the database to add to the trip
    :param trip_id: Trip.trip_id from the database
    :param session: active session to perform operations with
    :return: None
    :exception: Trip not found by id, User already in trip
    """
    trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise SplitViseException("Trip not found by id")

    guest = session.query(User).filter(User.user_id == guest_id).first()
    if not guest:
        raise SplitViseException("Guest not found by id")

    if guest in trip.users:
        raise SplitViseException("Guest already in trip")

    trip.users.append(guest)
    session.commit()


def get_trip_users(
        trip_id: int,
        *,
        session: Session
) -> list[User]:
    """
    Get Users from Trip; validate Trip exists
    :param trip_id: Trip.trip_id from the database
    :param session: active session to perform operations with
    :return: list of orm User objects
    :exception: Trip not found by id
    """
    trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise SplitViseException("Trip not found by id")

    return trip.users


def make_summary(
        trip_id: int,
        *,
        session: Session
) -> None:
    """
    Make trip summary. Mark all the events of the trip as settled up. Validate at least the existence of the trip
    being calculated
    :param trip_id: Trip.trip_id from the database
    :param session: active session to perform operations with
    :return: None
    :exception: Trip not found by id
    """
    trip = session.query(Trip).filter_by(trip_id=trip_id).first()  # type: ignore
    if not trip:
        raise SplitViseException("Trip not found by id")

    events = session.query(Event).filter_by(trip_id=trip_id).all()
    for event in events:
        event.settled_up = True

    summaries = []
    deltas = {}

    for user in trip.users:
        user_id = user.user_id
        debts = session.query(Event, Debt). \
            join(Debt, Debt.event_id == Event.event_id). \
            filter(Event.trip_id == trip_id, Debt.debtor_id == user_id, Event.settled_up).all()

        expenses = session.query(Event, Expense). \
            join(Expense, Expense.event_id == Event.event_id). \
            filter(Event.trip_id == trip_id, Expense.payer_id == user_id, Event.settled_up).all()

        total_debts = sum(debt[1].value for debt in debts)
        total_expenses = sum(expense[1].value for expense in expenses)

        deltas[user_id] = total_expenses - total_debts

    for user in trip.users:
        user_id = user.user_id
        if user_id not in deltas:
            continue
        delta = deltas[user_id]
        if delta < 0:
            for userTo in deltas.keys():
                delta_to = deltas[userTo]
                if delta_to > 0:
                    summaries.append(Summary(trip_id=trip_id, user_from_id=user_id, user_to_id=userTo,
                                             value=max(delta, -delta_to)))
    session.add_all(summaries)
    session.commit()
