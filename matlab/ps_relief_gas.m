function r = ps_relief_gas(W_kg_h, T_K, P1_kpa, P2_kpa, M, k, Z, Kd, Kb, Kc)
%PS_RELIEF_GAS  Gas/vapour PSV required area, ideal isentropic orifice flux (same model as process_safety/relief.py gas_area).
%   r = ps_relief_gas(W, T, P1, P2, M, k [, Z, Kd, Kb, Kc])
%   W kg/h, T K, P1 = relieving pressure kPa ABS, P2 = total back pressure kPa ABS, M kg/kmol.
%   r.area_mm2, r.regime ('critical'/'subcritical'), r.G_kg_m2_s.  Kb applies in critical flow only.
%   Defaults: Z 1, Kd 0.975 (API 520 gas), Kb 1, Kc 1.  The orifice letter table is not reproduced here.
  if nargin < 7 || isempty(Z),  Z = 1.0;    end
  if nargin < 8 || isempty(Kd), Kd = 0.975; end
  if nargin < 9 || isempty(Kb), Kb = 1.0;   end
  if nargin < 10 || isempty(Kc), Kc = 1.0;  end
  if k <= 1, error('ps_relief_gas:k', 'k must exceed 1'); end
  R = 8.314462618;
  rr = P2_kpa ./ P1_kpa;
  rc = (2 / (k + 1)) ^ (k / (k - 1));
  P1 = P1_kpa * 1e3;
  if rr <= rc
    G = P1 * sqrt(k * (M / 1000) / (Z * R * T_K)) * (2 / (k + 1)) ^ ((k + 1) / (2 * (k - 1)));
    regime = 'critical';  kb = Kb;
  else
    rho1 = P1 * (M / 1000) / (Z * R * T_K);
    G = sqrt(2 * P1 * rho1 * (k / (k - 1)) * (rr ^ (2 / k) - rr ^ ((k + 1) / k)));
    regime = 'subcritical';  kb = 1.0;
  end
  r.area_mm2 = W_kg_h / 3600 / (Kd * kb * Kc * G) * 1e6;
  r.regime = regime;
  r.G_kg_m2_s = G;
  r.critical_ratio = rc;
end
