function p = ps_gauge_to_abs(pg, gauge_unit, abs_unit)
%PS_GAUGE_TO_ABS  Gauge reading to absolute pressure, adding the standard atmosphere (101.325 kPa).
%   p = ps_gauge_to_abs(0, 'psig', 'psia')  -> 14.696
  pg_kpa = ps_units(pg, gauge_unit, 'kPag');
  p = ps_units(pg_kpa + 101.325, 'kPa abs', abs_unit);
end
