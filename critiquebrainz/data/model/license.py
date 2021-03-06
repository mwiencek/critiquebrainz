from critiquebrainz.data import db
from critiquebrainz.data.model.mixins import DeleteMixin


class License(db.Model, DeleteMixin):
    __tablename__ = 'license'

    id = db.Column(db.Unicode, primary_key=True)
    full_name = db.Column(db.Unicode, nullable=False)
    info_url = db.Column(db.Unicode)

    _reviews = db.relationship('Review', cascade='delete', lazy='dynamic', backref='license')

    @classmethod
    def create(cls, id, full_name, info_url=None):
        new = cls(id=id, full_name=full_name, info_url=info_url)
        db.session.add(new)
        db.session.commit()
        return new

    def to_dict(self):
        response = dict(id=self.id,
                        full_name=self.full_name,
                        info_url=self.info_url)
        return response
