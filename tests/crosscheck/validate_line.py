"""Line-fed release experiments against the HEM line model. Geometry: DNV JFSH Validation document (supply lines, roughness 1.5 micron);
vessel state and measured rates: RIVM 620550005/2012 (AA 3026: 7.53 bar(a), 5.5 C, 16.1 kg/s; AA 3029: 7.34 bar(a), 3.2 C, 18.0 kg/s;
JIVE 8051: 19.85 bar(a), 1.9 C, 6.86 kg/s). Fittings are NOT in the sources, so the loss coefficient implied by the measured rate is back-calculated
and labelled as such; it is not a prediction. Run: PYTHONPATH=. python3 tests/crosscheck/validate_line.py"""
from process_safety import line_flow as lf

CASES = [("AA 3026", "propane", 278.65, 7.53e5, [(67.0, 0.152), (13.0, 0.052)], 16.1),
         ("AA 3029", "propane", 276.35, 7.34e5, [(67.0, 0.152), (13.0, 0.052)], 18.0),
         ("JIVE 8051 (152 mm line)", "n-butane", 275.05, 19.85e5, [(79.0, 0.152), (1.85, 0.040)], 6.86)]
PA = 1.013e5


def implied_k(fl, T, P, seg, meas):
    lo, hi = 0.0, 4000.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        w = lf.line_discharge(fl, T, P, PA, seg, k_fittings=mid)["W_kg_s"]
        lo, hi = (mid, hi) if w > meas else (lo, mid)
    return 0.5 * (lo + hi)


def main():
    within = {}
    print("%-26s %9s %9s %7s  %s" % ("case", "model", "measured", "dev", "implied K_fittings if model > measured"))
    for nm, fl, T, P, seg, meas in CASES:
        r = lf.line_discharge(fl, T, P, PA, seg)
        dev = r["W_kg_s"] / meas - 1.0
        within[nm] = abs(dev) <= 0.10
        k = "-"
        if r["W_kg_s"] > meas:
            k = "%.0f" % implied_k(fl, T, P, seg, meas)
        print("%-26s %9.2f %9.2f %+6.0f%%  %s" % (nm, r["W_kg_s"], meas, 100 * dev, k))
    print("AA 3026 within 10 %%: %s; AA 3029 within 10 %%: %s; JIVE within 10 %%: %s" % (within["AA 3026"], within["AA 3029"], within["JIVE 8051 (152 mm line)"]))
    if within["AA 3029"]:
        print("CROSS-PREDICTION-WITHIN-10")
    print("LINE-VALIDATION-DONE")


if __name__ == "__main__":
    main()
