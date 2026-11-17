function r = ps_fireball(mass_kg, Hc_MJ_kg, radiated_fraction, tau, distances_m, target_kW_m2)
%PS_FIREBALL  BLEVE / fireball radiation (CCPS-style correlations descended from Roberts 1982), as process_safety/fireball.py.
%   D = 5.8 m^(1/3); duration 0.45 m^(1/3) s below 30 t, 2.6 m^(1/6) s above (coefficients are the widely quoted values, verify against
%   Roberts 1982).  SEP from the radiated fraction of the combustion energy; solid-sphere view factor; transmissivity tau is an input.
%   Overpressure and fragments are NOT modelled here (see ps_bleve for the burst blast lower bound).
%   r = ps_fireball(mass, Hc [, fraction=0.30, tau=1, distances_m, target_kW_m2])
  if nargin < 3 || isempty(radiated_fraction), radiated_fraction = 0.30; end
  if nargin < 4 || isempty(tau), tau = 1.0; end
  if mass_kg <= 0 || Hc_MJ_kg <= 0 || radiated_fraction < 0 || radiated_fraction > 1
    error('ps_fireball:input', 'mass and Hc positive, radiated fraction in [0,1]');
  end
  D = 5.8 * mass_kg ^ (1 / 3);
  if mass_kg < 30000, t = 0.45 * mass_kg ^ (1 / 3); else, t = 2.6 * mass_kg ^ (1 / 6); end
  r.diameter_m = D;
  r.duration_s = t;
  r.surface_emissive_power_kW_m2 = radiated_fraction * mass_kg * Hc_MJ_kg * 1e6 / (pi * D * D * t) / 1e3;
  r.centre_height_m = D / 2;
  r.tau = tau;
  if nargin >= 5 && ~isempty(distances_m)
    r.flux_kW_m2 = arrayfun(@(d) incident(r, d), distances_m);
    r.dose = r.flux_kW_m2 .^ (4 / 3) .* t;          % (kW/m2)^(4/3) s, for probit injury relations
  end
  if nargin >= 6 && ~isempty(target_kW_m2)
    r.distance_to_target_m = to_target(r, target_kW_m2);
  end
end

function q = incident(r, d)
  rr = hypot(d, r.diameter_m / 2);
  q = r.tau * r.surface_emissive_power_kW_m2 * (r.diameter_m / 2) ^ 2 / rr ^ 2 * (d / rr);
end

function d = to_target(r, target)
  % flux is not monotone near the centre (cosine factor): search outward from the peak
  hi = r.diameter_m * 100;
  if incident(r, hi) > target, d = NaN; return; end
  cand = (1:1999) * r.diameter_m / 200;
  f = arrayfun(@(x) incident(r, x), cand);
  [fp, i] = max(f);
  if fp < target, d = NaN; return; end
  lo = cand(i);
  for k = 1:80
    mid = (lo + hi) / 2;
    if incident(r, mid) > target, lo = mid; else, hi = mid; end
  end
  d = (lo + hi) / 2;
end
