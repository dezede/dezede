from contextlib import contextmanager

from fabric.context_managers import cd, path, shell_env, prefix, warn_only
from fabric.contrib import django
from fabric.contrib.files import (append, contains, sed, uncomment, exists,
                                  upload_template)
from fabric.decorators import task
from fabric.operations import sudo, run, prompt, local, put
from fabric.state import env
from fabric.utils import abort
from pathlib import Path


django.project('dezede')
import django
django.setup()
from django.conf import settings


GIT_REPOSITORY = 'https://github.com/dezede/dezede.git'
PROJECT_PATH = '/dezede/src'
RELATIVE_WORKON_HOME = '.virtualenvs'
VIRTUALENV_NAME = 'dezede'
DB_NAME = settings.DATABASES['default']['NAME']
DB_NAME_TEST = settings.DATABASES['default'].get('TEST_NAME',
                                                 'test_' + DB_NAME)
DB_USER = settings.DATABASES['default']['USER']
REDIS_SOCKET = '/var/run/redis/redis-server.sock'
REDIS_CONF = '/etc/redis/redis.conf'
REMOTE_BACKUP = '/dezede/backups/dezede.backup'
LOCAL_BACKUP = './backups/dezede.backup'


def set_env():
    env.project_path = Path(PROJECT_PATH)
    env.home = Path(run('echo $HOME', quiet=True))
    env.virtual_env = env.home / RELATIVE_WORKON_HOME / VIRTUALENV_NAME


@contextmanager
def workon_dezede(settings_module='dezede.settings.prod'):
    set_env()
    with cd(f'{env.project_path}'):
        with path(f"{env.virtual_env / 'bin'}", behavior='prepend'):
            with shell_env(DJANGO_SETTINGS_MODULE=settings_module):
                yield


def install_less_css():
    result = run('lessc', warn_only=True, quiet=True)
    if result.return_code:
        sudo('npm install')
        sudo('ln -s /usr/bin/nodejs /usr/bin/node', warn_only=True)


def upgrade_ubuntu():
    sudo('apt update')
    sudo('apt upgrade')
    sudo('apt autoclean')
    sudo('apt autoremove')


def install_ubuntu():
    upgrade_ubuntu()
    sudo('apt-get install '
         'git mercurial '
         'postgresql postgresql-server-dev-all postgis '
         'redis-server default-jre '
         'python3.6 python3-pip python3.6-dev virtualenvwrapper '
         # For image thumbnailing and conversion.
         'libjpeg-dev '
         # For CSS generation.
         'npm '
         # For media files analysis.
         'libav-tools '
         # For elasticsearch.
         'docker.io '
         # For lxml.
         'libxml2-dev libxslt1-dev '
         # For PDF generation.
         'texlive-xetex fonts-linuxlibertine '
         'texlive-lang-french texlive-fonts-extra')

    install_less_css()


def can_connect_postgresql():
    result = run(f'psql -U {DB_USER} {DB_NAME} -c ""',
                 warn_only=True, quiet=True)
    return not result.return_code


def can_connect_redis():
    result = run(f'redis-cli -s "{REDIS_SOCKET}" ECHO ""',
                 warn_only=True, quiet=True)
    return not result.return_code


def config_postgresql():
    if can_connect_postgresql():
        return

    pg_hba = '/etc/postgresql/9.*/main/pg_hba.conf'
    trust_rule = f'local {DB_NAME},{DB_NAME_TEST} {DB_USER} trust'
    if not contains(pg_hba, trust_rule, exact=True, use_sudo=True):
        previous_line = '# Database administrative login by Unix domain socket'
        sed(pg_hba, previous_line, '&\\n' + trust_rule, use_sudo=True)
    sudo('systemctl restart postgresql')

    for sql_command in (
            f'CREATE USER {DB_USER} SUPERUSER;',
            f'CREATE DATABASE {DB_NAME} OWNER {DB_USER};',
            'CREATE EXTENSION postgis;'):
        sudo(f'psql -c "{sql_command}"', user='postgres', warn_only=True)


def config_redis():
    if can_connect_redis():
        return

    escaped_socket = REDIS_SOCKET.replace('/', '\/')
    uncomment(REDIS_CONF, fr'^#\s*unixsocket {escaped_socket}$',
              use_sudo=True)
    uncomment(REDIS_CONF, r'^#\s*unixsocketperm 700$', use_sudo=True)
    sed(REDIS_CONF, 'unixsocketperm 700', 'unixsocketperm 777',
        use_sudo=True)

    sudo('systemctl restart redis-server')


def config_elasticsearch():
    upload_template(
        'prod/elasticsearch.service',
        '/etc/systemd/system/elasticsearch.service',
        use_sudo=True,
    )
    sudo('systemctl enable elasticsearch')


def update_submodules():
    with workon_dezede():
        run('git submodule init')
        run('git submodule update')


def clone():
    if exists(PROJECT_PATH):
        return

    sudo(f'mkdir -p "{PROJECT_PATH}"')
    sudo(f'chown {env.user} "{PROJECT_PATH}"')
    run(f'git clone "{GIT_REPOSITORY}" "{PROJECT_PATH}"')
    update_submodules()


def mkvirtualenv():
    set_env()

    if exists(env.virtual_env):
        return

    venv_wrapper = '/usr/share/virtualenvwrapper/virtualenvwrapper.sh'
    workon_home = env.home / RELATIVE_WORKON_HOME
    bashrc = (f'export WORKON_HOME="{workon_home}"\n'
              f'source "{venv_wrapper}"\n')
    append(f"{env.home / '.bashrc'}", bashrc)
    run(f'mkdir -p "{workon_home}"')
    with prefix(f'source "{venv_wrapper}"'):
        run(f'mkvirtualenv -p /usr/bin/python3.6 {VIRTUALENV_NAME}')


def pip_install():
    with workon_dezede():
        run('pip3 install -r requirements/base.txt')
        run('pip3 install -r requirements/prod.txt')


def npm_install():
    with workon_dezede():
        run('npm install')


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
    config_elasticsearch()

    clone()

    mkvirtualenv()
    pip_install()
    npm_install()

    collectstatic()

    migrate_db()

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
        run('find . '
            '-path "./media/*" -prune -o '
            '-path "./static/*" -prune -o '
            '-path "./node_modules/*" -prune -o '
            '-path "./.git/*" -prune -o '
            r'-name "*.pyc" -exec rm "{}" \;')

    pip_install()
    npm_install()
    migrate_db()
    collectstatic()

    restart()


@task
def update_index():
    with workon_dezede():
        run('./manage.py update_index')


@task
def deploy(domain='dezede.org', ip='127.0.0.1', port=8000, workers=9,
           timeout=6 * 60 * 60):
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
    sudo(f'mkdir -p "{ssl_folder}"')
    sudo(f'touch "{ssl_certificate}"')
    sudo(f'touch "{ssl_key}"')
    context.update(server_name=domain,
                   ssl_certificate=ssl_certificate, ssl_key=ssl_key)
    put('prod/nginx_default.conf', '/etc/nginx/sites-available/default',
        use_sudo=True)
    available = '/etc/nginx/sites-available/dezede'
    upload_template('prod/nginx.conf', available,
                    context=context, use_jinja=True, use_sudo=True)
    sudo(f'ln -s "{available}" /etc/nginx/sites-enabled', warn_only=True)
    sudo('systemctl restart nginx')

    with workon_dezede():
        sed('dezede/settings/prod.py',
            'ALLOWED_HOSTS = \[\]', fr"ALLOWED_HOSTS = \[\x27{domain}\x27\]")

    restart()


@task
def reset_remote_db():
    sure = prompt('Are you sure you want to reset the database?',
                  default='n', validate='[yn]') == 'y'
    if not sure:
        abort('Database reset canceled.')
    sudo(f"psql -c 'DROP DATABASE {DB_NAME};'", user='postgres')
    sudo(f"psql -c 'CREATE DATABASE {DB_NAME} OWNER {DB_USER};'",
         user='postgres')
    migrate_db()


@task
def save_remote_db():
    run(f'pg_dump -U {DB_USER} -Fc -b -v -f "{REMOTE_BACKUP}" {DB_NAME}')
    local(f'mkdir -p "{Path(LOCAL_BACKUP).parent}"')
    local(f'rsync --info=progress2 '
          f'"{env.hosts[0]}":"{REMOTE_BACKUP}" "{LOCAL_BACKUP}"')


@task
def restore_saved_db():
    local(f'sudo -u postgres dropdb --if-exists {DB_NAME}')
    local(f'sudo -u postgres dropuser --if-exists {DB_USER}')
    local(f'sudo -u postgres createuser --login -g clients {DB_USER}')
    local(f'sudo -u postgres createdb --owner {DB_USER} {DB_NAME}')
    with warn_only():
        for parent in Path(LOCAL_BACKUP).resolve().parents:
            local(f'chmod o+x {parent}')
    local(f'chmod o+r {LOCAL_BACKUP}')
    local(f'sudo -u postgres psql dezede -c "DROP SCHEMA public;"')
    local(f'sudo -u postgres pg_restore -e -d {DB_NAME} '
          f'-j 5 "{Path(LOCAL_BACKUP).resolve()}"')
    local(f'sudo -u postgres psql dezede '
          f'-c "ALTER SCHEMA public OWNER TO dezede;"')


@task
def clone_remote_db():
    save_remote_db()
    restore_saved_db()
