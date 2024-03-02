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


class ChatLog(Container):
	def __init__(self):
		super().__init__()
		self.compose()
		self.chatlog_window = RichLog(name="ChatLogWindow", id="ChatLogWindow")
		self.chatlog_window.styles.outline = ("round", "white")
		self.chatlog_window.styles.width = "auto"
		self.chatlog_window.styles.height = "1fr"
	def on_mount(self) -> None:
		self.styles.height = "2fr"
		self.styles.outline = ("round", "white")
		self.styles.width = "1fr"
	def compose(self) -> ComposeResult:
		yield self.chatlog_window


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
		self.chatlogs = ["Test1","Test2"]

 
	def on_mount(self) -> None:
		self.screen.styles.layout = "horizontal"
		#self.chatlogs = ["Test1","Test2"]
		pass
 
	def compose(self) -> ComposeResult:
		#self.dash_board = DashBoard()
		#self.main_windows = MainWindows()
		#self.main_windows.chatlog.chatlog_window.write("\n".join(self.chatlogs))
		yield self.dash_board
		yield self.main_windows

	def on_input_submitted(self, message: Input.Submitted) -> None:
		self.main_windows.chatlog.chatlog_window.write(message.value)

	def on_key(self) -> None:
		#self.exit()
		pass

if __name__ == "__main__":
	app = Root()
	app.run()