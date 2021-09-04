import datetime
from dateutil import tz

from apscheduler.schedulers.background import BackgroundScheduler

from config import scheduler_config
from Helper import HelperClass
from Logger import Logging

# Configuring the logger
logger_obj = Logging('Advance Image Downloader')  # Creating a custom based logger
logger_obj.initialize_logger()  # Instantiating the logger object

# Creating a scheduler object for scheduling the jobs
ap_scheduler = BackgroundScheduler(jobstores=scheduler_config.jobstores, executors=scheduler_config.executors,
                                   job_defaults=scheduler_config.job_defaults,
                                   timezone='Asia/Kolkata')
# Starting the scheduler
ap_scheduler.start()


class ScheduleJob:
    global ap_scheduler

    def __init__(self):
        """
        This function initializes the Scheduler object
        :param ap_scheduler(object): apscheduler object
        """
        try:
            self.scheduler = ap_scheduler
        except Exception as e:
            logger_obj.print_log('(Scheduler.py(__init__) - Something went wrong ' + str(e), 'exception')
            raise Exception(e)

    def insert_request(self, search_query, date, time, no_images, email, req_id):
        """
        This function adds the current request into the queue for processing
        :param search_query: Search query given by the user
        :param date: Date at which job must run
        :param time: Time at which job must run
        :param no_images: No of images user wants
        :param email: email of the user
        :param req_id: Unique Request Id of the request
        """
        try:
            # Splitting the values for inserting into proper date and time format
            date_list = date.split('-')
            time_list = time.split(':')
            year, month, day = date_list[0], date_list[1], date_list[2]
            hour, minute = time_list[0], time_list[1]

            date_inserted = datetime.datetime(day=int(day), month=int(month), year=int(year), hour=int(hour),
                                              minute=int(minute), tzinfo=tz.gettz('Asia/Kolkata'))

            current_date = datetime.datetime.now(tz.gettz('Asia/Kolkata'))

            print('Current date is {} and Date inserteed is {}'.format(current_date, date_inserted))
            # Checking for if past date and time is inserted
            if current_date <= date_inserted:
                # Creating an object for the Helper class to use the helper methods
                helper = HelperClass()

                # Scheduling the job at particular date and time
                self.scheduler.add_job(helper.helper_image, 'cron',
                                       [search_query, no_images, email, req_id, ScheduleJob()], day=day, month=month,
                                       year=year, hour=hour, minute=minute, id=str(req_id))

            else:
                logger_obj.print_log(
                    '(Scheduler.py(schedule_job) - Something went wrong. You have insert the past date and time',
                    'exception')
                raise Exception("You have inserted the past date and time")

        except Exception as e:
            logger_obj.print_log('(Scheduler.py(schedule_job) - Something went wrong. Inputs might be invalid' + str(e), 'exception')
            raise Exception('Inputs might be invalid')

    def delete_files_job_queue(self, req_id, time_to_delete):
        """
        This function is responsible for deleting the folder, zip files which are created to handle the request
        :param req_id: Unique request ID
        :param time_to_delete: Time to delete after
        :return:
        """
        try:
            current_date = datetime.datetime.now(tz.gettz('Asia/Kolkata'))  # Getting the current datetime value
            delete_time = current_date + datetime.timedelta(minutes=time_to_delete)  # Time to delete the files

            self.scheduler.add_job(HelperClass.helper_delete, 'cron', [req_id], day=delete_time.day,
                                   month=delete_time.month, year=delete_time.year,
                                   hour=delete_time.hour, minute=delete_time.minute, id=str(req_id))
        except Exception as e:
            logger_obj.print_log('(Scheduler.py(delete_files_job_queue) - Something went wrong ' + str(e), 'exception')
            raise Exception(e)
