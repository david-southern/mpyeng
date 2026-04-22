# Power Card Resistor Reference

## Design Parameters

| Parameter | Value |
|---|---|
| Supply voltage (Vcc) | 3.3 V |
| Fixed divider resistor (Rf) | 120 Ω |
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
| 1 | 0.190 V | 1.96 kΩ | **1.96 kΩ** | 0.190 V | +0.4 | 59 |
| 2 | 0.312 V | 1.15 kΩ | **1.15 kΩ** | 0.312 V | +0.1 | 97 |
| 3 | 0.433 V | 793.8 Ω | **787.0 Ω** | 0.437 V | +3.3 | 135 |
| 4 | 0.555 V | 593.5 Ω | **590.0 Ω** | 0.558 V | +2.7 | 173 |
| 5 | 0.677 V | 465.2 Ω | **464.0 Ω** | 0.678 V | +1.4 | 210 |
| 6 | 0.798 V | 376.0 Ω | **374.0 Ω** | 0.802 V | +3.3 | 249 |
| 7 | 0.920 V | 310.4 Ω | **309.0 Ω** | 0.923 V | +3.1 | 286 |
| 8 | 1.042 V | 260.2 Ω | **261.0 Ω** | 1.039 V | -2.3 | 322 |
| 9 | 1.163 V | 220.4 Ω | **221.0 Ω** | 1.161 V | -2.0 | 360 |
| 10 | 1.285 V | 188.2 Ω | **187.0 Ω** | 1.290 V | +4.9 | 400 |
| 11 | 1.407 V | 161.5 Ω | **162.0 Ω** | 1.404 V | -2.4 | 435 |
| 12 | 1.528 V | 139.1 Ω | **140.0 Ω** | 1.523 V | -5.3 | 472 |
| 13 | 1.650 V | 120.0 Ω | **121.0 Ω** | 1.643 V | -6.8 | 509 |
| 14 | 1.772 V | 103.5 Ω | **105.0 Ω** | 1.760 V | -11.7 | 546 |
| 15 | 1.893 V | 89.2 Ω | **88.7 Ω** | 1.897 V | +4.1 | 588 |
| 16 | 2.015 V | 76.5 Ω | **76.8 Ω** | 2.012 V | -2.8 | 624 |
| 17 | 2.137 V | 65.3 Ω | **64.9 Ω** | 2.142 V | +5.0 | 664 |
| 18 | 2.258 V | 55.4 Ω | **54.9 Ω** | 2.264 V | +5.8 | 702 |
| 19 | 2.380 V | 46.4 Ω | **46.4 Ω** | 2.380 V | -0.2 | 738 |
| 20 | 2.502 V | 38.3 Ω | **38.3 Ω** | 2.502 V | -0.1 | 775 |
| 21 | 2.623 V | 31.0 Ω | **30.9 Ω** | 2.624 V | +0.9 | 814 |
| 22 | 2.745 V | 24.3 Ω | **24.3 Ω** | 2.744 V | -0.7 | 851 |
| 23 | 2.867 V | 18.1 Ω | **18.2 Ω** | 2.865 V | -1.3 | 888 |
| 24 | 2.988 V | 12.5 Ω | **12.4 Ω** | 2.991 V | +2.6 | 927 |
| 25 | 3.110 V | 7.33 Ω | **7.32 Ω** | 3.110 V | +0.3 | 964 |

## Notes

- **E96 Rc** is the recommended resistor value to install in each card.
- All card resistors should be 1% tolerance metal film (E96 series).
- The fixed tray resistor (120 Ω) should also be 1% tolerance.
- ADC counts assume 10-bit resolution with Vref = 3.3 V (i.e. `analogReference(EXTERNAL)` or a 3.3V Arduino).
- Voltage spacing is intentionally linear; resistor values are therefore logarithmically distributed.
- Cards with Rc < 15 Ω draw significant current through the divider (~100–200 mA per tray).
  Consider raising Vmin or adding a small series resistor on the tray supply if this is a concern.
- Add a 100 kΩ pull-down resistor on each tray sense line to GND to produce a clean 0 V reading when no card is inserted.

## ADC Detection Windows

Suggested firmware threshold for each card: accept a reading if it falls within
**±40 ADC counts** of the nominal value (approximately ±130 mV). Adjust based on
observed noise floor during calibration.

| Card | E96 Rc | ADC count | Accept range |
|:---:|---:|:---:|---|
| 1 | **1.96 kΩ** | 59 | 19 – 99 |
| 2 | **1.15 kΩ** | 97 | 57 – 137 |
| 3 | **787.0 Ω** | 135 | 95 – 175 |
| 4 | **590.0 Ω** | 173 | 133 – 213 |
| 5 | **464.0 Ω** | 210 | 170 – 250 |
| 6 | **374.0 Ω** | 249 | 209 – 289 |
| 7 | **309.0 Ω** | 286 | 246 – 326 |
| 8 | **261.0 Ω** | 322 | 282 – 362 |
| 9 | **221.0 Ω** | 360 | 320 – 400 |
| 10 | **187.0 Ω** | 400 | 360 – 440 |
| 11 | **162.0 Ω** | 435 | 395 – 475 |
| 12 | **140.0 Ω** | 472 | 432 – 512 |
| 13 | **121.0 Ω** | 509 | 469 – 549 |
| 14 | **105.0 Ω** | 546 | 506 – 586 |
| 15 | **88.7 Ω** | 588 | 548 – 628 |
| 16 | **76.8 Ω** | 624 | 584 – 664 |
| 17 | **64.9 Ω** | 664 | 624 – 704 |
| 18 | **54.9 Ω** | 702 | 662 – 742 |
| 19 | **46.4 Ω** | 738 | 698 – 778 |
| 20 | **38.3 Ω** | 775 | 735 – 815 |
| 21 | **30.9 Ω** | 814 | 774 – 854 |
| 22 | **24.3 Ω** | 851 | 811 – 891 |
| 23 | **18.2 Ω** | 888 | 848 – 928 |
| 24 | **12.4 Ω** | 927 | 887 – 967 |
| 25 | **7.32 Ω** | 964 | 924 – 1004 |

---
*Generated for STEM lab power card prop. Fixed resistor = 120 Ω, Vcc = 3.3 V, E96 series.*