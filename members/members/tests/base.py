import unittest
import transaction
from subprocess import Popen

from pyramid import testing

from sqlalchemy import create_engine, engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, OperationalError

from members import models
from members.models.others import Order
from members.models.member import Member
from members.models.workgroups import Workgroup
from members.models.shift import Shift
from members.models.task import Task


'''
Base class for all our Tests,
Currently supports testing with sqlite database.
A test database is used for each Test.
Potentially, we'd also want to test with Postgres, but
that is more work bcs startin Postgres up is slow, so
we'd use the same db, but rollback everything after each Test
(see http://sontek.net/writing-tests-for-pyramid-and-sqlalchemy)
'''

db_type = 'sqlite'

class VokoTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if db_type == 'postgres':
            #TODO: where to get setting from? maybe:
            # from paste.deploy.loadwsgi import appconfig
            # settings = appconfig('config:' + os.path.join(here, '../../', 'development.ini'))
            cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
            cls.Session = sessionmaker()

    def setUp(self):
        self.config = testing.setUp()
        if db_type == 'sqlite':
            # template db contains some order data the members app relies on
            Popen('cp members-test-template.db members-test.db', shell=True).wait()
            self.engine = create_engine('sqlite:///members-test.db')
            self.DBSession = models.base.configure_session(self.engine)
            # these statements create the database model from models/ via CREATE statements
            # Interesting for when you don't use a prepared database
            #models.base.Base.metadata.bind = self.engine
            #models.base.Base.metadata.create_all(self.engine)
            # turn on Foreign Keys in sqlite (enforcement only works from version 3.6.19 though)
            self.engine.execute('pragma foreign_keys=on')
        else:
            self.DBSession = models.base.configure_session(create_engine('postgres://'))
        self.fill_data()

    def tearDown(self):
        if db_type == 'sqlite':
            self.DBSession.close()
            Popen('rm members-test.db', shell=True).wait()
        testing.tearDown()

    def fill_data(self):
        '''
        Fills in dummy content that we will use for testing
        2 members, Peter and Hans.
        2 workgroups, Systems and Besteling.
        Peter is the only member in Systems.
        Both are members in Bestel, with Hans leading that one.
        Bestel has a task with a shift of Peter.
        '''
        m1 = Member(fname=u'Peter', prefix=u'de', lname='Pan')
        self.DBSession.add(m1)
        m2 = Member(fname=u'Hans', prefix=u'de', lname='Wit')
        self.DBSession.add(m2)
        wg1 = Workgroup(name=u'Systems', desc=u'IT stuff')
        self.DBSession.add(wg1)
        wg2 = Workgroup(name=u'Besteling', desc=u'Besteling at wholesale')
        self.DBSession.add(wg2)
        self.DBSession.flush() # flush now to get member and workgroup IDs
        wg1.members.append(m1)
        wg1.leaders.append(m1)
        wg2.members.append(m1)
        wg2.members.append(m2)
        wg2.leaders.append(m2)
        t = Task('do stuff', wg2.id)
        self.DBSession.add(t)
        self.DBSession.flush()
        wg2.tasks.append(t)
        s = Shift(wg2.id, m1.mem_id, 1, t.id)
        self.DBSession.add(s)
        self.DBSession.flush()
