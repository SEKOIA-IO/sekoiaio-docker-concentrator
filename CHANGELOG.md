# Changelog

All notable changes with sekoiaio concentrator will be documented in this file.

## [2.7.6]

- Preserve the original message payload when forwarding events to Sekoia:
  - Replace `%msg%` with `%rawmsg-after-pri%` in `template.j2` and `template_tls.j2`
  - Fixes loss of the `CEF:0` banner (and other content stripped by rsyslog's RFC 3164 parser when a leading token ends with `:`, e.g. Forcepoint NGFW, ArcSight CEF sources)
  - The outbound payload now contains the exact bytes received from the source after the syslog `<PRI>`, instead of rsyslog's reparsed `%msg%`

## [2.7.5]

- Add `action.resumeRetryCount=-1` and `action.resumeInterval=30` to all output actions:
  - Fixes issue where rsyslog would suspend forwarding actions after network outages
  - Ensures queued logs are reliably resent when connectivity is restored
  - Prevents data loss during temporary network interruptions
  - Applies to TCP, RELP, and stats monitoring output actions in all templates (template.j2, template_tls.j2, stats_template.j2)

## [2.7.4]

- Update default regional intake endpoint

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