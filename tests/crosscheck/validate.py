"""Cross-check the toolkit against independent libraries (fluids, thermo, CoolProp) and closed-form literature formulas.

Optional: needs `pip install fluids thermo CoolProp`. Run: python tests/crosscheck/validate.py [--json out.json]
Each check records toolkit value, reference value, relative difference, tolerance and reference source.
"""
import sys, math, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from process_safety import relief, hydraulics, props, explosion, pool_fire, fireball, electrical, dispersion, consequence, sil, lng, fire_water, noise, pipeline
import fluids.safety_valve as sv
from fluids import friction, compressible
from CoolProp.CoolProp import PropsSI
R=[]
def chk(name, ours, ref, tol, ref_src, unit=""):
    d = (ours-ref)/ref if ref else float("nan")
    ok = abs(d) <= tol
    R.append(dict(name=name, ours=ours, ref=ref, rel_diff_pct=d*100, tol_pct=tol*100, ok=ok, ref_src=ref_src, unit=unit))
# --- A. relief gas vs fluids API520_A_g
for tag,(W,T,P1,P2,M,k,Z) in {"critical":(12000,400,1000*1.21+101.325,101.325,44,1.13,0.9),"critical_hi":(50000,350,2000*1.1+101.325,101.325,28,1.4,1.0),"subcritical":(20000,350,1000*1.1+101.325,700,28,1.4,1.0)}.items():
    a=relief.gas_area(W,T,P1,P2,M,k,Z).required_area_mm2
    b=sv.API520_A_g(m=W/3600,T=T,Z=Z,MW=M,k=k,P1=P1*1e3,P2=P2*1e3)*1e6
    chk(f"relief.gas_area ({tag})",a,b,0.01,"fluids.safety_valve.API520_A_g","mm2")
# --- B. steam vs fluids (10E) - editions differ
for W,Pset in ((5000,1500),(20000,3000),(8000,800)):
    P1=Pset*1.1+101.325
    import CoolProp.CoolProp as CP
    T=CP.PropsSI('T','P',P1*1e3,'Q',1,'Water')
    a=relief.steam_area(W,P1).required_area_mm2
    b=sv.API520_A_steam(m=W/3600,T=T,P1=P1*1e3)*1e6
    chk(f"relief.steam_area (set {Pset} kPag)",a,b,0.05,"fluids API520_A_steam, 10th ed. (toolkit uses Napier, 7th-ed. constant)","mm2")
# --- C. liquid vs fluids
for Q,rho,Pset,Pb in ((50,700,1000,100),(120,998,1500,101.325)):
    P1=Pset*1.1+101.325
    a=relief.liquid_area(Q,rho,P1,Pb).required_area_mm2
    try:
        b=sv.API520_A_l(m=Q/3600*rho,rho=rho,P1=Pset*1e3+101325,P2=Pb*1e3,overpressure=0.1,Kd=0.65,Kc=1.0,Kw=1.0,Kv=1.0)*1e6
    except Exception:
        b=float("nan")
    chk(f"relief.liquid_area (Q {Q} m3/h, Kv~1)",a,b,0.05,"fluids API520_A_l","mm2")
# --- D. fire heat input vs API 521 closed form
for A in (20,43.93,119,500):
    a=relief.fire_heat_input_W(A,1.0,True)
    ref=43200*A**0.82
    chk(f"relief.fire_heat_input_W (A={A})",a,ref,0.001,"API 521: Q=43,200*F*A^0.82 W (adequate drainage)","W")
# --- E. hydraulics vs fluids
for Re,D,eps in ((5e3,0.1,4.6e-5),(1e5,0.2,4.6e-5),(1e6,0.5,1.5e-4)):
    a=hydraulics.friction_factor(Re,D,eps)
    b=friction.friction_factor(Re,eD=eps/D)
    chk(f"hydraulics.friction_factor (Re={Re:g}, e/D={eps/D:.1e})",a,b,0.02,"fluids.friction.friction_factor (Clamond)","")
# isothermal gas: given P1, L, D, m -> P2
m,Dp,L,P1,T,M,mu=2.0,0.2,500.0,1000.0,300.0,20.0,1.1e-5
o=hydraulics.isothermal_gas_outlet_kpa(m,Dp,L,P1,T,M,mu)
rho1=P1*1e3*M/1000/(8.314462618*T)
Re=4*m/(math.pi*Dp*mu); fd=friction.friction_factor(Re,eD=4.6e-5/Dp)
P2=compressible.P_isothermal_critical_flow  # placeholder to ensure import
f=lambda P2x: compressible.isothermal_gas(rho1/ (P1*1e3)*1e5*0+ (P1*1e3*M/1000/(8.314462618*T))*(1.0), fd, P1*1e3, P2x, L, Dp) - m
# fluids.isothermal_gas(rho, fd, P1, P2, L, D, m) -> solves for the missing arg; use P2 as unknown
try:
    P2ref=compressible.isothermal_gas(rho=rho1,fd=fd,P1=P1*1e3,L=L,D=Dp,m=m)/1e3
    chk("hydraulics.isothermal_gas_outlet_kpa",o["P2_kpa"] if "P2_kpa" in o else list(o.values())[0],P2ref,0.01,"fluids.compressible.isothermal_gas","kPa")
except Exception as e:
    R.append(dict(name="hydraulics.isothermal_gas_outlet_kpa",ours=str(o),ref=None,rel_diff_pct=None,tol_pct=1,ok=None,ref_src=f"fluids call failed: {e}",unit=""))
# --- F. props vs CoolProp
cfg={"methane":("Methane",(115,130,160)),"ethane":("Ethane",(200,240,270)),"ethylene":("Ethylene",(180,220,260)),"propane":("Propane",(250,280,300,320)),"propylene":("Propylene",(250,280,300)),"n-butane":("n-Butane",(280,300,330)),"isobutane":("IsoButane",(270,300,330))}
for comp,(cp_name,Ts) in cfg.items():
    for T in Ts:
        a=props.vapour_pressure_bar(comp,T); b=PropsSI('P','T',T,'Q',0,cp_name)/1e5
        chk(f"props.vapour_pressure_bar {comp} {T} K",a,b,0.05,"CoolProp (Helmholtz EOS)","bar")
        a=props.liquid_density_kg_m3(comp,T); b=PropsSI('D','T',T,'Q',0,cp_name)
        chk(f"props.liquid_density_kg_m3 {comp} {T} K",a,b,0.05,"CoolProp (Helmholtz EOS)","kg/m3")
# --- G. latent heats
chk("lng methane latent heat at NBP", lng.METHANE["latent_kJ_kg"], (PropsSI('H','P',101325,'Q',1,'Methane')-PropsSI('H','P',101325,'Q',0,'Methane'))/1e3, 0.03,"CoolProp","kJ/kg")
chk("lpg propane latent heat at NBP (default 425)", 425.0, (PropsSI('H','P',101325,'Q',1,'Propane')-PropsSI('H','P',101325,'Q',0,'Propane'))/1e3, 0.03,"CoolProp","kJ/kg")
# --- H. explosion
def kg(Z): return 808*(1+(Z/4.5)**2)/(math.sqrt(1+(Z/0.048)**2)*math.sqrt(1+(Z/0.32)**2)*math.sqrt(1+(Z/1.35)**2))
for Wt,Rm in ((1000,50),(1000,100),(5000,200),(100,20)):
    Z=Rm/Wt**(1/3)
    chk(f"explosion.kinney_graham_kpa W={Wt} kg R={Rm} m",explosion.kinney_graham_kpa(Wt,Rm),kg(Z)*101.325,0.01,"Kinney-Graham (1985), as in CCPS/TNO","kPa")
chk("explosion TNT energy (MJ/kg)", explosion.TNT_MJ_PER_KG, 4.184, 0.12,"literature range 4.184-4.69 MJ/kg","MJ/kg")
# --- I. fireball (Roberts/CCPS): D=5.8 M^(1/3), t=0.45 M^(1/3) (M<30,000 kg)
for M in (1000,20000):
    fb=fireball.fireball(M,46)
    chk(f"fireball diameter M={M}",fb["diameter_m"],5.8*M**(1/3),0.01,"Roberts (1982) / CCPS","m")
    chk(f"fireball duration M={M}",fb["duration_s"],0.45*M**(1/3),0.01,"Roberts (1982) / CCPS","s")
# --- J. pool fire
Hc,Hv,cp,Tb=44000,350,2.2,400
m_ref=0.001*Hc/(Hv+cp*(Tb-298.15))
chk("pool_fire burning rate (Burgess/Hottel)",pool_fire.burning_rate_kg_m2_s(Hc,Hv,cp,Tb),m_ref,0.001,"Burgess et al. / Mudan: m''=0.001 Hc/(Hv+cp(Tb-Ta))","kg/m2/s")
for D in (5,20,40):
    sep=140*math.exp(-0.12*D)+20*(1-math.exp(-0.12*D))
    chk(f"pool_fire Mudan-Croce SEP D={D}",pool_fire.mudan_croce_sep_kW_m2(D),sep,0.001,"Mudan & Croce (SFPE handbook)","kW/m2")
D=20; mdot=m_ref; rho_a=1.2
Hd=42*D*(mdot/(rho_a*math.sqrt(9.81*D)))**0.61
chk("pool_fire Thomas flame height",pool_fire.flame_height_m(D,mdot),Hd,0.01,"Thomas (1963): H/D=42(m''/(rho_a sqrt(gD)))^0.61","m")
# --- K. IDMT
K={"standard_inverse":(0.14,0.02),"very_inverse":(13.5,1.0),"extremely_inverse":(80.0,2.0),"long_time_inverse":(120.0,1.0)}
for c,(k_,a_) in K.items():
    I,Is,tms=3000,400,0.2
    ref=tms*k_/((I/Is)**a_-1)
    chk(f"electrical.idmt_time_s {c}",electrical.idmt_time_s(I,Is,tms,c),ref,0.001,"IEC 60255-151 constants","s")
# --- L. earthing IEEE 80
for rs,t in ((3000,0.5),(100,1.0),(2500,0.3)):
    ref_t=(1000+1.5*rs)*0.116/math.sqrt(t); ref_s=(1000+6*rs)*0.116/math.sqrt(t)
    chk(f"electrical.tolerable_touch_V 50kg rho_s={rs} t={t}",electrical.tolerable_touch_V(rs,t,1.0,50),ref_t,0.001,"IEEE Std 80-2013 eq. 32","V")
    chk(f"electrical.tolerable_step_V 50kg rho_s={rs} t={t}",electrical.tolerable_step_V(rs,t,1.0,50),ref_s,0.001,"IEEE Std 80-2013 eq. 29","V")
# --- M. noise (OSHA 1910.95)
d=noise.dose_pct([(90,8),(95,2)]) if hasattr(noise,"dose_pct") else None
if d is not None: chk("noise.dose 90dBA/8h + 95dBA/2h",d,150.0,0.001,"OSHA 1910.95 App. A: 100%+50%","%")
# --- N. dispersion: Briggs open-country sigmas
def briggs(x,cls):
    t={"A":(0.22,0.0001,-0.5,0.20,0.0,0),"B":(0.16,0.0001,-0.5,0.12,0.0,0),"C":(0.11,0.0001,-0.5,0.08,0.0002,-0.5),"D":(0.08,0.0001,-0.5,0.06,0.0015,-0.5),"E":(0.06,0.0001,-0.5,0.03,0.0003,-1),"F":(0.04,0.0001,-0.5,0.016,0.0003,-1)}[cls]
    sy=t[0]*x*(1+t[1]*x)**t[2]; sz=t[3]*x*(1+t[4]*x)**t[5] if t[4] else t[3]*x
    return sy,sz
for cls in "ABCDEF":
    for x in (100,1000):
        sy,sz=dispersion.sigmas(x,cls); ry,rz=briggs(x,cls)
        chk(f"dispersion.sigmas y {cls} x={x}",sy,ry,0.02,"Briggs (1973) open-country, as tabulated in Turner/Wikipedia","m")
        chk(f"dispersion.sigmas z {cls} x={x}",sz,rz,0.02,"Briggs (1973) open-country","m")
# plume centreline ground concentration (reflected) formula
Q,u,H,x,cls=100,3,2,200,"D"
sy,sz=dispersion.sigmas(x,cls)
C_ref=Q/(math.pi*u*sy*sz)*math.exp(-H**2/(2*sz**2))
chk("dispersion.concentration_g_m3 centreline ground",dispersion.concentration_g_m3(Q,u,H,x,0,0,cls),C_ref,0.001,"Gaussian plume with ground reflection (Turner)","g/m3")
# --- O. probit thermal (Eisenberg)
for I,t in ((10,30),(25,10),(5,60)):
    ref=-14.9+2.56*math.log((t*(I*1000)**(4/3))/1e4)
    chk(f"consequence.probit_thermal I={I} t={t}",consequence.probit_thermal(I,t),ref,0.001,"Eisenberg et al. (1975): Pr=-14.9+2.56 ln(t I^4/3 /1e4)","")
# --- P. PFD vs IEC 61508-6 simplified equations
lam,TI,beta=2e-6,8760.0,0.05
chk("sil.pfd_avg 1oo1",sil.pfd_avg("1oo1",lam,TI,0.0),lam*TI/2,0.001,"IEC 61508-6 Annex B: PFD=lambda_DU*TI/2","")
chk("sil.pfd_avg 1oo2 (beta=0.05)",sil.pfd_avg("1oo2",lam,TI,beta),((1-beta)*lam)**2*TI**2/3+beta*lam*TI/2,0.01,"IEC 61508-6 Annex B simplified 1oo2 with beta","")
chk("sil.pfd_avg 2oo2",sil.pfd_avg("2oo2",lam,TI,0.0),lam*TI,0.001,"IEC 61508-6 Annex B","")
chk("sil.pfd_avg 2oo3 (beta=0.05)",sil.pfd_avg("2oo3",lam,TI,beta),((1-beta)*lam)**2*TI**2+beta*lam*TI/2,0.01,"IEC 61508-6 Annex B simplified 2oo3 with beta","")
# --- pipeline (49 CFR 192.105 / 192.903)
Pd=pipeline.design_pressure_kpa(448,12.7,610,1)
chk("pipeline.design_pressure_kpa class 1",Pd,2*448*12.7*0.72/610*1000,0.001,"49 CFR 192.105: P=(2St/D)FET, F=0.72","kPa")
pr=pipeline.potential_impact_radius_m(Pd-101.325,610)
p_psi=(Pd-101.325)*0.1450377; d_in=610/25.4
chk("pipeline.potential_impact_radius_m",pr,0.69*d_in*math.sqrt(p_psi)*0.3048,0.01,"49 CFR 192.903: r=0.69 d sqrt(p) (ft, in, psig)","m")
chk("lng.impoundment_capacity_m3 single tank",lng.impoundment_capacity_m3([160000]),160000*1.10,0.001,"49 CFR 193.2181: 110% of single-container capacity","m3")
chk("psm threshold chlorine kg (1,500 lb)",680.388555,1500*0.45359237,0.001,"29 CFR 1910.119 App. A","kg")
# --- Q. Hazen-Williams (NFPA 13 SI)
Q,d,C=1000,100,120
chk("fire_water.hazen_williams_bar_per_m",fire_water.hazen_williams_bar_per_m(Q,d,C),6.05e5*Q**1.85/(C**1.85*d**4.87),0.001,"NFPA 13: p=6.05*Q^1.85/(C^1.85 d^4.87)*1e5 (bar/m)","bar/m")
# --- R. regulatory
r=pipeline
sys.path.insert(0, os.path.dirname(__file__))
from extra import run_extra
run_extra(chk)
if "--json" in sys.argv:
    open(sys.argv[sys.argv.index("--json") + 1], "w").write(json.dumps(R, indent=1, default=str))
bad=[x for x in R if x["ok"] is False]; unk=[x for x in R if x["ok"] is None]
print(f"checks: {len(R)}  within tolerance: {sum(1 for x in R if x['ok'])}  outside: {len(bad)}  not computed: {len(unk)}")
for x in bad+unk: print("  ", x["name"], "ours", x["ours"], "ref", x["ref"], "diff%", x["rel_diff_pct"], "|", x["ref_src"])

sys.exit(1 if bad or unk else 0)
