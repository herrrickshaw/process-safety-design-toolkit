function y = ps_units(x, from, to)
%PS_UNITS  Convert x between SI and US-customary units (same exact definitions as process_safety/units.py).
%   y = ps_units(150, 'psig', 'kPag')      gauge to gauge, factor only
%   y = ps_units(212, 'degF', 'degC')      temperature reading, with offset
%   y = ps_units(10, 'dF', 'dK')           temperature DIFFERENCE, factor only
%   Gauge <-> absolute pressure is refused: use ps_gauge_to_abs / ps_abs_to_gauge.
%   Definitions: inch 0.0254 m, pound 0.45359237 kg, standard gravity 9.80665 m/s2, gallon 231 in3, Btu_IT 1055.05585262 J.
  [dimA, fA, oA] = lookup(from);
  [dimB, fB, oB] = lookup(to);
  if ~strcmp(dimA, dimB)
    if (strcmp(dimA, 'pressure_gauge') && strcmp(dimB, 'pressure_abs')) || (strcmp(dimA, 'pressure_abs') && strcmp(dimB, 'pressure_gauge'))
      error('ps_units:gaugeAbs', 'gauge and absolute pressure differ by the atmosphere: use ps_gauge_to_abs / ps_abs_to_gauge');
    end
    error('ps_units:dimension', 'cannot convert %s (%s) to %s (%s)', from, dimA, to, dimB);
  end
  y = ((x .* fA + oA) - oB) ./ fB;
end

function [dim, f, off] = lookup(u)
  in = 0.0254; ft = 12 * in; lb = 0.45359237; g = 9.80665; lbf = lb * g; psi = lbf / in^2;
  gal = 231 * in^3; btu = 1055.05585262; R5 = 5 / 9;
  T = {
    'm','length',1,0; 'mm','length',1e-3,0; 'ft','length',ft,0; 'in','length',in,0;
    'm2','area',1,0; 'mm2','area',1e-6,0; 'ft2','area',ft^2,0; 'in2','area',in^2,0;
    'm3','volume',1,0; 'ft3','volume',ft^3,0; 'gal','volume',gal,0;
    'kg','mass',1,0; 'lb','mass',lb,0;
    'kPa abs','pressure_abs',1e3,0; 'psia','pressure_abs',psi,0;
    'kPag','pressure_gauge',1e3,0; 'barg','pressure_gauge',1e5,0; 'psig','pressure_gauge',psi,0;
    'Pa','pressure_plain',1,0; 'kPa','pressure_plain',1e3,0; 'bar','pressure_plain',1e5,0; 'MPa','pressure_plain',1e6,0; 'psi','pressure_plain',psi,0; 'ksi','pressure_plain',1e3*psi,0;
    'K','temperature',1,0; 'degC','temperature',1,273.15; 'degF','temperature',R5,459.67*R5; 'degR','temperature',R5,0;
    'dK','temperature_difference',1,0; 'dF','temperature_difference',R5,0;
    'kg/s','mass_flow',1,0; 'kg/h','mass_flow',1/3600,0; 'lb/s','mass_flow',lb,0; 'lb/h','mass_flow',lb/3600,0;
    'm3/h','volume_flow',1/3600,0; 'gpm','volume_flow',gal/60,0; 'm3/s','volume_flow',1,0; 'L/s','volume_flow',1e-3,0;
    'kg/m3','density',1,0; 'lb/ft3','density',lb/ft^3,0;
    'kJ/kg','energy_per_mass',1e3,0; 'Btu/lb','energy_per_mass',btu/lb,0;
    'm/s','velocity',1,0; 'ft/s','velocity',ft,0;
    'kW/m2','heat_flux',1e3,0; 'Btu/h/ft2','heat_flux',btu/3600/ft^2,0;
    'kW','power',1e3,0; 'W','power',1,0; 'Btu/h','power',btu/3600,0; 'hp','power',550*ft*lbf,0
  };
  idx = find(strcmp(T(:,1), u), 1);
  if isempty(idx)
    error('ps_units:unknown', 'unknown unit %s', u);
  end
  dim = T{idx,2}; f = T{idx,3}; off = T{idx,4};
end
