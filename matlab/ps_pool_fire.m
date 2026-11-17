function r = ps_pool_fire(area_m2, Hc_kJ_kg, Hv_kJ_kg, cp_kJ_kgK, Tb_K, Ta_K, radiant_fraction, tau, distances_m, target_kW_m2)
%PS_POOL_FIRE  Pool-fire screening: Burgess/Zabetakis burning rate, Thomas flame height (no wind), Mudan-Croce surface emissive power,
%   point-source radiation.  Same model and limits as process_safety/pool_fire.py: point source is unreliable inside about 2-3 pool
%   diameters; no wind tilt, flame drag, smoke obscuration or spreading.  Correlation constants are the toolkit's (verify before use).
%   r = ps_pool_fire(area, Hc, Hv, cp, Tb [, Ta=298.15, radiant_fraction=0.25, tau=1, distances_m, target_kW_m2])
%   Hc, Hv in kJ/kg, cp kJ/kg/K.  r.flux_kW_m2 (if distances given) and r.distance_to_target_m (if target given).
  if nargin < 6 || isempty(Ta_K), Ta_K = 298.15; end
  if nargin < 7 || isempty(radiant_fraction), radiant_fraction = 0.25; end
  if nargin < 8 || isempty(tau), tau = 1.0; end
  if area_m2 <= 0 || Hc_kJ_kg <= 0 || Hv_kJ_kg <= 0 || cp_kJ_kgK <= 0 || Tb_K <= 0
    error('ps_pool_fire:input', 'area, Hc, Hv, cp and Tb must be positive');
  end
  g = 9.80665; rho_air = 1.2;
  D = sqrt(4 * area_m2 / pi);
  m = 0.001 * Hc_kJ_kg / (Hv_kJ_kg + cp_kJ_kgK * max(Tb_K - Ta_K, 0));          % Burgess
  H = D * 42 * (m / (rho_air * sqrt(g * D))) ^ 0.61;                              % Thomas
  e = exp(-0.12 * D);
  r.diameter_m = D;
  r.burning_rate_kg_m2_s = m;
  r.mass_burn_rate_kg_s = m * area_m2;
  r.flame_height_m = H;
  r.Q_kW = m * area_m2 * Hc_kJ_kg;
  r.heat_release_MW = r.Q_kW / 1e3;
  r.sep_mudan_croce_kW_m2 = 140 * e + 20 * (1 - e);
  r.radiant_fraction = radiant_fraction;  r.tau = tau;
  if nargin >= 9 && ~isempty(distances_m)
    r.flux_kW_m2 = arrayfun(@(d) incident(r, d), distances_m);
  end
  if nargin >= 10 && ~isempty(target_kW_m2)
    r.distance_to_target_m = to_target(r, target_kW_m2);
  end
end

function q = incident(r, d)
  rr = hypot(d, r.flame_height_m / 2);
  q = r.tau * r.radiant_fraction * r.Q_kW / (4 * pi * rr * rr);
end

function d = to_target(r, target)
  lo = 0; hi = 1e4;
  if incident(r, 0) < target, d = 0; return; end
  for i = 1:100
    mid = (lo + hi) / 2;
    if incident(r, mid) > target, lo = mid; else, hi = mid; end
  end
  d = (lo + hi) / 2;
end
