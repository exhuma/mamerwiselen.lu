from os import listdir
from os.path import exists
from pipes import quote
import SocketServer
import fabric.api as fab
import fabric.contrib.project as project
import os
import shutil
import sys

from pelican.server import ComplexHTTPRequestHandler


fab.env.roledefs['prod'] = ['dozer.foobar.lu']

# Local path configuration (can be absolute or relative to fabfile)
fab.env.deploy_path = 'output'
DEPLOY_PATH = fab.env.deploy_path

# Remote server configuration
production = 'exhuma@dozer.foobar.lu:22'
dest_path = '/var/www/mamerwiselen.lu/www/htdocs'

# Port for `serve`
PORT = 8000


@fab.task
def process_pdf():
    """
    Removes contacts from PDF documents
    """
    cmd = 'pdftk {fname} cat 1 4-end output {pname}'
    for fname in listdir('wisel_private'):
        if not fname.lower().endswith('.pdf'):
            continue
        basename, _, extension = fname.rpartition('.')
        infile = 'wisel_private/' + basename + '.' + extension
        outfile = 'content/dewisel/' + basename + '-public.pdf'
        thumbnail = 'wisel_thumbnails/' + basename + '.jpg'
        if not exists(outfile):
            fab.local(cmd.format(fname=quote(infile), pname=quote(outfile)))
            fab.local('git add %s' % quote(outfile))

        if not exists(thumbnail):
            fab.local('convert -thumbnail x400 -background white -alpha remove '
                      '%s[0] %s' % (quote(infile), quote(thumbnail)))
            fab.local('git add %s' % quote(thumbnail))


@fab.task
def clean():
    """Remove generated files"""
    if os.path.isdir(DEPLOY_PATH):
        shutil.rmtree(DEPLOY_PATH)
        os.makedirs(DEPLOY_PATH)


@fab.task
def build():
    """Build local version of site"""
    fab.local('pelican -s pelicanconf.py')


@fab.task
def rebuild():
    """`clean` then `build`"""
    clean()
    build()


@fab.task
def regenerate():
    """Automatically regenerate site upon file modification"""
    fab.local('pelican -r -s pelicanconf.py')


@fab.task
def serve():
    """Serve site at http://localhost:8000/"""
    os.chdir(fab.env.deploy_path)

    class AddressReuseTCPServer(SocketServer.TCPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(('', PORT), ComplexHTTPRequestHandler)

    sys.stderr.write('Serving on port {0} ...\n'.format(PORT))
    server.serve_forever()


@fab.task
def reserve():
    """`build`, then `serve`"""
    build()
    serve()


@fab.task
def preview():
    """Build production version of site"""
    fab.local('pelican -s publishconf.py')


@fab.hosts(production)
@fab.task
def publish():
    """Publish to production via rsync"""
    fab.local('pelican -s publishconf.py')
    project.rsync_project(
        remote_dir=dest_path,
        exclude=".DS_Store",
        local_dir=DEPLOY_PATH.rstrip('/') + '/',
        delete=True,
        extra_opts='-c',
    )
