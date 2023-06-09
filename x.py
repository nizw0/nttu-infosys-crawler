from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import (Center, Container, HorizontalScroll, Middle, VerticalScroll)
from textual.widgets import (Button, ContentSwitcher, Footer, Header, Input, LoadingIndicator, ProgressBar, Static)


class LoginForm(Container):

    def compose(self) -> ComposeResult:
        with Middle():
            yield Input(placeholder='Username (Student ID)', classes='label')
            yield Input(placeholder='Password', password=True, classes='label')
            with Center():
                yield Button(id='login', label='Login', variant='primary')


class Loading(Container):

    def compose(self) -> ComposeResult:
        yield LoadingIndicator()

    async def on_render(self) -> None:
        await self.app.action_quit()


class Result(Container):

    def compose(self) -> ComposeResult:
        yield Static('finish')
        yield Button(label='Close', variant='success')

    async def on_button_pressed(self) -> None:
        await self.app.action_quit()


class Switcher(Container):

    def compose(self) -> ComposeResult:
        with ContentSwitcher(initial='LoginForm'):
            yield LoginForm(id='LoginForm')
            yield Loading(id='Loading')
            yield Result(id='Result')

    @on(Button.Pressed, '#login')
    def next(self) -> None:
        self.query_one(ContentSwitcher).current = 'Loading'


class CrawlerApp(App):
    TITLE = '校務系統成績抓抓'
    CSS_PATH = 'main.css'
    BINDINGS = [
        Binding(key='ctrl+c', action='quit', description='Quit'),
        Binding(key='d', action='toggle_dark', description='Toggle dark mode'),
    ]

    def compose(self) -> ComposeResult:
        yield Header(name='123', show_clock=True)
        yield Switcher()
        yield Footer()

    def on_button_pressed(self) -> None:
        pass

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark


if __name__ == '__main__':
    app = CrawlerApp()
    app.run()
