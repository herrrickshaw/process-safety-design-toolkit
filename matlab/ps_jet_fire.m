function r = ps_jet_fire(mass_kg_s, Hc_MJ_kg, M, radiant_fraction, tau, distances_m, allowable_kW_m2)
%PS_JET_FIRE  Jet-fire point-source radiation: Q = m Hc, flame length L = 0.00326 Q^0.478 (Q in W), Hajek-Ludwig radiant fraction
%   F = min(0.40, 0.048 sqrt(MW)) unless given, K = tau F Q / (4 pi D^2) from the flame centre (the toolkit's QRA jet fire and API 521
%   point-source method).  Least accurate within 2-3 flame lengths: r.warnings says when a distance falls inside 2 flame lengths.
%   No wind tilt, no impingement or momentum effects.  Verify the correlation constants and the allowable levels against your basis.
%   r = ps_jet_fire(m_kg_s, Hc_MJ_kg, M [, radiant_fraction, tau=1, distances_m, allowable_kW_m2])
  if nargin < 4 || isempty(radiant_fraction), radiant_fraction = min(0.40, 0.048 * sqrt(M)); end
  if nargin < 5 || isempty(tau), tau = 1.0; end
  if mass_kg_s <= 0 || Hc_MJ_kg <= 0 || M <= 0, error('ps_jet_fire:input', 'mass flow, Hc and M must be positive'); end
  Q = mass_kg_s * Hc_MJ_kg * 1e6;                  % W
  r.Q_MW = Q / 1e6;
  r.flame_length_m = 0.00326 * Q ^ 0.478;
  r.radiant_fraction = radiant_fraction;
  r.tau = tau;
  r.warnings = {};
  if nargin >= 6 && ~isempty(distances_m)
    r.flux_kW_m2 = tau * radiant_fraction * Q ./ (4 * pi * max(distances_m, 0.5) .^ 2) / 1e3;
    for i = 1:numel(distances_m)
      if distances_m(i) < 2 * r.flame_length_m
        r.warnings{end + 1} = sprintf('%.1f m is inside 2 flame lengths (%.1f m): point-source result unreliable', distances_m(i), 2 * r.flame_length_m);
      end
    end
  end
  if nargin >= 7 && ~isempty(allowable_kW_m2)
    r.safe_distance_m = sqrt(tau * radiant_fraction * Q ./ (4 * pi * allowable_kW_m2 * 1e3));
    for i = 1:numel(r.safe_distance_m)
      if r.safe_distance_m(i) < 2 * r.flame_length_m
        r.warnings{end + 1} = sprintf('%.3g kW/m2: %.1f m is inside 2 flame lengths (%.1f m)', allowable_kW_m2(i), r.safe_distance_m(i), 2 * r.flame_length_m);
      end
    end
  end
end
