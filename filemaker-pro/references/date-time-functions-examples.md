# Date, Time & Timestamp Functions — Examples

Adapted from [Darrin Southern, CadenceUX](https://github.com/CadenceUX/claris-filemaker-pro-skill/blob/bda594e15f4a6981e93403c4b187d262ca820116/references/date-time-functions-examples.md), commit `bda594e15f4a6981e93403c4b187d262ca820116`, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). CadenceUX explanatory prose is retained/adapted; all concrete examples and application patterns are independently authored replacements. No endorsement is implied.

Validation: signatures checked against `function-catalog.json`; selected calendar/arithmetic results checked locally, **not in FileMaker**. Upstream's engine-test claims are historical provenance, not validation of these replacements. Results involving `Get`, fields, or display formats specify expected kinds rather than fixed current values. Date displays below use US month/day/year unless specified; date strings require the file's matching creation-system format. Supply the named fields before using field-based examples. Provenance/test levels: [replacement ledger](replacement-ledger.json), text/date section.

## Contents
- [Date functions](#date-functions): Date, Day, DayName, DayOfWeek, DayOfYear, Month, MonthName, WeekOfYear, WeekOfYearFiscal, Year
- [Common patterns](#common-patterns): range, business days, next-month business day, age bracket, overdue flag, ISO formatting/parsing
- [Time and timestamp functions](#time-and-timestamp-functions): Hour, Minute, Seconds, Time, Timestamp
- [Interaction patterns](#interaction-patterns): time extraction, H:MM duration, sortable timestamp text

## Date functions

All 10 date functions with syntax, parameters, return types and usage patterns.
Reference: https://help.claris.com/en/pro-help/content/date-functions.html

**Overview:** FileMaker stores dates internally as day ordinals from 1 January 0001 (day 1). Date arithmetic is integer addition/subtraction — no special functions are needed for days between two dates. These functions handle construction, decomposition and week/day-of-week calculations.

**Date arithmetic basics:**
```filemaker
// Elapsed days since a specimen was collected:
Get ( CurrentDate ) - Specimen::CollectedOn
// Days until a permit expires; negative means expired:
Permit::ExpiresOn - Get ( CurrentDate )
// Follow-up interval from today and transit interval from a field:
Get ( CurrentDate ) + 21
Shipment::DepartedOn + 14
// Date fields store numbers; construct dates with Date, including overflow:
Date ( Month ( Specimen::CollectedOn ) ; Day ( Specimen::CollectedOn ) + 45 ; Year ( Specimen::CollectedOn ) )
// Expected kinds: day counts for subtraction; dates for the constructed/add-day results.
// Select a Date calculation result type when a date display is required.
```

### Date ( month ; day ; year )
Constructs a date value from numeric month, day and year components. Handles overflow — a day beyond the last day of a month rolls to the next month.
Parameters: `month` (1–12); `day` (1–31, can overflow); `year` (4-digit).
Returns: date.
```filemaker
Date ( 8 ; 18 ; 2032 ) // → 8/18/2032, scheduled inspection
Date ( 14 ; 1 ; 2031 ) // → 2/1/2032, month overflow
Date ( 9 ; 0 ; 2032 ) // → 8/31/2032, day before September begins
Date ( 9 ; -3 ; 2032 ) // → 8/28/2032, four days before September begins
Date ( 4 ; 24 ; 2032 ) - Date ( 4 ; 6 ; 2032 ) // → 18 elapsed days
```
First day of current month, using day subtraction instead of reconstruction:
```filemaker
Let ( reportDay = Get ( CurrentDate ) ; reportDay - Day ( reportDay ) + 1 )
// Expected kind: first date of the current reporting month
```
Last day of current month (day 0 of next month = last day of this month):
```filemaker
Let ( reportDay = Get ( CurrentDate ) ;
  Date ( Month ( reportDay ) + 1 ; 0 ; Year ( reportDay ) )
)
// Expected kind: last date of the current reporting month
```
Add N months, clamped to the end of the target month. Plain month addition with the original day **overflows**: a non-leap-year end-of-January renewal shifted one month can land in March instead of February.
```filemaker
// Warranty review moved three months forward; negative shifts subtract months.
Let ( [
  reviewDate = Date ( 11 ; 30 ; 2031 ) ;
  shiftMonths = 3 ;
  targetFirst = Date ( Month ( reviewDate ) + shiftMonths ; 1 ; Year ( reviewDate ) ) ;
  targetLast = Date ( Month ( targetFirst ) + 1 ; 0 ; Year ( targetFirst ) )
] ;
  Min ( targetLast ; targetFirst + Day ( reviewDate ) - 1 )
)
// → 2/29/2032; using 11/30/2030 instead produces 2/28/2031.
// Select a Date calculation result type for the numeric Min result.
```
Same day next year:
```filemaker
Let ( serviceDate = Equipment::CommissionedOn ;
  Date ( Month ( serviceDate ) ; Day ( serviceDate ) ; Year ( serviceDate ) + 1 )
)
// Expected kind: anniversary date; a leap-day anniversary can overflow into March.
```

### Day ( date )
Extracts the day-of-month component (1–31).
Parameters: `date` — a date value or expression. Returns: number.
```filemaker
Day ( "8/18/2032" ) // → 18; assumes MM/DD/YYYY date interpretation
Day ( Specimen::CollectedOn ) // Expected kind: collection day of month
```

### DayName ( date )
Returns the full English name of the day of the week.
Parameters: `date`. Returns: text.
```filemaker
DayName ( Date ( 3 ; 5 ; 2032 ) ) // → Friday
DayName ( Inspection::ScheduledOn ) // Expected kind: English weekday of the scheduled inspection
DayName ( "3/5/2032" ) // → Friday in an MM/DD/YYYY file
```
Useful for display fields and conditional logic:
```filemaker
Let ( weekdayLabel = DayName ( Get ( CurrentDate ) ) ;
  If ( weekdayLabel = "Sunday" or weekdayLabel = "Saturday" ; "Closed to deliveries" ; "Receiving open" )
)
// Expected kind: delivery-access label based on today's weekday
```

### DayOfWeek ( date )
Returns the day of the week as a number (1 = Sunday … 7 = Saturday).
Parameters: `date`. Returns: number.
```filemaker
DayOfWeek ( "3/6/2032" ) // → 7 in an MM/DD/YYYY file
DayOfWeek ( Date ( 3 ; 7 ; 2032 ) ) // → 1
DayOfWeek ( Shipment::DepartedOn ) // Expected kind: weekday number for the departure date
```
ISO weekday (1=Monday … 7=Sunday):
```filemaker
Mod ( DayOfWeek ( Inspection::ScheduledOn ) + 5 ; 7 ) + 1
// Expected kind: ISO weekday number for the inspection
```
Next Monday from any date (includes the same day if already Monday):
```filemaker
Let ( arrivalDate = Shipment::ArrivesOn ;
  arrivalDate + Mod ( 2 - DayOfWeek ( arrivalDate ) ; 7 )
)
// Expected kind: Monday on or after arrival, not necessarily strictly later
```
Skip weekends — next business day, without a holiday calendar:
```filemaker
Let ( [
  candidate = Permit::SubmittedOn + 1 ;
  weekday = DayOfWeek ( candidate )
] ;
  candidate + Case ( weekday = 7 ; 2 ; weekday = 1 ; 1 ; 0 )
)
// Expected kind: next Monday–Friday date; Saturday advances two days, Sunday one
```

### DayOfYear ( date )
Returns the ordinal day of the year (1–366).
Parameters: `date`. Returns: number.
```filemaker
DayOfYear ( Date ( 3 ; 1 ; 2032 ) ) // → 61, leap-year sampling day
```
Days remaining in year (leap-year safe):
```filemaker
Let ( auditDay = Get ( CurrentDate ) ;
  DayOfYear ( Date ( 12 ; 31 ; Year ( auditDay ) ) ) - DayOfYear ( auditDay )
)
// Expected kind: remaining calendar days, excluding today
```

### Month ( date )
Extracts the month component (1–12).
Parameters: `date`. Returns: number.
```filemaker
Month ( "11/23/2032" ) // → 11; assumes MM/DD/YYYY date interpretation
```
Quarter calculation:
```filemaker
Div ( Month ( Shipment::DepartedOn ) - 1 ; 3 ) + 1
// Expected kind: 1 (Q1), 2 (Q2), 3 (Q3), or 4 (Q4)
```
Financial year quarter (July–June):
```filemaker
Div ( Mod ( Month ( Grant::ReceivedOn ) + 5 ; 12 ) ; 3 ) + 1
// Expected kind: July–September = 1, October–December = 2,
// January–March = 3, April–June = 4
```

### MonthName ( date )
Returns the full English name of the month.
Parameters: `date`. Returns: text.
```filemaker
MonthName ( "11/23/2032" ) // → November in an MM/DD/YYYY file
```
Short month name (first 3 characters):
```filemaker
Left ( MonthName ( Date ( 11 ; 23 ; 2032 ) ) ; 3 ) // → Nov, sample-batch heading
```

### WeekOfYear ( date )
Returns the week number of the year, 1–54. Partial weeks at the start and end of the year count as full weeks, so 1 January is always week 1. For ISO 8601 week numbers use `WeekOfYearFiscal ( date ; 2 )`.
Parameters: `date`. Returns: number.
```filemaker
WeekOfYear ( "1/1/2032" ) // → 1 in an MM/DD/YYYY file
WeekOfYear ( Inspection::ScheduledOn ) // Expected kind: calendar week number, not necessarily ISO
```

### WeekOfYearFiscal ( date ; startingDay )
Returns the week number using a custom fiscal week start day.
Parameters: `date`; `startingDay` — 1 (Sunday) through 7 (Saturday). Returns: number.
```filemaker
WeekOfYearFiscal ( Date ( 1 ; 11 ; 2032 ) ; 1 ) // → 2, Sunday-start operations week
WeekOfYearFiscal ( Date ( 1 ; 1 ; 2032 ) ; 5 ) // → 1, Thursday-start reporting week
WeekOfYearFiscal ( Date ( 1 ; 2 ; 2032 ) ; 1 ) // → 53, prior Sunday-start week-year
```
ISO 8601 week number — starting day 2 (Monday) applies the ISO rule: week 1 is the first week with four or more days in the new year.
```filemaker
WeekOfYearFiscal ( Date ( 1 ; 1 ; 2027 ) ; 2 ) // → 53, belongs to 2026's final ISO week
WeekOfYearFiscal ( Date ( 12 ; 30 ; 2030 ) ; 2 ) // → 1, belongs to 2031's first ISO week
```
Pair with the ISO week-year when formatting: the week number alone doesn't say which year it belongs to.

### Year ( date )
Extracts the 4-digit year component.
Parameters: `date`. Returns: number.
```filemaker
Year ( Equipment::CommissionedOn ) // Expected kind: equipment commissioning year
Year ( "8/18/2032" ) // → 2032 in an MM/DD/YYYY file
```
Age in years, illustrated as complete years of equipment service:
```filemaker
Let ( [
  asOf = Get ( CurrentDate ) ;
  commissioned = Equipment::CommissionedOn ;
  elapsedYears = Year ( asOf ) - Year ( commissioned ) ;
  anniversaryPending = Month ( asOf ) < Month ( commissioned ) or
    ( Month ( asOf ) = Month ( commissioned ) and Day ( asOf ) < Day ( commissioned ) )
] ;
  elapsedYears - anniversaryPending
)
// Expected kind: full service years, subtracting one before this year's anniversary
```

## Common patterns

**Date range check:**
```filemaker
Let ( inspectionDate = Inspection::ScheduledOn ;
  inspectionDate ≥ Date ( 4 ; 1 ; 2032 ) and inspectionDate ≤ Date ( 9 ; 30 ; 2032 )
)
// Expected kind: Boolean, including both endpoints of the inspection season
```

**Business days (Mon–Fri) from `start` up to, not including, `end`**, no public holidays. Upstream reports 140 engine-tested date pairs for its original pattern; that claim does not validate this independently authored replacement. Require end ≥ start.
```filemaker
// Count full working weeks, then walk backward through at most six tail dates.
Let ( [
  windowStart = Inspection::WindowStart ;
  windowStop = Inspection::WindowEnd ;
  span = windowStop - windowStart ;
  blocks = Div ( span ; 7 ) ;
  tail = Mod ( span ; 7 )
] ;
  blocks * 5 + While ( [ remaining = tail ; count = 0 ] ; remaining > 0 ;
    [ weekday = DayOfWeek ( windowStop - remaining ) ;
      count = count + ( weekday > 1 and weekday < 7 ) ;
      remaining = remaining - 1 ] ; count )
)
// Expected kind: weekday count; full-week arithmetic bounds the loop to six dates.
```
To include the end date, use `Inspection::WindowEnd + 1` as the stopping value. For holidays, subtract a count of matching weekday dates from a holidays table (for example, an `ExecuteSQL` query with `BETWEEN`); preserve the half-open boundary by excluding the end or querying through end minus one. Do not double-subtract weekend holidays or duplicate holiday rows. `While` requires FileMaker 18 or later.

**First business day of next month:**
```filemaker
Let ( [
  referenceDay = Get ( CurrentDate ) ;
  nextMonth = Date ( Month ( referenceDay ) + 1 ; 1 ; Year ( referenceDay ) ) ;
  weekday = DayOfWeek ( nextMonth )
] ;
  nextMonth + Case ( weekday = 7 ; 2 ; weekday = 1 ; 1 ; 0 )
)
// Expected kind: next month's first Monday–Friday date; holidays not considered
```

**Age bracket** (exact age — subtract a year if the birthday hasn't happened yet):
```filemaker
// Museum membership reporting; same thresholds as the upstream age-band pattern.
Let ( [
  reportDate = Get ( CurrentDate ) ;
  born = Member::BirthDate ;
  anniversary = Date ( Month ( born ) ; Day ( born ) ; Year ( reportDate ) ) ;
  ageYears = Year ( reportDate ) - Year ( born ) - ( reportDate < anniversary )
] ;
  Case ( ageYears ≥ 65 ; "Senior: 65+" ;
         ageYears ≥ 50 ; "Established: 50–64" ;
         ageYears ≥ 35 ; "Mid-career: 35–49" ;
         ageYears ≥ 25 ; "Adult: 25–34" ;
         ageYears ≥ 18 ; "Young adult: 18–24" ;
         "Youth: under 18" )
)
// Expected kind: age-band label; Date overflow treats leap-day anniversary as March 1 in a non-leap year.
```

**Overdue flag:**
```filemaker
If ( Loan::ReturnBy < Get ( CurrentDate ) and Loan::State ≠ "Returned" ; 1 ; 0 )
// Expected kind: 1 for an unreturned overdue museum loan, otherwise 0
```

**Format date as ISO 8601 (YYYY-MM-DD) text:**
```filemaker
Let ( catalogDate = Specimen::CollectedOn ;
  Right ( "0000" & Year ( catalogDate ) ; 4 ) & "-" &
  Right ( "00" & Month ( catalogDate ) ; 2 ) & "-" &
  Right ( "00" & Day ( catalogDate ) ; 2 )
)
// Expected kind: zero-padded date text, e.g. 2032-08-18 for that collection date
```

**Parse ISO date string to FileMaker date:**
```filemaker
Let ( exportedDate = "2032-08-18" ;
  Date ( GetAsNumber ( Middle ( exportedDate ; 6 ; 2 ) ) ;
         GetAsNumber ( Middle ( exportedDate ; 9 ; 2 ) ) ;
         GetAsNumber ( Left ( exportedDate ; 4 ) ) )
)
// → 8/18/2032. Fixed-position parsing assumes valid YYYY-MM-DD input;
// it does not validate separators or reject impossible dates (Date can normalize overflow).
```

## Time and timestamp functions

All 4 time functions plus 1 timestamp function with syntax, parameters, return types and usage patterns.
Reference: https://help.claris.com/en/pro-help/content/time-functions.html

**Overview:** FileMaker stores time values as seconds since midnight, so arithmetic is addition/subtraction of seconds. A `Timestamp` is stored as seconds since the FileMaker epoch (1 January 0001, 00:00:00). Time fields accept `HH:MM:SS`; timestamp fields combine a date and time.

**Time arithmetic basics:**
```filemaker
// Inspection duration in seconds and hours:
Inspection::FinishedAt - Inspection::StartedAt
( Inspection::FinishedAt - Inspection::StartedAt ) / 3600
// Add a 20-minute cooling interval:
Specimen::HeatedAt + 20 * 60
// Construct midnight from an overflowing prior-hour component:
Time ( -1 ; 60 ; 0 ) // → midnight (00:00:00)
// Was the access event logged today?
GetAsDate ( AccessLog::RecordedAt ) = Get ( CurrentDate )
// Field/Get examples return duration, time or Boolean kinds, not fixed values.
// Use timestamps for elapsed time across dates; time-only subtraction has no date context.
```

### Hour ( time )
Extracts the hour from a time or timestamp — 0–23 for a time of day, but a duration keeps counting.
Parameters: `time` — a time or timestamp value or expression. Returns: number.
```filemaker
Hour ( Time ( 38 ; 20 ; 0 ) ) // → 38, multi-day equipment run
Hour ( "6:42:17" ) // → 6, departure hour
```
Business hours check:
```filemaker
Let ( receivingHour = Hour ( Get ( CurrentTime ) ) ;
  receivingHour ≥ 7 and receivingHour < 15
)
// Expected kind: true during receiving hours, 7 AM inclusive to 3 PM exclusive
```
Duration in hours from a start timestamp:
```filemaker
Let ( elapsed = Get ( CurrentTimestamp ) - Equipment::RunStartedAt ;
  Hour ( GetAsTime ( elapsed ) )
)
// Expected kind: extracted whole duration hours; do not confuse timestamp numeric coercion with a Time.
// Upstream limits its direct Hour(timestamp difference) pattern to ≤24h and recommends
// dividing by 3600 for longer intervals. For total (possibly fractional) hours use:
( Get ( CurrentTimestamp ) - Equipment::RunStartedAt ) / 3600
// This arithmetic works for both short and multi-day intervals; local engine behavior is untested.
```

### Minute ( time )
Extracts the minute component from a time or timestamp value (0–59).
Parameters: `time` — a time or timestamp value or expression. Returns: number.
```filemaker
Minute ( "6:42:17" ) // → 42, departure minute
```
Round a time down to the nearest 15 minutes:
```filemaker
Let ( departure = Dispatch::LeavesAt ;
  Time ( Hour ( departure ) ; Div ( Minute ( departure ) ; 15 ) * 15 ; 0 )
)
// Expected kind: time at the beginning of the departure's quarter-hour slot
```

### Seconds ( time )
Extracts the seconds component from a time or timestamp value (0–59; can return fractional seconds if sub-second precision is present).
Parameters: `time` — a time or timestamp value or expression. Returns: number.
```filemaker
Seconds ( "6:42:17" ) // → 17, instrument-log seconds component
```
Total seconds since midnight:
```filemaker
Let ( readingTime = Instrument::ReadAt ;
  Seconds ( readingTime ) + 60 * ( Minute ( readingTime ) + 60 * Hour ( readingTime ) )
)
// Expected kind: seconds from midnight for a time-of-day value.
// Same as the underlying numeric Time value, not a Timestamp's epoch seconds.
```

### Time ( hours ; minutes ; seconds )
Constructs a time value from numeric hour, minute and second components. Handles overflow — excess minutes roll over to hours.
Parameters: `hours` (0–23, can overflow); `minutes` (0–59, can overflow); `seconds` (0–59, can overflow). Returns: time.
```filemaker
Time ( 6 ; 42 ; 17 ) // → 6:42:17, scheduled departure
Time ( 6.25 ; 8 ; 12 ) // → 6:23:12, fractional hour contributes 15 minutes
Time ( 6 ; 42 ; 95 ) // → 6:43:35, seconds overflow
```
Add 2.5 hours to a time:
```filemaker
// Estimate completion after a two-and-a-half-hour sterilization cycle:
Time ( Hour ( Sterilizer::StartedAt ) ; Minute ( Sterilizer::StartedAt ) + 150 ; Seconds ( Sterilizer::StartedAt ) )
// Equivalent numeric addition:
Sterilizer::StartedAt + 150 * 60
// Expected kind: time 2.5 hours later; Time can represent durations beyond 24h
```
Round a time to the nearest hour:
```filemaker
Let ( bookedTime = Dispatch::LeavesAt ;
  Time ( Hour ( bookedTime ) + ( Minute ( bookedTime ) ≥ 30 ) ; 0 ; 0 )
)
// Expected kind: whole-hour time, half-hour ties rounded upward
```
Convert decimal hours to a Time value:
```filemaker
Let ( benchHours = 3.4 ; Time ( 0 ; 0 ; benchHours * 3600 ) )
// → 3:24:00, duration of a lab procedure
```

### Timestamp ( date ; time )
Constructs a timestamp value by combining a date and a time.
Parameters: `date` — a date value; `time` — a time value. Returns: timestamp.
```filemaker
Timestamp ( Date ( 8 ; 18 ; 2032 ) ; Time ( 6 ; 42 ; 17 ) )
// → 8/18/2032 6:42:17 AM, specimen handoff timestamp in US display
```
Convert a timestamp back to its components:
```filemaker
GetAsDate ( Handoff::RecordedAt ) // Expected kind: date part
GetAsTime ( Handoff::RecordedAt ) // Expected kind: time part
// Date requires three parameters: passing only a timestamp to Date is an error.
// Component functions also accept a timestamp directly; these are separate calculations:
Month ( Handoff::RecordedAt )
Day ( Handoff::RecordedAt )
Year ( Handoff::RecordedAt )
Hour ( Handoff::RecordedAt )
```
Timestamp arithmetic:
```filemaker
// Minutes since a specimen handoff:
( Get ( CurrentTimestamp ) - Handoff::RecordedAt ) / 60
// Was an access event recorded within the last 24 hours? Exclude future entries too:
Let ( ageSeconds = Get ( CurrentTimestamp ) - AccessLog::RecordedAt ;
  ageSeconds ≥ 0 and ageSeconds < 24 * 60 * 60
)
// Schedule a recheck 48 hours after a recorded inspection:
Inspection::RecordedAt + 2 * 24 * 60 * 60
// Expected kinds: elapsed minutes, Boolean recent-event flag, future timestamp.
```

## Interaction patterns

Time in a Timestamp field:
```filemaker
GetAsTime ( Handoff::RecordedAt ) // Expected kind: time portion of the timestamp
Mod ( Handoff::RecordedAt ; 24 * 60 * 60 )
// Expected kind: the same time portion as a plain number of seconds, not typed Time
```
Format a duration as `H:MM`:
```filemaker
Let ( [
  elapsed = Inspection::FinishedAt - Inspection::StartedAt ;
  hours = Div ( elapsed ; 3600 ) ;
  minutes = Div ( elapsed - hours * 3600 ; 60 )
] ;
  hours & ":" & Right ( "00" & minutes ; 2 )
)
// Expected kind: duration text, e.g. 27:08 for 97680 seconds.
// Assumes nonnegative elapsed time; remaining seconds are truncated, not rounded.
```
Sort-safe timestamp string (ISO 8601–style):
```filemaker
Let ( handoffTime = Handoff::RecordedAt ;
  Right ( "0000" & Year ( handoffTime ) ; 4 ) & "-" &
  Right ( "00" & Month ( handoffTime ) ; 2 ) & "-" &
  Right ( "00" & Day ( handoffTime ) ; 2 ) & " " &
  Right ( "00" & Hour ( handoffTime ) ; 2 ) & ":" &
  Right ( "00" & Minute ( handoffTime ) ; 2 )
)
// Expected kind: YYYY-MM-DD HH:MM, chronologically sortable at minute precision
// within the same time basis; no seconds, timezone or UTC conversion is supplied.
```
