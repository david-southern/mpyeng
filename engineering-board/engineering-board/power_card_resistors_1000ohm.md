# Power Card Resistor Reference

## Design Parameters

| Parameter | Value |
|---|---|
| Supply voltage (Vcc) | 3.3 V |
| Fixed divider resistor (Rf) | 1000 Ω |
| Resistor series | E96 (1% metal film) |
| Number of cards | 25 |
| Voltage range | 0.190 V – 3.110 V |
| Voltage step (target) | ~121 mV |

## Voltage Divider Formula

```
V_out = Vcc × Rf / (Rf + Rc)
Rc    = Rf × (Vcc / V_target − 1)
```

## Card Resistor Table

| Card | Target V | Ideal Rc | E96 Rc | Actual V | Error (mV) | ADC count (10-bit) |
|:---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.190 V | 16.4 kΩ | **16.5 kΩ** | 0.189 V | -1.4 | 58 |
| 2 | 0.312 V | 9.59 kΩ | **9.53 kΩ** | 0.313 V | +1.7 | 97 |
| 3 | 0.433 V | 6.62 kΩ | **6.65 kΩ** | 0.431 V | -2.0 | 134 |
| 4 | 0.555 V | 4.95 kΩ | **4.99 kΩ** | 0.551 V | -4.1 | 171 |
| 5 | 0.677 V | 3.88 kΩ | **3.92 kΩ** | 0.671 V | -5.9 | 208 |
| 6 | 0.798 V | 3.13 kΩ | **3.16 kΩ** | 0.793 V | -5.1 | 246 |
| 7 | 0.920 V | 2.59 kΩ | **2.61 kΩ** | 0.914 V | -5.9 | 283 |
| 8 | 1.042 V | 2.17 kΩ | **2.15 kΩ** | 1.048 V | +6.0 | 325 |
| 9 | 1.163 V | 1.84 kΩ | **1.82 kΩ** | 1.170 V | +6.9 | 363 |
| 10 | 1.285 V | 1.57 kΩ | **1.58 kΩ** | 1.279 V | -5.9 | 397 |
| 11 | 1.407 V | 1.35 kΩ | **1.33 kΩ** | 1.416 V | +9.6 | 439 |
| 12 | 1.528 V | 1.16 kΩ | **1.15 kΩ** | 1.535 V | +6.6 | 476 |
| 13 | 1.650 V | 1.00 kΩ | **1.00 kΩ** | 1.650 V | +0.0 | 512 |
| 14 | 1.772 V | 862.7 Ω | **866.0 Ω** | 1.768 V | -3.2 | 548 |
| 15 | 1.893 V | 743.0 Ω | **750.0 Ω** | 1.886 V | -7.6 | 585 |
| 16 | 2.015 V | 637.7 Ω | **634.0 Ω** | 2.020 V | +4.6 | 626 |
| 17 | 2.137 V | 544.5 Ω | **549.0 Ω** | 2.130 V | -6.3 | 660 |
| 18 | 2.258 V | 461.3 Ω | **464.0 Ω** | 2.254 V | -4.2 | 699 |
| 19 | 2.380 V | 386.6 Ω | **383.0 Ω** | 2.386 V | +6.1 | 740 |
| 20 | 2.502 V | 319.1 Ω | **316.0 Ω** | 2.508 V | +5.9 | 777 |
| 21 | 2.623 V | 257.9 Ω | **255.0 Ω** | 2.629 V | +6.1 | 815 |
| 22 | 2.745 V | 202.2 Ω | **200.0 Ω** | 2.750 V | +5.0 | 852 |
| 23 | 2.867 V | 151.2 Ω | **150.0 Ω** | 2.870 V | +2.9 | 890 |
| 24 | 2.988 V | 104.3 Ω | **105.0 Ω** | 2.986 V | -1.9 | 926 |
| 25 | 3.110 V | 61.1 Ω | **60.4 Ω** | 3.112 V | +2.0 | 965 |

## Notes

- **E96 Rc** is the recommended resistor value to install in each card.
- All card resistors should be 1% tolerance metal film (E96 series).
- The fixed tray resistor (1000 Ω) should also be 1% tolerance.
- ADC counts assume 10-bit resolution with Vref = 3.3 V (i.e. `analogReference(EXTERNAL)` or a 3.3V Arduino).
- Voltage spacing is intentionally linear; resistor values are therefore logarithmically distributed.
- With Rf = 1000 Ω, worst-case divider current (lowest Rc card) is well under 4 mA per tray.
- Add a 100 kΩ pull-down resistor on each tray sense line to GND to produce a clean 0 V reading when no card is inserted.

## ADC Detection Windows

Suggested firmware threshold for each card: accept a reading if it falls within
**±40 ADC counts** of the nominal value (approximately ±130 mV). Adjust based on
observed noise floor during calibration.

| Card | E96 Rc | ADC count | Accept range |
|:---:|---:|:---:|---|
| 1 | **16.5 kΩ** | 58 | 18 – 98 |
| 2 | **9.53 kΩ** | 97 | 57 – 137 |
| 3 | **6.65 kΩ** | 134 | 94 – 174 |
| 4 | **4.99 kΩ** | 171 | 131 – 211 |
| 5 | **3.92 kΩ** | 208 | 168 – 248 |
| 6 | **3.16 kΩ** | 246 | 206 – 286 |
| 7 | **2.61 kΩ** | 283 | 243 – 323 |
| 8 | **2.15 kΩ** | 325 | 285 – 365 |
| 9 | **1.82 kΩ** | 363 | 323 – 403 |
| 10 | **1.58 kΩ** | 397 | 357 – 437 |
| 11 | **1.33 kΩ** | 439 | 399 – 479 |
| 12 | **1.15 kΩ** | 476 | 436 – 516 |
| 13 | **1.00 kΩ** | 512 | 472 – 552 |
| 14 | **866.0 Ω** | 548 | 508 – 588 |
| 15 | **750.0 Ω** | 585 | 545 – 625 |
| 16 | **634.0 Ω** | 626 | 586 – 666 |
| 17 | **549.0 Ω** | 660 | 620 – 700 |
| 18 | **464.0 Ω** | 699 | 659 – 739 |
| 19 | **383.0 Ω** | 740 | 700 – 780 |
| 20 | **316.0 Ω** | 777 | 737 – 817 |
| 21 | **255.0 Ω** | 815 | 775 – 855 |
| 22 | **200.0 Ω** | 852 | 812 – 892 |
| 23 | **150.0 Ω** | 890 | 850 – 930 |
| 24 | **105.0 Ω** | 926 | 886 – 966 |
| 25 | **60.4 Ω** | 965 | 925 – 1005 |

---
*Generated for STEM lab power card prop. Fixed resistor = 1000 Ω, Vcc = 3.3 V, E96 series.*