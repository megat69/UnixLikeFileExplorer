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
			# Lists all files at the given path
			self.list_files()

			# Looks for the given key
			self.handle_input()
			if self.key == ":":
				self.running = False


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
				self.stdscr.addstr(i, 0, f"{prefix} {file}", curses.A_REVERSE if i == self.selected_item else curses.A_NORMAL)

			# If we do not want the filename to be accompanied by emojis
			else:
				# Writes the filename to the screen
				self.stdscr.addstr(i, 0, file, curses.A_REVERSE if i == self.selected_item else curses.A_NORMAL)


	@staticmethod
	def get_files_at_path(path: str):
		"""
		Returns the files at the given file.
		"""
		return os.listdir(path)


if __name__ == '__main__':
	app = App()
	app.run()
