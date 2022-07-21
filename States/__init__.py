from aiogram.dispatcher.filters.state import StatesGroup, State


class CurrentForm(StatesGroup):
    city: State = State()


class DailyForm(StatesGroup):
    city: State = State()
