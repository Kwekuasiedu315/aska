from datetime import datetime, timedelta, timezone


def get_relative_time(dt):
    if not dt:
        return dt
    # Get the current time in the same time zone as the dt argument
    now = datetime.now(timezone.utc).astimezone(dt.tzinfo)

    # Calculate the difference between the two times
    diff = now - dt

    # If the difference is less than 1 minute, return "now"
    if diff < timedelta(minutes=1):
        return "now"

    # If the difference is less than 1 hour, return the number of minutes
    elif diff < timedelta(hours=1):
        return f"{diff.seconds // 60} minutes ago"

    # If the difference is less than 1 day, return the number of hours
    elif diff < timedelta(days=1):
        return f"{diff.seconds // 3600} hours ago"

    # Otherwise, return the date of the datetime object
    else:
        return dt.strftime("%Y-%m-%d")
