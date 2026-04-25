# Card Resistance Tester

# Purpose of this App

- Develop a test fixture for measuring the resistance of various resistors to be used in power cards
- Log all serial results to the serial console
- Establish a good range of card resistances to provide the most consistent separation of resulting
  card voltage levels
- Guarantee that no two adjacent power cards will have overlapping voltage levels, even with
  component tolerances and measured voltage noise
- Establish a testing circuit forming a voltage divisor between the +3.3V supply, the test resistor,
  the test pin, a fixed-voltage resistor, and finally ground.
    - The fixed resistor value will be specified as TEST_FIXED_TESISTANCE_OHMS
    - I will not specify the test resistance values, as I intend to do many runs of this test
      with different resistor values to find the best combination for the power cards.
    - The voltage at the test pin can be converted to resistance using:
      `R_test = R_fixed * (V_in - V_out) / V_out`
      where `V_in = 3.3 V` and `R_fixed` is the known fixed resistor value. Include the computed R_test
      resistance in the log.
- Measure the voltage at the test pin.
- To minimize the effect of noise, do not use instant voltage values, but instead calculate a
  "smoothed voltage" using an Exponential Moving Average (EMA), applied each sample at
  `ANALOG_POLL_FREQUENCY_SEC` intervals:
  `smoothed_voltage = ALPHA * raw_voltage + (1 - ALPHA) * smoothed_voltage`
  where `ALPHA` is a tunable constant (e.g. 0.05; lower = smoother but slower to respond,
  higher = faster but noisier). EMA is preferred over a trailing average because it uses O(1)
  memory, weights recent samples more heavily, and avoids reset artifacts at window boundaries.
- Calculate a "voltage delta" as `abs(raw_voltage - last_voltage)` each sample. Apply a
  **median filter** (window size N=5) to the raw delta values to produce `smoothed_deltav`.
  A median filter is used here (rather than EMA) because it rejects isolated ADC spikes more
  effectively, reducing false noise exceptions without slowing the response to genuine voltage
  changes.
- As each smoothed results are calculated, track the max/min/average voltage and voltage delta
  values.
- Log these results every HEARTBEAT_FREQUENCY_SEC seconds, with this log format:
    - f"V: {smoothed_voltage:4.2f}/∧{max_voltage:4.2f}/∨{min_voltage:<4.2f} "
    - f" - ΔV: {smoothed_deltav:6.4f} / μΔV {avg_deltav:<6.4f} / ∧ΔV {max_deltav:6.4f} "
    - f" - R_test: {R_test:.0f}ohm, Excp {delta_exceptions} - reset: {timer_elapsed_sec(LAST_EXCEPTION_TIMER):.2f}s ago"
- If the voltage delta exceeds an ALLOWABLE_NOISE_VOLTAGE_THRESHOLD, record an exception
- Include the total count of exceptions during this test run and the elapsed time since the last
  exception in the periodic result logs.
- If the voltage reads zero for longer than RESISTOR_CHANGE_SECONDS_THRESHOLD, then that means I
  have changed from one test resistor to another. In that once we get a non-zero smoothed voltage
  reading, case reset all the tracking values, including the exception values, to start a new test
  run.
- While the resistor is being changed, do not log a test-run end message. Instead, log a message
  indicating "Test resistor is not present" every HEARTBEAT_FREQUENCY_SEC seconds until the new
  resistor is detected and the test run is reset.
