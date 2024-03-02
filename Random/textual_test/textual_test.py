from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, VerticalScroll
from textual.widgets import Button, Footer, Header, Static, Placeholder, Welcome, Label
from textual.widget import Widget
from textual import events



class MainWindows(Vertical):
	def on_mount(self) -> None:
		self.styles.outline = ("round", "white")
		self.styles.width = "2fr"
		pass

	def compose(self) -> ComposeResult:
			yield ChatLog()
			yield Input()


class ChatLog(Placeholder):
	
	def on_mount(self) -> None:
		self.styles.height = "2fr"
		self.styles.outline = ("round", "white")
		self.styles.width = "1fr"
	def render(self) -> RenderResult:
		return "Chat Log"


class Input(Placeholder):
	
	def on_mount(self) -> None:
		self.styles.height = "1fr"
		self.styles.width = "1fr"
		self.styles.outline = ("round", "white")
  
	def render(self) -> RenderResult:
		return "Input:"

class DashBoard(Vertical):
    	
	def on_mount(self) -> None:
		self.styles.width = "1fr"
		self.styles.height = "1fr"
		self.styles.outline = ("round", "white")
  
	def render(self) -> RenderResult:
		return "DashBoard"

class Root(App):
	#CSS_PATH = "textual_test.tcss"
 
	def on_mount(self) -> None:
		self.screen.styles.layout = "horizontal"
		pass
 
	def compose(self) -> ComposeResult:
		yield DashBoard()
		yield MainWindows()


	def on_key(self) -> None:
		self.exit()

if __name__ == "__main__":
	app = Root()
	app.run()