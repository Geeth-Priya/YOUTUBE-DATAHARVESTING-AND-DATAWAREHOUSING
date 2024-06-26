# YOUTUBE-DATAHARVESTING-AND-DATAWAREHOUSING
## ****DOMAIN**:SOCIAL MEDIA**
### **Introduction**
  This project involves building a comprehensive framework to integrate data from Youtube ,store the integrated data in MySQL Database and create an  interactive web application for data analysis using Streamlit.The primary objectives are to effectively gather valuable Youtube data, establish robust storage mechanism, and visualize insights interactively for analysis purposes.
### Table of Contents
* Technologies Used
* Installation
* Usage
* Features
* Contact
#### Technologies Used
* Virtual Code
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
##### Import libraries from Modules
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
   3. Select the Collect and Store data button.
   4. It collects the data from the entered YouTube Channel Id and the fetched data will be stored in MySql Database.
   5. Select Table View: choose the table for view which displays details from different tables- Channels Table,Videos Table, Comments Table.
   6. Select a Table to display its corresponding details.
   7. Use the sidebar menu to select query options for data analysis and visualization.
   8. Customize queries to explore insights from the stored data in the MySQL database.

      
