from sparts.tasks.queue import QueueTask
from sparts.vtask import ExecuteContext
from ..base import SingleTaskTestCase 
from twisted.internet.defer import Deferred


class IncrementCounterTask(QueueTask):
    def execute(self, item, context):
        return item

class TestDeferredSuccess(SingleTaskTestCase):
    TASK = IncrementCounterTask

    def setUp(self):
        super(TestDeferredSuccess, self).setUp()
        self.seen = set()

    def saw_item(self, item):
        self.seen.add(item)

    def makeContext(self, item):
        d = Deferred()
        d.addCallback(self.saw_item)

        ctx = ExecuteContext(item=item, deferred=d)
        return ctx

    def test_execute_happens(self):
        self.task.queue.put(self.makeContext('foo'))
        self.task.queue.put(self.makeContext('bar'))
        self.task.queue.put(self.makeContext('baz'))
        self.task.queue.join()

        self.assertContains('foo', self.seen)
        self.assertContains('bar', self.seen)
        self.assertContains('baz', self.seen)


class RaiseExceptionTask(QueueTask):
    def execute(self, item, context):
        raise Exception(item)


class TestDeferredErrback(SingleTaskTestCase):
    TASK = RaiseExceptionTask

    def setUp(self):
        super(TestDeferredErrback, self).setUp()
        self.seen = set()

    def handle_error(self, error):
        self.seen.add(error.getErrorMessage())

    def makeContext(self, item):
        d = Deferred()
        d.addErrback(self.handle_error)

        ctx = ExecuteContext(item=item, deferred=d)
        return ctx

    def test_execute_happens(self):
        self.task.queue.put(self.makeContext('foo'))
        self.task.queue.put(self.makeContext('bar'))
        self.task.queue.put(self.makeContext('baz'))
        self.task.queue.join()

        self.assertContains('foo', self.seen)
        self.assertContains('bar', self.seen)
        self.assertContains('baz', self.seen)