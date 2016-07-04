# coding: utf-8

from __future__ import unicode_literals
from contextlib import contextmanager

from fabric.context_managers import cd, path, shell_env, prefix
from fabric.contrib import django
from fabric.contrib.files import (append, contains, sed, uncomment, exists,
                                  upload_template)
from fabric.decorators import task
from fabric.operations import sudo, run, prompt, local
from fabric.state import env
from fabric.utils import abort
from unipath import Path


django.project('dezede')
from cachalot.api import invalidate as invalidate_cachalot
from django.conf import settings


GIT_REPOSITORY = 'https://github.com/dezede/dezede.git'
PROJECT_PATH = '/dezede/src'
RELATIVE_WORKON_HOME = '.virtualenvs'
VIRTUALENV_NAME = 'dezede'
DB_NAME = settings.DATABASES['default']['NAME']
DB_NAME_TEST = settings.DATABASES['default'].get('TEST_NAME',
                                                 'test_' + DB_NAME)
DB_USER = settings.DATABASES['default']['USER']
REDIS_SOCKET = '/tmp/redis.sock'
REDIS_CONF = '/etc/redis/redis.conf'
REMOTE_BACKUP = '/dezede/backups/dezede.backup'
LOCAL_BACKUP = './backups/dezede.backup'


def set_env():
    env.project_path = Path(PROJECT_PATH)
    env.home = Path(run('echo $HOME', quiet=True))
    env.virtual_env = env.home.child(RELATIVE_WORKON_HOME, VIRTUALENV_NAME)


@contextmanager
def workon_dezede(settings_module='dezede.settings.prod'):
    set_env()
    with cd(env.project_path):
        with path(env.virtual_env.child('bin'), behavior='prepend'):
            with shell_env(DJANGO_SETTINGS_MODULE=settings_module):
                yield


def add_elasticsearch_repo():
    sudo('wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch '
         '| apt-key add -')
    append('/etc/apt/sources.list.d/elasticsearch.list',
           'deb http://packages.elastic.co/elasticsearch/1.7/debian '
           'stable main', use_sudo=True)


def install_less_css():
    result = run('lessc', warn_only=True, quiet=True)
    if result.return_code:
        sudo('npm install -g less@2.5.3')
        sudo('ln -s /usr/bin/nodejs /usr/bin/node', warn_only=True)


def upgrade_ubuntu():
    sudo('apt-get update')
    sudo('apt-get upgrade')


def install_ubuntu():
    add_elasticsearch_repo()
    upgrade_ubuntu()
    sudo('apt-get install '
         'git mercurial '
         'postgresql postgresql-server-dev-all postgis '
         'redis-server elasticsearch default-jre '
         'python3.5 python3-pip python3.5-dev virtualenvwrapper '
         # For image thumbnailing and conversion.
         'libjpeg-dev '
         # For CSS generation.
         'npm '
         # For media files analysis.
         'libav-tools '
         # For lxml.
         'libxml2-dev libxslt1-dev '
         # For PDF generation.
         'texlive-xetex fonts-linuxlibertine texlive-latex-recommended '
         'texlive-lang-french texlive-latex-extra texlive-fonts-extra')
    install_less_css()
    sudo('systemctl enable elasticsearch')
    sudo('systemctl start elasticsearch')


def can_connect_postgresql():
    result = run('psql -U %s %s -c ""' % (DB_USER, DB_NAME),
                 warn_only=True, quiet=True)
    return not result.return_code


def can_connect_redis():
    result = run('redis-cli -s "%s" ECHO ""' % REDIS_SOCKET,
                 warn_only=True, quiet=True)
    return not result.return_code


def config_postgresql():
    if can_connect_postgresql():
        return

    pg_hba = '/etc/postgresql/9.*/main/pg_hba.conf'
    trust_rule = 'local %s,%s %s trust' % (DB_NAME, DB_NAME_TEST, DB_USER)
    if not contains(pg_hba, trust_rule, exact=True, use_sudo=True):
        previous_line = '# Database administrative login by Unix domain socket'
        sed(pg_hba, previous_line, '&\\n' + trust_rule, use_sudo=True)
    sudo('systemctl restart postgresql')

    for sql_command in (
            'CREATE USER %s SUPERUSER;' % DB_USER,
            'CREATE DATABASE %s OWNER %s;' % (DB_NAME, DB_USER),
            'CREATE EXTENSION postgis;'):
        sudo('psql -c "%s"' % sql_command, user='postgres', warn_only=True)


def config_redis():
    if can_connect_redis():
        return

    uncomment(REDIS_CONF,
              r'^#\s*unixsocket %s$' % REDIS_SOCKET.replace('/', '\/'),
              use_sudo=True)
    uncomment(REDIS_CONF, r'^#\s*unixsocketperm 700$', use_sudo=True)
    sed(REDIS_CONF, 'unixsocketperm 700', 'unixsocketperm 777',
        use_sudo=True)

    sudo('systemctl restart redis-server')


def update_submodules():
    with workon_dezede():
        run('git submodule init')
        run('git submodule update')


def clone():
    if exists(PROJECT_PATH):
        return

    sudo('mkdir -p "%s"' % PROJECT_PATH)
    sudo('chown %s "%s"' % (env.user, PROJECT_PATH))
    run('git clone "%s" "%s"' % (GIT_REPOSITORY, PROJECT_PATH))
    update_submodules()


def mkvirtualenv():
    set_env()

    if exists(env.virtual_env):
        return

    venv_wrapper = '/usr/share/virtualenvwrapper/virtualenvwrapper.sh'
    workon_home = env.home.child(RELATIVE_WORKON_HOME)
    bashrc = ('export WORKON_HOME="%s"\n'
              'source "%s"\n' % (workon_home, venv_wrapper))
    append(env.home.child('.bashrc'), bashrc)
    run('mkdir -p "%s"' % workon_home)
    with prefix('source "%s"' % venv_wrapper):
        run('mkvirtualenv -p /usr/bin/python3.4 %s' % VIRTUALENV_NAME)


def pip_install():
    with workon_dezede():
        run('pip3 install -r requirements/base.txt')
        run('pip3 install -r requirements/prod.txt')


def collectstatic():
    with workon_dezede():
        run('./manage.py collectstatic --noinput')


@task
def set_permissions():
    with workon_dezede():
        if not exists('media'):
            run('mkdir media')
        run('chmod -R o-rwx *', warn_only=True)
        run('chmod -R o+rx static media')


def migrate_db():
    with workon_dezede():
        run('./manage.py migrate')


@task
def install():
    install_ubuntu()

    config_postgresql()
    config_redis()

    clone()

    mkvirtualenv()
    pip_install()

    migrate_db()

    collectstatic()
    set_permissions()


@task
def restart():
    sudo('supervisorctl restart dezede:*')


@task
def update():
    upgrade_ubuntu()

    with workon_dezede():
        run('git pull')
        update_submodules()
        run('find . -name "*.pyc" -delete')

    pip_install()
    migrate_db()
    collectstatic()

    restart()


@task
def update_index():
    with workon_dezede():
        run('./manage.py update_index')


@task
def deploy(domain='dezede.org', ip='127.0.0.1', port=8000, workers=9,
           timeout=300):
    set_env()

    sudo('apt-get install '
         'supervisor '  # Daemonizes Django (using gunicorn) & rq
         'nginx')  # HTTP server

    context = env.copy()
    context.update(ip=ip, port=port, workers=int(workers), timeout=timeout)
    upload_template(
        'prod/supervisor.conf', '/etc/supervisor/conf.d/dezede.conf',
        context=context, use_jinja=True, use_sudo=True)

    ssl_folder = '/etc/letsencrypt/live/dezede.org/'
    ssl_certificate = ssl_folder + 'fullchain.pem'
    ssl_key = ssl_folder + 'privkey.pem'
    sudo('mkdir -p "%s"' % ssl_folder)
    sudo('touch "%s"' % ssl_certificate)
    sudo('touch "%s"' % ssl_key)
    context.update(server_name=domain,
                   ssl_certificate=ssl_certificate, ssl_key=ssl_key)
    available = '/etc/nginx/sites-available/dezede'
    upload_template('prod/nginx', available,
                    context=context, use_jinja=True, use_sudo=True)
    sudo('unlink /etc/nginx/sites-enabled/default', warn_only=True)
    sudo('ln -s "%s" /etc/nginx/sites-enabled' % available, warn_only=True)
    sudo('systemctl restart nginx')

    with workon_dezede():
        sed('dezede/settings/prod.py',
            'ALLOWED_HOSTS = \[\]', r"ALLOWED_HOSTS = \[\x27%s\x27\]" % domain)

    restart()


@task
def reset_remote_db():
    sure = prompt('Are you sure you want to reset the database?',
                  default='n', validate='[yn]') == 'y'
    if not sure:
        abort('Database reset canceled.')
    sudo("psql -c 'DROP DATABASE %s;'" % DB_NAME, user='postgres')
    sudo("psql -c 'CREATE DATABASE %s OWNER %s;'" % (DB_NAME, DB_USER),
         user='postgres')
    migrate_db()


@task
def save_remote_db():
    run('pg_dump -U %s -Fc -b -v -f "%s" %s'
        % (DB_USER, REMOTE_BACKUP, DB_NAME))
    local('rsync "%s":"%s" "%s"' % (env.hosts[0], REMOTE_BACKUP, LOCAL_BACKUP))


@task
def restore_saved_db():
    local('sudo -u postgres dropdb %s' % DB_NAME)
    local('sudo -u postgres createdb %s' % DB_NAME)
    local('sudo -u postgres pg_restore -e -d %s -j 5 "%s"'
          % (DB_NAME, LOCAL_BACKUP))
    invalidate_cachalot()


@task
def clone_remote_db():
    save_remote_db()
    restore_saved_db()
