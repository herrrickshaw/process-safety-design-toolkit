function ps_run_tests()
%PS_RUN_TESTS  Self-contained identity tests for the MATLAB/Octave tools. Prints ALL PASSED or the failures, errors on failure.
%   Runs in MATLAB and in GNU Octave:  octave-cli --eval "addpath('matlab'); ps_run_tests"
%   No remembered example numbers: closed-form identities, analytic limits, and unit definitions only.
  here = fileparts(mfilename('fullpath')); addpath(here);
  fails = {};  n = 0;
  results = {};
  results = [results; t_units()];
  results = [results; t_relief()];
  results = [results; t_omega()];
  results = [results; t_viewfactor()];
  results = [results; t_depressure()];
  results = [results; t_facility()];
  for i = 1:size(results, 1)
    n = n + 1;
    if ~results{i, 2}, fails{end + 1} = results{i, 1}; end %#ok<AGROW>
  end
  if isempty(fails)
    printf('ALL PASSED %d checks\n', n);
  else
    printf('FAILED %d of %d:\n', numel(fails), n);
    printf('  %s\n', fails{:});
    error('ps_run_tests:failed', '%d checks failed', numel(fails));
  end
end

function ok = close(a, b, rtol)
  ok = abs(a - b) <= rtol * max(abs(b), realmin) + 1e-300;
end

function out = t_units()
  lb = 0.45359237; g = 9.80665; in = 0.0254;
  out = {};
  out(end + 1, :) = {'psi in Pa from lb, g, in', close(ps_units(1, 'psi', 'Pa'), lb * g / in^2, 1e-14)};
  out(end + 1, :) = {'gallon 231 in3', close(ps_units(1, 'gal', 'm3'), 231 * in^3, 1e-14)};
  out(end + 1, :) = {'212 F is 100 C', close(ps_units(212, 'degF', 'degC'), 100, 1e-12)};
  out(end + 1, :) = {'-40 F equals -40 C', close(ps_units(-40, 'degF', 'degC'), -40, 1e-12)};
  out(end + 1, :) = {'difference has no offset', close(ps_units(10, 'dF', 'dK'), 10 * 5 / 9, 1e-14)};
  out(end + 1, :) = {'lb/h to kg/s', close(ps_units(3600, 'lb/h', 'kg/s'), lb, 1e-14)};
  out(end + 1, :) = {'hp = 550 ft lbf/s', close(ps_units(1, 'hp', 'W'), 550 * 12 * in * lb * g, 1e-14)};
  err = '';
  try, ps_units(10, 'psig', 'psia'); catch e, err = e.identifier; end
  out(end + 1, :) = {'gauge to absolute refused', strcmp(err, 'ps_units:gaugeAbs')};
  out(end + 1, :) = {'0 psig is one atmosphere abs', close(ps_gauge_to_abs(0, 'kPag', 'kPa abs'), 101.325, 1e-14)};
  out(end + 1, :) = {'gauge/abs round trip', close(ps_abs_to_gauge(ps_gauge_to_abs(150, 'psig', 'psia'), 'psia', 'psig'), 150, 1e-12)};
  vals = [0 1 123.456 -40];  units_ = {'m','ft','mm','in','kg','lb','K','degC','degF','kPag','psig','kg/s','lb/h','gpm','m3/h'};
  ok = true;
  for u = 1:numel(units_)
    partner = partner_of(units_{u});
    for v = vals
      back = ps_units(ps_units(v, units_{u}, partner), partner, units_{u});
      if abs(back - v) > 1e-9 * max(1, abs(v)), ok = false; end
    end
  end
  out(end + 1, :) = {'round trips', ok};
end

function p = partner_of(u)
  map = struct('m', 'ft', 'ft', 'm', 'mm', 'in', 'in', 'mm', 'kg', 'lb', 'lb', 'kg', 'K', 'degF', 'degC', 'degF', 'degF', 'K', ...
               'kPag', 'psig', 'psig', 'kPag', 'kg_s', 'lb/h');
  switch u
    case 'kg/s', p = 'lb/h';
    case 'lb/h', p = 'kg/s';
    case 'gpm', p = 'm3/h';
    case 'm3/h', p = 'gpm';
    otherwise, p = map.(u);
  end
end

function out = t_relief()
  out = {};
  k = 1.13; M = 44; T = 400; Z = 0.9; P1 = 1500 * 1.21 + 101.325; P2 = 101.325;
  a = ps_relief_gas(12000, T, P1, P2, M, k, Z);
  b = ps_relief_gas(24000, T, P1, P2, M, k, Z);
  out(end + 1, :) = {'critical regime selected', strcmp(a.regime, 'critical')};
  out(end + 1, :) = {'area proportional to flow', close(b.area_mm2 / a.area_mm2, 2, 1e-12)};
  c = ps_relief_gas(12000, T * 4, P1, P2, M, k, Z);
  out(end + 1, :) = {'area proportional to sqrt(T)', close(c.area_mm2 / a.area_mm2, 2, 1e-12)};
  d = ps_relief_gas(12000, T, P1, P2, M * 4, k, Z);
  out(end + 1, :) = {'area inverse to sqrt(M)', close(d.area_mm2 / a.area_mm2, 0.5, 1e-12)};
  % continuity of the flux at the critical ratio: subcritical branch must meet the critical branch
  rc = (2 / (k + 1)) ^ (k / (k - 1));
  e1 = ps_relief_gas(12000, T, 1000, 1000 * rc * 0.999999, M, k, Z);
  e2 = ps_relief_gas(12000, T, 1000, 1000 * rc * 1.000001, M, k, Z);
  out(end + 1, :) = {'flux continuous across critical ratio', close(e1.G_kg_m2_s, e2.G_kg_m2_s, 1e-5) && strcmp(e1.regime, 'critical') && strcmp(e2.regime, 'subcritical')};
  % choked flux closed form (independent expression)
  R = 8.314462618;
  G = P1 * 1e3 * sqrt(k * M / 1000 / (Z * R * T)) * (2 / (k + 1)) ^ ((k + 1) / (2 * (k - 1)));
  out(end + 1, :) = {'choked flux closed form', close(a.G_kg_m2_s, G, 1e-12)};
end

function out = t_omega()
  out = {};
  r1 = ps_omega_flux(1500, 500, 1.0);
  out(end + 1, :) = {'omega=1 chokes at exp(-1/2)', close(r1.eta_critical, exp(-0.5), 1e-6)};
  rl = ps_omega_flux(1500, 500, 1e-6, 750);
  G_liq = sqrt(2 * 1500e3 * 500 * (1 - 0.5));
  out(end + 1, :) = {'omega->0 is incompressible liquid flow', close(rl.G_kg_m2_s, G_liq, 1e-4)};
  a = ps_omega_flux(1500, 500, 5); b = ps_omega_flux(1500, 500, 10);
  out(end + 1, :) = {'choked flux falls as omega rises', b.G_kg_m2_s < a.G_kg_m2_s};
  c = ps_omega_flux(1500, 2000, 5);
  out(end + 1, :) = {'flux scales with sqrt(rho0)', close(c.G_kg_m2_s / a.G_kg_m2_s, 2, 1e-9)};
  % the choked flux is the maximum over eta
  etas = logspace(-6, 0, 2000); P0 = 1500e3; best = 0;
  for e = etas
    num = 5 * log(1 / e) - 4 * (1 - e); g = sqrt(max(num, 0)) / (5 * (1 / e - 1) + 1);
    best = max(best, g);
  end
  out(end + 1, :) = {'choked flux is the maximum over eta', close(a.G_kg_m2_s, sqrt(2 * P0 * 500) * best, 5e-4)};
end

function out = t_viewfactor()
  out = {};
  X = 4; Y = 3; d = 5; n = 300;
  F = ps_view_factor([0 0 0], [0 0 1], [0 0 d], [0 Y 0], [X 0 0], n);
  a = X / d; b = Y / d;
  Fh = (1 / (2 * pi)) * (a / sqrt(1 + a^2) * atan(b / sqrt(1 + a^2)) + b / sqrt(1 + b^2) * atan(a / sqrt(1 + b^2)));
  out(end + 1, :) = {'matches Howell differential element to rectangle', close(F, Fh, 5e-4)};
  Fs = ps_view_factor([0 0 0], [0 0 1], [-0.05 -0.05 100], [0 0.1 0], [0.1 0 0], 50);
  out(end + 1, :) = {'far field is A/(pi d^2)', close(Fs, 0.01 / (pi * 100^2), 1e-3)};
  Fb = ps_view_factor([0 0 0], [0 0 -1], [0 0 d], [0 Y 0], [X 0 0], 60);
  out(end + 1, :) = {'target facing away sees nothing', Fb == 0};
  Fback = ps_view_factor([0 0 0], [0 0 1], [0 0 d], [X 0 0], [0 Y 0], 60);
  out(end + 1, :) = {'emitter facing away emits nothing (one-sided)', Fback == 0};
  F2 = ps_view_factor([0 0 0], [0 0 1], [0 0 d], [X 0 0], [0 Y 0], 120, true);
  F1 = ps_view_factor([0 0 0], [0 0 1], [0 0 d], [0 Y 0], [X 0 0], 120);
  out(end + 1, :) = {'two-sided equals the facing side', close(F2, F1, 1e-12)};
  out(end + 1, :) = {'view factor bounded in [0,1]', F > 0 && F < 1};
end

function out = t_depressure()
  out = {};
  V = 30; P0 = 5000; Pt = 1000; T0 = 300; M = 20; k = 1.3; A = 800;
  iso = ps_depressure(V, P0, Pt, T0, M, k, A, 0.85, 'isothermal');
  adi = ps_depressure(V, P0, Pt, T0, M, k, A, 0.85, 'adiabatic');
  out(end + 1, :) = {'target above choke pressure', Pt > iso.choke_pressure_kpa};
  out(end + 1, :) = {'isothermal numeric = closed form', close(iso.t_s, iso.t_closed_s, 1e-6)};
  out(end + 1, :) = {'adiabatic numeric = closed form', close(adi.t_s, adi.t_closed_s, 1e-6)};
  out(end + 1, :) = {'adiabatic faster than isothermal', adi.t_s < iso.t_s};
  half = ps_depressure(V, P0, Pt, T0, M, k, 2 * A, 0.85, 'isothermal');
  out(end + 1, :) = {'doubling the orifice halves the time', close(half.t_s / iso.t_s, 0.5, 1e-6)};
  out(end + 1, :) = {'isentropic minimum temperature', close(adi.Tmin_K, T0 * (Pt / P0) ^ ((k - 1) / k), 1e-14) && adi.Tmin_K < T0};
end

function out = t_facility()
  out = {};
  r = ps_egress(60, 1.2, 200, 2, 1.3, 30, 60, 300);
  out(end + 1, :) = {'egress RSET identity', close(r.rset_s, 30 + 60 + max(60 / 1.2, 200 / (1.3 * 2)), 1e-14)};
  out(end + 1, :) = {'egress governed by exit flow here', strcmp(r.governing, 'flow through the exit')};
  out(end + 1, :) = {'egress margin', close(r.margin_s, 300 - r.rset_s, 1e-14) && r.escape_before_untenable};
  w = ps_egress(60, 1.2, 200, 4, 1.3, 30, 60);
  out(end + 1, :) = {'doubling exit width halves flow time', close(w.t_flow_s / r.t_flow_s, 0.5, 1e-14)};
  il = ps_illumination(100, 3000, 0.6, 0.8, 300);
  out(end + 1, :) = {'illumination n_exact identity', close(il.n_exact, 300 * 100 / (3000 * 0.6 * 0.8), 1e-14)};
  out(end + 1, :) = {'illumination meets target', il.achieved_lux >= 300 && il.n_luminaires == ceil(il.n_exact)};
  err = '';
  try, ps_illumination(100, 3000, 1.5, 0.8, 300); catch e, err = e.identifier; end
  out(end + 1, :) = {'illumination rejects UF > 1', strcmp(err, 'ps_illumination:input')};
end
