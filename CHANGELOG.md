# Changelog

All notable changes with sekoiaio concentrator will be documented in this file.

## [2.7.3]

- Customize destination endpoint

## [2.7.2]

- Reset counters for forwarder monitoring events
- Added the ability to define a custom queue size for an intake.
- Introduced the capability to send events to Sekoia using the RELP protocol.

## [2.7.1]

- Support USA1 region
- Fix TLS template

## [2.7.0]

- Enable forwarder monitoring

## [2.6.0]

- Add the support of TLS

## [2.5.1]

- Check the format of Intake keys.

## [2.5]

- Added the support of multi-region

## [2.4]

- Capacity to import a custom rsyslog configuration

## [2.3]

- Improve performances for multiple ruleset configuration (ref: https://www.rsyslog.com/doc/concepts/multi_ruleset.html#rulesets-and-queues)

## [2.2]

- Update main queue settings

## [2.1]

- Add local timestamp in rsyslog header instead of received timestamp 

## [2.0]

- Manage syslog RFC 3164 (only 5424 in 1.0 version)
- Add advanced debug options
- Update implementation from bash to jinja

## [1.0] 

- Initial version