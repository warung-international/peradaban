import datetime


def get_bot_uptime(self, *, brief=False):
    """Get the bot's uptime."""
    now = datetime.datetime.utcnow()
    delta = now - self.bot.start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    if not brief:
        if days:
            fmt = "{d} days, {h} hours, {m} minutes, and {s} seconds"
        else:
            fmt = "{h} hours, {m} minutes, and {s} seconds"
    else:
        fmt = "{h}h {m}m {s}s"
        if days:
            fmt = "{d}d " + fmt

    return fmt.format(d=days, h=hours, m=minutes, s=seconds)
