from setuptools import setup, find_packages


setup(
    name="basic-antivirus-simulation",
    version="1.0.0",
    description="Basic signature-based antivirus simulation",
    package_dir={"": "src"},
    packages=find_packages("src"),
    py_modules=["antivirus_scanner"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "antivirus-cli=basic_antivirus_simulation.cli:main",
            "antivirus-gui=basic_antivirus_simulation.gui_app:main",
        ]
    },
    python_requires=">=3.10",
)
