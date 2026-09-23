import json
import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from db.models import AuditEvent

def log_audit_event(db: Session, event_name: str, user_id: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> AuditEvent:
    event = AuditEvent(
        user_id=user_id,
        event=event_name,
        timestamp=datetime.datetime.utcnow(),
        metadata_json=json.dumps(metadata) if metadata else None
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
