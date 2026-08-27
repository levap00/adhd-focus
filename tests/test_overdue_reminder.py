from datetime import timedelta

from backend.web_push import WEB_PUSH_OVERDUE_MIN_DELAY_MINUTES, is_task_ready_for_overdue_reminder


def test_overdue_reminder_skips_the_due_alarm_window():
    window = timedelta(minutes=480)
    assert is_task_ready_for_overdue_reminder(timedelta(minutes=10), window) is False
    assert is_task_ready_for_overdue_reminder(timedelta(minutes=25), window) is False
    assert is_task_ready_for_overdue_reminder(timedelta(minutes=WEB_PUSH_OVERDUE_MIN_DELAY_MINUTES), window) is False
    assert is_task_ready_for_overdue_reminder(timedelta(minutes=46), window) is True
    assert is_task_ready_for_overdue_reminder(timedelta(minutes=500), window) is False
