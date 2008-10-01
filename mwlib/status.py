import simplejson
import sys

from mwlib.log import Log

log = Log('mwlib.statusfile')


class Status(object):
    def __init__(self,
        filename=None,
        podclient=None,
        progress_range=(0, 100),
        auto_dump=True,
    ):
        self.filename = filename
        self.podclient = podclient
        self.status = {}
        self.progress_range = progress_range
    
    def __call__(self, status=None, progress=None, article=None, auto_dump=True,
        **kwargs):
        if status is not None and status != self.status.get('status'):
            print 'STATUS: %s' % status
            self.status['status'] = status
            if self.podclient is not None:
                self.podclient.post_status(status)
        
        if progress is not None:
            assert 0 <= progress and progress <= 100, 'progress not in range 0..100'
            progress = int(
                self.progress_range[0]
                + progress*(self.progress_range[1] - self.progress_range[0])/100
            )
            if progress != self.status.get('progress'):
                print 'PROGRESS: %d%%' % progress
                self.status['progress'] = progress
                if self.podclient is not None:
                    self.podclient.post_progress(progress)
        
        if article is not None and article != self.status.get('article'):
            print 'ARTICLE: %r' % article
            self.status['article'] = article
            if self.podclient is not None:
                self.podclient.post_current_article(article)
        
        sys.stdout.flush()
        
        self.status.update(kwargs)
        
        if auto_dump:
            self.dump()
    
    def dump(self):
        if not self.filename:
            return
        try:    
            open(self.filename, 'wb').write(
                simplejson.dumps(self.status).encode('utf-8')
            )
        except Exception, exc:
            log.ERROR('Could not write status file %r: %s' % (
                self.filename, exc
            ))

    
class EntertainingStatus(Status):
    def __init__(self,
        filename=None,
        podclient=None,
        progress_range=(0, 100),
        auto_dump=True,
        metabook = None
                 ):

        self.article_names = [a["title"] for a in metabook["items"]]
        self.article_ptr = 0
        Status.__init__(self, filename, podclient, progress_range, auto_dump)

        def nextArticle(self):
            if self.article_names:
                if self.article_ptr == len(self.article_names):
                    self.article_ptr = 0
            self.article_ptr += 1
            return self.article_names[self.article_ptr - 1]

        def __call__(**kargs):
            status = kargs.get("status")
            if status is not None and status != self.status.get('status'):
                if not "article" in kargs:
                    kargs["article"] = self.nextArticle()
            Status.__call__(self, **kargs)
