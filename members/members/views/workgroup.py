import transaction
from pyramid.view import view_config

from datetime import datetime

from members.models.workgroups import Workgroup
from members.models.member import Member
from members.models.setup import DBSession
from members.models.shift import Shift
from members.views.base import BaseView


def get_possible_members(session):
    return session.query(Member).filter(Member.mem_active==True).all()


def mkworkgroup(session, request=None, id=None):
    ''' make a WorkGroup object, use request if possible '''
    if (request and request.matchdict.has_key('id') and
            request.matchdict['id'] != 'fresh') or id:
        if not id:
            id = request.matchdict['id']
        wg = session.query(Workgroup).filter(Workgroup.id==id).first()
        if wg:
            wg.exists = True
    else:
        wg = Workgroup('', '')
    if request and wg:
        # overwrite workgroup properties from request
        for attr in ['name', 'desc', 'leader_id']:
            if request.params.has_key(attr):
                wg.__setattr__(attr, request.params[attr])
    return wg


@view_config(renderer='../templates/edit-workgroup.pt',
             route_name='new_workgroup',
             permission='edit')
class NewWorkgroupView(BaseView):

    tab = 'workgroups'

    def __call__(self):
        self.possible_members = get_possible_members(DBSession())
        return dict(wg = Workgroup('', ''), msg="You're about to make a new workgroup.")


@view_config(renderer='../templates/workgroup.pt',
             route_name='workgroup',
             permission='view')
class WorkgroupView(BaseView):

    tab = 'workgroups'

    def __call__(self):
        id = self.request.matchdict['id']
        try:
            id = int(id)
        except:
            return dict(wg = None, msg = 'Invalid ID.')
        wg = mkworkgroup(DBSession(), self.request, id=id)
        if not wg:
            return dict(wg=None, shifts=None, msg="No workgroup with id %d" % id)


        self.user_is_wgleader = wg.leader_id == self.user.id

        now = datetime.now()
        self.month = self.request.params.has_key('month') and self.request.params['month']\
            or now.month
        self.year = self.request.params.has_key('year') and self.request.params['year']\
            or now.year
        self.session = DBSession()
        shifts = self.session.query(Shift).filter(Shift.id==wg.id\
                                             and Shift.month==self.month\
                                             and Shift.year==self.year)\
                                     .all()
        return dict(wg=wg, shifts=shifts)


@view_config(renderer='../templates/edit-workgroup.pt',
             route_name='workgroup-edit',
             permission='edit')
class WorkgroupEditView(BaseView):

    tab = 'workgroups'

    def __call__(self):
        print 'wg view called.'
        id = self.request.matchdict['id']
        if id != 'fresh':
            try:
                id = int(id)
            except:
                return dict(m = None, msg = 'Invalid ID.')

        self.session = DBSession()
        wg = mkworkgroup(self.session, self.request)
        if not wg:
            return dict(wg=None, msg="No workgroup with id %d" % id)
        if not self.request.params.has_key('action'):
            self.possible_members = get_possible_members(self.session)
            return dict(wg = wg, msg='')
        else:
            action = self.request.params['action']
            if action == "save":
                if self.request.params.has_key('wg_members'):
                    wg.members = []
                    for mid in self.request.POST.getall('wg_members'):
                        m = self.session.query(Member).filter(Member.id == mid).first()
                        wg.members.append(m)
                try:
                    self.session.add(wg)
                    self.session.flush()
                    new_id = wg.id
                    transaction.commit()
                    self.session = DBSession()
                except Exception, e:
                    return dict(wg = None, msg=u'Something went wrong: %s' % e)
                self.possible_members = get_possible_members(self.session)
                return dict(wg = mkworkgroup(self.session, self.request, id=new_id), msg='Workgroup has been saved.')

            elif action == 'delete':
                try:
                    self.session.delete(self.session.query(Workgroup)\
                        .filter(Workgroup.id == wg.id).first()\
                    )
                    self.session.flush()
                    transaction.commit()
                except Exception, e:
                    return dict(wg = None, msg=u'Something went wrong: %s' % e)
                return dict(wg = None, msg='Workgroup %s has been deleted.' % wg)





@view_config(renderer='../templates/list-workgroups.pt', route_name='workgrouplist')
class WorkgrouplistView(BaseView):

    tab = 'workgroups'

    def __call__(self):
        dbsession = DBSession()
        wg_query = dbsession.query(Workgroup)

        # ordering
        # key is what the outside world see, value is what SQLAlchemy uses
        order_idxs = {'id': Workgroup.id, 'name': Workgroup.name}
        order_by = 'id'
        if self.request.params.has_key('order_by')\
          and order_idxs.has_key(self.request.params['order_by']):
            order_by = self.request.params['order_by']
        order_alt = (order_by=='id') and 'name' or 'id'
        wg_query = wg_query.order_by(order_idxs[order_by])

        return dict(workgroups=wg_query.all(), msg='', order_by=order_by, order_alt=order_alt, came_from='/workgroups')


