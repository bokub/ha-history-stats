The `history_stats` sensor platform provides quick statistics about another component, using data from the history.

It can track how long the component has been in a specific state, in a custom time period.

Examples of what you can track :
- How long you were at home this week
- How long the lights were ON yesterday
- How long you watched TV today

> Note: This component used to support time aliases, but they have been removed. The old code is still available in the time-aliases branch.

## Configuration

To enable the history statistics sensor, add the following lines to your `configuration.yaml`:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: history_stats
    name: Lamp ON today
    entity_id: light.my_lamp
    state: 'on'
    start: '{{ now().replace(hour=0).replace(minute=0).replace(second=0) }}'
    end: '{{ now() }}'
```

Configuration variables:

 - **entity_id** (*Required*): The entity you want to track
 - **state** (*Required*): The state you want to track
 - **name** (*Optional*): Name displayed on the frontend
 - **start**: When to start the measure (timestamp or datetime).
 - **end**: When to stop the measure (timestamp or datetime)
 - **duration**: Duration of the measure (seconds)


You have to provide **exactly 2** of `start`, `end` and `duration`.

You can use [template extensions](/topics/templating/#home-assistant-template-extensions) such as `now()` or `as_timestamp()` to handle dynamic dates, as shown in the examples below.


## Time periods

The `history_stats` component will execute a measure within a precise time period. You should always provide 2 of the following :
- When the period starts (`start` variable)
- When the period ends (`end` variable)
- How long is the period (`duration` variable)

As `start` and `end` variables can be either datetimes or timestamps, you can configure almost any period you want.

Don't forget that `duration` is a number of seconds, not a datetime. It is recommended to use it only if your period has a fixed length (24 hours, or 7 days, for example).

### {% linkable_title Examples %}

Here are some examples of periods you could work with, and what to write in your `configuration.yaml`:

**Today**: starts at 00:00 of the current day and ends right now.
```yaml
    start: '{{ now().replace(hour=0).replace(minute=0).replace(second=0) }}'
    end: '{{ now() }}'
```
**Yesterday**: ends today at 00:00, lasts 24 hours.
```yaml
    end: '{{ now().replace(hour=0).replace(minute=0).replace(second=0) }}'
    duration: '{{ 24 * 3600 }}'
```
**This morning (6AM - 11AM)**: starts today at 6, lasts 5 hours.
```yaml
    start: '{{ now().replace(hour=6).replace(minute=0).replace(second=0) }}'
    duration: '{{ 5 * 3600 }}'
```

**Current week**: starts last Monday at 00:00, ends right now.

Here, last Monday is _today_ as a timestamp, minus 86400 times the current weekday (86400 is the number of seconds in one day, the weekday is 0 on Monday, 6 on Sunday).
```yaml
    start: '{{ as_timestamp( now().replace(hour=0).replace(minute=0).replace(second=0) ) - now().weekday() * 86400 }}'
    end: '{{ now() }}'
```
**Last 30 days**: ends today at 00:00, lasts 30 days. Easy one.
```yaml
    end: '{{ now().replace(hour=0).replace(minute=0).replace(second=0) }}'
    duration: '{{ 30 * 24 * 3600 }}'
```

**All your history** starts at timestamp = 0, and ends right now.
```yaml
    start: '{{ 0 }}'
    end: '{{ now() }}'
```

If you want to check if your period is right, just click on your component, the `from` and `to` attributes will show the start and end of the period, nicely formatted.

