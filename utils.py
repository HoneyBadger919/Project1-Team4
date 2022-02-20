
# code for SMS message
def send(message):
        # Replace the number with your own @ carrier and gmail address and password. *Not secure*
        to_number = '1234567890@vtext.com'
        auth = ('email@gmail.com','password')
        server = smtplib.SMTP('smtp.gmail.com', 587 )
        server.starttls()
        server.login(auth[0], auth[1])
        # Send text message through SMS gateway of destination number
        server.sendmail( auth[0], to_number, message)