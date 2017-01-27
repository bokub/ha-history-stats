# ha-history-stats
A home-assistant component that gives statistics about your history.

To try this component, just `add history_stats.py` in `.homeassistant/custom_components/sensor/` and restart home-assistant

-----------------

### Example configuration

    sensor:
      - platform: history_stats
        entity_id: device_tracker.android_boris
        state: 'home'
        duration: '{{ 3600 * 24 }}'
        end: '{{ as_timestamp(now().replace(hour=0).replace(minute=0).replace(second=0)) }}'
        name: Boris at home yesterday

      - platform: history_stats
        entity_id: light.kitchen_lamp
        state: 'on'
        start: '{{ as_timestamp(now()) - 7 * 24 * 3600 }}'
        end: '{{ as_timestamp(now()) }}'
        name: Kitchen lamp, last 7 days
        
        
Will be rendered like this :

![preview](http://i.imgur.com/t3juZql.png)
        
        
### Parameters
 

 - **entity_id** : The entity you want to track

 - **state**: The state you want to track

 - **name**: What to display on the frontend

 - **start**: When to start the measure, timestamp

 - **end**: When to stop the measure, timestamp

 - **duration**: Duration of the measure, seconds
 
Only 2 of _start_, _end_ and _duration_ should be provided, of course.

-----------------

Discuss it on the [home-assistant forum](https://community.home-assistant.io/t/history-statistics-component/10194)
