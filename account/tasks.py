from django.core.mail import send_mail
from .models import FailedEmailTasks
from celery import shared_task, Task

# Define a custom Task class to handle failure scenarios
class CallbackTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        This method is called if the task throws an exception.
        
        Parameters:
        - exc: The exception raised by the task.
        - task_id: Unique id of the failed task.
        - args: Original arguments for the task that failed.
        - kwargs: Original keyword arguments for the task that failed.
        - einfo: Exception information object.
        
        Here, we log the exception details to our FailedEmailTasks model, which can be used for debugging or retrying the task later.
        """
        FailedEmailTasks.objects.create(
            task_id=task_id, 
            exc=str(exc), 
            args=args, 
            kwargs=kwargs, 
            einfo=str(einfo)
        )

# Decorate the function with shared_task to turn it into a Celery task with additional settings.
@shared_task(bind=True, base=CallbackTask, max_retries=2)
def send_email_task(self, subject, message, from_email, recipient_list, html_message):
    """
    This is the Celery task for sending emails.

    Parameters:
    - subject: Email subject
    - message: Email plain text content
    - from_email: Sender email address
    - recipient_list: List of recipient email addresses
    - html_content: HTML content for rich text emails
    
    If the task fails, Celery will attempt to retry it based on the defined max_retries parameter.
    """
    try:
        send_mail(
            subject, 
            message, 
            from_email, 
            recipient_list, 
            html_message=html_message
        )
    except Exception as exc:
        # If an exception occurs, retry the task after a delay.
        self.retry(exc=exc, countdown=60)  # countdown is the delay before the retry, in seconds.
 