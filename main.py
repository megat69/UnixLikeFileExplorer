import curses
import _curses
import os
import configparser


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


	def main(self, stdscr):
		"""
		The app's main function.
		:param stdscr: The curses screen.
		"""
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
			self.selected_item = max(0, min(self.selected_item, len(self.get_files_at_path(self.path)) - 1))

		# Returns the pressed key
		return self.key


	def list_files(self):
		"""
		Displays the list of files in the window.
		"""
		# Runs through all files and at the current path
		for i, file in enumerate(self.get_files_at_path(self.path)):
			# Displays the file name accompanied by emojis if the user wants to
			if self.config["DISPLAY"].getboolean("UseEmojis"):
				# Chooses as emoji either a document if the element is a file, or a folder if it is a folder;
				if os.path.isfile(os.path.join(self.path, file)):
					prefix = "📄"
				else:
					prefix = "📁"

				# Writes the filename to the screen
				self.stdscr.addstr(i * 2 + 2, 1, f"{prefix} {file}", curses.A_REVERSE if i == self.selected_item else curses.A_NORMAL)

			# If we do not want the filename to be accompanied by emojis
			else:
				# Writes the filename to the screen
				self.stdscr.addstr(i * 2 + 2, 1, file, curses.A_REVERSE if i == self.selected_item else curses.A_NORMAL)


	def apply_aesthetic(self):
		"""
		Displays the project aesthetic.
		"""
		# Displays the title
		self.display_middle_screen("THE_FILE_GLOBBER", flags=curses.A_REVERSE)


	@staticmethod
	def get_files_at_path(path: str):
		"""
		Returns the files at the given file.
		"""
		return os.listdir(path)

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
