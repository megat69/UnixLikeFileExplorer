import curses
import _curses
import os
import platform
import subprocess
import configparser
import typing


class App:
	"""
	The App.
	"""
	EXIT_APP = '$'
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
		self.temp_path = self.path  # The path currently being written
		# Which item is currently being selected
		self.selected_item = 0
		# The window size
		self.rows, self.cols = 0, 0
		# Whether to accept a file in the indexing
		self.file_acceptation_condition = lambda filename: not filename.startswith(".")

		# Loads the configuration
		self.config = configparser.ConfigParser()
		self.config.read(os.path.join(self.path, "config.ini"))


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
			if self.key == App.EXIT_APP:
				self.running = False


	def update(self):
		"""
		Updates the app.
		"""
		# Clears the screen
		self.stdscr.clear()

		# Calculates the amount of rows and columns in the app, mostly to update columns
		self.rows, self.cols = self.stdscr.getmaxyx()


	def handle_input(self):
		"""
		Handles all key inputs.
		"""
		# Handles the current key
		self.key = self.stdscr.getkey()

		# If it is a special key, we detect it
		if self.key in ("\b", "\0", "\n") or self.key.startswith("KEY_"):
			# Grabs all the files and folders at the current path
			folders, files = self.get_files_at_path(self.path, self.file_acceptation_condition)

			# Selecting an item upwards or downwards
			if self.key == "KEY_UP":
				self.selected_item -= 1
			elif self.key == "KEY_DOWN":
				self.selected_item += 1

			# Selecting an item in another column
			if self.key == "KEY_LEFT":
				self.selected_item -= self.rows - 5
			elif self.key == "KEY_RIGHT":
				self.selected_item += self.rows - 5

			# Removing the last character of the temporary path if using the backspace key
			elif self.key in ("KEY_BACKSPACE", "\b", "\0"):
				# If there is at least a character in the temp path, we remove the last character
				if len(self.temp_path) > 0:
					self.temp_path = self.temp_path[:-1]

			# Adds the selected folder's name to the temporary path if the user pressed Enter
			elif self.key in ("\n", "KEY_ENTER"):
				if len(folders) > self.selected_item >= 0:  # If the selected item is a folder
					temp_path = os.path.join(self.path, folders[self.selected_item])
					if os.path.exists(temp_path):
						# Also normalizes the path upon pressing enter
						temp_path = os.path.normpath(temp_path)

						# Setting the current path to the temp path
						self.path = temp_path
						self.temp_path = self.path
						self.selected_item = 0

				else:  # If the selected item is a file, we open it
					filepath = os.path.join(self.path, files[self.selected_item - len(folders)])
					if platform.system() == 'Darwin':  # macOS
						subprocess.call(('open', filepath))
					elif platform.system() == 'Windows':  # Windows
						os.startfile(filepath)
					else:  # linux variants
						subprocess.call(('xdg-open', filepath))

			# Clamps the selected item for it not to bug
			self.selected_item = max(0, min(self.selected_item, len(files) + len(folders) - 1))

		# If it is a regular key, we add the key to the temporary path
		else:
			self.temp_path += self.key

		# If the temp path is a valid path, we make the current path be the contents of the temporary path
		if os.path.exists(self.temp_path):
			self.path = self.temp_path

		# Returns the pressed key
		return self.key


	def list_files(self):
		"""
		Displays the list of files in the window.
		"""
		# Gets all the folders and files at the current path
		folders, files = self.get_files_at_path(self.path, self.file_acceptation_condition)

		# Defines the maximum column length any filename has been at
		max_column_length = 0
		current_column = 0

		# Defines a function to display all the elements of a list with the given prefix
		def display_all_list_elements(elements: list[str], prefix: str, use_prefix: bool, display_selected: bool,
		                              starting_row: int = 1, color_pair: int = 1, index_minus: int = 0) -> None:
			""" Displays all the elements in the list along with the prefix if use_prefix is True. """
			nonlocal max_column_length, current_column
			# Defines a temporary max column length for the next max column length
			temp_max_column_length = 0

			# Fetches all elements
			for i, element in enumerate(elements):
				# Chooses the row position
				row_position = i + 2 + starting_row
				# While the row position exceeds the amount of rows in the console, we reduce it accordingly.
				while row_position >= (self.rows - 2):
					row_position -= (self.rows - 2)

				# Sets the temp max column length to the highest value it can have from the elements
				temp_max_column_length = max(temp_max_column_length, len(element) + 2)

				# Adds the temp max column length to the max column length and resets it if the length of the columns is reached
				if (i + 2 + starting_row) - (current_column * (self.rows - 5)) >= self.rows - 2:
					max_column_length += temp_max_column_length + 1
					temp_max_column_length = 0
					current_column += 1

				# Corrects the position if the column is not the first one
				if current_column != 0:
					row_position += 3

				# Displays the file name accompanied by emojis if the user wants to# Writes the filename to the screen
				try:
					self.stdscr.addstr(
						row_position,
						1 + max_column_length,
						(f"{prefix} " if use_prefix else "") + element,
						(curses.A_REVERSE if i == (self.selected_item - index_minus) and display_selected else curses.A_NORMAL) |
						curses.color_pair(color_pair)
					)
				except curses.error: pass

		# Runs through all folders at the current path 📁
		display_all_list_elements(
			folders, "📁", self.config["DISPLAY"].getboolean("UseEmojis"),
			self.selected_item < len(folders), color_pair = 2
		)

		# Then runs through all the files at the current path 📄
		display_all_list_elements(
			files, "📄", self.config["DISPLAY"].getboolean("UseEmojis"),
			self.selected_item >= len(folders), len(folders) + 1, index_minus = len(folders)
		)


	def apply_aesthetic(self):
		"""
		Displays the project aesthetic.
		"""
		# Displays the title
		self.display_middle_screen("THE_FILE_GLOBBER", flags=curses.A_REVERSE)

		# Displays the temporary path at the bottom of the screen
		self.stdscr.addstr(self.rows - 1, 0, self.temp_path[:self.cols - 1])

		# Displays the current path on top of the file tree
		self.stdscr.addstr(2, 1, self.path[:self.cols - 1])


	@staticmethod
	def get_files_at_path(path: str, addition_condition: typing.Callable = lambda name: True,
	                      show_parent_folder: bool = True) -> tuple[list, list]:
		"""
		Returns the folders and files at the given path in the correct order.
		:param path: The path of the folder to run the function on.
		:param addition_condition: A condition on whether to add the item to the list, generally a lambda. Default will always add to the list.
		:param show_parent_folder: Shows the parent folder if True. Default is True.
		:return: Returns the folder and files as a tuple of two lists of strings.
		>>> App.get_files_at_path(os.path.dirname(os.path.abspath(__file__)))
		(['..', '.git', '.idea', '__pycache__'], ['.gitignore', 'config.ini', 'main.py'])
		>>> App.get_files_at_path(os.path.dirname(os.path.abspath(__file__)), lambda filename: not filename.startswith('.'))
		(['..', '__pycache__'], ['config.ini', 'main.py'])
		>>> App.get_files_at_path(os.path.dirname(os.path.abspath(__file__)), lambda filename: not filename.startswith('.'), show_parent_folder=False)
		(['__pycache__'], ['config.ini', 'main.py'])
		"""
		# Lists all files at the given path
		all_files = os.listdir(path)

		# Sets up all the files and folders as a list
		folders, files = [], []
		if show_parent_folder:
			folders.append("..")

		try:  # Try block in case the permission is not granted by the OS to look at this folder
			# Fetches all the elements and determines whether it is a file or a folder, the adds it to the correct list
			for element in all_files:
				# Checks if the element is viable and if so, adds it to the correct list
				if addition_condition(element):
					if os.path.isdir(os.path.join(path, element)):
						folders.append(element)
					else:
						files.append(element)
		except PermissionError:
			pass

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
