from os import listdir
from os.path import exists
from pipes import quote

import fabric.api as fab

fab.env.roledefs['prod'] = ['dozer.foobar.lu']

ROOT_PATH = '/var/www/mamerwiselen.lu/www/htdocs'
SYNC_IGNORES = {
    '--exclude "*~"',
    '--exclude ".*.swp"',
    '--exclude ".git"',
    '--exclude ".gitignore"',
    '--exclude "LICENSE.txt"',
    '--exclude "README.txt"',
    '--exclude "fabfile.py"',
    '--exclude "wisel_private"',
}


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
        outfile = 'wisel/' + basename + '-public.pdf'
        thumbnail = 'wisel_thumbnails/' + basename + '.jpg'
        if not exists(outfile):
            fab.local(cmd.format(fname=quote(infile), pname=quote(outfile)))
            fab.local('git add %s' % quote(outfile))

        if not exists(thumbnail):
            fab.local('convert -thumbnail x400 -background white -alpha remove '
                      '%s[0] %s' % (quote(infile), quote(thumbnail)))
            fab.local('git add %s' % quote(thumbnail))


@fab.task
def publish():
    fab.execute(process_pdf)
    rsync_cmd = [
        'rsync',
        '-av',
        '--progress',
    ] + list(SYNC_IGNORES) + [
        '.',
        'dozer.foobar.lu:%s' % ROOT_PATH,
    ]
    fab.local(' '.join(rsync_cmd))
