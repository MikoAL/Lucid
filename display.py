import os
import time
from time import monotonic
import requests
import yaml
import httpx

from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, VerticalScroll
from textual.widgets import Button, Footer, Header, Static, Placeholder, Welcome, Label, Input, Markdown, RichLog
from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message
from textual.events import Load
from textual import events, on, work


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
		self.server_status = ServerStatus()
		yield self.server_status
		yield Placeholder()
		yield Placeholder()


class ServerStatus(Label):
    
	def __init__(self):
		super().__init__()
		self.styles.width = "1fr"
		self.styles.height = "1fr"
		self.styles.margin = (1, 1)
		self.styles.outline = ("round", "white")
		self.styles.content_align = ("center", "middle")
		self.not_connected()
	def not_connected(self):
		self.renderable = ":red_circle: Not Connected To Server"
		self.styles.color = "red 70%"
	def connected(self):
		self.renderable = ":green_circle: Connection Established"
		self.styles.color = "green 70%"
	 
class ServerHandler(Widget):
		
	def __init__(self):

		super().__init__()
		self.display = "none"

	class ServerAlive(Message):
		def __init__(self, server_alive: bool):
			self.server_alive = server_alive
			super().__init__()
	@work(exclusive=False)
	async def send_message(message, user_name=user_name, server=server):
		data = {'content': message, 'source': user_name, 'timestamp': time.time(), 'type': 'conversation'}
		async with httpx.Client() as client:
			client.post(f'{server}/postbox', json=data)
	@work(exclusive=False)
	async def get_display(server=server):
		async with httpx.Client() as client:
			response = client.get(f'{server}/display')
			return response.json()['content']

	@work(exclusive=False)
	async def check_server_alive(self) -> None:
		async with httpx.AsyncClient() as client:
			try:
				response = await client.get(server)
				if response.status_code == 200:
					self.post_message(self.ServerAlive(server_alive=True))
				else:
					self.post_message(self.ServerAlive(server_alive=False))
			except httpx.RequestError:
				self.post_message(self.ServerAlive(server_alive=False))

	


class Root(App):
	CSS_PATH = "display.tcss"
	def __init__(self):
		super().__init__()
		self.dash_board = DashBoard()
		self.main_windows = MainWindows()
		self.server_handler = ServerHandler()
	async def on_load(self) -> None:
		self.set_interval(1, self.server_handler.check_server_alive)
		pass
	def on_mount(self) -> None:
		self.screen.styles.layout = "horizontal"
		self.main_windows.chatlog.write(self.css_tree) 
		pass
 
	def compose(self) -> ComposeResult:
		yield self.server_handler
		yield self.dash_board
		yield self.main_windows
		
  
	@on(ServerHandler.ServerAlive)
	def server_alive_ui_update(self, message: ServerHandler.ServerAlive) -> None:
		#self.dash_board.server_status.connected()
		if message.server_alive:
			self.dash_board.server_status.connected()
		else:
			self.dash_board.server_status.not_connected()
			#self.dash_board.server_status.connected()
	def on_input_submitted(self, message: Input.Submitted) -> None:
		self.main_windows.chatlog.write(message.value)

	def on_key(self, event: events.Key) -> None:
		if event.key == "escape":
			self.exit()
		pass

if __name__ == "__main__":
	app = Root()
	app.run()