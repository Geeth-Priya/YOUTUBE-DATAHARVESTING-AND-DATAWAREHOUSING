#YouTube API Libraries
import googleapiclient.discovery
from googleapiclient.errors import HttpError

#MySQL Libraries
import mysql.connector
from datetime import datetime,timezone
import re
import json
import pandas as pd

#Streamlit Libraries
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
from streamlit_lottie import st_lottie
import seaborn as sb
import matplotlib.pyplot as plt


#API Key Connection
def Api_Connect():
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)
    return youtube
youtube=Api_Connect()



#collecting channel_details 
def channel_data(channel_id): 
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id)
    response=request.execute()
    
    data={
    "Channel_id":response["items"][0]["id"],
    "Channel_Name":response["items"][0]["snippet"]["title"],
    "Subscription_Count":response["items"][0]["statistics"]["subscriberCount"],
    "Channel_Views":response["items"][0]["statistics"]["viewCount"],
    "Channel_Description":response["items"][0]["snippet"]["description"],
    "Playlist_Id":response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"],
    "Channel_Published":response["items"][0]["snippet"]["publishedAt"],
    "Channel_Videocount":response["items"][0]["statistics"]["videoCount"]
    }
    return data



#collecting video_ids from the uploads
def Video_data(channel_id): 
    request = youtube.channels().list(
            part="contentDetails",
            id=channel_id)
    response=request.execute()

    Playlists=response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    video_ids=[]
    next_Page_Token=None
    while True:
        request_videos = youtube.playlistItems().list(
                part="snippet",
                maxResults=50,
                playlistId=Playlists,
                pageToken=next_Page_Token
            )
        response = request_videos.execute()

        video_ids.extend(item["snippet"]["resourceId"]["videoId"]
                         for item in response.get("items",[]))
        
        next_Page_Token=response.get("nextPageToken")
        if not next_Page_Token:
            break
    return video_ids



#collecting video information 
def video_data_informations(id_s): 
    video_information=[]
    for video_info in (id_s):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_info)
        response=request.execute()


        data={
            "Channel_id":response["items"][0]["snippet"]["channelId"],
            "Video_Id":response["items"][0]["id"],
            "Video_Name":response["items"][0]["snippet"]["title"],
            "Video_Description":response["items"][0]["snippet"]["description"],
            "Tags":response["items"][0].get("tags"),
            "PublishedAt":response["items"][0]["snippet"]["publishedAt"],
            "View_Count": response["items"][0]["statistics"]["viewCount"],
            "Like_Count": response["items"][0]["statistics"].get("likeCount",0),
            "Dislike_Count":response["items"][0]["statistics"].get("dislikeCount",0),
            "Favorite_Count": response["items"][0]["statistics"].get("favoriteCount",0),
            "Comment_Count": response["items"][0]["statistics"].get("commentCount",0),
            "Duration":response["items"][0]["contentDetails"]["duration"],
            "Thumbnail":response["items"][0]["snippet"]["thumbnails"],
            "Caption_Status":response["items"][0]["contentDetails"]["caption"]
            }
        video_information.append(data)

    return video_information



#Collecting comment details 
def comment_data(id_s):
    comments=[]
    for video_id in id_s:
        try:
            request = youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=100)
            response = request.execute()
            for item in response.get("items", []):
                data={
                    "Channel_id":item["snippet"]["topLevelComment"]["snippet"]["channelId"],
                    "Comment_Id":item["snippet"]["topLevelComment"]["id"],
                    "Video_Id":item["snippet"]["topLevelComment"]["snippet"]["videoId"],
                    "Comment_Text" :item["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                    "Comment_Author":item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                    "Comment_PublishedAt":item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                    }
                comments.append(data)
        except HttpError as e:
            if e.resp.status == 403:
                print("Comments are disabled")
            else:
                print(f"HttpError occurred: {e}")
    return comments 



#Function to collect channel data,video data,comment data and converting into DataFrame
def information_collection(channel_id):
    get_channel_information=channel_data(channel_id)
    get_video_ids=Video_data(channel_id)
    get_video_information=video_data_informations(get_video_ids)
    get_comment_information=comment_data(get_video_ids)

    channel_df = pd.DataFrame([get_channel_information])
    video_df = pd.DataFrame(get_video_information)
    comment_df = pd.DataFrame(get_comment_information)

    return channel_df,video_df,comment_df



#MySQL Connection
def connect_to_mysql():
        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="xyz",
        auth_plugin="mysql_native_password",
        database="project"
        )
        mycursor=mydb.cursor()
        return mydb, mycursor 



#creating table for channel details
def Channel_Details_Table(channel_df):
    mydb, mycursor = connect_to_mysql()

    if mydb and mycursor:
        try:
            mycursor.execute("SHOW TABLES LIKE 'Channel_details'")
            table_exists = mycursor.fetchone()

            if not table_exists:
                mycursor.execute('''CREATE TABLE Channel_details (
                                    Channel_id VARCHAR(255) PRIMARY KEY,
                                    Channel_Name VARCHAR(255),
                                    Subscription_Count INT,
                                    Channel_Views INT,
                                    Channel_Description TEXT,
                                    Playlist_Id VARCHAR(255),
                                    Channel_Published TIMESTAMP,
                                    Channel_Videocount INT
                                    )''')
                mydb.commit()
                print("Channel_details table created successfully.")

            #Inserting values into the Channel Details Table
            for index, row in channel_df.iterrows():
                sql = '''INSERT INTO Channel_details (
                            Channel_id,
                            Channel_Name,
                            Subscription_Count,
                            Channel_Views,
                            Channel_Description,
                            Playlist_Id,
                            Channel_Published,
                            Channel_Videocount
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'''

                values = (
                    row["Channel_id"],
                    row["Channel_Name"],
                    row["Subscription_Count"],
                    row["Channel_Views"],
                    row["Channel_Description"],
                    row["Playlist_Id"],
                    published_date_conversion(row["Channel_Published"]),
                    row["Channel_Videocount"]
                )

                mycursor.execute(sql, values)
                mydb.commit()

            print("Data inserted into Channel_details table successfully.")

        except mysql.connector.Error as err:
            print("Error executing MySQL operation:", err)
        finally:
            if mycursor:
                mycursor.close()
            if mydb:
                mydb.close()
                print("MySQL connection closed.")
    else:
        print("Failed to establish MySQL connection.")
        return "Failed to establish MySQL connection."
    
#converting datatimeformat
def published_date_conversion(dt_str):
    dt_str=dt_str.replace("z","")
    dt_object=datetime.fromisoformat(dt_str)
    dt_object=dt_object.replace(tzinfo=timezone.utc)
    formatted_timedate=dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_timedate



#creating table for video details
def Video_Details_Table(video_df):
    mydb, mycursor = connect_to_mysql()
    if mydb and mycursor:
        try:
            mycursor.execute("SHOW TABLES LIKE 'Video_details'")
            table_exists = mycursor.fetchone()

            if not table_exists:
                mycursor.execute('''CREATE TABLE  Video_details(
                    Channel_id VARCHAR(255),
                    Video_Id VARCHAR(255) PRIMARY KEY,
                    Video_Name VARCHAR(255) NOT NULL,
                    Video_Description TEXT,
                    Tags VARCHAR(255) NOT NULL,
                    PublishedAt DATETIME,
                    View_Count INT NOT NULL,
                    Like_Count INT NOT NULL,
                    Dislike_Count INT NOT NULL,
                    Favorite_Count INT NOT NULL,
                    Comment_Count INT NOT NULL,
                    Duration INT NOT NULL,
                    Thumbnail VARCHAR(255),
                    Caption_Status VARCHAR(255)
                )''')
                mydb.commit()
                print("Video_details table created successfully.")  

            #Inserting Values into Video Details Table
            for index, row in video_df.iterrows():
                try:
                    thumbnail = row["Thumbnail"]
                    if isinstance(thumbnail, dict):
                        thumbnail = json.dumps(thumbnail)  #Converting dictionary to JSON string
                    if len(thumbnail) > 255:  
                        thumbnail = thumbnail[:255]

                    tags = row["Tags"]
                    if isinstance(tags, str) and len(tags) > 255:
                        tags = tags[:255]  # Truncate tags if longer than 255 characters
                    if not tags:
                        tags = ""

                    # Convert duration string (ISO 8601 format) to total seconds
                    duration_seconds = convert_duration(row["Duration"])
                    if duration_seconds is None:
                        continue
                    
                    #Inserting valur into video details
                    sql = '''INSERT INTO Video_details (
                        Channel_id,
                        Video_Id,
                        Video_Name,
                        Video_Description,
                        Tags,
                        PublishedAt,
                        View_Count,
                        Like_Count,
                        Dislike_Count,
                        Favorite_Count,
                        Comment_Count,
                        Duration,
                        Thumbnail,
                        Caption_Status
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

                    values = (
                        row["Channel_id"],
                        row["Video_Id"],
                        row["Video_Name"],
                        row["Video_Description"],
                        tags,
                        published_date_conversion(row["PublishedAt"]),
                        row["View_Count"],
                        row["Like_Count"],
                        row["Dislike_Count"],
                        row["Favorite_Count"],
                        row["Comment_Count"],
                        duration_seconds, 
                        thumbnail,
                        row["Caption_Status"]
                    )

                    mycursor.execute(sql, values)
                    mydb.commit()
                    print("Data inserted into Channel_details table successfully.")

                except mysql.connector.Error as err:
                    if err.errno == 1406:
                        print(f"Data too long for column 'Tags' for Video_Id {row['Video_Id']}")
                    else:
                        print(f"Error inserting row for Video_Id {row['Video_Id']}: {err}")

        except mysql.connector.Error as err:
            print(f"Error accessing MySQL: {err}")
        finally:
            if mycursor:
                mycursor.close()
            if mydb:
                mydb.close()
                print("MySQL connection closed.")

#converting datatime format
def published_date_conversion(dt_str):
    dt_str = dt_str.replace("z", "")
    dt_object = datetime.fromisoformat(dt_str)
    dt_object = dt_object.replace(tzinfo=timezone.utc)
    formatted_timedate = dt_object.strftime('%Y-%m-%d %H:%M:%S')

#converting duration format
def convert_duration(duration_str):
    pattern=r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match=re.match(pattern,duration_str)
    if not match:
        return None
    hours=int(match.group(1) or 0)
    minutes=int(match.group(2) or 0)
    seconds=int(match.group(3) or 0)
    seconds=hours*3600+minutes*60+seconds
    return seconds



#creating table for comment details
def Comment_Details_Table(comment_df):
    mydb, mycursor = connect_to_mysql()
    
    if mydb and mycursor:
        try:
            mycursor.execute("SHOW TABLES LIKE 'Comment_details'")
            table_exists = mycursor.fetchone()

            if not table_exists:
                mycursor.execute('''CREATE TABLE Comment_details(Channel_id VARCHAR(255),
                                    Comment_Id VARCHAR(255) PRIMARY KEY,
                                    Video_Id VARCHAR(50),
                                    Comment_Text TEXT,
                                    Comment_Author VARCHAR(255) NOT NULL,
                                    Comment_PublishedAt DATETIME)''')

                mydb.commit()

            #Inserting values into Comment Details Table
            for index,row in comment_df.iterrows():
                sql='''INSERT INTO Comment_details(Channel_id,
                                    Comment_Id,
                                    Video_Id,
                                    Comment_Text,
                                    Comment_Author,
                                    Comment_PublishedAt
                                    )
                                    VALUES(%s,%s,%s,%s,%s,%s)'''

                Values=(row["Channel_id"],
                        row["Comment_Id"],
                            row["Video_Id"],
                            row["Comment_Text"],
                            row["Comment_Author"],
                            published_date_conversion(row["Comment_PublishedAt"])
                            )
                mycursor.execute(sql,Values)
                mydb.commit()
                print("Comment_Details_Table created successfully.")
        except mysql.connector.Error as err:
            print("Error executing MySQL operation:", err)
        finally:
            if mycursor:
                mycursor.close()
            if mydb:
                mydb.close()
                print("MySQL connection closed.")
    else:
        print("Failed to establish MySQL connection.")
        return "Failed to establish MySQL connection."

#converting datatime format
def published_date_conversion(dt_str):
    dt_str=dt_str.replace("z","")
    dt_object=datetime.fromisoformat(dt_str)
    dt_object=dt_object.replace(tzinfo=timezone.utc)
    formatted_timedate=dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_timedate



#function to upload all the channel details,video details, comment details into MySQL Database
def Tables(channel_df, video_df, comment_df):
    Channel_Details_Table(channel_df,)
    Video_Details_Table(video_df)
    Comment_Details_Table(comment_df)

    return "Tables Created Successfully"



#Function to display Channel Table
def show_channels_table():
    mydb, mycursor = connect_to_mysql()
    if mydb and mycursor:
        mycursor=mydb.cursor(dictionary=True) 
        mycursor.execute("SELECT * FROM Channel_details")
        Channel_list=mycursor.fetchall()
        print(Channel_list)
        if Channel_list:
            channel_df1=st.dataframe(Channel_list)
        else:
            st.write("No records found")
            return None
        return channel_df1
    else:
        return "Failed to establish MySQL connection."
    


#Function to display Videos Table
def show_videos_table():
    mydb,mycursor=connect_to_mysql()
    if mydb and mycursor:
        mycursor=mydb.cursor(dictionary=True)
        mycursor.execute("SELECT * FROM Video_details")
        video_list=mycursor.fetchall()
        print(video_list)
        if video_list:
            video_df1=st.dataframe(video_list)
        else:
            st.write("No records found.")
            return None
        return video_df1
    else:
        return "Failed to establish MySQL connection."
    


#Function to display Comments Table
def show_comments_table():
    mydb,mycursor=connect_to_mysql()
    if mydb and mycursor:
        mycursor=mydb.cursor(dictionary=True)
        mycursor.execute("SELECT * FROM Comment_details")
        comment_list=mycursor.fetchall()
        print(comment_list)
        if comment_list:
            comment_df1=st.dataframe(comment_list)
        else:
            st.write("No records found.")
            return None
        return comment_df1
    else:
        return "Failed to establish MySQL connection."
    


#Function to check if the channel id already exists
def channel_exist(channel_id):
    mydb,mycursor=connect_to_mysql()
    if mydb and mycursor:
        mycursor=mydb.cursor(dictionary=True)
        mycursor.execute("SELECT EXISTS(SELECT 1 FROM Channel_details WHERE Channel_id=%s)", (channel_id,))
        exists = mycursor.fetchone()
        if exists:
            exists_value = list(exists.values())[0]
            print("Channel_id already exists")
            return exists_value == 1
        else:
            print("No result found")
    else:
        return "Failed to establish MySQL connection."



#Streamlit Section
logo=Image.open("youtube_logo.jpg")
st.set_page_config(page_title="YouTube App",page_icon=logo)


#creating sidebar option menu
with st.sidebar:
    selected=option_menu("",["Home","DataHarvesting","DataWarehousing","QueryData"])


#Homepage
if selected=="Home":
    st.title(":red[YOUTUBE DATAHARVESTING AND DATAWAREHOUSING]")
    def load_lottiefile(filepath: str):
        with open(filepath,"r") as f:
            return json.load(f)
    lottie_coding=load_lottiefile(r"C:\My Setups\Youtube Project\coding.json")
    st.lottie(
        lottie_coding,
        width=500,
        height=500,
    )


#DataHarvesting Zone
elif selected=="DataHarvesting":
    st.markdown("""<h1 style='text-align: center; color:red;'>DataHarvesting</h1>""",unsafe_allow_html=True)

    channel_id=st.text_input("Enter the Channel Id")

    mydb,mycursor=connect_to_mysql()
    if st.button("Collect and Store Data"):
        if mydb and mycursor:
            print(channel_exist(channel_id))
            if (channel_exist(channel_id)):
                st.success("Channel details already exists.")
            else:
                channel_df,video_df,comment_df=information_collection(channel_id)
                Tables(channel_df, video_df, comment_df)
                st.success("Data Collected and Stored Succesfuuly")
                #mydb,mycursor.close()
        else:
            st.error("Failed to connect MySQL Database")
        

#DataWarehousing Zone
elif selected=="DataWarehousing":
    mydb,mycursor=connect_to_mysql()
    st.markdown("""<h1 style='text-align: center; color:red;'>DataWarehousing</h1>""",unsafe_allow_html=True)
    def get_all_channels():
        mycursor=mydb.cursor()
        mycursor.execute("SELECT Channel_id FROM Channel_details")
        all_channels_list=mycursor.fetchall()
        return [channel[0] for channel in all_channels_list]
    def display_tables(channel_id):
        pass
    if mydb and mycursor:
        all_channels=get_all_channels()
        show_table=st.selectbox("CHOOSE THE TABLE FOR VIEW", ("Channels_Table","Videos_Table","Comments_Table"))

        if show_table=="Channels_Table":
            show_channels_table()
        if show_table=="Videos_Table":
            show_videos_table()
        if show_table=="Comments_Table":
            show_comments_table()


#converting duration format
def convert_duration(duration):
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    return '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)


#Query Zone
if selected=="QueryData":
    st.markdown("""<h1 style='text-align: center; color:red;'>DataWarehousing</h1>""",
                unsafe_allow_html=True
    )
#MySQL Connection
    mydb, mycursor = connect_to_mysql()

    #Creating queries using selectbox
    Question=st.selectbox("Select your question",("1.What are the names of all the videos and their corresponding channels?",
                                                "2.Which channels have the most number of videos, and how many videos do they have?",
                                                "3.What are the top 10 most viewed videos, and their respective channels?",
                                                "4.How many comments were made on each video, and what are their corresponding video names?",
                                                "5.Which videos have the highest number of likes, and what are their corresponding channel names?",
                                                "6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
                                                "7.What is the total number of views for each channel, and what are their corresponding channel names?",
                                                "8.What are the names of all the channels that have published videos in the year 2022?",
                                                "9.What is the average duration of all videos in each channel, and what are their corresponding channel names?",
                                                "10.Which videos have the highest number of comments, and what are their corresponding channel names?"
                                                ))
    

    #qestion 1
    if Question=="1.What are the names of all the videos and their corresponding channels?":
        query1 = '''
            SELECT Video_name, channel_name
            FROM channel_details
            JOIN video_details ON channel_details.channel_id = video_details.channel_id ORDER BY channel_name
        '''
        mycursor.execute(query1)
        q = mycursor.fetchall()
        df = pd.DataFrame(q, columns=["Video Name", "Channel Name"]).reset_index(drop=True)
        df.index += 1
        st.dataframe(df)


    #qestion 2
    elif Question=="2.Which channels have the most number of videos, and how many videos do they have?":
        query2 = '''
            SELECT Channel_name,count(Video_Id) FROM Video_details join channel_details 
            on channel_details.channel_id=video_details.Channel_id GROUP BY Channel_name
        '''
        mycursor.execute(query2)
        q1 = mycursor.fetchall()
        df1 = pd.DataFrame(q1, columns=["Channel Name", "No of Videos"]).reset_index(drop=True)
        df1.index += 1
        st.write(df1)
        fig, ax = plt.subplots(figsize=(10, 6))
        sb.barplot(data=df1, x="Channel Name", y="No of Videos", ax=ax)
        ax.set_xlabel("Channel Name")
        ax.set_ylabel("No of Videos")
        ax.set_title("Total Number of Videos By Channel")
        ax.set_xticklabels(df1["Channel Name"], rotation=45, ha="right")
        st.pyplot(fig)


    #qestion 3
    elif Question=="3.What are the top 10 most viewed videos, and their respective channels?":
        query3 = '''
            SELECT Channel_Name,Video_Name,View_Count From Video_details 
            JOIN Channel_details ON Channel_details.Channel_id=Video_details.Channel_id
            ORDER BY Video_details.View_count DESC LIMIT 10
        '''
        mycursor.execute(query3)
        q2 = mycursor.fetchall()
        df2 = pd.DataFrame(q2, columns=["Channel Name", "Video Name","Total Views"]).reset_index(drop=True)
        df2.index += 1
        st.dataframe(df2)
        fig, ax = plt.subplots(figsize=(10, 6))
        sb.barplot(data=df2, x="Video Name", y="Total Views", ax=ax)
        ax.set_xlabel("Video Name")
        ax.set_ylabel("Total Views")
        ax.set_title("Top 10 Most Viewed Videos")
        ax.set_xticklabels(df2["Video Name"], rotation=90)
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        st.pyplot(fig)


    #qestion 4
    elif Question=="4.How many comments were made on each video, and what are their corresponding video names?":
        query4 = '''
            SELECT Comment_count,Video_name FROM Video_details ORDER BY Comment_count DESC LIMIT 10
        '''
        mycursor.execute(query4)
        q3 = mycursor.fetchall()
        df3 = pd.DataFrame(q3, columns=["Comment Count", "Video Name"]).reset_index(drop=True)
        df3.index += 1
        st.dataframe(df3)
        fig, ax = plt.subplots(figsize=(10, 6))
        sb.barplot(data=df3, x="Video Name", y="Comment Count", ax=ax)
        ax.set_xlabel("Video Name")
        ax.set_ylabel("Comment Count")
        ax.set_title("Total No of Comments")
        ax.set_xticklabels(df3["Video Name"], rotation=90)
        st.pyplot(fig)


    #qestion 5
    elif Question=="5.Which videos have the highest number of likes, and what are their corresponding channel names?":
        query5 = '''
            SELECT Channel_Name,Video_Name,Like_Count FROM Video_Details 
            JOIN Channel_Details ON Channel_Details.Channel_Id=Video_Details.Channel_Id 
            ORDER BY Like_Count DESC LIMIT 10
        '''
        mycursor.execute(query5)
        q4 = mycursor.fetchall()
        df4 = pd.DataFrame(q4, columns=["Channel Name","Video name","No of Likes"]).reset_index(drop=True)
        df4.index += 1
        st.dataframe(df4)
        fig, ax = plt.subplots(figsize=(10, 6))
        sb.barplot(data=df4, x="Video name", y="No of Likes", ax=ax)
        ax.set_xlabel("Video name")
        ax.set_ylabel("No of Likes")
        ax.set_title("Highest Number of Likes")
        ax.set_xticklabels(df4["Video name"], rotation=90)
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        st.pyplot(fig)


    #qestion 6
    elif Question=="6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?":
        query6 = '''
            SELECT Video_Name,Like_Count,Dislike_Count FROM Video_Details 
        '''
        mycursor.execute(query6)
        q5 = mycursor.fetchall()
        df5 = pd.DataFrame(q5, columns=["Video Name","No of Likes","No of Dislikes"]).reset_index(drop=True)
        df5.index += 1
        st.dataframe(df5)
        
        
    #qestion 7
    elif Question=="7.What is the total number of views for each channel, and what are their corresponding channel names?":
        query7 = '''
            SELECT Channel_Name,Channel_Views FROM Channel_Details 
        '''
        mycursor.execute(query7)
        q6 = mycursor.fetchall()
        df6 = pd.DataFrame(q6, columns=["Channel Name","Total Views"]).reset_index(drop=True)
        df6.index += 1
        st.dataframe(df6)
        df6["Total Views in k"] = df6["Total Views"] / 1000
        fig, ax = plt.subplots(figsize=(10, 6))
        sb.barplot(data=df6, x="Channel Name", y="Total Views in k", ax=ax)
        ax.set_xlabel("Channel Name")
        ax.set_ylabel("Total Views")
        ax.set_title("Total Number of Views")
        ax.set_xticklabels(df6["Channel Name"], rotation=90)
        st.pyplot(fig)


    #qestion 8
    elif Question=="8.What are the names of all the channels that have published videos in the year 2022?":
        query8 = '''
            SELECT Channel_Name, PublishedAt FROM Video_details 
            JOIN Channel_details 
            ON Channel_details.channel_id=Video_details.channel_id 
            WHERE YEAR(PublishedAt)=2022
        '''
        mycursor.execute(query8)
        q7 = mycursor.fetchall()
        df7 = pd.DataFrame(q7, columns=["Channel Name","Published Year(2022)"]).reset_index(drop=True)
        df7.index += 1
        st.dataframe(df7)


    #qestion 9
    elif Question=="9.What is the average duration of all videos in each channel, and what are their corresponding channel names?":
        query9 = '''
            SELECT Channel_Name,AVG(Duration) FROM Video_Details join channel_details 
            on channel_details.channel_id=video_details.channel_id 
            group by Channel_Name 
        '''
        mycursor.execute(query9)
        q8 = mycursor.fetchall()    
        results_formatted = [(channel_name, convert_duration(avg_duration)) for channel_name, avg_duration in q8]

        df8 = pd.DataFrame(results_formatted, columns=["Channel Name","Average Duration"]).reset_index(drop=True)
        df8.index += 1
        st.dataframe(df8)
        df8 = df8.sort_values(by="Average Duration")
        fig, ax = plt.subplots(figsize=(10, 6))
        sb.barplot(data=df8, x="Channel Name", y="Average Duration", ax=ax)
        ax.set_xlabel("Channel Name")
        ax.set_ylabel("Average Duration")
        ax.set_title("Average Duration of Channels")
        ax.set_xticklabels(df8["Channel Name"], rotation=90)
        st.pyplot(fig)


    #qestion 10
    elif Question=="10.Which videos have the highest number of comments, and what are their corresponding channel names?":
        query9 = '''
            SELECT Channel_Name,Video_Name,Comment_count FROM Video_details
            JOIN Channel_details 
            ON Channel_details.channel_id=Video_details.channel_id 
            ORDER BY Video_details.Comment_Count DESC LIMIT 10
        '''
        mycursor.execute(query9)
        q9 = mycursor.fetchall()
        df9 = pd.DataFrame(q9, columns=["Channel Name","Video Name","No of Comment"]).reset_index(drop=True)
        df9.index += 1
        st.dataframe(df9)
        fig, ax = plt.subplots(figsize=(10, 6))
        sb.barplot(data=df9, x="Video Name", y="No of Comment", ax=ax)
        ax.set_xlabel("Video Name")
        ax.set_ylabel("No of Comment")
        ax.set_title("Highest Number of Comments")
        ax.set_xticklabels(df9["Video Name"], rotation=90)
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        st.pyplot(fig)

