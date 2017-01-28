# ha-history-stats
A home-assistant component that gives statistics about your history.

To try this component, just `add history_stats.py` in `.homeassistant/custom_components/sensor/` and restart home-assistant

-----------------

The `history_stats` sensor platform provides quick statistics about another component, using data from the history.

It can track how long the component has been in a specific state, in a custom time period.

Examples of what you can track :
- How long you were at home this week
- How long the lights were ON yesterday
- How long you watched TV today

## Configuration

To enable the statistics sensor, add the following lines to your `configuration.yaml`:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: history_stats
    name: Lamp ON today
    entity_id: light.my_lamp
    state: 'on'
    start: '{{ _TODAY_ }}'
    end: '{{ _NOW_ }}'
```

Configuration variables:

 - **entity_id** (*Required*): The entity you want to track
 - **state** (*Required*): The state you want to track
 - **name** (*Optional*): Name displayed on the frontend
 - **start**: When to start the measure (timestamp).
 - **end**: When to stop the measure (timestamp)
 - **duration**: Duration of the measure (seconds)



<p class='note'>
You have to provide **exactly 2** of _start_, _end_ and _duration_. They can be templates, so the timestamps are dynamic.
</p>


## Time Aliases

Because timestamps can be difficult to handle, the `history_stats` component has built-in aliases to help you write your templates, and make them easier to understand.
Note that those aliases will not work with other components of Home Assistant.

Imagine that the current datetime is the following : `Tuesday, 14 Feb 2017 18:42:12`.
Here are the aliases you can use, and what they refer to:

| Alias                   | Datetime equivalent             | Explanation                                 |
| ----------------------- | ------------------------------- | ------------------------------------------- |
| \_NOW_                  | Tuesday, 14 Feb 2017 18:42:12   | The current timestamp                       |
| \_THIS_MINUTE_          | Tuesday, 14 Feb 2017 18:42:00   | The beginning of the current minute         |
| \_THIS_HOUR_            | Tuesday, 14 Feb 2017 18:00:00   | The beginning of the current hour           |
| \_TODAY_ or \_THIS_DAY_ | Tuesday, 14 Feb 2017 00:00:00   | The current day, at midnight                |
| \_THIS_WEEK_            | Monday, 13 Feb 2017 00:00:00    | The last monday, at midnight                |
| \_THIS_MONTH_           | Wednesday, 01 Feb 2017 00:00:00 | First day of the current month, at midnight |
| \_THIS_YEAR_            | Sunday, 01 Jan 2017 00:00:00    | First day of the current year, at midnight  |

| Alias         | Value in seconds |
| ------------- | ---------------- |
| \_ONE_MINUTE_ | 60               |
| \_ONE_HOUR_   | 3600             |
| \_ONE_DAY_    | 86400            |
| \_ONE_WEEK_   | 604800           |

Each one of those aliases will be converted to a real timestamp, which is a number of seconds, so you can use basic operators like `+`, `-` or `*` as well as numbers.

You can also use [template extensions](https://home-assistant.io/topics/templating/#home-assistant-template-extensions) instead of the `history_stats` aliases. For example, `_THIS_HOUR_` is the equivalent of `as_timestamp(now().replace(hour=0).replace(minute=0).replace(second=0))`

### Examples

Here are some examples of periods you could work with, and what to write in your `configuration.yaml`:

    
| Time period               | start                            | end             | duration               |
| ------------------------- | :------------------------------: | :-------------: | :--------------------: |
| Today                     | `{{ _TODAY_ }}    `              | `{{ _NOW_ }}`   |                        |
| Yesterday                 |                                  | `{{ _TODAY_ }}` | `{{ _ONE_DAY_ }}`      |
| Yesterday (alternative)   | `{{ _TODAY_ - _ONE_DAY_ }}    `  | `{{ _TODAY_ }}` |                        |
| This morning (6AM - 11AM) | `{{ _TODAY_ + 6 * _ONE_HOUR_ }}` |                 | `{{ 5 * _ONE_HOUR_ }}` |
| Current month             | `{{ _THIS_MONTH_ }}`             | `{{ _NOW_ }}`   |                        |
| Last 30 days              |                                  | `{{ _TODAY_ }}` | `{{ 30 * _ONE_DAY_ }}` |
| All your history          | `{{ 0 }}`                        | `{{ _NOW_ }}`   |                        |

-----------------

Discuss it on the [home-assistant forum](https://community.home-assistant.io/t/history-statistics-component/10194)
