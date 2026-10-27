# Numeric Functions — Examples (Number, Financial, Trigonometric, Repeating)

Adapted from **Darrin Southern / CadenceUX**, [claris-filemaker-pro-skill](https://github.com/CadenceUX/claris-filemaker-pro-skill), commit `bda594e15f4a6981e93403c4b187d262ca820116`, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Changes: retained the CadenceUX synthesis, function coverage and factual guidance; replaced all concrete examples, added explicit fixtures and verification boundaries, and corrected misleading sustainability and edge-case guidance. No FileMaker engine was available. Outputs below are **expected**, not observed in FileMaker; decimal formatting and last digits may vary. Python mathematical checks are recorded in the development replacement manifest. Names prefixed `Demo` describe hypothetical schema to create, not existing database objects.

## Contents
- [Number Functions](#filemaker-number-functions--syntax--examples): Abs, Ceiling, Combination, Div, Exp, Factorial, Floor, Int, Lg, Ln, Log, Mod, Random, Round, SetPrecision, Sign, Sqrt, Truncate
- [Financial Functions](#filemaker-financial-functions--syntax--examples): FV, NPV, PMT, PV, Combined example: Loan amortisation summary
- [Trigonometric Functions](#filemaker-trigonometric-functions--syntax--examples): Pi, Degrees, Radians, Sin, Cos, Tan, Acos, Asin, Atan, Practical examples
- [Repeating Functions](#filemaker-repeating-functions--syntax--examples): Extend, GetRepetition, Last, Interaction patterns

---

# FileMaker Number Functions — Syntax & Examples

Source: https://help.claris.com/en/pro-help/content/number-functions.html  
All 18 native number functions with format, parameters, and examples.

## Abs ( number )
Returns the absolute value of a number (removes the sign).
For signed warehouse adjustments, both directions have the same magnitude:
```filemaker
Abs ( -18.75 ) // expected 18.75
Abs ( 18.75 )  // expected 18.75
```

## Ceiling ( number )
Rounds a number **up** to the next integer, regardless of the decimal value.
Whole-slot allocation, including negative and already-integral inputs:
```filemaker
Ceiling ( 6.25 )  // expected 7
Ceiling ( -6.25 ) // expected -6
Ceiling ( 8 )     // expected 8
```

## Combination ( setSize ; numberOfChoices )
Returns the number of unique ways to choose `numberOfChoices` items from a set of `setSize` (order does not matter). Useful in statistics and combinatorics; results form Pascal's triangle.
Choose three reviewers from nine; then calculate the probability that a random four-cell sample contains exactly two cells from each of two five-cell groups:
```filemaker
Combination ( 9 ; 3 ) // expected 84
Combination ( 5 ; 2 ) ^ 2 / Combination ( 10 ; 4 )
// expected 0.476190476190476…; favourable unordered samples / all samples
```

## Div ( number ; divisor )
Returns the integer quotient of `number ÷ divisor`, always rounding **toward negative infinity** (equivalent to applying Floor to the quotient).
```filemaker
Div ( 17.5 ; 4 )  // expected 4 complete bins
Div ( -17.5 ; 4 ) // expected -5, not -4
Div ( 29 ; 6 )    // expected 4
```

## Exp ( number )
Returns the value of the mathematical constant *e* (~2.71828) raised to the power of `number`.
A decay model, its zero-time identity, and its reverse growth multiplier:
```filemaker
Exp ( -2 ) // expected approximately 0.1353352832366127
Exp ( 0 * 7 ) // expected 1
Exp ( 3 ) // expected approximately 20.08553692318767
SetPrecision ( Exp ( -2 ) ; 25 )
// expected approximately 0.1353352832366126918939995
```
Use SetPrecision when additional digits are needed.

## Factorial ( number {; numberOfFactors } )
Returns the factorial of `number` (n!), stopping at 1 by default, or stopping after `numberOfFactors` multiplications if specified. Useful in statistics and combinatorics.
```filemaker
Factorial ( 4 ) // expected 24 arrangements of four distinct badges
Factorial ( 7 ) // expected 5040 arrangements of seven badges
Factorial ( 9 ; 4 ) // expected 3024: 9 × 8 × 7 × 6, four factors only
```

## Floor ( number )
Rounds a number **down** to the next lower integer, regardless of the decimal value.
```filemaker
Floor ( 7.8 )  // expected 7
Floor ( -7.2 ) // expected -8
Floor ( 12 )   // expected 12
```

## Int ( number )
Drops all digits to the right of the decimal point without rounding. For positive numbers behaves like `Floor`; for negative numbers, truncates toward zero (unlike `Floor`).
```filemaker
Int ( 6.8 )    // expected 6
Int ( -6.8 )   // expected -6; Floor of this input would be -7
Int ( 21.999 ) // expected 21
```

## Lg ( number )
Returns the base-2 logarithm of `number`.
Binary storage levels:
```filemaker
Lg ( 32 )    // expected 5, because 2^5 = 32
Lg ( 2 ^ 0 ) // expected 0: the multiplicative identity
Lg ( 4096 )  // expected 12
```

## Ln ( number )
Returns the natural (base-*e*) logarithm of `number`.
```filemaker
Ln ( 7 / 7 )   // expected 0
Ln ( Exp ( 3 ) ) // expected approximately 3; inverse functions
Ln ( 25 )      // expected approximately 3.218875824868201
```

## Log ( number )
Returns the common (base-10) logarithm of `number`.
```filemaker
Log ( 10000 )   // expected 4
Log ( 1000000 ) // expected 6
Log ( 9 / 9 )   // expected 0
```

## Mod ( number ; divisor )
Returns the remainder after `number` is divided by `divisor`. Useful for unit conversions and cyclic calculations.
```filemaker
Mod ( 347 ; 8 ) // expected 3 unpacked pieces
Mod ( 53 ; 7 )  // expected 4
Mod ( -17 ; 5 ) // expected 3; takes the divisor's sign
```
Convert a 24-hour reading to its 12-hour remainder (special-case remainder 0 if displaying 12):
```filemaker
Let ( eveningHour = 21 ; Mod ( eveningHour ; 12 ) ) // expected 9 (PM)
```
Split a service contract into complete years and remaining months:
```filemaker
Let ( duration = 53 ;
  Int ( duration / 12 ) & " yr + " & Mod ( duration ; 12 ) & " mo"
) // expected "4 yr + 5 mo"
```

## Random
Returns a random number ≥ 0 and < 1. Takes no parameters.
```filemaker
Let ( draw = Random ; draw ≥ 0 and draw < 1 ) // expected 1, not a fixed draw
```
For a positive integer N, generate an integer from 1 through N. This version explicitly binds the upper limit to a local variable; substitute your own positive-integer input:
```filemaker
Let ( upper = 37 ; 1 + Floor ( upper * Random ) ) // expected integer 1…37
```
Assign one of 64 test lanes:
```filemaker
Let ( laneCount = 64 ; 1 + Floor ( laneCount * Random ) ) // expected 1…64
```
Each evaluation can differ; no particular random output is asserted.

## Round ( number ; precision )
Rounds `number` to `precision` decimal places. Halves round **away from zero**. FileMaker uses decimal arithmetic, avoiding binary-float surprises. Use a negative `precision` to round to tens, hundreds, etc.
```filemaker
Round ( 86.375 ; 2 ) // expected 86.38: decimal tie
Round ( 8.5 ; 0 )    // expected 9
Round ( -8.5 ; 0 )   // expected -9: tie away from zero
Round ( 7.65 ; 1 )   // expected 7.7: decimal arithmetic
Round ( 48762.12 ; -3 ) // expected 49000
Round ( 86.375 ; -1 ) // expected 90
```

## SetPrecision ( expression ; precision )
Evaluates `expression` with extended decimal precision from 16 to 400 digits. Supports all functions except trigonometric. Does **not** simply truncate an already-computed result — the expression is evaluated with the requested precision.
```filemaker
SetPrecision ( 2 / 7 ; 30 )
// expected 0.285714285714285714285714285714
SetPrecision ( 4 / 11 ; 50 )
// expected 0.36363636363636363636363636363636363636363636363636
```
An entire conditional calculation, not just a final literal, can be evaluated at extended precision:
```filemaker
Let ( isAccelerated = 0 ;
  SetPrecision (
    If ( isAccelerated ; Exp ( 12 ) ; Average ( 2 / 7 ; 4 / 11 ; 3 / 13 ) ) ; 25
  )
) // expected approximately 0.2933732933732933732933733
```

## Sign ( number )
Returns `-1` if `number` is negative, `0` if zero, `1` if positive.
```filemaker
Sign ( -3.2 ) // expected -1
Sign ( 4 - 4 ) // expected 0
Sign ( 0.08 ) // expected 1
```
Use all three states to label a temperature change:
```filemaker
Let ( change = -1.25 ;
  Case ( Sign ( change ) < 0 ; "Cooling" ;
         Sign ( change ) = 0 ; "Steady" ; "Warming" )
) // expected "Cooling"
```

## Sqrt ( number )
Returns the square root of `number`.
```filemaker
Sqrt ( 144 ) // expected 12, a square tile's side from its area
Sqrt ( 7 )   // expected approximately 2.645751311064591
Sqrt ( 6 - 6 ) // expected 0
```

## Truncate ( number ; precision )
Removes digits beyond `precision` decimal places **without rounding**. Unlike `Round`, always truncates toward zero.
```filemaker
Truncate ( 48.987 ; 2 )  // expected 48.98
Truncate ( 6.999 ; 0 )   // expected 6
Truncate ( -6.999 ; 1 )  // expected -6.9
```
**Truncate vs Int vs Round:** apply the three operations to the same sensor reading:
```filemaker
Truncate ( 4.7 ; 0 ) // expected 4
Int ( 4.7 )          // expected 4, same for positive input
Round ( 4.7 ; 0 )    // expected 5
```

---

# FileMaker Financial Functions — Syntax & Examples

Source: https://help.claris.com/en/pro-help/content/financial-functions.html  
All 4 financial functions with syntax, parameters, return types, and usage patterns. Syntax is retained from the upstream reference, not engine-verified here.

**Overview:** FileMaker's four financial functions cover standard time-value-of-money calculations: present value, future value, loan payments, and net present value of unequal cash flows. All assume **periodic** (equal-interval) payments unless otherwise noted. Interest rates must be expressed **per period**, dividing an annual nominal rate by 12 for monthly payments.

**Key concepts:**
- `interestRate` — rate **per period** as a decimal; for example a 6% nominal annual rate gives a monthly rate of 0.005.
- `periods` / `term` — number of payment periods.
- **Signs:** unlike spreadsheet functions, FileMaker's PMT, PV and FV return **positive** results for positive inputs — no absolute-value adjustment is needed. All assume payment at the end of each period. With `interestRate` 0, PV and FV return payment multiplied by periods.

## FV ( payment ; interestRate ; periods )
Returns the **future value** of an investment with equal periodic payments at a constant interest rate. Useful for savings calculations — the accumulated amount after regular deposits.
Parameters: `payment` — fixed payment per period (positive); `interestRate` — rate per period as decimal; `periods` — number of periods.  
Returns: number (positive = accumulated value).
Three reserve models: monthly deposits, annual deposits plus an opening lump sum, and a rate period aligned to four deposits per year:
```filemaker
FV ( 125 ; 0.06 / 12 ; 36 ) // expected approximately 4917.013120585483
FV ( 850 ; 0.07 ; 12 ) + 3200 * ( 1 + 0.07 ) ^ 12
// expected approximately 22412.196664913204
FV ( 300 ; 0.08 / 4 ; 20 ) // expected approximately 7289.210939675316
```
Real-world: evaluate a gallery's replacement-equipment fund. Inputs are local fixture values, not fields:
```filemaker
Let ( [
  depositPerQuarter = 450 ;
  nominalAnnual = 0.048 ;
  savingYears = 6 ;
  paymentsPerYear = 4
] ;
  FV ( depositPerQuarter ; nominalAnnual / paymentsPerYear ; savingYears * paymentsPerYear )
) // expected approximately 12430.230139405176
```

## NPV ( payment ; interestRate )
Returns the **net present value** of a series of **unequal** future cash flows, discounted at a constant rate. Unlike FV/PV (which assume equal payments), the payment series is supplied by a **repeating field**. The upstream introduction also describes a list of values; do not interpret that as permission to pass an arbitrary return-delimited text list: `payment` must be a repeating field (or an expression returning a reference to one).
Parameters: `payment` — repeating cash flows (positive = inflow, negative = outflow); `interestRate` — discount rate per period as decimal.  
Returns: number.

Fixture to create: numeric `DemoCashFlows::Recovery` with five repetitions holding -3600, 1200, 1400, 1700, 900. Evaluate from that record:
```filemaker
NPV ( DemoCashFlows::Recovery ; 0.08 )
// expected approximately 668.914015541393
```
Put the initial investment in repetition 1 as a negative value. FileMaker discounts **every** repetition, the first included: repetition *i* is divided by (1 + rate)^*i*. In this fixture the hypothetical undiscounted-initial convention would give approximately 722.427136784704 instead. The result represents the transaction's discounted profit under FileMaker's timing convention.

## PMT ( principal ; interestRate ; term )
Returns the **payment amount** required per period to fully repay a loan of `principal` over `term` periods at `interestRate` per period. The result is **positive**.
Parameters: `principal` — loan amount (positive); `interestRate` — rate per period as decimal; `term` — number of payment periods.  
Returns: number.
```filemaker
PMT ( 18500 ; 0.054 / 12 ; 36 ) // expected approximately 557.790139510376
```
Total interest on a small workshop loan, retaining full payment precision until display:
```filemaker
Let ( [
  borrowed = 42000 ;
  monthlyRate = 0.072 / 12 ;
  paymentCount = 5 * 12 ;
  instalment = PMT ( borrowed ; monthlyRate ; paymentCount )
] ;
  instalment * paymentCount - borrowed
) // expected approximately 8137.150944892293
```

## PV ( payment ; interestRate ; periods )
Returns the **present value** of an investment that makes equal periodic payments — the lump sum today equivalent to receiving `payment` each period for `periods` periods, discounted at `interestRate`. Useful for annuity valuation or funding a fixed income stream.
Parameters: `payment` — fixed payment received per period (positive); `interestRate` — rate per period as decimal; `periods` — number of periods.  
Returns: number — positive for a positive `payment` (enter money you pay out as negative).
```filemaker
PV ( 720 ; 0.045 ; 8 ) // expected approximately 4749.037968498285
```
Retirement reserve: can 280000 fund a 1600 monthly withdrawal for 15 years at a constant nominal annual 3.6% return?
```filemaker
Let ( [
  requiredNow = PV ( 1600 ; 0.036 / 12 ; 15 * 12 ) ;
  available = 280000
] ;
  Case ( available ≥ requiredNow ; "Funded for this horizon" ; "Reserve shortfall" )
) // expected "Funded for this horizon"; requiredNow approximately 222282.918941358
```
This is a fixed-rate model, not an investment guarantee or a direct answer for an unspecified lifetime. **Correction to upstream:** sustainability requires available savings ≥ PV of withdrawals, not the reverse.

## Combined example: Loan amortisation summary
An equipment-finance summary, using a JSON result so numeric values remain available separately from display labels:
```filemaker
Let ( [
  financed = 68000 ;
  periodRate = 0.048 / 12 ;
  periods = 7 * 12 ;
  payment = PMT ( financed ; periodRate ; periods ) ;
  repaid = periods * payment
] ;
  JSONSetElement ( "{}" ;
    [ "paymentMonthly" ; Round ( payment ; 2 ) ; JSONNumber ] ;
    [ "paidOverall" ; Round ( repaid ; 2 ) ; JSONNumber ] ;
    [ "interestOverall" ; Round ( repaid - financed ; 2 ) ; JSONNumber ]
  )
)
// expected values: paymentMonthly 954.73, paidOverall 80197.18, interestOverall 12197.18
```
Apply currency and thousands-separator formatting on the layout. String concatenation does not insert thousands separators; rounding an instalment before multiplying can also change totals. This is a summary, not a period-by-period amortisation schedule.

---

# FileMaker Trigonometric Functions — Syntax & Examples

Source: https://help.claris.com/en/pro-help/content/trigonometric-functions.html  
All 9 trigonometric functions with syntax, parameters, return types, and usage patterns.

**Overview:** FileMaker's trigonometric functions work in **radians** (not degrees). Use Degrees and Radians to convert. Results carry about 16–17 significant digits; π is approximately 3.1415926535897932. Trigonometric functions don't support SetPrecision. Tiny rounding errors can make an inverse-function identity differ from its exact mathematical value in the last digits. Round before comparing or displaying. No exact FileMaker last-digit result is claimed here.

**Key constants and conversions:**
```filemaker
Round ( Pi ; 6 )       // expected 3.141593
Radians ( 540 ) / Pi   // expected approximately 3: three half-turns
Degrees ( Pi / 3 )     // expected approximately 60
Radians ( 30 )         // expected π/6
Radians ( 120 )        // expected 2π/3
Radians ( 720 )        // expected 4π: two full turns
```

## Pi
A constant — returns the value of π (pi) to FileMaker's full numeric precision.  
Parameters: none. Returns: number.
Area of a round sampling dish:
```filemaker
Round ( Pi * 6 ^ 2 ; 3 ) // expected 113.097 square units
```

## Degrees ( angleInRadians )
Converts an angle from **radians to degrees**.  
Parameters: `angleInRadians` — angle in radians. Returns: number (degrees).
```filemaker
Degrees ( Atan ( Sqrt ( 3 ) ) ) // expected approximately 60
Degrees ( 0.7 )                // expected approximately 40.10704565915762
```
Display a ramp's slope as an angle:
```filemaker
Let ( [ rise = 2 ; run = 5 ] ; Degrees ( Atan ( rise / run ) ) )
// expected approximately 21.80140948635181 degrees
```

## Radians ( angleInDegrees )
Converts an angle from **degrees to radians**.  
Parameters: `angleInDegrees` — angle in degrees. Returns: number (radians).
```filemaker
Radians ( 135 ) // expected approximately 2.356194490192345
```

## Sin ( angleInRadians )
Returns the **sine** of an angle (opposite/hypotenuse in a right triangle).  
Range of results: -1 to 1. Parameters: `angleInRadians` — angle in radians. Returns: number.
```filemaker
Sin ( Radians ( 30 ) ) // expected approximately 0.5
Sin ( 0.4 )           // expected approximately 0.3894183423086505
```
Vertical component of a robot's move, also applicable to layout positioning:
```filemaker
Let ( [ travel = 18 ; heading = 30 ] ; travel * Sin ( Radians ( heading ) ) )
// expected approximately 9 vertical units
```

## Cos ( angleInRadians )
Returns the **cosine** of an angle (adjacent/hypotenuse in a right triangle).  
Range of results: -1 to 1. Parameters: `angleInRadians` — angle in radians. Returns: number.
```filemaker
Cos ( 0.4 )           // expected approximately 0.9210609940028851
Cos ( Radians ( 120 ) ) // expected approximately -0.5
```
Horizontal component of the same robot's move:
```filemaker
Let ( [ travel = 18 ; heading = 30 ] ; travel * Cos ( Radians ( heading ) ) )
// expected approximately 15.5884572681199 horizontal units
```

## Tan ( angleInRadians )
Returns the **tangent** of an angle (opposite/adjacent in a right triangle; equivalent to sine divided by cosine).  
Undefined at ±90°, ±270°, etc. (returns a very large number near these angles).  
Parameters: `angleInRadians` — angle in radians. Returns: number.
```filemaker
Tan ( 0.25 )           // expected approximately 0.2553419212210363
Tan ( Radians ( 22 ) ) // expected approximately 0.4040262258351568
```
Survey a mast from 35 m away, adding the observer's instrument height:
```filemaker
Let ( [ baseline = 35 ; elevation = 22 ; instrumentHeight = 1.4 ] ;
  instrumentHeight + baseline * Tan ( Radians ( elevation ) )
) // expected approximately 15.54091790423049 m
```

## Acos ( number )
Returns the **arccosine** (inverse cosine) of a number — the angle (in radians) whose cosine equals `number`.  
Domain: -1 to 1 (outside this range returns empty/error). Range of results: 0 to π (0° to 180°).  
Parameters: `number` — a value between -1 and 1. Returns: number (radians).
For a triangle with adjacent-to-hypotenuse ratio 0.25, compare the radian result and two degree conversions:
```filemaker
Acos ( 0.25 )             // expected approximately 1.318116071652818
180 * Acos ( 0.25 ) / Pi  // expected approximately 75.52248781407008
Degrees ( Acos ( 0.25 ) ) // expected approximately 75.52248781407008
```

## Asin ( number )
Returns the **arcsine** (inverse sine) of a number — the angle (in radians) whose sine equals `number`.  
Domain: -1 to 1. Range of results: -π/2 to π/2 (-90° to 90°).  
Parameters: `number` — a value between -1 and 1. Returns: number (radians).
```filemaker
Asin ( -0.8 )             // expected approximately -0.9272952180016123
Degrees ( Asin ( -0.8 ) ) // expected approximately -53.13010235415598
```

## Atan ( number )
Returns the **arctangent** (inverse tangent) of a number — the angle (in radians) whose tangent equals `number`.  
Domain: any real number. Range of results: -π/2 to π/2 (-90° to 90°).  
Parameters: `number` — any real number. Returns: number (radians).
```filemaker
Atan ( 2 )             // expected approximately 1.10714871779409
Degrees ( Atan ( 2 ) ) // expected approximately 63.43494882292201
```
Bearing/heading from coordinate differences (2-argument atan, atan2): FileMaker has no native Atan2. This new fixture calculates an east-origin mathematical heading from a warehouse waypoint (7, 9) to (3, 12). It guards vertical and coincident points **before division**, unlike an eager quotient calculation:
```filemaker
Let ( [ east = 3 - 7 ; north = 12 - 9 ] ;
  Case (
    east = 0 ; Case ( north > 0 ; 90 ; north < 0 ; -90 ; "Undefined heading" ) ;
    Let ( acute = Degrees ( Atan ( north / east ) ) ;
      Case ( east > 0 ; acute ; north < 0 ; acute - 180 ; acute + 180 )
    )
  )
) // expected approximately 143.130102354156 degrees
```
The output range is -180°…180°; a coincident point has no heading, not a genuine 0° heading. This is not a compass north-origin convention.

## Practical examples

**Distance between two GPS coordinates (Haversine formula):** a hypothetical ferry leg on a spherical Earth from (10°, 20°) to (10.5°, 20.75°). Radius is 6371 km. Clamp the Haversine intermediate to [0,1] and handle antipodes explicitly so rounding cannot produce a negative square-root input or division by zero:
```filemaker
Let ( [
  originLat = Radians ( 10 ) ;
  destinationLat = Radians ( 10.5 ) ;
  halfLat = ( destinationLat - originLat ) / 2 ;
  halfLon = Radians ( 20.75 - 20 ) / 2 ;
  raw = Sin ( halfLat ) ^ 2 + Cos ( originLat ) * Cos ( destinationLat ) * Sin ( halfLon ) ^ 2 ;
  bounded = Min ( 1 ; Max ( 0 ; raw ) ) ;
  arc = Case ( bounded = 1 ; Pi ; 2 * Atan ( Sqrt ( bounded / ( 1 - bounded ) ) ) )
] ;
  Round ( 6371 * arc ; 2 )
) // expected 99.12 km; spherical approximation, not road distance
```

**X/Y coordinates on a circle (clock-face or pie-chart positioning):** place eight inspection markers around a ring, with a -90° offset to start at the top. This fixture places the second marker (zero-based slot 1):
```filemaker
Let ( [
  slot = 1 ; slots = 8 ;
  theta = Radians ( -90 + 360 * slot / slots ) ;
  radius = 75 ; centreX = 160 ; centreY = 120
] ;
  JSONSetElement ( "{}" ;
    [ "x" ; Round ( centreX + radius * Cos ( theta ) ; 0 ) ; JSONNumber ] ;
    [ "y" ; Round ( centreY + radius * Sin ( theta ) ; 0 ) ; JSONNumber ]
  )
) // expected x=213, y=67; layout Y increases downward
```

---

# FileMaker Repeating Functions — Syntax & Examples

Source: https://help.claris.com/en/pro-help/content/repeating-functions.html  
All 3 repeating functions with syntax, parameters, return types, and usage patterns.

**Overview:** Repeating fields store multiple values in a single field, indexed 1 through N (where N is the number of repetitions configured in the field definition). FileMaker's three Repeating functions let you: extend a non-repeating value across all repetitions of a calculation (`Extend`), access a specific repetition by index (`GetRepetition`), and retrieve the last non-blank value from a repeating field (`Last`). Repeating fields are a legacy feature; consider JSON arrays or related records for new designs, but these functions remain essential for maintaining existing solutions.

**Repeating field basics:** create hypothetical numeric `DemoSamples::Reading`, five repetitions, holding 14, 0, 22, empty, empty. Repetition 2 is a real zero, not blank.
```filemaker
DemoSamples::Reading[3] // expected 22 in the described fixture
```
Calculation context normally evaluates repetition 1 unless used in a repeating context or with GetRepetition. Defining five repetitions does not itself make every calculation iterate.

## Extend ( non-repeatingField )
Makes a non-repeating (single-value) field available as if it had as many repetitions as the repeating field it is being combined with in a calculation. Without `Extend`, using a non-repeating field in a repeating calculation only populates repetition 1; `Extend` propagates the value across all repetitions.
Parameters: `non-repeatingField` — any non-repeating field or expression. Returns: a repeating value (same type as the input).

Fixture: on `DemoPacking`, numeric `Count` repetitions are 2, 4, 3; numeric `UnitMass` repetitions are 1.5, 0.75, 2.2; non-repeating `LossFraction` is 0.04. Use a three-repetition numeric calculation:
```filemaker
DemoPacking::Count * DemoPacking::UnitMass * Extend ( DemoPacking::LossFraction )
// expected repetitions 0.12, 0.12, 0.264: estimated lost mass
```
Apply one shared adjustment across repeating prices: create repeating `DemoPricing::Base` = 8, 12, 20 and non-repeating global `Discount` = 0.15:
```filemaker
DemoPricing::Base * Extend ( 1 - DemoPricing::Discount )
// expected repeating calculation 6.8, 10.2, 17
```
Conditional across repetitions: with `DemoSamples::Hold` a single text field, suppress readings on a held batch:
```filemaker
Case ( Extend ( DemoSamples::Hold = "Quarantine" ) ; 0 ; DemoSamples::Reading )
// expected all calculation repetitions 0 when Hold is "Quarantine"
```

## GetRepetition ( repeatingField ; number )
Returns the value of a specific repetition of a repeating field. This is the primary way to access individual repetitions in a calculation when you know the index at runtime (rather than design time).
Parameters: `repeatingField` — a repeating field; `number` — the repetition index (1-based). Returns: same type as the field.
Use the five-repetition Reading fixture above:
```filemaker
GetRepetition ( DemoSamples::Reading ; 3 ) // expected 22
GetRepetition ( DemoSamples::Reading ; 4 ) // expected empty
```
Dynamic month lookup: create a 12-repetition numeric `DemoCapacity::MonthlySlots`; repetition 9 contains 72. A fixed inspection date makes the example reproducible; replace it with the current date for a live monthly lookup:
```filemaker
Let ( inspectionDate = Date ( 9 ; 14 ; 2027 ) ;
  GetRepetition ( DemoCapacity::MonthlySlots ; Month ( inspectionDate ) )
) // expected 72, September capacity
```
Sum selected repetitions (not necessarily adjacent):
```filemaker
GetRepetition ( DemoSamples::Reading ; 1 ) + GetRepetition ( DemoSamples::Reading ; 3 )
// expected 36
```
Find the first populated slot without treating zero as empty. This three-slot search uses While instead of a fixed chain of branch variables:
```filemaker
While ( [ slot = 1 ; found = 0 ] ; slot ≤ 3 and found = 0 ;
  [ found = If ( IsEmpty ( GetRepetition ( DemoSamples::Reading ; slot ) ) ; 0 ; slot ) ;
    slot = slot + 1 ] ; found
) // expected 1; expected 0 if the first three repetitions are all blank
```
Build a ¶-delimited list as a bridge to modern patterns. Create text `DemoSamples::Labels`, three repetitions = "North", empty, "West":
```filemaker
List ( GetRepetition ( DemoSamples::Labels ; 1 ) ;
       GetRepetition ( DemoSamples::Labels ; 3 ) ;
       GetRepetition ( DemoSamples::Labels ; 2 ) )
// expected North¶West; List ignores empties, including when all supplied slots are empty
```

## Last ( repeatingField )
Returns the value of the **last non-blank repetition** in a repeating field. Useful for "current value" patterns where repetitions are used as a simple history log (earliest to latest, left to right).
Parameters: `repeatingField` — a repeating field. Returns: same type as the field.
```filemaker
Last ( DemoSamples::Reading ) // expected 22, not the maximum by definition
```
Running-total/log pattern: create ten-repetition numeric `DemoMeter::Cumulative`, and have each authorised script run append the next cumulative meter reading to the next empty slot:
```filemaker
Last ( DemoMeter::Cumulative ) // expected <most recently appended nonblank reading>
```
Last supplies the latest entry, not a sum. Chronological meaning depends on append order.
Check whether the final slot is occupied:
```filemaker
not IsEmpty ( GetRepetition ( DemoMeter::Cumulative ; 10 ) )
// expected 1 only if slot 10 is nonblank
```
Only a gap-free append invariant makes that equivalent to "all ten filled"; an occupied final repetition alone does not prove it.

## Interaction patterns

Convert a repeating field to a JSON array (bridging legacy to modern):
```filemaker
JSONMakeArray ( List ( DemoSamples::Reading ) ; "" ; JSONNumber )
// expected [14,0,22]; List skips blank slots, so positions are not preserved
```
Aggregate functions naturally span repetitions, ignoring blanks:
```filemaker
Sum ( DemoSamples::Reading )   // expected 36
Max ( DemoSamples::Reading )   // expected 22
Count ( DemoSamples::Reading ) // expected 3, including the stored zero
```
