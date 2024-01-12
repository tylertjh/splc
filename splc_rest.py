#gui testing
import RPi.GPIO as GPIO
import webbrowser, sys
import time
import tkinter
from tkinter import *
import tkinter.font
import sqlite3 as sql
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from cryptography.fernet import Fernet
from tkinter import messagebox



Gui = tkinter.Tk()
Login = Toplevel()
Gui.title("WMAT417900 SPLC RESET")
Gui.config(background= "#caccce")
Gui.attributes('-fullscreen',True)
Login.title("WMAT417900 SPLC RESET")
Login.config(background= '#caccce')
Login.attributes('-fullscreen',True)

#fonts used throughout
Font1 = tkinter.font.Font(family = 'Arial', size = 28, weight = 'bold')
Font2 = tkinter.font.Font(family = 'Arial', size = 14, weight = 'bold')
Font3 = tkinter.font.Font(family = 'Arial', size = 18, weight = 'bold')
Font4 = tkinter.font.Font(family = 'Arial', size = 12)
Font5 = tkinter.font.Font(family = 'Arial', size = 24, weight = 'bold')

#loading button images
button1 = PhotoImage(file='/home/pi/Documents/.SPLC/SPLC_BUTTON100.png')
button2 = PhotoImage(file='/home/pi/Documents/.SPLC/SPLC_BUTTON102.png')

# Create a database connection
conn = sql.connect("/home/pi/Documents/.SPLC/user_data.db")
c = conn.cursor()

# Create the requests table
c.execute('''CREATE TABLE IF NOT EXISTS requests
             (username text, password text, email text)''')

# Create the authorized table
c.execute('''CREATE TABLE IF NOT EXISTS authorized
             (username text, password text, email text)''')

# Create the admin table
c.execute('''CREATE TABLE IF NOT EXISTS admin
             (username text, password text, email text)''')

# Commit the changes to the database
conn.commit()

#opening encryption key file
with open("/home/pi/Documents/.SPLC/key.key", 'rb') as key_file:
    key = key_file.read()



#decrypt password using keyfile
def decrypt_password(encrypted_password):
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(encrypted_password).decode()

#encrypt password using keyfile
def encrypt_password(password):
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(password.encode())

#check entered credentials on sql table
def check_credentials(username, password):
    c.execute("SELECT * FROM authorized WHERE username=?", (username,))
    row = c.fetchone()
    if row is None:
        c.execute("SELECT * FROM admin WHERE username=?", (username,))
        row = c.fetchone()
        if row is None:
            return False
    encrypted_password = row[1]
    decrypted_password = decrypt_password(encrypted_password)
    if password != decrypted_password:
        return False
    return True

#runs login verify if users hits enter key
def on_enter_click_login(event):
    login_verify()
    
#gets username and password. Checks if credentials are valid
def login_verify():
    
    username = username_verify.get()
    password = password_verify.get()

    if check_credentials(username, password):
        username_login_entry.delete(0, END)
        password_login_entry.delete(0, END)
        login_sucess()
        show_user_managment(username)

    else:
       login_failed()
#if user is on admin sql table show the user management button on gui    
def show_user_managment(username):
    c.execute("SELECT * FROM admin WHERE username=?", (username,))
    row = c.fetchone()
    if row is None:
        return False
    user_management_button.place(anchor='center', relx=0.1, rely=0.9)
    exit_button.place(anchor=CENTER, relx=.9, rely=.9)
    
    
#After successful login_verify this hides login screen and shows button panel. Also logs the user out after a time period.
def login_sucess():
    Gui.deiconify()
    Login.withdraw()
    Gui.after(300000, Gui.withdraw)
    Login.after(300000, Login.deiconify)
    
#After unsuccesful long_verify the login failed window displays.
def login_failed():
    global login_failed_screen
    login_failed_screen = Toplevel()
    login_failed_screen.title("Login Failed!")
    screen_width = login_failed_screen.winfo_screenwidth()
    screen_height = login_failed_screen.winfo_screenheight()
    app_width = 250
    app_height = 150
    y = (screen_height/2)-(app_height/2)
    x=960-(app_width/2)
    login_failed_screen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
    Label(login_failed_screen, text="Login Failed!", font= Font3).place(anchor=CENTER, relx=.5, rely=.3)
    Button(login_failed_screen, text="Ok", font= Font4, command=delete_login_failed).place(anchor=CENTER, relx=.5, rely=.6)
    
    
#closes login failed screen
def delete_login_failed():
    login_failed_screen.destroy()

#closes Gui and shows login screen. if user management is open it closes that upon logout
def logout():
    Login.deiconify()
    Gui.withdraw()
    user_management_button.place_forget()
    user_management_screen.destroy()
    exit_button.place_forget()
    

#closes usermanagement screen if gui auto logs out
def on_unmap(event):
    user_management_screen.destroy()

#request access
def request_access():
    global request_access_screen
    request_access_screen = Toplevel()
    request_access_screen.title("Request Access")
    screen_width = request_access_screen.winfo_screenwidth()
    screen_height = request_access_screen.winfo_screenheight()
    app_width = 550
    app_height = 325
    y = (screen_height/2)-(app_height/2)
    x=960-(app_width/2)
    request_access_screen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
    username = StringVar()
    password = StringVar()
    email = StringVar()
    
    def on_enter_click_submit(event):
        submit_verify()

    
    def send_email():
        username1 = username_entry.get()
        password1 = password_entry.get()
        email1 = email_entry.get()

        # Encrypt the password
        encrypted_password = encrypt_password(password1)

        # Insert the user data into the database
        c.execute("INSERT INTO requests VALUES (?, ?, ?)", (username1, encrypted_password, email1))
        conn.commit()

        smtp_server = "mail.micron.com"
        sender_email = f"{email.get()}"
        receiver_email = "thamer@micron.com"
        cc_email = "jbobrien@micron.com"

        #Creation of MIMEMultipart object
        message = MIMEMultipart()

        #setup of the Object Header
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Cc'] = cc_email
        message['Subject'] = "WMAT417900 SPLC Button Access Request"

        #HTML Setup
        html = '''<html>
        <head>
        <head/>
        <body>
        <p>
        <font>
        Hello, 
        <br>
        <br>
        I would like access to WMAT417900 SPLC remote button.
        <br>
        <br>
        My username is: {}
        </br>
        </br>
        Thank you
        </font>
        </p>

        </body>
        </html>'''.format(username.get())

        #Creation of MIMEtext part with HTML
        htmlpart = MIMEText(html, 'html')

        #part attach
        message.attach(htmlpart)

        #sending the email
        with smtplib.SMTP(smtp_server) as server:
            server.send_message(message)
            server.quit()
         # Clear the input fields
        username_entry.delete(0, END)
        password_entry.delete(0, END) 
        request_access_screen.destroy()

      
    #checks to make sure all fields for requesting acces are filled
    def submit_verify():
        email_entry1 = email_entry.get()
        username_entry1 = username_entry.get()
        password_entry1 = password_entry.get()
        if len(email_entry1 and username_entry1 and password_entry1)== 0:
            submit_fail()
        else:
            send_email()
            submit_success()
    def on_enter_click_submit_fail(event):
        delete_submit_fail()
    #pop up if not all fields are filled out when requesting access.         
    def submit_fail():
        global submit_fail_screen
        submit_fail_screen = Toplevel()
        submit_fail_screen.title("Request failed!")
        screen_width = submit_fail_screen.winfo_screenwidth()
        screen_height = submit_fail_screen.winfo_screenheight()
        app_width = 350
        app_height = 150
        y = (screen_height/2)-(app_height/2)
        x=960-(app_width/2)
        submit_fail_screen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
        Label(submit_fail_screen, text="Request Failed!", font= Font3).place(anchor=CENTER, relx=.5, rely=.3)
        Label(submit_fail_screen, text="Please fill in all information for request!", font= Font4).place(anchor=CENTER, relx=.5, rely=.5)
        Button(submit_fail_screen, text="Ok", font= Font4, command=delete_submit_fail).place(anchor=CENTER, relx=.5, rely=.75)
        submit_fail_screen.bind("<Return>", on_enter_click_submit_fail)
        
     #closes submit fail screen    
    def delete_submit_fail():
        submit_fail_screen.destroy()
    def on_enter_click_submit_success(event):
        request_access_close()
    #pop up to show that your submission for requesting access was submitted successfully
    def submit_success():
        global submit_success_screen
        submit_success_screen = Toplevel()
        submit_success_screen.title("Request Submitted!")
        screen_width = submit_success_screen.winfo_screenwidth()
        screen_height = submit_success_screen.winfo_screenheight()
        app_width = 550
        app_height = 325
        y = (screen_height/2)-(app_height/2)
        x=960-(app_width/2)
        submit_success_screen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
        Label(submit_success_screen, font=Font3,text="Request Submitted!").place(anchor=CENTER, relx=.5, rely=.4)
        Label(submit_success_screen, font=Font4,text="Administrators will contact you when your access has been approved.").place(anchor=CENTER, relx=.5, rely=.5)
        Button(submit_success_screen, font=Font4, text="Ok", width=12, height=1, command= request_access_close).place(anchor=CENTER, relx=.5, rely=.65)
        submit_success_screen.bind("<Return>", on_enter_click_submit_success)
        
    #closes those screens    
    def request_access_close():
        submit_success_screen.destroy()
        request_access_screen.destroy()
        
    #cancels the request access
    def cancel():
        request_access_screen.destroy()
        
    #tkinter request access screen stuff    
    Label(request_access_screen, text = "").pack()
    Label(request_access_screen, font=Font3,text="Please enter details below").pack()
    Label(request_access_screen, font=Font4, text = "Once access is approved the username and password \n entered here will be your login.").pack()
    Label(request_access_screen, font=Font4, text = "Do not use your Micron password!").pack()
    email_label = Label(request_access_screen, font=Font2, text="Email:")
    email_label.pack()
    email_entry = Entry(request_access_screen, font=Font4, textvariable=email)
    email_entry.pack()
    username_label = Label(request_access_screen, font=Font2, text="Username:")
    username_label.pack()
    username_entry = Entry(request_access_screen, font=Font4, textvariable=username)
    username_entry.pack()
    password_label = Label(request_access_screen, font=Font2, text="Password:")
    password_label.pack()
    password_entry = Entry(request_access_screen, font=Font4, textvariable=password, show='*')
    password_entry.pack()
    Label(request_access_screen, text="").pack()
    Button(request_access_screen, text="Submit", font=Font4, command=submit_verify).place(ancho=CENTER, relx=0.42, rely=0.90)
    Button(request_access_screen, text="Cancel", font=Font4, command=cancel).place(ancho=CENTER, relx=0.57, rely=0.90)
    
    request_access_screen.bind("<Return>", on_enter_click_submit)
    
#user management screen to approve requests, delete users and promote users to administrators    
def user_management():
    global user_management_screen
    user_management_screen = Toplevel(Gui)
    user_management_screen.title("User Management")
    screen_width = user_management_screen.winfo_screenwidth()
    screen_height = user_management_screen.winfo_screenheight()
    app_width = 200
    app_height = 325
    y = (screen_height/2)-(app_height/2)
    x=960-(app_width/2)
    user_management_screen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
    user_management_screen.wm_attributes("-topmost", 2)
    Label(user_management_screen, font=Font2, text="User Management").place(anchor='center', relx=0.5, rely=0.1)
    Button(user_management_screen, text='Access Requests', font=Font4, command=access_requests).place(anchor='center', relx=0.5, rely=0.3)
    Button(user_management_screen, text='Authorized Users', font=Font4, command=authorized_users).place(anchor='center', relx=0.5, rely=0.5)
    Button(user_management_screen, text='Administrators', font=Font4, command=admin_users).place(anchor='center', relx=0.5, rely=0.7)

#access requests screen pop up
def access_requests():
    global access_requests_screen
    global user_management_screen
    access_requests_screen = Toplevel(user_management_screen)
    access_requests_screen.title("Access Requests")
    screen_width = access_requests_screen.winfo_screenwidth()
    screen_height = access_requests_screen.winfo_screenheight()
    app_width = 200
    app_height = 325
    y = (screen_height/2)-(app_height/2)
    x=960-(app_width/2)
    access_requests_screen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
    access_requests_screen.wm_attributes("-topmost", 1)
   
    user_management_screen.withdraw()
    # Get the usernames from the requests table
    c.execute("SELECT username FROM requests")
    requests_usernames = [row[0] for row in c.fetchall()]
    requests_usernames.sort()
    # Create the listboxes to display the usernames
    global requests_listbox
    requests_listbox = Listbox(access_requests_screen)
    for username in requests_usernames:
        requests_listbox.insert(END, username)
        
    #moves user from requests to authorized table in database and sends approval email
    def move_to_authorized():
    
        global receiver_email
      
        if messagebox.askyesno("Confirmation", "Are you sure you want to approve this user?", parent=access_requests_screen):
            selection = requests_listbox.curselection()
            if selection:
                selected_username = requests_listbox.get(selection)
                c.execute("SELECT password, email FROM requests WHERE username=?", (selected_username,))
                row = c.fetchone()
                selected_email = row[1]
                c.execute("INSERT INTO authorized VALUES (?, ?, ?)", (selected_username, row[0], selected_email))
                c.execute("DELETE FROM requests WHERE username=?", (selected_username,))
                conn.commit()

                smtp_server = "mail.micron.com"
                sender_email = "WMAT417900-SPLC_BUTTON-no-reply@micron.com"
                receiver_email = selected_email

                #send confirmation email to user approved.
                message = MIMEMultipart()

                #setup of the Object Header
                message['From'] = sender_email
                message['To'] = receiver_email
                message['Subject'] = "DO NOT REPLY - WMAT417900 SPLC Button Access Request Has Been Approved"

                #HTML Setup
                html = '''<html>
                <head>
                <head/>
                <body>
                <p>
                <font>
                Congratulations!
                <br>
                <br>
                Your access request to WMAT417900 SPLC remote button has been approved by the administrators
                </br>
                </br>
                Have a great day.
                </font>
                </p>
                </body>
                </html>'''

                #Creation of MIMEtext part with HTML
                htmlpart = MIMEText(html, 'html')

                #part attach
                message.attach(htmlpart)

                #sending the email
                with smtplib.SMTP(smtp_server) as server:
                    server.send_message(message)
                    server.quit()

                requests_listbox.delete(selection)
            else:
                messagebox.showerror("Error", "Please select an item to approve.")

    # deletes user from requests table in database and sends email about request being denied
    def deny():
        if messagebox.askyesno("Confirmation", "Are you sure you want to deny this user?", parent=access_requests_screen):
            selection = requests_listbox.curselection()
            if selection:
                selected_username = requests_listbox.get(selection)
                c.execute("SELECT password, email FROM requests WHERE username=?", (selected_username,))
                row = c.fetchone()
                selected_email = row[1]
                c.execute("DELETE FROM requests WHERE username=?", (selected_username,))
                conn.commit()

                smtp_server = "mail.micron.com"
                sender_email = "WMAT417900-SPLC_BUTTON-no-reply@micron.com"
                receiver_email = selected_email

                #send confirmation email to user approved.
                message = MIMEMultipart()

                #setup of the Object Header
                message['From'] = sender_email
                message['To'] = receiver_email
                message['Subject'] = "DO NOT REPLY - WMAT417900 SPLC Button Access Request Has Been Denied"

                #HTML Setup
                html = '''<html>
                <head>
                <head/>
                <body>
                <p>
                <font>
                Hello,
                <br>
                <br>
                Your access request to WMAT417900 SPLC remote button has been denied by the administrators.
                <br>
                <br>
                Contact Brodie O'brien with questions
                </br>
                </br>
                Have a great day.
                </font>
                </p>

                </body>
                </html>'''

                #Creation of MIMEtext part with HTML
                htmlpart = MIMEText(html, 'html')

                #part attach
                message.attach(htmlpart)

                #sending the email
                with smtplib.SMTP(smtp_server) as server:
                    server.send_message(message)
                    server.quit()

                requests_listbox.delete(selection)
            else:
                messagebox.showerror("Error", "Please select an item to deny.")

    requests_listbox.place(anchor='center', relx=0.5, rely=0.45 )
    Label(access_requests_screen, text="Access Requests", font=Font2).place(anchor='center',relx=0.5, rely=0.1)
    move_to_authorized_button = Button(access_requests_screen, text="Approve", font=Font4, command=move_to_authorized)
    move_to_authorized_button.place(anchor='center', relx=0.5, rely=0.81)
    deny_request_button = Button(access_requests_screen, text="Deny", font=Font4, command=deny)
    deny_request_button.place(anchor='center', relx=0.5, rely=0.93)
    access_requests_screen.protocol("WM_DELETE_WINDOW", close_accces_requests)
   
#closes request access screena and shows the usermanagement screen again  
def close_accces_requests():
    global access_requests_screen
    global user_management_screen
    access_requests_screen.destroy()
    user_management_screen.deiconify()

#authorized user managements screen. Delete users or promote to administrators.
def authorized_users():
    global authorized_users_screen
    authorized_users_screen = Toplevel(Gui)
    authorized_users_screen.title("Authorized Users")
    screen_width = authorized_users_screen.winfo_screenwidth()
    screen_height = authorized_users_screen.winfo_screenheight()
    app_width = 200
    app_height = 325
    y = (screen_height/2)-(app_height/2)
    x=960-(app_width/2)
    authorized_users_screen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
    user_management_screen.withdraw()
     # Get the usernames from the authorized table
    c.execute("SELECT username FROM authorized")
    authorized_usernames = [row[0] for row in c.fetchall()]
    authorized_usernames.sort()
    global authorized_listbox
    authorized_listbox = Listbox(authorized_users_screen)
    for username in authorized_usernames:
        authorized_listbox.insert(END, username)
    authorized_listbox.place(anchor='center', relx=0.5, rely=0.45 )
    Label(authorized_users_screen, text="Authorized Users", font=Font2).place(anchor='center',relx=0.5, rely=0.1)

    #moves user from authorized user table in data base to admin table in data base
    def move_to_admin():
        if messagebox.askyesno("Confirmation", "Are you sure you want to make this user an admin?", parent=authorized_users_screen):
            selection= authorized_listbox.curselection()
            if selection:
                selected_username = authorized_listbox.get(selection)
                c.execute("SELECT password, email FROM authorized WHERE username=?", (selected_username,))
                row=c.fetchone()
                selected_password=row[0]
                selected_email=row[1]
                c.execute("INSERT INTO admin VALUES (?, ?, ?)", (selected_username, selected_password, selected_email))
                c.execute("DELETE FROM authorized WHERE username=?", (selected_username,))
                conn.commit()
                authorized_listbox.delete(selection)
            else:
                messagebox.showerror("Error", "Please select an user to move to administrators.")
    
    move_to_admin_button = Button(authorized_users_screen, text="Make Admin", font=Font4, command=move_to_admin)
    move_to_admin_button.place(anchor='center', relx=0.5, rely=0.81)
    delete_authorized_button = Button(authorized_users_screen, text="Delete", font=Font4, command=delete_authorized)
    delete_authorized_button.place(anchor='center', relx=0.5, rely=0.93)
    authorized_users_screen.protocol("WM_DELETE_WINDOW", close_authorized_users)

#closes authorized user management screen and opens user management screen
def close_authorized_users():
    authorized_users_screen.destroy()
    user_management_screen.deiconify()

#deletes selected user from authorized user table
def delete_authorized():
    if messagebox.askyesno("Confirmation", "Are you sure you want to delete this user?", parent=authorized_users_screen):
            selection= authorized_listbox.curselection()
            if authorized_listbox.curselection():
                selected_username = authorized_listbox.get(authorized_listbox.curselection())
                c.execute("DELETE FROM authorized WHERE username=?", (selected_username,))
                conn.commit()
                authorized_listbox.delete(authorized_listbox.curselection())
            else:
                messagebox.showerror("Error", "Please select a user to delete.")

#deletes selected admin from admin table
def delete_admin():
    if messagebox.askyesno("Confirmation", "Are you sure you want to delete this user?", parent=admin_users_screen):
            selection= admin_listbox.curselection()
            if admin_listbox.curselection():
                selected_username = admin_listbox.get(admin_listbox.curselection())
                c.execute("DELETE FROM admin WHERE username=?", (selected_username,))
                conn.commit()
                admin_listbox.delete(admin_listbox.curselection())
            else:
                messagebox.showerror("Error", "Please select a user to delete.")
#admin user management screen. Delete admins
def admin_users():
    global admin_users_screen
    global admin_listbox
    global authorized_listbox
    admin_users_screen=Toplevel(user_management_screen)
    admin_users_screen.title("Administrators")
    screen_width = admin_users_screen.winfo_screenwidth()
    screen_height = admin_users_screen.winfo_screenheight()
    app_width = 200
    app_height = 325
    y = (screen_height/2)-(app_height/2)
    x=960-(app_width/2)
    admin_users_screen.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
    admin_users_screen.wm_attributes("-topmost", 1)

    user_management_screen.withdraw()

    # Get the usernames from the requests table
    c.execute("SELECT username FROM admin")
    admin_usernames = [row[0] for row in c.fetchall()]
    admin_usernames.sort()
    admin_listbox = Listbox(admin_users_screen)
    for username in admin_usernames:
        admin_listbox.insert(END, username)
    admin_listbox.place(anchor='center', relx=0.5, rely=0.45 )
    Label(admin_users_screen, text="Administrators", font=Font2).place(anchor='center',relx=0.5, rely=0.1)
    delete_admin_button = Button(admin_users_screen, text="Delete", font=Font4, command=delete_admin)
    delete_admin_button.place(anchor='center', relx=0.5, rely=0.865)
    admin_users_screen.protocol("WM_DELETE_WINDOW", close_admin_users)

#closes admin user management screen and opens user management screen
def close_admin_users():
    admin_users_screen.destroy()
    user_management_screen.deiconify()

#closes gui and login screen
def close():
    Gui.quit()
    Login.quit()
#when button is clicked changes image to button2 to simulate the button lighting up.     
def clicked(Event):
    SPLC.config(image=button2)
 
#when button is released image changes back and toggles GPIO pins to trigger relays.  
def released(Event):
    SPLC.config(image=button1)
    relay1 = 38
    relay2 = 40
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(relay1, GPIO.OUT)
    GPIO.setup(relay2, GPIO.OUT)
    GPIO.output(relay1, True)
    GPIO.output(relay2, True)
    time.sleep(0.5)
    GPIO.output(relay1, False)
    GPIO.output(relay2, False)
   
   
#login screen format
Label(Login, text="WMAT417900 SPLC RESET", font=Font1, background= "#caccce").place(anchor=CENTER, relx=.5, rely=.4)
Label(Login, text="Please enter details below to login", font=Font3, background= "#caccce").place(anchor=CENTER, relx=.5, rely=.44)

username_verify = StringVar()
password_verify = StringVar()

Label(Login, text="Username:", background= "#caccce", font=Font2).place(anchor=CENTER, relx=.5, rely=.47)
username_login_entry = Entry(Login, textvariable=username_verify, font= Font4)
username_login_entry.place(anchor=CENTER, relx=.5, rely=.50)
Label(Login, text="Password:", background= "#caccce", font=Font2).place(anchor=CENTER, relx=.5, rely=.53)
password_login_entry = Entry(Login, textvariable=password_verify, font=Font4, show= '*')
password_login_entry.place(anchor=CENTER, relx=.5, rely=.56)
Button(Login, text="Login", font= Font4, command = login_verify).place(anchor=CENTER, relx=.5, rely=.61)
Register= Button(Login, text="Request Access", font=Font4, command=request_access).place(anchor=CENTER, relx=.5, rely=0.66)
    
#main gui window format     
Label(Gui,text='WMAT417900 SPLC RESET', font = Font1, bg='#caccce', padx = 50, pady = 50).place(anchor=CENTER, relx= .5, rely= .55)
SPLC = Button(Gui, image=button1, bg='#caccce', fg='#caccce', activeforeground='#caccce', activebackground='#caccce', relief=SUNKEN, borderwidth=0, highlightthickness=0)
SPLC.bind('<Button-1>', clicked)
SPLC.bind('<ButtonRelease-1>', released) 
SPLC.place(anchor=CENTER, relx= .5, rely= .45)
Button(Gui, text="Logout", font= Font4, command=logout).place(anchor=CENTER, relx=.5, rely=.6)
exit_button = Button(Gui, text="Exit", font=Font4, command=close)
exit_button.place_forget()
user_management_button = Button(Gui, text='User Management', font=Font4, command=user_management)
user_management_button.place_forget()
 
 #runs login_verify() if users hits enter on login screen
Login.bind("<Return>", on_enter_click_login)

#closes user management screen if gui withdraws.  
Gui.bind("<Unmap>", on_unmap)

#main loop
Gui.withdraw()
Gui.mainloop()
exit(0)
