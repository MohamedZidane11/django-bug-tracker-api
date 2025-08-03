from datetime import datetime
from typing import Dict, Any, Optional, List
from .firebase_config import db


class BugReport:
    SEVERITY_CHOICES = ['low', 'medium', 'high', 'critical']
    STATUS_CHOICES = ['open', 'in_progress', 'resolved', 'closed']

    def __init__(self, title: str, description: str, severity: str = 'medium',
                 status: str = 'open', reporter: str = '', assignee: str = '',
                 created_at: datetime = None, updated_at: datetime = None,
                 bug_id: str = None):
        self.bug_id = bug_id
        self.title = title
        self.description = description
        self.severity = severity if severity in self.SEVERITY_CHOICES else 'medium'
        self.status = status if status in self.STATUS_CHOICES else 'open'
        self.reporter = reporter
        self.assignee = assignee
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'bug_id': self.bug_id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'status': self.status,
            'reporter': self.reporter,
            'assignee': self.assignee,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], bug_id: str = None):
        created_at = None
        updated_at = None

        if 'created_at' in data and data['created_at']:
            created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        if 'updated_at' in data and data['updated_at']:
            updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))

        return cls(
            bug_id=bug_id,
            title=data.get('title', ''),
            description=data.get('description', ''),
            severity=data.get('severity', 'medium'),
            status=data.get('status', 'open'),
            reporter=data.get('reporter', ''),
            assignee=data.get('assignee', ''),
            created_at=created_at,
            updated_at=updated_at
        )

    def save(self) -> str:
        """Save bug report to Firestore"""
        self.updated_at = datetime.utcnow()

        if self.bug_id:
            # Update existing document
            doc_ref = db.collection('bugs').document(self.bug_id)
            doc_ref.update(self.to_dict())
        else:
            # Create new document
            doc_ref = db.collection('bugs').add(self.to_dict())[1]
            self.bug_id = doc_ref.id

        return self.bug_id

    @classmethod
    def get_by_id(cls, bug_id: str) -> Optional['BugReport']:
        """Get bug report by ID"""
        doc_ref = db.collection('bugs').document(bug_id)
        doc = doc_ref.get()

        if doc.exists:
            return cls.from_dict(doc.to_dict(), doc.id)
        return None

    @classmethod
    def get_all(cls) -> List['BugReport']:
        """Get all bug reports"""
        bugs = []
        docs = db.collection('bugs').order_by('created_at', direction=firestore.Query.DESCENDING).stream()

        for doc in docs:
            bugs.append(cls.from_dict(doc.to_dict(), doc.id))

        return bugs

    def delete(self) -> bool:
        """Delete bug report"""
        if self.bug_id:
            db.collection('bugs').document(self.bug_id).delete()
            return True
        return False

    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """Get bug statistics"""
        bugs = cls.get_all()

        total_bugs = len(bugs)
        open_bugs = len([b for b in bugs if b.status in ['open', 'in_progress']])
        closed_bugs = len([b for b in bugs if b.status in ['resolved', 'closed']])

        # Count severity levels
        severity_counts = {}
        for severity in cls.SEVERITY_CHOICES:
            severity_counts[severity] = len([b for b in bugs if b.severity == severity])

        most_common_severity = max(severity_counts.keys(), key=lambda k: severity_counts[k]) if bugs else 'medium'

        # Count status levels
        status_counts = {}
        for status in cls.STATUS_CHOICES:
            status_counts[status] = len([b for b in bugs if b.status == status])

        return {
            'total_bugs': total_bugs,
            'open_bugs': open_bugs,
            'closed_bugs': closed_bugs,
            'severity_distribution': severity_counts,
            'status_distribution': status_counts,
            'most_common_severity': most_common_severity,
        }