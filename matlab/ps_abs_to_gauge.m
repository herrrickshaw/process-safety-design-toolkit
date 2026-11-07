function pg = ps_abs_to_gauge(p, abs_unit, gauge_unit)
%PS_ABS_TO_GAUGE  Absolute pressure to gauge reading, subtracting the standard atmosphere (101.325 kPa).
  p_kpa = ps_units(p, abs_unit, 'kPa abs');
  pg = ps_units(p_kpa - 101.325, 'kPag', gauge_unit);
end
