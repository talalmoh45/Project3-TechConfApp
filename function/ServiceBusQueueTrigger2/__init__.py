import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    # TODO: Get connection to database
    connection = psycopg2.connect(
        dbname ='techconfdb',
        user = 'taloo',
        password = '0541431847Aa',
        host = 'techconfserver.postgres.database.azure.com'
    )

    cursor = connection.cursor()

    try:
        # TODO: Get notification message and subject from database using the notification_id
        cursor.execute("SELECT message, subject FROM notification where id = {};".format(notification_id))
        notification = cursor.fetchone()
        subject, body = notification[0][0], notification[0][1]

        # TODO: Get attendees email and name
        cursor.execute("SELECT email, first_name, last_name FROM attendee;")
        attendees = cursor.fetchall()

        # TODO: Loop through each attendee and send an email with a personalized subject
        for (email, first_name) in attendees:
            mail = Mail(
                from_email = 'talal.moh45@hotmail.com',
                to_emails = email,
                subject = subject,
                plain_text_content = "Hello this is TechConf Reminder"
            )

        try:
            SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
            SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
            sendgrid = SendGridAPIClient(SENDGRID_API_KEY)
            sendgrid.send(mail)
            
        except Exception as e:
            logging.error('cannot send email', e)

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified

        status = "Notified {} attendees".format(len(attendees))
        completed_date = datetime.utcnow()

        cursor.execute("Update notification set status = {}, completed_date = {} where id = {};".format(status, completed_date, notification_id))
        connection.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        connection.rollback()
    finally:
        # TODO: Close connection
        cursor.close()
        connection.close()