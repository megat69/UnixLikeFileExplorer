import curses
import _curses
import os
import configparser
import typing


class App:
	"""
	The App.
	"""
	def __init__(self):
		"""
		Initializes the app.
		"""
		# The curses standard screen
		self.stdscr: _curses.window = None
		# Whether the app is currently running
		self.running = False
		# The currently pressed key
		self.key = ""
		# The current path
		self.path = os.path.dirname(os.path.abspath(__file__))
		# Which item is currently being selected
		self.selected_item = 0
		# The window size
		self.rows, self.cols = 0, 0

		# Loads the configuration
		self.config = configparser.ConfigParser()
		self.config.read("config.ini")


	def run(self):
		"""
		Runs the app.
		"""
		# Launches the app using curses
		curses.wrapper(self.main)


	def late_init(self):
		"""
		Makes the init after the curses launch.
		"""
		# Defines the curses color pairs
		curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # NORMAL COLOR
		curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # FOLDER COLOR


	def main(self, stdscr):
		"""
		The app's main function.
		:param stdscr: The curses screen.
		"""
		# Does the late init
		self.late_init()

		# Defines the standard curses screen
		self.stdscr = stdscr

		# Runs for as long as needed
		self.running = True
		while self.running:
			# Updates the app
			self.update()

			# Applying the asthetic
			self.apply_aesthetic()

			# Lists all files at the given path
			self.list_files()

			# Looks for the given key
			self.handle_input()
			if self.key == ":":
				self.running = False


	def update(self):
		"""
		Updates the app.
		"""
		self.rows, self.cols = self.stdscr.getmaxyx()


	def handle_input(self):
		"""
		Handles all key inputs.
		"""
		# Handles the current key
		self.key = self.stdscr.getkey()

		# If it is a special key, we detect it
		if self.key.startswith("KEY_"):
			if self.key == "KEY_UP":
				self.selected_item -= 1
			elif self.key == "KEY_DOWN":
				self.selected_item += 1
			files, folders = self.get_files_at_path(self.path)
			self.selected_item = max(0, min(self.selected_item, len(files) + len(folders) - 1))

		# Returns the pressed key
		return self.key


	def list_files(self):
		"""
		Displays the list of files in the window.
		"""
		# Gets all the folders and files at the current path
		folders, files = self.get_files_at_path(self.path)

		# Defines a function to display all the elements of a list with the given prefix
		def display_all_list_elements(elements: list[str], prefix: str, use_prefix: bool, display_selected: bool,
		                              starting_row: int = 1, color_pair: int = 1, index_minus: int = 0) -> None:
			""" Displays all the elements in the list along with the prefix if use_prefix is True. """
			for i, element in enumerate(elements):
				# Displays the file name accompanied by emojis if the user wants to# Writes the filename to the screen
				self.stdscr.addstr(
					i * 2 + 2 + starting_row,
					1,
					(f"{prefix} " if use_prefix else "") + element,
					(curses.A_REVERSE if i == (self.selected_item - index_minus) and display_selected else curses.A_NORMAL) |
					curses.color_pair(color_pair)
				)

		# Runs through all folders at the current path 📁
		display_all_list_elements(folders, "📁", self.config["DISPLAY"].getboolean("UseEmojis"),
		                          self.selected_item < len(folders), color_pair=2)

		# Then runs through all the files at the current path 📄
		display_all_list_elements(files, "📄", self.config["DISPLAY"].getboolean("UseEmojis"),
		                          self.selected_item >= len(folders), len(folders) * 2 + 1, index_minus=len(folders))


	def apply_aesthetic(self):
		"""
		Displays the project aesthetic.
		"""
		# Displays the title
		self.display_middle_screen("THE_FILE_GLOBBER", flags=curses.A_REVERSE)


	@staticmethod
	def get_files_at_path(path: str) -> tuple[list, list]:
		"""
		Returns the folders and files at the given path in the correct order.
		"""
		# Lists all files at the given path
		all_files = os.listdir(path)

		# Sets up all the files and folders as a list
		folders, files = [], []

		# Fetches all the elements and determines whether it is a file or a folder, the adds it to the correct list
		for element in all_files:
			if os.path.isdir(os.path.join(path, element)):
				folders.append(element)
			else:
				files.append(element)

		# Returns the folders followed by the files
		return folders, files

	def display_middle_screen(self, text: str, rows: int = 0, flags = curses.A_NORMAL):
		"""
		Displays the given text at the middle of the screen.
		:param text: The text to display.
		:param rows: The row number.
		:param flags: The different flags to add to the text.
		"""
		# Gets the middle of the screen
		middle_screen = self.cols // 2 - len(text) // 2
		# Displays the text on the screen
		self.stdscr.addstr(rows, middle_screen, text, flags)


if __name__ == '__main__':
	app = App()
	app.run()
