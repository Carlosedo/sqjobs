from __future__ import absolute_import

from django.conf import settings
from django.core.management.base import BaseCommand

from sqjobs import create_sqs_worker, create_sqs_broker, create_eager_broker
from sqjobs.contrib.django.djsqjobs.utils import register_all_jobs

from sqjobs.contrib.django.djsqjobs.beat import Beat


class Command(BaseCommand):
    help = 'sqjobs commands'
    args = True

    def handle(self, *args, **options):
        if args[0] == 'worker':
            if len(args) != 2:
                self.help_text()
                return

            self._execute_worker(args[1])

        elif args[0] == 'beat':
            if len(args) not in (2, 3):
                self.help_text()
                return

            self._execute_beat(*args[1:])

    def _execute_worker(self, queue_name):
        worker = create_sqs_worker(
            queue_name=queue_name,
            access_key=settings.SQJOBS_SQS_ACCESS_KEY,
            secret_key=settings.SQJOBS_SQS_SECRET_KEY,
            region=settings.SQJOBS_SQS_REGION,
            use_ssl=getattr(settings, 'SQJOBS_SQS_USE_SSL', True),
        )

        register_all_jobs(worker)
        worker.execute()

    def _execute_beat(self, sleep_interval, skip_jobs=True):
        broker = create_sqs_broker(
            access_key=settings.SQJOBS_SQS_ACCESS_KEY,
            secret_key=settings.SQJOBS_SQS_SECRET_KEY,
            region=settings.SQJOBS_SQS_REGION,
            use_ssl=getattr(settings, 'SQJOBS_SQS_USE_SSL', True),
        )
        beat = Beat(broker, int(sleep_interval), skip_jobs)
        register_all_jobs(beat)
        beat.run_forever()

    def help_text(self):
        self.stdout.write('Use:')
        self.stdout.write('./manage.py sqjobs worker QUEUE_NAME')
        self.stdout.write('./manage.py sqjobs beat SLEEP_INTERVAL [SKIP_JOBS]')
