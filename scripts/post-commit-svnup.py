#!/usr/bin/python2.4

import os
import sys
import pyramid
from pyramid.path import path
from datetime import datetime


os.umask(002)

VERBOSE=True

BETABUILD_CHECKOUT_DIR=path('/data/website-build/build')
WWW_DIR = '/data/ftp.python.org/pub/www.python.org'
UPDATEBETADIRS = ['data','styles','js','files','images']

BUILDINPROCESS = BETABUILD_CHECKOUT_DIR / 'status/buildinprocess'
BUILDQUEUED = BETABUILD_CHECKOUT_DIR / 'status/buildqueued'
PEPQUEUED = BETABUILD_CHECKOUT_DIR / 'status/pepqueued'
PEPDIR = BETABUILD_CHECKOUT_DIR / 'data/dev/peps'
JOBSDIR = BETABUILD_CHECKOUT_DIR / 'data/community/jobs'


def log(message):
    if VERBOSE:
        print message

def cmd(command):
    log(command)
    child = os.popen(command)
    data = child.read()
    err = child.close()
    if err:
        raise RuntimeError, '%s failed w/ exit code %d' % (command, err)
    return data

def logStatus(revision,status):
    log('logStatus(%s,%s)'% (revision,status))
    statusfile = BETABUILD_CHECKOUT_DIR / 'status/updates/index.html'
    lastsuccessfulrevisionfile = BETABUILD_CHECKOUT_DIR / 'status/lastrev.txt'
    svnlogfile = BETABUILD_CHECKOUT_DIR / 'status/log/index.html'
    log('writing %s' % statusfile)
    log('writing %s' % lastsuccessfulrevisionfile)
    log('writing %s' % svnlogfile)

    fp = file(statusfile,'a')
    fp.write('%s : update to revision %s %s\n' %
             (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), revision, status))
    fp.close()

    # Log the changes
    print 'before success check %s' % status
    if status == 'succeeded' and revision != '':
        print 'inside success check'
        # get the last successful revision number
        fp = file(lastsuccessfulrevisionfile,'r')
        lasttext = fp.read().strip()
        try:
            last = str( int(lasttext)+1 )
            last = int(lasttext)
        except ValueError:
            log('last revision int conversion failed')
            last = 'HEAD'
        fp.close()

        # get the log between the last successful and this revision and save it
        svnlog = cmd(
            'svn log file:///data/repos/www/trunk/beta.python.org/build/data '
            '-r %s:%s' % (last,revision))
        fp = file(svnlogfile,'w+')
        fp.write('<pre>')
        fp.write(svnlog)
        fp.close()

        # Log the revision if it was successful
        fp = file(lastsuccessfulrevisionfile,'w+')
        fp.write(revision)
        fp.close()

    return

def update(revision):
    if BUILDINPROCESS.exists():
        return

    BUILDINPROCESS.touch()
    log(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    log('building')

    # pre hooks
    try:
        # Get the svn repo synchronised with the post commit version...
        os.chdir(BETABUILD_CHECKOUT_DIR)
        if revision != '':
            for d in UPDATEBETADIRS:
	        cmd('whoami')
                try:
                    cmd('svn up %s --revision %s'%(d, revision))
                except RuntimeError, error:
                    log('%s: %s' % (error.__class__.__name__, error))

        # Build this directory
        cmd('./scripts/server-build.py')

        # perform a copy and sync from out to the target directory referring
        # to a previous install log for changes.
        cmd('./scripts/installwatch.py -f out -t %s -l installwatch.log'
            % WWW_DIR)
        BUILDINPROCESS.remove()
        logStatus(revision,'succeeded')

    except:
        BUILDINPROCESS.remove()
        logStatus(revision,'failed')

def main():
    """
    Just gets the arguments which should be repos and rev from the subversion
    post commit hook
    """
    if PEPQUEUED.exists():
        PEPQUEUED.remove()
        os.chdir(BETABUILD_CHECKOUT_DIR / "peps")
        try:
            cmd("svn up")
        except RuntimeError, error:
            log('%s: %s' % (error.__class__.__name__, error))
        cmd("./pep2pyramid.py --force -d %s" % PEPDIR)
        cmd("./pep2rss.py %s" % PEPDIR)
        BUILDQUEUED.touch()

    if BUILDINPROCESS.exists():
        # allow new checkins to queue a new build during another build
        # (leave BUILDQUEUED in place)
        return

    if BUILDQUEUED.exists():
        revision = BUILDQUEUED.text()
        log('revision %s' % revision)
        BUILDQUEUED.remove()
        update(revision)

        #rebuild jobs rss
        cmd("%s/jobs2rss.py %s"%(JOBSDIR, JOBSDIR))
        log('Rebuilding jobs.rss')



if __name__ == "__main__":
    main()
