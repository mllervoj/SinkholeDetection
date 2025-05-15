import os
import subprocess
import sys
import venv


def create_venv(venv_dir):
    """Create a virtual environment in the specified directory if it doesn't exist."""
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment in '{venv_dir}'...")
        venv.create(venv_dir, with_pip=True)
        print("Virtual environment created.")
    else:
        print(f"Virtual environment already exists in '{venv_dir}'.")


def install_requirements(venv_dir, requirements_file):
    """Install requirements using the pip from the virtual environment."""
    # Determine the pip path depending on the OS.
    if os.name == "nt":  # Windows
        pip_executable = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        pip_executable = os.path.join(venv_dir, "bin", "pip")

    # Check if pip exists in the venv.
    if not os.path.exists(pip_executable):
        print("Error: pip not found in the virtual environment.")
        sys.exit(1)

    print("Installing dependencies from requirements.txt...")
    try:
        subprocess.check_call([pip_executable, "install", "-r", requirements_file])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error installing dependencies.")
        sys.exit(e.returncode)

def createStart(fileBAT):  
    with open(fileBAT, "w") as f:
        f.write("""@echo off\nstart "" "venv\Scripts\pythonw.exe" "scripts\start.py"\n""")



if __name__ == "__main__":
    venv_directory = "venv"
    req_file = "requirements.txt"
    start_fileBAT = "start.bat"

    create_venv(venv_directory)
    install_requirements(venv_directory, req_file)
    createStart(start_fileBAT)

    print("\nSetup complete. To activate the virtual environment, run:")
    if os.name == "nt":
        print(f"{venv_directory}\\Scripts\\activate")
        print("\nif that returns an error, run: ")
        print("Set-ExecutionPolicy Unrestricted -Scope Process")
    else:
        print(f"source {venv_directory}/bin/activate")
