from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from base import Base
from base import DBSession
from base import VokoValidationError
from member import Member
from task import Task
from workgroups import Workgroup
from others import get_order_label


class Shift(Base):
    '''
    A shift is not identifiable by any number of its attributes, as
    anyone can do more than one shift in the same workgroup in the
    order period. This is why they have their own id.
    '''
    __tablename__ = 'wg_shifts'

    id = Column(Integer, primary_key=True)
    mem_id = Column(Integer, ForeignKey('members.mem_id'), nullable=False)
    order_id = Column(Integer, nullable=False)
    task_id = Column(Integer, ForeignKey('wg_tasks.id'), nullable=False)
    state = Column(Unicode(255), default=u'assigned')

    member = relationship(Member, backref='scheduled_shifts')
    task = relationship(Task)

    def __init__(self, mem_id, o_id, t_id):
        self.mem_id = mem_id
        self.order_id = o_id
        self.task_id = t_id
        self.state = 'assigned'

    def __repr__(self):
        return "Shift - task '%s' in order '%d' by member %s"\
               " in the '%s'-group [state is %s]" %\
                (str(self.task), self.order_id, self.member.fullname,
                 self.workgroup, self.state)

    def validate(self):
        '''
        validate if this object is valid, raise VokoValidationError otherwise
        '''
        if self.task_id == '--':
            raise VokoValidationError('Please select a task.')
        task = DBSession.query(Task).get(self.task_id)
        if not task:
            raise VokoValidationError('No task specified.')
        if self.mem_id == '--':
            raise VokoValidationError('Please select a member.')
        m = DBSession.query(Member).get(self.mem_id)
        if not m:
            raise VokoValidationError('No member specified.')
        if not m in task.workgroup.members:
            raise VokoValidationError('The member of this shift (%s) is not '\
                        'a member in the workgroup %s.' % (m, task.workgroup))
        if not self.state in ['assigned', 'worked']:
            raise VokoValidationError('The state must be either "assigned" '\
                        'or "worked". Cannot set it to %s' % (self.state))

    @property
    def order(self):
        return get_order_label(self.order_id)

    @property
    def workgroup(self):
        return self.task.workgroup


def get_shift(session, request):
    ''' get shift object from id '''
    if (request and 's_id' in request.matchdict
         and int(request.matchdict['s_id']) >= 0):
            shift = session.query(Shift).get(request.matchdict['s_id'])
            if shift:
                shift.exists = True
    else:
        shift = None
    return shift
