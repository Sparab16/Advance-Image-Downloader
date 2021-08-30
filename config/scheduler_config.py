from apscheduler.executors.pool import ThreadPoolExecutor

# Configuring the APScheduler
jobstores = {
}

executors = {
    'default': ThreadPoolExecutor(20),

}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}