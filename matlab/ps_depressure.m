function r = ps_depressure(V_m3, P0_kpa, Pt_kpa, T0_K, M, k, area_mm2, Cd, mode)
%PS_DEPRESSURE  Time to depressure a gas segment from P0 to Pt through an orifice to atmosphere (isothermal or adiabatic bound).
%   Numerical (ode45 with a pressure event) through choked and subcritical flow, plus the choked closed form for comparison.
%   Same models as process_safety/depressuring.py.  mode: 'isothermal' (heat input holds T, slower) or 'adiabatic' (isentropic, faster).
%   r.t_s numerical time, r.t_closed_s closed form (valid while Pt > choke pressure), r.Tmin_K isentropic end temperature.
  if nargin < 8 || isempty(Cd), Cd = 0.85; end
  if nargin < 9 || isempty(mode), mode = 'adiabatic'; end
  R = 8.314462618; ATM = 101.325;
  Rs = R / (M / 1000); A = area_mm2 * 1e-6;
  m0 = P0_kpa * 1e3 * V_m3 / (Rs * T0_K);
  adiabatic = strcmp(mode, 'adiabatic');
  p = struct('m0', m0, 'P0', P0_kpa, 'T0', T0_K, 'k', k, 'M', M, 'Cd', Cd, 'A', A, 'Pt', Pt_kpa, 'ATM', ATM, 'adiabatic', adiabatic);
  opts = odeset('Events', @(t, m) ev(t, m, p), 'RelTol', 1e-10, 'AbsTol', 1e-12 * m0);
  [~, ~, te] = ode45(@(t, m) rhs(t, m, p), [0 1e6], m0, opts);
  if isempty(te), error('ps_depressure:notReached', 'target pressure not reached'); end
  r.t_s = te(1);
  phi = (2 / (k + 1)) ^ ((k + 1) / (2 * (k - 1)));
  inv_tau = Cd * A * phi * sqrt(k * R * T0_K / (M / 1000)) / V_m3;
  if adiabatic
    r.t_closed_s = 2 / ((k - 1) * inv_tau) * ((P0_kpa / Pt_kpa) ^ ((k - 1) / (2 * k)) - 1);
  else
    r.t_closed_s = log(P0_kpa / Pt_kpa) / inv_tau;
  end
  r.Tmin_K = T0_K * (Pt_kpa / P0_kpa) ^ ((k - 1) / k);
  r.choke_pressure_kpa = ATM / (2 / (k + 1)) ^ (k / (k - 1));
end

function [P, T] = state(m, p)
  x = m / p.m0;
  if p.adiabatic
    P = p.P0 * x ^ p.k;  T = p.T0 * x ^ (p.k - 1);
  else
    P = p.P0 * x;  T = p.T0;
  end
end

function dm = rhs(~, m, p)
  [P, T] = state(m, p);
  dm = -p.Cd * p.A * mflux(P, p.ATM, T, p.M, p.k);
end

function [val, term, dirn] = ev(~, m, p)
  [P, ~] = state(m, p);
  val = P - p.Pt;  term = 1;  dirn = -1;
end

function G = mflux(P1_kpa, P2_kpa, T, M, k)
  R = 8.314462618; rr = P2_kpa / P1_kpa; rc = (2 / (k + 1)) ^ (k / (k - 1)); P1 = P1_kpa * 1e3;
  if rr <= rc
    G = P1 * sqrt(k * (M / 1000) / (R * T)) * (2 / (k + 1)) ^ ((k + 1) / (2 * (k - 1)));
  else
    rho1 = P1 * (M / 1000) / (R * T);
    G = sqrt(2 * P1 * rho1 * (k / (k - 1)) * (rr ^ (2 / k) - rr ^ ((k + 1) / k)));
  end
end
