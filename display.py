import os
import time
import requests
import yaml

from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, VerticalScroll
from textual.widgets import Button, Footer, Header, Static, Placeholder, Welcome, Label, Input, Markdown, RichLog
from textual.widget import Widget
from textual.message import Message
from textual import events

script_dir = os.path.dirname(os.path.realpath(__file__))
# Change the working directory to the script's directory
os.chdir(script_dir)

# Reading from a YAML file
with open('settings.yaml', 'r') as file:
	settings = yaml.safe_load(file)

host = settings['host']
port = settings['port']
server = f'http://{host}:{port}'

user_name = settings['user_name']

class MainWindows(Vertical):
	def __init__(self):
		super().__init__()
		self.compose()
		self.styles.width = "2fr"
		self.styles.height = "1fr"
		self.chatlog = ChatLog()
		self.chatinput = ChatInput()

	#def on_mount(self) -> None:
		#self.styles.outline = ("round", "white")


	def compose(self) -> ComposeResult:

		yield self.chatlog
		yield self.chatinput


class ChatLog(RichLog):
	def __init__(self):
		super().__init__()
		self.compose()
	def on_mount(self):
		self.styles.margin = (1, 1)
		self.styles.outline = ("ascii", "white")
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
	def on_mount(self):
		self.styles.margin = (1, 1)
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
		#self.styles.outline = ("round", "white")
	def compose(self) -> ComposeResult:
		yield ServerStatus()
		yield Placeholder()
		yield Placeholder()
	#def render(self) -> RenderResult:
	#	return ServerStatus()
class ServerStatus(Label):
	def __init__(self):
		super().__init__()
		self.styles.width = "1fr"
		self.styles.height = "1fr"
		self.styles.margin = (1, 1)
		self.styles.outline = ("round", "white")
		self.renderable = "Server is not alive"

  
	#def on_mount(self) -> None:
	#	self.styles.width = "1fr"
	#	self.styles.height = "1fr"
	#	self.styles.outline = ("round", "white")
  
	class ServerAlive(Message):
		def __init__(self, server_alive: bool):
			self.server_alive = server_alive
			super().__init__()

	def server_alive(self) -> None:
		try:
			response = requests.get(server)
			self.post_message(self.ServerAlive(server_alive=True))
		except requests.exceptions.RequestException as e:
			self.post_message(self.ServerAlive(server_alive=False))
   
	def on_server_alive(self, message: ServerAlive) -> None:
		if message.server_alive:
			self.renderable = "Server is alive"
		else:
			self.renderable = "Server is not alive"


class Root(App):
	CSS_PATH = "display.tcss"
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