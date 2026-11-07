function r = ps_illumination(area_m2, flux_lm, uf, mf, target_lux)
%PS_ILLUMINATION  Lumen method: E = N * flux * UF * MF / A.  Luminaires needed for a target, with the lux achieved.
%   UF (photometric table) and MF (maintenance plan) and the target (the standard the site follows) are inputs.
  if flux_lm <= 0 || area_m2 <= 0 || uf <= 0 || uf > 1 || mf <= 0 || mf > 1 || target_lux <= 0
    error('ps_illumination:input', 'flux, area, target positive; UF and MF in (0,1]');
  end
  r.n_exact = target_lux * area_m2 / (flux_lm * uf * mf);
  r.n_luminaires = ceil(r.n_exact - 1e-12);
  r.achieved_lux = r.n_luminaires * flux_lm * uf * mf / area_m2;
end
