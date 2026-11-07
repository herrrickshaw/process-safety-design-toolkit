function r = ps_egress(distance_m, speed_m_s, people, width_m, specific_flow, detect_s, premove_s, aset_s)
%PS_EGRESS  Required safe egress time RSET = detect + premove + max(travel, exit flow); margin against an ASET you supply.
%   Every speed, flow and time is an input (none coded).  Screening bound only: no merging flows, stairs or queues upstream.
  if min([distance_m speed_m_s width_m specific_flow]) <= 0 || people < 1 || detect_s < 0 || premove_s < 0
    error('ps_egress:input', 'distance, speed, width, specific flow positive; people >= 1; times not negative');
  end
  r.t_travel_s = distance_m / speed_m_s;
  r.t_flow_s = people / (specific_flow * width_m);
  r.rset_s = detect_s + premove_s + max(r.t_travel_s, r.t_flow_s);
  if r.t_flow_s > r.t_travel_s, r.governing = 'flow through the exit'; else, r.governing = 'travel distance'; end
  if nargin >= 8 && ~isempty(aset_s)
    r.margin_s = aset_s - r.rset_s;
    r.aset_over_rset = aset_s / r.rset_s;
    r.escape_before_untenable = aset_s > r.rset_s;
  end
end
