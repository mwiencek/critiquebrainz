from . import db
from sqlalchemy.dialects.postgresql import UUID
from rate import Rate
from datetime import datetime

class Publication(db.Model):

    __tablename__ = 'publication'
    
    id = db.Column(UUID, server_default=db.text('uuid_generate_v4()'), primary_key=True)
    release_group = db.Column(UUID, index=True, nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Unicode, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    edits = db.Column(db.Integer, nullable=False, default=0)
    rating = db.Column(db.Integer, nullable=False, default=0)
    
    user = db.relationship('User')
    spam_reports = db.relationship('SpamReport')
    _rates = db.relationship('Rate', lazy='dynamic')
    
    __table_args__ = (db.UniqueConstraint('release_group', 'user_id'), )

    # a list of allowed values of `inc` parameter in API calls
    allowed_includes = ['user']

    def to_dict(self, includes=[]):
        response = dict(id = self.id, 
            release_group = self.release_group,
            user_id = self.user_id, 
            text = self.text, 
            created = self.created,
            last_updated = self.last_updated, 
            edits = self.edits, 
            rating = self.rating, 
            rates = self._rates.count(),
            rates_positive = self._rates_positive.count(),
            rates_negative = self._rates_negative.count(),
            rates_ratio = self.rates_ratio)

        if 'user' in includes:
            response['user'] = self.user.to_dict()
        return response

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def rates(self):
        return self._rates.all()

    @property
    def _rates_positive(self):
        return self._rates.filter_by(placet=True)

    @property
    def _rates_negative(self):
        return self._rates.filter_by(placet=False)

    @property
    def rates_positive(self):
        return self._rates_positive.all()

    @property
    def rates_negative(self):
        return self._rates_negative.all()

    @property
    def rates_ratio(self):
        if self._rates.count() == 0:
            return 0
        else:
            return float(self._rates_positive.count())/float(self._rates.count())

    @classmethod
    def fetch_sorted_by_rating(cls, release_group, user_id, limit, offset, rating):
        # subquery counting rates
        subquery = db.session.query(Rate.publication_id, db.func.count('*').\
                   label('count')).group_by(Rate.publication_id).subquery()
                   
        # query with outerjoined subquery
        query = db.session.query(cls).\
                outerjoin((subquery, cls.id == subquery.c.publication_id))

        if user_id: 
            query = query.filter(cls.user_id==user_id)
        if release_group: 
            query = query.filter(cls.release_group==release_group)
        
        query = query.filter(cls.rating>=rating)
        count = query.count()
        query = query.order_by(cls.rating.desc(), subquery.c.count.desc()).\
                      limit(limit).\
                      offset(offset)
        return (query.all(), count)

    @classmethod
    def create(cls, release_group, user, text):
        publication = Publication(release_group=release_group, user=user, text=text)
        db.session.add(publication)
        db.session.commit()
        return publication

