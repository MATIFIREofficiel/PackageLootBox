from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='LootBox',
    version='0.0.1',
    description=(
        'A simple package for managing lootboxes with Create, Update, and Delete modules'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='MATIFIREofficiel',
    author_email='matthias.gaste42@gmail.com',
    url='https://github.com/VyOk9/LootBox',
    packages=find_packages(),
    python_requires='>=3.12.0',
    include_package_data=True,
    install_requires=[
        'supabase',
        'python-dotenv',
    ],
)
