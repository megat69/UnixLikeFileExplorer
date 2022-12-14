import curses
import _curses
import sys
import os
import glob
from pathlib import Path
import platform
import subprocess
import configparser
import typing


class App:
	"""
	The App.
	"""
	# Key used to exit the app
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
		self.path = str(Path.home())
		self.temp_path = self.path  # The path currently being written
		# Which item is currently being selected
		self.selected_item = 0
		# The window size
		self.rows, self.cols = 0, 0

		# Loads the configuration
		self.config = configparser.ConfigParser()
		self.config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"))

		# Whether to accept a file in the indexing
		if self.config["GENERAL"].getboolean("ShowHiddenFiles") is False:
			self.file_acceptation_condition = lambda filename: not filename.startswith(".")
		else:
			self.file_acceptation_condition = lambda filename: True


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
				self.quit()


	def quit(self, force: bool = False):
		"""
		Quits the app.
		"""
		if force:
			self.running = False
		else:
			# Remembering the selected element
			selected_element = self.display_menu(("Yes", "No"), "Do you want to quit ?")

			# If we selected "Yes" to the question of whether to leave, we leave.
			if not bool(selected_element):
				self.running = False

	def display_menu(self, commands: tuple[str, ...], label: str = None) -> int:
		"""
		Displays the given command menu and returns which command was selected (index).
		:param commands: A tuple of strings corresponding to each option in the menu.
		:param label: (Optional) The title to label the menu.
		:return: The index of the selected item in the commands menu.
		"""
		# Finding the middle of the screen
		screen_middle_y, screen_middle_x = self.rows // 2, self.cols // 2

		# Finding the selected element
		selected_element = 0

		# Initializing the key
		key = ""
		# Clearing the screen
		self.stdscr.clear()
		# Looping until the user selects an item
		while key not in ("\n", "\t"):
			# Displays the menu title
			if label is not None:
				self.stdscr.addstr(
					screen_middle_y - 2,
					screen_middle_x - len(label) // 2,
					label
				)

			# Displays the menu
			for i, command in enumerate(commands):
				# Displays the menu item
				self.stdscr.addstr(
					screen_middle_y - len(commands) // 2 + i,
					screen_middle_x - len(command) // 2,
					command,
					curses.A_NORMAL if i != selected_element else curses.A_REVERSE
					# Reverses the color if the item is selected
				)

			# Fetches a key
			key = self.stdscr.getkey()

			# Selects another item
			if key == "KEY_UP":
				selected_element -= 1
			elif key == "KEY_DOWN":
				selected_element += 1
			# Wrap-around
			if selected_element < 0:
				selected_element = len(commands) - 1
			elif selected_element > len(commands) - 1:
				selected_element = 0

		# Clears the screen
		self.stdscr.clear()

		# Returns the selected element
		return selected_element

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
		if self.key in ("\b", "\0", "\n", App.EXIT_APP, "SHF_PADSLASH") or self.key.startswith("KEY_"):
			# Gets the correct path
			if self.temp_path.count(":") > (1 if platform.system() == "Windows" else 0):  # Pattern
				tmp = self.temp_path.split(":")
				pattern = tmp.pop()
				path = ":".join(tmp)
				del tmp
				show_parent_folder = False
			else:  # No pattern
				pattern = None
				path = self.path
				show_parent_folder = True

			# Grabs all the files and folders at the current path
			folders, files = self.get_files_at_path(path, self.file_acceptation_condition, pattern=pattern, show_parent_folder=show_parent_folder)

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
						self.change_path_to(temp_path)
						self.selected_item = 0

				else:  # If the selected item is a file, we open it
					filepath = os.path.join(self.path, files[self.selected_item - len(folders)])
					if platform.system() == 'Darwin':  # macOS
						subprocess.call(('open', filepath))
					elif platform.system() == 'Windows':  # Windows
						os.startfile(filepath)
					else:  # linux variants
						subprocess.call(('xdg-open', filepath))

			# Bugfix for exclamation mark
			if self.key == "SHF_PADSLASH":
				self.temp_path += "!"

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
		# Detects whether the user inputted a pattern
		if self.temp_path.count(":") > (1 if platform.system() == "Windows" else 0):  # Pattern
			tmp = self.temp_path.split(":")
			pattern = tmp.pop()
			path = ":".join(tmp)
			del tmp
			show_parent_folder = False
		else:  # No pattern
			pattern = None
			path = self.path
			show_parent_folder = True

		# Gets all the folders and files at the current path
		folders, files = self.get_files_at_path(path, self.file_acceptation_condition, pattern=pattern, show_parent_folder=show_parent_folder)

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

		# Runs through all folders at the current path ????
		display_all_list_elements(
			folders, "????", self.config["DISPLAY"].getboolean("UseEmojis"),
			self.selected_item < len(folders), color_pair = 2
		)

		# Then runs through all the files at the current path ????
		display_all_list_elements(
			files, "????", self.config["DISPLAY"].getboolean("UseEmojis"),
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
	                      show_parent_folder: bool = True, pattern: str | None = None) -> tuple[list, list]:
		"""
		Returns the folders and files at the given path in the correct order.
		:param path: The path of the folder to run the function on.
		:param addition_condition: A condition on whether to add the item to the list, generally a lambda. Default will always add to the list.
		:param show_parent_folder: Shows the parent folder if True. Default is True.
		:param pattern: Which pattern to use at the target path. Default is None, so no pattern.
		:return: Returns the folder and files as a tuple of two lists of strings.
		>>> App.get_files_at_path(os.path.dirname(os.path.abspath(__file__)))
		(['..', '.git', '.idea', '__pycache__'], ['.gitignore', 'config.ini', 'main.py', 'README.md', 'requirements-windows.txt', 'setup.py'])
		>>> App.get_files_at_path(os.path.dirname(os.path.abspath(__file__)), lambda filename: not filename.startswith('.'))
		(['..', '__pycache__'], ['config.ini', 'main.py', 'README.md', 'requirements-windows.txt', 'setup.py'])
		>>> App.get_files_at_path(os.path.dirname(os.path.abspath(__file__)), lambda filename: not filename.startswith('.'), show_parent_folder=False)
		(['__pycache__'], ['config.ini', 'main.py', 'README.md', 'requirements-windows.txt', 'setup.py'])
		>>> App.get_files_at_path(os.path.dirname(os.path.abspath(__file__)), pattern="*.py")
		(['..'], ['main.py', 'setup.py'])
		>>> App.get_files_at_path(os.path.dirname(os.path.abspath(__file__)), pattern="*.py", show_parent_folder=False)
		([], ['main.py', 'setup.py'])
		"""
		# Lists all files at the given path
		if pattern is None:
			all_files = os.listdir(path)
		else:
			all_files = glob.glob(pattern, root_dir=path)

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

	def change_path_to(self, new_path: str):
		"""
		Changes the path and temp path to the given path.
		"""
		self.path = new_path
		self.temp_path = self.path


if __name__ == '__main__':
	# Checks if the user wants to see the help
	if "-h" in sys.argv or "--help" in sys.argv:
		print("""
		--------- 'THE_FILE_GLOBBER' ---------
		A console application that functions as a file explorer, but entirely cross-platform.
		It's main objective is to allow the use of Unix-like patterns on Windows.
		
		--------- HELP ---------
		Command line arguments :
		-h, --help                : Shows this message and exits
		-p, --default-path <path> : Changes the app's default path from the user's home directory to the given path
		-q, --quit-symbol <char>  : Changes the app's default key used to exit ('$') with another specified key. Must be exactly one character. 
		""".replace("\t", ""))
		sys.exit(0)

	# Instanciates the app
	app = App()

	# Parses the command line arguments with required arguments
	for i in range(1, len(sys.argv), 2):
		# Changes the default path
		if sys.argv[i] in ("--default-path", "-p"):
			app.change_path_to(sys.argv[i + 1])

		# Changes the app's default key used to exit
		elif sys.argv[i] in ("--quit-symbol", "-q"):
			App.EXIT_APP = sys.argv[i + 1][0]

	app.run()
