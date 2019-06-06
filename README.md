# Data Wrangling Project
Python programming for data science applications and SQL databases.

## Description
Wrote Python code to munge data sourced from Open Street Map, an open-source map of the world.

- Due to the large file size, parse the XML source data in small segments and assemble the dataset on the fly.
- Programmatically perform data quality control through data checks, cleansing, and make corrections if possible.
- Validate the data, and eliminate corrupt data from the dataset.
- Implement sophisticated techniques to parse the input data file in sections, build dictionaries, and track data metrics.
- Load the sanitized output into a SQL database and apply SQL queries to analyze the dataset.

## Method
The project is presented in a Jupyter notebook.
Code is contained in Python files and the Jupyter notebook.

The large database makes Pandas and Numpy impractical due to computer memory constraints. Instead, an iterable approach is taken to munge the data in small blocks.

## Data
The dataset is an area of New York City extracted from [Open Street Map](https://www.openstreetmap.org) in XML format.
A small test dataset is included to allow readers to run the code: `UpperWestSideTest.osm`.

## Notebook Files
The notebook is provided in two formats:

- `data_wrangling_notebook_web.html` &nbsp; is a HTML file of the notebook for convenient viewing in a browser. Use this file if you do not have Jupyter installed on your computer **_or_** &nbsp; to read the notebook without running any code.
- `data_wrangling_notebook.ipynb` &nbsp; is the source file for the Jupyter notebook. If you have Jupyter installed on your computer, you can execute the code in the notebook.

## Code
The code is contained in Python files and the Jupyter notebook.
#### Code Execution Sequence
Execute the standalone Python files in the following order:

1. initial\_scan.py
2. fix\_it\_demo.py
3. main\_process.py
4. xml\_csv\_validation\_routines.py
5. database\_routines.py
6. database\_age\_plot.py

## Report
The notebook contains the report and the code.
To read the **detailed** report, and run the code in steps as documented therein, open the Jupyter notebook as explained below.   
A **summary** report, without code, is provided in a PDF format file: `data_wrangling_summary_report.pdf`.

## Installation
To install Jupyter on your computer, click [here](https://jupyter.org/).

## Usage
In the directory where the notebook file is located, run the command:
`jupyter notebook data_wrangling_notebook.ipynb`
