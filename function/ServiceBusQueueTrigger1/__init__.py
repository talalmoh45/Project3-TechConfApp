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
        user = 'talaladmin',
        password = '0541431847Aa',
        host = 'tecno-server.postgres.database.azure.com'
    )

    cursor = connection.cursor()

    try:
        # TODO: Get notification message and subject from database using the notification_id
        cursor.execute('SELECT message, subject FROM notification WHERE id={};'.format(notification_id))
        result = cursor.fetchall()
        subject, message = result[0][0], result[0][1]
        # TODO: Get attendees email and name
        cursor.execute('SELECT email, name FROM attendees;')
        att = cursor.fetchall()

        # TODO: Loop through each attendee and send an email with a personalized subject
        for (email, first_name) in att:
            mail = Mail(
                from_email = 'talal.moh45@hotmail.com',
                to_emails = email,
                subjet = subject,
                content = Content("text/plain", "Hello this is TechConf Reminder")
            )

        try:
            SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
            SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
            sendgrid = SendGridAPIClient(SENDGRID_API_KEY)
            sendgrid.send(mail)
            
        except error:
            logging.error('cannot send email')


        status = "Notified {} attendees".format(len(att))

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        cursor.execute("UPDATE notification SET status = '{}', completed_date = '{}' WHERE id = {};".format(status, datetime.utcnow(), notification_id))
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        connection.rollback()
    finally:
        # TODO: Close connection
        cursor.close()
        connection.close()