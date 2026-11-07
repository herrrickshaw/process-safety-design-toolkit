function r = ps_bleve(mass_kg, Hc_MJ_kg, V_vessel_m3, P_burst_kpa_abs, gamma, radiated_fraction, tau, distances_m)
%PS_BLEVE  BLEVE screening: fireball radiation (ps_fireball) plus the blast of the pressurised VAPOUR SPACE at burst (Brode energy,
%   TNT equivalent with ground reflection, Kinney-Graham overpressure).  Both parts are the toolkit's screening models.
%   LIMITS (read before using the blast numbers): the Brode energy of the gas present is a LOWER BOUND, because the superheated liquid
%   that flashes at failure carries much more energy and is NOT included; fragments and their ranges are NOT modelled; the fireball
%   exists only for flammable contents that ignite.  Use a validated BLEVE model (and the vessel's failure analysis) for design.
%   r = ps_bleve(mass_kg, Hc, V_vapour_m3, P_burst_kpa_abs, gamma [, fraction=0.30, tau=1, distances_m])
  if nargin < 6 || isempty(radiated_fraction), radiated_fraction = 0.30; end
  if nargin < 7 || isempty(tau), tau = 1.0; end
  if nargin < 8, distances_m = []; end
  r.fireball = ps_fireball(mass_kg, Hc_MJ_kg, radiated_fraction, tau, distances_m);
  E = ps_blast('brode_J', P_burst_kpa_abs, 101.325, V_vessel_m3, gamma);
  W = ps_blast('burst_tnt_kg', E, true);
  r.blast.brode_energy_J = E;
  r.blast.tnt_equivalent_kg = W;
  r.blast.note = 'vapour-space energy only: a lower bound; flashing liquid and fragments not included';
  if ~isempty(distances_m)
    r.blast.overpressure_kpa = arrayfun(@(d) ps_blast('overpressure_kpa', W, d), distances_m);
  end
end
