import django
import logging
import os
import subprocess
import sys
import time


def test_db_connection():
    conn = django.db.connections['default']
    conn.cursor()


def wait_for_connection():
    logging.info('Waiting for database connection...')
    while True:
        try:
            test_db_connection()
            return
        except django.db.utils.OperationalError:
            pass
        time.sleep(0.5)


def migrate_to_latest_models():
    logging.info('Running migrations...')
    settings = ['--settings', os.environ['DJANGO_SETTINGS_MODULE']]
    cmd = '/var/lib/luminous/bin/luminous-server'
    # PRODUCTION VERSION:
    # subprocess.check_call([cmd, 'makemigrations', '--check', '--noinput'] + settings)
    subprocess.check_call([cmd, 'makemigrations', '--noinput'] + settings)
    subprocess.check_call([cmd, 'migrate', '--noinput'] + settings)


def create_test_user():
    logging.info('Creating test users...')
    from django.contrib.auth.models import User
    u, _ = User.objects.get_or_create(username='test')
    u.set_password('test')
    u.is_staff = True
    from django.contrib.auth.models import Permission
    for p in Permission.objects.all():
        u.user_permissions.add(p)
    u.save()


def run_supervisor():
    logging.info('Running supervisord...')
    return subprocess.call(['supervisord', '-c', '/etc/supervisor/supervisord.conf'])


def main():
    log_format = '[RUN SERVER] %(asctime)-15s: %(levelname)+8s  %(message)s'
    log_kwargs = {'format': log_format, 'level': logging.INFO}
    logging.basicConfig(**log_kwargs)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'luminous_project.settings.dev'
    django.setup()
    wait_for_connection()
    migrate_to_latest_models()
    create_test_user()
    return run_supervisor()


if __name__ == "__main__":
    sys.exit(main())
