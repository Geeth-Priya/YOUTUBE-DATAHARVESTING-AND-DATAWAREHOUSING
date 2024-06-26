# YouTube Data Harvesting and Data Warehousing
## ****Domain**: Social Media**
### **Introduction**
  This project involves building a comprehensive framework to integrate data from Youtube ,store the integrated data in a MySQL Database, and create an  interactive web application for data analysis using Streamlit.The primary objectives are to effectively gather valuable Youtube data, establish robust storage mechanism, and visualize insights interactively for analysis purposes.
### Table of Contents
* Technologies Used
* Installation
* Import Libraries from Modules
* Usage
* Features
* Contact
#### Technologies Used
* python
* pandas
* mysql
* streamlit
* matplotlib
* seaborn
#### Installation
* pip install google-api-python-client
* pip install pandas
* pip install mysql-connector-python
* pip install stramlit
##### Import Libraries from Modules
* import googleapiclient.discovery
* import requests
* import re
* import json
* import pandas as pd

* import mysql.connector
* from datetime import datetime, timezone
* from mysql.connector import Error as MySQLError

* import streamlit as st
* from streamlit_option_menu import option_menu
* from streamlit_lottie import st_lottie
* import seaborn as sb
* import matplotlib.pyplot as plt

#### Usage
 Follow these steps to effectively use the application:
 1. Access the Streamlit App in the web browser
 2. Enter the Youtube Channel ID in the provided textbox on the Streamlit Interface.
 3. Select the "Collect and Store data" button.
    * It collects the data from the entered YouTube Channel Id and stores it in the MySQL Database.
 4. Choose the table for view which displays details from different tables- Channels Table,Videos Table, Comments Table.
 5. Select a Table to display its corresponding details.
 6. Use the sidebar menu to select query options for data analysis and visualization.
 7. Use the input box provided to select from a variety of queries for data analysis and visualization.
 8. By selecting the Query, streamlit will process the request and display the answers along with the relevant visualizations
#### Features
- **Data Collection:** Retrieve data from YouTube channels using the YouTube API.
- **Data Storage:** Store the collected data in a MySQL Database.
- **Interactive Analysis:** Use Streamlit to create an interactive web application for data visualization and analysis.
- **Visualization:** Visualize the data insights using matplotlib and seaborn for statistical plotting.

      
