function F = ps_view_factor(target, target_normal, corner, edge_u, edge_v, n, two_sided)
%PS_VIEW_FACTOR  View factor from a differential target element to a flat rectangular emitting face, by midpoint integration.
%   F = (1/pi) * integral of cos(t1) cos(t2) / r^2 dA2.  The face is the parallelogram corner + s*edge_u + t*edge_v (0<=s,t<=1) and emits
%   toward +normal = cross(edge_u, edge_v) only unless two_sided.  Incident flux = transmissivity * SEP * F.  Same model as viewfactor.py.
%   F = ps_view_factor([-15 0 0], [1 0 0], [0 10 0], [0 -20 0], [0 0 31], 200)
  if nargin < 6 || isempty(n), n = 200; end
  if nargin < 7, two_sided = false; end
  target = target(:)'; tn = target_normal(:)' / norm(target_normal);
  edge_u = edge_u(:)'; edge_v = edge_v(:)'; corner = corner(:)';
  fn = cross(edge_u, edge_v); area = norm(fn); fn = fn / area;
  s = ((1:n) - 0.5) / n;
  [S, Tt] = meshgrid(s, s);
  P = corner(1) + S(:) * edge_u(1) + Tt(:) * edge_v(1);
  Q = corner(2) + S(:) * edge_u(2) + Tt(:) * edge_v(2);
  Z = corner(3) + S(:) * edge_u(3) + Tt(:) * edge_v(3);
  d = [P - target(1), Q - target(2), Z - target(3)];
  r2 = sum(d .^ 2, 2); r = sqrt(r2);
  c1 = (d * tn') ./ r;
  c2 = -(d * fn') ./ r;
  if two_sided, c2 = abs(c2); end
  ok = (c1 > 0) & (c2 > 0) & (r2 > 0);
  F = sum(c1(ok) .* c2(ok) ./ r2(ok)) * (area / (n * n)) / pi;
end
