import sqlite3

# Connect to SQLite database (creates social_media.db if it doesn't exist)
conn = sqlite3.connect('social_media.db')
cursor = conn.cursor()

# Create tables if they don't exist
def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            gmail TEXT UNIQUE,
            age INTEGER,
            gender TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Posts (
            post_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            content TEXT,
            post_date TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Comments (
            comment_id INTEGER PRIMARY KEY,
            post_id INTEGER,
            user_id INTEGER,
            comment TEXT,
            comment_date TEXT,
            FOREIGN KEY (post_id) REFERENCES Posts(post_id),
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    ''')
    
    # Check if tables already have data
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:
        # Add sample data only if tables are empty
        sample_users = [
            ("john_doe", "jdSecure@123", "john.doe@gmail.com", 28, "M"),
            ("alejandro_fernandez", "Alejo@2023", "a.fernandez@yahoo.com", 34, "M"),
            ("giulia_rossi", "giuliaR#99", "g.rossi@outlook.com", 26, "F"),
            ("arjun_menon", "menonPass@1", "arjun.menon@gmail.com", 31, "M"),
            ("priya_sharma", "PSharma_2024", "priya.sharma@rediffmail.com", 24, "F"),
            ("mohammad_ali", "Ali@786peace", "m.ali@gmail.com", 38, "M"),
            ("emily_clark", "EmiClark!32", "emilyc@yahoo.com", 29, "F"),
            ("rahul_verma", "rahulV#88", "rahulv@hotmail.com", 27, "M"),
            ("zainab_khan", "zKhan@secure", "zainab.khan@outlook.com", 25, "F"),
            ("marco_bianchi", "Marco2024!", "marco.b@gmail.com", 33, "M"),
            
            ("isabella_martinez", "IsaMart@321", "isamartinez@gmail.com", 22, "F"),
            ("krishna_iyer", "KriIyer@91", "krishna.iyer@yahoo.com", 35, "M"),
            ("sarah_jones", "sJones@2023", "sarah.jones@outlook.com", 30, "F"),
            ("yusuf_siddiqui", "Yusuf786!", "y.siddiqui@gmail.com", 32, "M"),
            ("manpreet_kaur", "mpKaur#2024", "manpreet.k@rediffmail.com", 27, "F"),
            ("daniel_smith", "danS!234", "dan.smith@yahoo.com", 40, "M"),
            ("ananya_reddy", "Ananya@93", "ananya.r@gmail.com", 23, "F"),
            ("rohit_pandey", "RPandey!56", "rohitp@hotmail.com", 36, "M"),
            ("lucia_gomez", "LuciaG@pass", "lucia.gomez@gmail.com", 28, "F"),
            ("fatima_sheikh", "Fatima#456", "fatima.s@yahoo.com", 29, "F"),
            
            ("anthony_white", "TonyW_123", "a.white@gmail.com", 41, "M"),
            ("vignesh_warrior", "viggy@89", "vignesh.warrior@outlook.com", 26, "M"),
            ("rajat_aggarwal", "rajat#pass", "rajat.aggarwal@yahoo.com", 31, "M"),
            ("maria_lombardi", "Lombardi!23", "maria.l@rediffmail.com", 35, "F"),
            ("ahmed_hassan", "Ahmed@Secure", "ahmed.hassan@gmail.com", 39, "M"),
            ("olivia_brown", "LivBrown$2024", "olivia.brown@outlook.com", 24, "F"),
            ("deepika_nair", "Dnair@2023", "deepika.n@gmail.com", 30, "F"),
            ("sanjay_patel", "SanjayP@44", "s.patel@yahoo.com", 33, "M"),
            ("juan_ramirez", "JuanR_2024", "juan.ramirez@gmail.com", 28, "M"),
            ("samira_khatun", "Samira786!", "samira.khatun@rediffmail.com", 25, "F"),
]

        
        for username, password, gmail, age, gender in sample_users:
            cursor.execute('''
                INSERT INTO Users (username, password, gmail, age, gender)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password, gmail, age, gender))
    
    # Get all user IDs
    cursor.execute("SELECT user_id FROM Users")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT COUNT(*) FROM Posts")
    if cursor.fetchone()[0] == 0:
        # Add sample posts only if table is empty
        sample_posts = [
            # john_doe - 3 posts
            ("john_doe", "Discussed recent political reforms and their impact on local communities. Important times ahead.", "2021-11-12 09:30:00"),
            ("john_doe", "Started learning advanced Python programming for data science projects. Excited to upskill!", "2023-06-25 14:45:00"),
            ("john_doe", "Attended a local basketball game last night, amazing atmosphere and teamwork!", "2024-03-03 19:20:00"),
            
            # alejandro_fernandez - 2 posts
            ("alejandro_fernandez", "Preparing for the summer soccer league. Training hard every day!", "2022-05-18 16:00:00"),
            ("alejandro_fernandez", "Exploring fashion trends in Madrid, love how vintage styles are making a comeback.", "2023-10-09 12:00:00"),

            # giulia_rossi - 3 posts
            ("giulia_rossi", "Attended an insightful webinar on European politics and the future of the EU.", "2020-09-15 10:10:00"),
            ("giulia_rossi", "Experimenting with eco-friendly fashion materials for my design projects.", "2022-11-22 15:30:00"),
            ("giulia_rossi", "Enjoying a photography course to capture urban street styles better.", "2024-07-01 09:00:00"),
            
            # arjun_menon - 1 post
            ("arjun_menon", "Just finished an upskilling course on cloud computing. Ready for new challenges.", "2023-03-10 13:25:00"),
            
            # priya_sharma - 4 posts
            ("priya_sharma", "Exploring sustainable fashion brands that help reduce environmental impact.", "2021-12-02 18:40:00"),
            ("priya_sharma", "Volunteered at an education awareness camp this weekend, very fulfilling experience.", "2022-08-15 10:15:00"),
            ("priya_sharma", "Learning digital marketing strategies to promote local artists and craftsmen.", "2024-01-12 20:05:00"),
            ("priya_sharma", "Enjoyed playing badminton after a long week, great way to stay active!", "2025-04-20 17:50:00"),
            
            # mohammad_ali - 0 posts
            
            # emily_clark - 3 posts
            ("emily_clark", "Started a course on early childhood education; teaching kids is so rewarding.", "2020-10-08 11:30:00"),
            ("emily_clark", "Attended a conference on innovative teaching methodologies last month.", "2022-02-17 09:00:00"),
            ("emily_clark", "Playing tennis every weekend to stay fit and focused.", "2023-07-20 16:10:00"),
            
            # rahul_verma - 2 posts
            ("rahul_verma", "Excited about the upcoming cricket season, hoping my team wins!", "2021-07-19 14:00:00"),
            ("rahul_verma", "Learning about AI applications in healthcare. So much potential!", "2023-11-02 19:45:00"),
            
            # zainab_khan - 4 posts
            ("zainab_khan", "Just enrolled in an advanced SEO course to boost my blogging skills.", "2020-12-14 14:40:00"),
            ("zainab_khan", "Working on content marketing strategies to increase engagement.", "2021-06-10 15:20:00"),
            ("zainab_khan", "Attended a webinar on social media trends for 2023.", "2023-05-07 10:30:00"),
            ("zainab_khan", "Practicing yoga regularly to maintain work-life balance.", "2024-09-11 07:45:00"),
            
            # marco_bianchi - 1 post
            ("marco_bianchi", "Researching the intersection of AI and fashion technology. Fascinating developments.", "2023-03-14 11:15:00"),
            
            # isabella_martinez - 0 posts
            
            # krishna_iyer - 3 posts
            ("krishna_iyer", "Completed a course on machine learning applications in finance.", "2022-09-10 18:20:00"),
            ("krishna_iyer", "Working on an automated deployment pipeline for a project at work.", "2024-05-04 09:50:00"),
            ("krishna_iyer", "Played football with friends over the weekend, great fun and exercise.", "2025-02-01 16:30:00"),
            
            # sarah_jones - 1 post
            ("sarah_jones", "Shopping for sustainable brands is more rewarding than ever.", "2024-09-10 11:20:00"),
            
            # yusuf_siddiqui - 0 posts
            
            # manpreet_kaur - 2 posts
            ("manpreet_kaur", "Volunteered at a local literacy program. Every little effort counts!", "2023-11-08 14:15:00"),
            ("manpreet_kaur", "Preparing for my certification exam on project management.", "2024-03-19 20:10:00"),
            
            # daniel_smith - 2 posts
            ("daniel_smith", "Training for the upcoming marathon. Discipline is key!", "2021-10-30 07:40:00"),
            ("daniel_smith", "Enjoyed a weekend basketball tournament with my team.", "2023-01-14 18:00:00"),
            
            # ananya_reddy - 3 posts
            ("ananya_reddy", "Working on an app UI redesign to improve user experience.", "2024-03-05 14:00:00"),
            ("ananya_reddy", "Learning new JavaScript frameworks to enhance my frontend skills.", "2023-06-15 11:25:00"),
            ("ananya_reddy", "Enjoyed attending a conference on women in tech.", "2022-10-10 16:45:00"),
            
            # rohit_pandey - 1 post
            ("rohit_pandey", "Attended a seminar on environmental policies and their impact.", "2021-12-03 19:45:00"),
            
            # lucia_gomez - 2 posts
            ("lucia_gomez", "Browsing vintage fashion markets, love the unique finds!", "2024-10-23 13:30:00"),
            ("lucia_gomez", "Practicing photography to capture urban street styles.", "2023-08-12 09:10:00"),
            
            # fatima_sheikh - 0 posts
            
            # anthony_white - 1 post
            ("anthony_white", "Playing basketball with friends keeps me energized and focused.", "2025-01-12 20:00:00"),
            
            # vignesh_warrior - 1 post
            ("vignesh_warrior", "Building automated deployment pipelines. DevOps skills in action!", "2024-06-16 09:50:00"),
            
            # rajat_aggarwal - 1 post
            ("rajat_aggarwal", "Preparing for law finals with case studies and mock trials.", "2025-05-01 08:30:00"),
            
            # maria_lombardi - 1 post
            ("maria_lombardi", "Sketching fashion designs inspired by classic Italian styles.", "2023-02-14 13:00:00"),
            
            # ahmed_hassan - 2 posts
            ("ahmed_hassan", "Experimenting with JavaScript frameworks for a new project.", "2021-06-05 20:45:00"),
            ("ahmed_hassan", "Learning cybersecurity fundamentals to secure my applications.", "2022-04-10 10:30:00"),
    
    # olivia_brown - 0 posts
    
    # deepika_nair - 0 posts
    
    # sanjay_patel - 0 posts
    
    # juan_ramirez - 1 post
    ("juan_ramirez", "Preparing for a regional soccer tournament, hope to win!", "2024-09-05 17:15:00"),
    
    # samira_khatun - 0 posts
]

        
        for username, content, post_date in sample_posts:
            cursor.execute('''
                SELECT user_id FROM Users WHERE username = ?
            ''', (username,))
            user_id = cursor.fetchone()[0]
            cursor.execute('''
                INSERT INTO Posts (user_id, content, post_date)
                VALUES (?, ?, ?)
            ''', (user_id, content, post_date))
    
    # Get all post IDs
    cursor.execute("SELECT post_id FROM Posts")
    post_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT COUNT(*) FROM Comments")
    if cursor.fetchone()[0] == 0:
        # Add sample comments only if table is empty
        sample_comments = [
    ("john_doe", 1, "Great insights, thanks for sharing!", "2025-05-15 10:05:00"),
    ("alejandro_fernandez", 1, "Totally agree with this!", "2025-05-15 10:10:00"),
    ("giulia_rossi", 2, "This helped me a lot, appreciate it!", "2025-05-15 11:15:00"),
    ("arjun_menon", 3, "Could be better explained, but nice effort.", "2025-05-15 12:05:00"),
    ("priya_sharma", 5, "Amazing post, keep it up!", "2025-05-15 13:20:00"),
    ("mohammad_ali", 5, "Thanks for sharing!", "2025-05-15 13:45:00"),
    ("emily_clark", 6, "Love the details in this one!", "2025-05-15 14:05:00"),
    ("rahul_verma", 6, "Good work.", "2025-05-15 14:20:00"),
    ("zainab_khan", 7, "Spam comment here! Ignore this!", "2025-05-15 15:10:00"),  # spam
    ("zainab_khan", 7, "Another useless comment.", "2025-05-15 15:15:00"),  # spam
    ("marco_bianchi", 8, "This is very informative.", "2025-05-15 16:00:00"),
    ("marco_bianchi", 9, "Love the way this is presented!", "2025-05-15 16:30:00"),
    ("isabella_martinez", 10, "Helpful and clear explanation.", "2025-05-15 17:05:00"),
    ("krishna_iyer", 11, "I disagree with this part.", "2025-05-15 18:00:00"),
    ("krishna_iyer", 11, "But overall, good job.", "2025-05-15 18:05:00"),
    ("sarah_jones", 12, "Keep sharing such quality content!", "2025-05-15 19:05:00"),
    ("yusuf_siddiqui", 13, "Interesting perspective.", "2025-05-15 20:00:00"),
    ("manpreet_kaur", 14, "www.clickme.com.", "2025-05-15 21:00:00"),
    ("daniel_smith", 15, "Terrible advice, don’t follow this.", "2025-05-15 22:00:00"),  # negative
    ("ananya_reddy", 16, "Thanks for sharing!", "2025-05-15 23:00:00"),
    ("rohit_pandey", 17, "Loved this!", "2025-05-16 00:00:00"),
    ("lucia_gomez", 18, "Awesome content!", "2025-05-16 01:00:00"),
    ("fatima_sheikh", 19, "Very useful post.", "2025-05-16 02:00:00"),
    ("anthony_white", 20, "Want instant money?? - click here www.instantmoney.com", "2025-05-16 03:00:00"),
    ("vignesh_warrior", 20, "Want instant money?? - click here www.instantmoney.com", "2025-05-16 03:15:00"),  # spam
    ("vignesh_warrior", 21, "Another spam, sorry!", "2025-05-16 03:20:00"),  # spam
    ("rajat_aggarwal", 22, "This is great content.", "2025-05-16 04:00:00"),
    ("maria_lombardi", 23, "Well done!", "2025-05-16 05:00:00"),
    ("ahmed_hassan", 24, "Could be improved.", "2025-05-16 06:00:00"),
    ("olivia_brown", 25, "Thanks for the update!", "2025-05-16 07:00:00"),
    ("deepika_nair", 26, "Keep up the good work.", "2025-05-16 08:00:00"),
    ("sanjay_patel", 27, "Not helpful at all.", "2025-05-16 09:00:00"),  # negative
    ("juan_ramirez", 28, "Really useful info.", "2025-05-16 10:00:00"),
    ("samira_khatun", 29, "Love this post!", "2025-05-16 11:00:00"),
    ("john_doe", 30, "Great, looking forward to more.", "2025-05-16 12:00:00"),
    ("alejandro_fernandez", 31, "Thanks for sharing!", "2025-05-16 13:00:00"),
    ("giulia_rossi", 32, "Very clear explanation.", "2025-05-16 14:00:00"),
    ("arjun_menon", 33, "I disagree with some points.", "2025-05-16 15:00:00"),
    ("priya_sharma", 34, "Good job!", "2025-05-16 16:00:00"),
    ("mohammad_ali", 35, "Helpful info.", "2025-05-16 17:00:00"),
    ("emily_clark", 36, "Awesome post!", "2025-05-16 18:00:00"),
    ("rahul_verma", 37, "Thanks for this.", "2025-05-16 19:00:00"),
    ("zainab_khan", 38, "Nice one!", "2025-05-16 20:00:00"),
    ("marco_bianchi", 39, "Spam comment again!", "2025-05-16 21:00:00"),  # spam
    ("marco_bianchi", 40, "Ignore this spam comment.", "2025-05-16 21:05:00"),  # spam
    ("isabella_martinez", 41, "Great insight.", "2025-05-16 22:00:00"),
    ("krishna_iyer", 42, "Thanks for the info.", "2025-05-16 23:00:00"),
    ("sarah_jones", 43, "Looking forward to more posts.", "2025-05-17 00:00:00"),
    ("yusuf_siddiqui", 44, "Not very helpful.", "2025-05-17 01:00:00"),  # negative
    ("manpreet_kaur", 45, "Very informative.", "2025-05-17 02:00:00"),
    ("daniel_smith", 46, "Thanks!", "2025-05-17 03:00:00"),
    ("ananya_reddy", 47, "Great read!", "2025-05-17 04:00:00"),
    ("rohit_pandey", 48, "Interesting post.", "2025-05-17 05:00:00"),
    ("lucia_gomez", 49, "Nice article.", "2025-05-17 06:00:00"),
    ("fatima_sheikh", 50, "Thats so lame!", "2025-05-17 07:00:00")
]

        
        for username, post_id, comment, comment_date in sample_comments:
            cursor.execute('''
                SELECT user_id FROM Users WHERE username = ?
            ''', (username,))
            user_id = cursor.fetchone()[0]
            cursor.execute('''
                INSERT INTO Comments (post_id, user_id, comment, comment_date)
                VALUES (?, ?, ?, ?)
            ''', (post_id, user_id, comment, comment_date))
    
    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database and tables created successfully!")
    conn.close()