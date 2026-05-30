def calculate_next_interval(
    interval_days,
    ease_factor,
    quality
):
    if quality == 0:
        return 1, max(1.3, ease_factor - 0.2)

    if quality == 1:
        return 2, ease_factor

    if quality == 2:
        return int(interval_days * 2), ease_factor

    if quality == 3:
        return int(interval_days * ease_factor), (
            ease_factor + 0.15
        )

    return interval_days, ease_factor
