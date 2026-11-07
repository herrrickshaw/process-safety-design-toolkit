function r = ps_omega_flux(P0_kpa, rho0, omega, P_back_kpa)
%PS_OMEGA_FLUX  Two-phase / flashing mass flux by the omega method (homogeneous equilibrium, Leung single parameter).
%   v/v0 = omega (P0/P - 1) + 1  gives  G(eta) = sqrt(2 P0/v0) sqrt(omega ln(1/eta) - (omega-1)(1-eta)) / (omega (1/eta - 1) + 1).
%   The choked flux is found by MAXIMISING G over eta = P/P0 (no tabulated chart). Same model as process_safety/twophase.py.
%   r = ps_omega_flux(P0_kpa, rho0, omega [, P_back_kpa]);  r.G_kg_m2_s, r.eta_critical, r.regime.
  if omega <= 0 || rho0 <= 0, error('ps_omega_flux:input', 'omega and rho0 must be positive'); end
  P0 = P0_kpa * 1e3;
  scale = sqrt(2 * P0 * rho0);
  gfun = @(le) gdim(exp(le), omega);                  % optimise on ln(eta)
  [le_c, ~] = fminbnd(@(le) -gfun(le), log(1e-12), 0, optimset('TolX', 1e-13));
  eta_c = exp(le_c);
  choked = (nargin < 4) || isempty(P_back_kpa) || (P_back_kpa / P0_kpa <= eta_c);
  if choked, eta = eta_c; else eta = P_back_kpa / P0_kpa; end
  r.G_kg_m2_s = scale * gdim(eta, omega);
  r.eta_critical = eta_c;
  if choked, r.regime = 'choked'; else r.regime = 'subcritical'; end
end

function g = gdim(eta, omega)
  num = omega .* log(1 ./ eta) - (omega - 1) .* (1 - eta);
  g = sqrt(max(num, 0)) ./ (omega .* (1 ./ eta - 1) + 1);
end
