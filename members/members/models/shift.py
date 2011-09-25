from sqlalchemy import Column, Integer, Unicode, ForeignKey
from sqlalchemy.orm import relationship

from setup import Base
from member import Member
from workgroups import Workgroup


class Shift(Base):
    '''
    A shift is not identifiable by any number of its attributes, as
    anyone can do more than one shift in the same workgroup in the
    same month and day. This is why they have their own id.
    '''
    __tablename__ = 'wg_shifts'

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    wg_id = Column(Integer, ForeignKey('workgroups.id'))
    mem_id = Column(Integer, ForeignKey('members.id'))
    state = Column(Unicode(255), default='assigned')

    member = relationship(Member, backref='scheduled_shifts')
    workgroup = relationship(Workgroup)

    def __init__(self, wg_id, mem_id, year, month, day):
        self.wg_id = wg_id
        self.mem_id = mem_id
        self.year = year
        self.month = month
        self.day = day

    def __repr__(self):
        return "Shift on %d/%d/%s by member %s in group: %s [state: %s]" %\
                (self.year, self.month, str(self.day), self.member.fullname(), self.workgroup, self.state)

    def set_day(self, day):
        ''' more like these? '''
        assert(day in xrange(1, 25, 1))
        self.day = day

    def set_state(self, state):
        assert(state in ['assigned', 'worked'])
        self.state = state

