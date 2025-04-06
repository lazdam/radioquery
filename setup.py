from setuptools import setup, find_packages
from setuptools.command.install import install
import os

class PostInstallCommand(install):
    """Custom install command to set up directory structure."""
    def run(self):
        # Run the standard install first
        install.run(self)

        # Create necessary directories
        base_dir = os.path.expanduser("~/RQUERY")
        dirs_to_create = [
            os.path.join(base_dir, "FIRST"),
            os.path.join(base_dir, "VLASS"),
            os.path.join(base_dir, "tests"),
        ]
        for path in dirs_to_create:
            os.makedirs(path, exist_ok=True)
        print("📂 Created default RQUERY folders in your home directory. To configure this path, navigate to setup.py.")

setup(
    name="radioquery",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,  # Tells setuptools to include files specified in MANIFEST.in
    package_data={
        # Include any .txt files in the vlass_configs subfolder
        "radioquery": ["survey_configs/vlass_configs/*.txt"],
    },
    install_requires=[
        "numpy<2.0.0",    
        "astropy>=6.0.1",
        "pytest",
        "requests",
        "tqdm"
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
    author="Mattias Lazda",
    description="A package for querying radio survey images like FIRST and VLASS",
)