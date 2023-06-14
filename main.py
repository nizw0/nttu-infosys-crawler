import json

import termcharts
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Middle, VerticalScroll
from textual.widget import Widget
from textual.widgets import (Button, Footer, Header, Input, LoadingIndicator, Pretty, Static)

from util import fetch_scores


class LoginForm(Widget):

    def compose(self) -> ComposeResult:
        with Middle():
            yield Input(id='username', placeholder='Username (Student ID)', classes='label')
            yield Input(id='password', placeholder='Password', password=True, classes='label')
            with Center():
                yield Button(id='login', label='Login', variant='primary')

    @on(Button.Pressed, '#login')
    def submit(self) -> None:
        username = self.query_one('#username').value
        password = self.query_one('#password').value
        if not username and not password:
            return
        with open('./config.json', 'w') as f:
            json.dump({'username': username, 'password': password}, f)


class CrawlerApp(App):
    TITLE = '校務系統成績抓抓'
    CSS_PATH = 'main.css'
    BINDINGS = [
        Binding(key='q', action='quit', description='Quit'),
        Binding(key='d', action='toggle_dark', description='Toggle dark mode'),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield LoadingIndicator()
        yield LoginForm()
        with VerticalScroll():
            with Center():
                yield Static(id='ranks')
                yield Static(id='scores')
                yield Static(id='credits')
                yield Pretty('')
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(LoadingIndicator).display = False
        self.query_one('#ranks').display = False
        self.query_one('#scores').display = False
        self.query_one('#credits').display = False
        self.query_one(Pretty).display = False

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    @on(Button.Pressed, '#login')
    def next(self) -> None:
        self.update_data()

    @work(exclusive=True)
    def update_data(self) -> None:
        self.query_one(LoadingIndicator).display = True
        self.query_one(LoginForm).display = False
        self.query_one('#ranks').display = False
        self.query_one('#scores').display = False
        self.query_one('#credits').display = False
        self.query_one(Pretty).display = False
        data = fetch_scores()
        ranks = termcharts.bar(dict((datum['semYear'], int(datum['sort'])) for datum in data), title='ranks')
        scores = termcharts.bar(dict((datum['semYear'], int(datum['avg_score'])) for datum in data), title='scores')
        credits = termcharts.bar(dict((datum['semYear'], int(datum['sum_credit'])) for datum in data), title='credits')
        self.call_from_thread(self.query_one(Pretty).update, data)
        self.call_from_thread(self.query_one('#ranks').update, ranks)
        self.call_from_thread(self.query_one('#scores').update, scores)
        self.call_from_thread(self.query_one('#credits').update, credits)

    def on_worker_state_changed(self, event) -> None:
        self.log(event)
        self.query_one('#ranks').display = True
        self.query_one('#scores').display = True
        self.query_one('#credits').display = True
        self.query_one(Pretty).display = True
        self.query_one(LoadingIndicator).display = False


if __name__ == '__main__':
    app = CrawlerApp()
    app.run()
