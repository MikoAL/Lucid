from datetime import datetime
import time

import getchlib

from rich.live import Live
from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()

def typed_text(live, text):
	global menu_text
	typed = ""
	for char in text:
		typed += char
		menu_text += char
		time.sleep(0.5)
		live.update(make_layout())

menu_text = "Welcome to the menu!"

def make_layout() -> Layout:
	"""Define the layout."""
	layout = Layout(name="root")

	layout.split(
		Layout(name="header", size=3),
		Layout(name="main", ratio=1),
		Layout(name="footer", size=7),
	)
	layout["main"].split_row(
		Layout(name="side"),
		Layout(name="body", ratio=2, minimum_size=60),
	)
	layout["side"].split(Layout(name="box1"), Layout(name="box2"))
	return layout

text = Text('')



class Header:
	"""Display header with clock."""

	def __rich__(self) -> Panel:
		grid = Table.grid(expand=True)
		grid.add_column(justify="center", ratio=1)
		grid.add_column(justify="right")
		grid.add_row(
			"[b]Rich[/b] Layout application",
			datetime.now().ctime().replace(":", "[blink]:[/]"),
		)
		return Panel(grid, style="black on grey70")
input_text = ""
layout = make_layout()
layout["header"].update(Header())
layout["box1"].update(Panel("This is the first box", title="Box 1"))
layout['footer'].update(Panel(Align.left(text, vertical='top'), box=box.ROUNDED, title_align='left', title='Input:'))
with Live(layout, refresh_per_second=10 ,screen=True) as live:
	while True:
		input_text = get_input()
		layout['footer'].update(Panel(Align.left(input_text, vertical='top'), box=box.ROUNDED, title_align='left', title='Input:'))
	 

