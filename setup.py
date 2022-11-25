import platform
import os ; os.chdir(os.path.dirname(__file__))

# Requests the PIP prefix from the user
pip_prefix = input("Please enter your PIP prefix (pip, pip3, python -m pip, py -p pip...). Leave blank for 'pip'.\n")
if pip_prefix == "":
	pip_prefix = "pip"

# Installs the dependencies required if on Windows
if platform.system() == "Windows":
	os.system(f"{pip_prefix} install -r requirements-windows.txt")
