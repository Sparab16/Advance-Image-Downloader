from config import email_config
from Cassandra import Cassandra
from Download import Download
from Scrapper import ImageScrapperClass
from Logger import Logging
from Email import SendEmail

logger_obj = Logging('Advance Image Downloader')  # Creating a custom based logger
logger_obj.initialize_logger()  # Instantiating the logger object


class HelperClass:

    def helper_image(self, search_query, no_images, email, req_id, schedule_job):
        """
        this helper method responsible for calling the respective methods for inserting the images into the database
        :param search_query: Search query given by user
        :param no_images: Number of images to download
        :param email: Email of the user
        :param req_id: Unique request ID of the user
        :param schedule_job: scheduler object
        """
        try:
            # Send email about job starts execution
            message = 'Subject: {}\n\n{}'.format('Job scheduling started',
                                                 'Your job has been started and it might take few minutes to complete.'
                                                 ' You will get confirmation and the download link in the mail once the'
                                                 ' process is completed.')

            self.helper_email(email, str(req_id), search_query, message)

            # Initializing the cassandra database object
            cassandra = Cassandra()

            # Connecting to the default keyspace
            cassandra.connect_keyspace()

            # Creating the table if not exists
            cassandra.create_table()

            # Initializing the image_scrapper for web scrapping
            image_scrapper = ImageScrapperClass(no_images)

            # Opening the URL provided in the Chrome tab
            image_scrapper.get_request(search_query)

            # Storing the URL
            image_scrapper.fetch_thumbnails(req_id, email, cassandra)

            self.helper_download(email, search_query, req_id, schedule_job, cassandra)

        except Exception as e:
            logger_obj.print_log('(HelperClass.py(helper_image) - Something went wrong ' + str(e), 'exception')

            # Sending the error message
            error_message = 'Subject: Error in job\n\nThere is some error occurred while performing your job ' \
                            'activities. Would you like to retry again? \n' + email_config.host_name
            self.helper_email(email, message=error_message)

            # Deleting the URL and files which are inserted/created
            self.helper_delete(str(req_id))
            raise Exception(e)

    @staticmethod
    def helper_email(email, req_id=None, search_query=None, message=None):
        """
        This helper method is responsible for calling methods for sending an email
        :param email: Email address of  the receiver
        :param reqs_id: Unique request ID
        :param search_query: Search query of the user
        :param message: Message to be sent
        """
        try:
            if not message:
                message = 'Subject: Your Images are Downloaded\n\nKindly download your images through the following ' \
                          'link. Link is valid for {} minutes\n {}'.format(
                    email_config.time_to_delete_min,
                    email_config.host_name + 'download/' + search_query.replace(' ', '') + '/' + str(req_id))

            # Initializing the email object
            email_obj = SendEmail()
            # Sending the notification
            email_obj.send_notification(email, message)

        except Exception as e:
            logger_obj.print_log('(HelperClass.py(helper_email) - Something went wrong ' + str(e), 'exception')
            raise Exception(e)

    @staticmethod
    def helper_delete(req_id):
        """
        This helper method is responsible for calling the methods to delete the files after some amount of time
        :param req_id: Unique request ID
        """
        try:
            print("Delete operation started")
            logger_obj.print_log('Deleting operation started', 'info')

            # Deleting the files from the system
            Download.delete_file(req_id)

            logger_obj.print_log('All the files are deleted', 'info')
            print("All the files are deleted now")

            # Initializing the cassandra database object
            cassandra = Cassandra()
            logger_obj.print_log('Connected to the cassandra', 'info')
            print('Connected to the cassandra')
            # Connecting to the default keyspace
            cassandra.connect_keyspace()
            # Deleting the database records
            cassandra.delete_url(req_id)
            logger_obj.print_log('Delete operation from cassandra is done', 'info')
            print('Delete operation from the cassandra is done')

        except Exception as e:
            logger_obj.print_log('(HelperClass.py(helper_delete) - Something went wrong ' + str(e), 'exception')
            raise Exception(e)

    def helper_download(self, email, search_query, req_id, schedule_job, cassandra=None):
        """
        This helper method is responsible for calling the methods to download the images over an internet
        :param email: Email address of  the receiver
        :param search_query: Search query of the user
        :param req_id: Unique request ID
        :param schedule_job: SchedulerClass object
        :param cassandra: Cassandra object
        """
        try:
            logger_obj.print_log('Inside the download function', 'info')

            # Initializing the cassandra database object
            if not cassandra:
                cassandra = Cassandra()
                # Connecting to the default keyspace
                cassandra.connect_keyspace()
                logger_obj.print_log('Connection to the database established', 'info')

            # First check whether the req_id exists in the database
            result = cassandra.select_query(req_id)

            if result:
                logger_obj.print_log('Result is found', 'info')

                # Creating the download class object for performing download operations
                download_obj = Download(result)

                str_req_id = str(req_id)

                # Creating directory for saving images
                Download.create_dir(str_req_id)
                logger_obj.print_log('Directory is created', 'info')

                # Downloading Images
                download_obj.download_images(search_query, str_req_id)
                logger_obj.print_log('Images are downloaded over the internet', 'info')

                # Creating a zip file
                Download.create_zip(str_req_id)
                logger_obj.print_log('Zip file is created', 'info')

                # Calling the delete_files function
                schedule_job.delete_files_job_queue(str_req_id, email_config.time_to_delete_min)

                # Sending the mail
                self.helper_email(email, str_req_id, search_query)
            else:
                logger_obj.print_log('(app.py) - Something went wrong You are not allowed to access', 'exception')
                raise Exception('You are not allowed to access or the Link has expired')

        except Exception as e:
            logger_obj.print_log('(app.py) - Something went wrong You are not allowed to access', 'exception')
            raise Exception(e)
