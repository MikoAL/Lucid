from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, VerticalScroll
from textual.widgets import Button, Footer, Header, Static, Placeholder, Welcome, Label, Input, Markdown, RichLog
from textual.widget import Widget
from textual import events



class MainWindows(Vertical):
    def __init__(self):
        super().__init__()
        self.compose()
        self.chatlog = ChatLog()
        self.chatinput = ChatInput()

    def on_mount(self) -> None:
        self.styles.outline = ("round", "white")
        self.styles.width = "2fr"

    def compose(self) -> ComposeResult:

        yield self.chatlog
        yield self.chatinput


class ChatLog(RichLog):
	def __init__(self):
		super().__init__()
		self.compose()

		self.styles.outline = ("round", "white")
		self.styles.width = "1fr"
		self.styles.height = "2fr"
		self.styles.align = ("center", "middle")
		self.styles.text_align = "center"
		self.styles.padding = 1 
	def render(self) -> RenderResult:
		return self


class ChatInput(Container):
	def __init__(self):
		super().__init__()
		self.input_box = Input()
		self.compose()
	def on_mount(self) -> None:
		self.styles.height = "1fr"
		self.styles.width = "1fr"
		self.styles.outline = ("round", "white")
		self.input_box.styles.align = ("center", "middle")
		self.input_box.styles.width = "1fr"
		self.input_box.styles.height = "1fr"
	
	def on_input_submitted(self, message: Input.Submitted) -> None:
		self.input_box.clear()
		pass
	def compose(self) -> ComposeResult:
		yield self.input_box


class DashBoard(Vertical):
    	
	def on_mount(self) -> None:
		self.styles.width = "1fr"
		self.styles.height = "1fr"
		self.styles.outline = ("round", "white")
  
	def render(self) -> RenderResult:
		return "DashBoard"

class Root(App):
	#CSS_PATH = "textual_test.tcss"
	def __init__(self):
		super().__init__()
		self.dash_board = DashBoard()
		self.main_windows = MainWindows()


 
	def on_mount(self) -> None:
		self.screen.styles.layout = "horizontal"
		pass
 
	def compose(self) -> ComposeResult:

		yield self.dash_board
		yield self.main_windows

	def on_input_submitted(self, message: Input.Submitted) -> None:
		self.main_windows.chatlog.write(message.value)

	def on_key(self, event: events.Key) -> None:
		if event.key == "escape":
			self.exit()
		pass

if __name__ == "__main__":
	app = Root()
	app.run()