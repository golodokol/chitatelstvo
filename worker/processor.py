from __future__ import annotations

import logging
import uuid

from sqlalchemy.orm import Session

from config.settings import USE_LLM
from db import repository as repo
from db.models import ParentNotification
from db.session import SessionLocal
from gamification.engine import GamificationRequest, LearnerState, generate_reward
from notifications.dispatcher import dispatch_parent_notifications, send_pending_notification

logger = logging.getLogger(__name__)


def process_event(event_id: str) -> None:
    db: Session = SessionLocal()
    try:
        eid = uuid.UUID(event_id)
        event = repo.mark_event_processing(db, eid)
        if not event:
            logger.info("Событие %s пропущено (уже обрабатывается или завершено)", event_id)
            return

        child = repo.get_child_with_family(db, event.child_id)
        if not child or not child.family:
            repo.mark_event_failed(db, eid, "child or family not found")
            return

        badges = [b.badge_name for b in child.badges]
        req = GamificationRequest(
            event_type=event.event_type,
            learner=LearnerState(
                child_name=child.name,
                current_level=child.current_level,
                current_badges=badges,
                total_points=child.total_points,
                tale_title=event.tale_title or "",
                module_week=child.module_week,
            ),
            notes=event.notes or "",
        )

        reward = generate_reward(req, use_llm=USE_LLM)
        repo.save_reward_and_update_child(db, event, child, reward)

        notification_ids = dispatch_parent_notifications(
            db,
            family=child.family,
            child=child,
            event_id=event.id,
            parent_message=reward.parent_message,
            next_action=reward.next_action,
        )

        from job_queue.redis_queue import enqueue

        for nid in notification_ids:
            note = db.get(ParentNotification, nid)
            if note and note.status == "pending":
                enqueue("send_notification", {"notification_id": str(nid)})

        logger.info("Событие %s обработано (%s)", event_id, reward.source)
    except Exception as exc:
        logger.exception("Ошибка обработки события %s", event_id)
        try:
            repo.mark_event_failed(db, uuid.UUID(event_id), str(exc))
        except Exception:
            pass
    finally:
        db.close()


def process_send_notification(notification_id: str) -> None:
    db: Session = SessionLocal()
    try:
        send_pending_notification(db, uuid.UUID(notification_id))
    except Exception as exc:
        logger.exception("Ошибка отправки уведомления %s: %s", notification_id, exc)
    finally:
        db.close()
