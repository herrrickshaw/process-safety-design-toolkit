function varargout = ps_blast(action, varargin)
%PS_BLAST  Blast screening: TNT equivalence, Kinney-Graham free-air overpressure, Brode burst energy (process_safety/explosion.py).
%   W = ps_blast('tnt_equivalent', fuel_kg, Hc_MJ_kg, yield_fraction)             yield default 0.05 (very uncertain)
%   P = ps_blast('overpressure_kpa', W_tnt_kg, R_m)                                incident overpressure, kPa
%   R = ps_blast('distance_m', W_tnt_kg, target_kpa)                               distance where overpressure falls to target
%   E = ps_blast('brode_J', P1_kpa_abs, P0_kpa_abs, V_m3, gamma)                   E = (P1 - P0) V / (gamma - 1)
%   W = ps_blast('burst_tnt_kg', E_J [, ground_burst=true])                        ground reflection doubles the charge
%   Kinney-Graham coefficients and the TNT heat of detonation (4.5 MJ/kg, sources quote 4.1-4.68) are the toolkit's recalled values.
  switch action
    case 'tnt_equivalent'
      y = 0.05; if numel(varargin) >= 3, y = varargin{3}; end
      varargout{1} = y * varargin{1} * varargin{2} / 4.5;
    case 'overpressure_kpa'
      varargout{1} = kg(varargin{1}, varargin{2});
    case 'distance_m'
      W = varargin{1}; target = varargin{2};
      lo = 0.5 * W ^ (1 / 3); hi = 1e5;
      for i = 1:200
        mid = (lo + hi) / 2;
        if kg(W, mid) > target, lo = mid; else, hi = mid; end
      end
      varargout{1} = (lo + hi) / 2;
    case 'brode_J'
      varargout{1} = (varargin{1} - varargin{2}) * 1e3 * varargin{3} / (varargin{4} - 1);
    case 'burst_tnt_kg'
      w = varargin{1} / 4.5e6;
      if numel(varargin) < 2 || varargin{2}, w = 2 * w; end
      varargout{1} = w;
    otherwise
      error('ps_blast:action', 'unknown action %s', action);
  end
end

function p = kg(W, R)
  Z = R / W ^ (1 / 3);
  p = 101.325 * 808 * (1 + (Z / 4.5) ^ 2) / sqrt((1 + (Z / 0.048) ^ 2) * (1 + (Z / 0.32) ^ 2) * (1 + (Z / 1.35) ^ 2));
end
