#!/usr/bin/env python

# From src/User/mdata.f
#      data ewscheme  / +1                  /   ! Chooses EW scheme
#      data Gf_inp    / 1.16639d-5          /   ! G_F
#      data aemmz_inp / 7.7585538055706d-03 /   ! alpha_EM(m_Z)=1/128.89
#      data xw_inp    / 0.2312d0            /   ! sin^2(theta_W)
#      data wmass_inp / 80.398d0            /   ! W mass
#      data zmass_inp / 91.1876d0           /   ! Z mass

# ewcheme tells which scheme of experimental input is used, i.e. which of these
# values are taken as constants and which are derived. These are defined in
# src/Need/coupling.f The defaults is 1. 

# From src/Need/coupling.f:
#c-----------------------------------------------------
#c     option=1 : LUSIFER and AlpGen (iewopt=3) default
#c-----------------------------------------------------
#
#c-- equal to the input values
#         zmass  = zmass_inp
#         wmass  = wmass_inp
#         Gf = Gf_inp
#         inlabel(1)='(+)'
#         inlabel(2)='(+)'
#         inlabel(5)='(+)'
#c-- derived
#         xw  = One-(wmass/zmass)**2
#         aemmz  = Rt2*Gf*wmass**2*xw/pi

# ........
#      gwsq=fourpi*aemmz/xw
#      esq=gwsq*xw
#      gw=dsqrt(gwsq)
################################################################################
# Branching ratios are actually calculated in src/Need/branch.f
#      facz=esq/4d0*zmass/(6d0*pi)
#      facw=gwsq/8d0*wmass/(6d0*pi)
#
#
#      pwidth_e=facz*(le**2+re**2)
#      pwidth_n=facz*(ln**2)*3d0
#c      pwidth_d=3*facz*(L(1)**2+R(1)**2)
#c      pwidth_u=3*facz*(L(2)**2+R(2)**2)
#c calculated zwidth=3*pwidth_d+2*pwidth_u+3*pwidth_e+3*pwidth_n
#      brzee=pwidth_e/zwidth
#      brznn=pwidth_n/zwidth
#      brwen=facw/wwidth
#      brtau=factau/tauwidth
################################################################################
#Some of these parameters are defined in src/Need/mcfm_init.f
#
#c---  Widths: note that the top width is calculated in the program
#c---  The W width of 2.1054 is derived using the measured BR of
#c---    10.80 +/- 0.09 % (PDG) and the LO partial width calculation
#c---    for Mw=80.398 GeV
#      wwidth=2.1054d0
#      zwidth=2.4952d0
#      tauwidth=2.269d-12
################################################################################
# From src/Need/couplz.f
#      sin2w=two*sqrt(xw*(1d0-xw))
#      le=(-1d0-two*(-1d0)*xw)/sin2w
#      re=(-two*(-1d0)*xw)/sin2w

# From src/Need/coupling.f
import math
Gf = 1.16639e-5          #   ! G_Fermi
aemmz = 7.7585538055706e-03   # alpha_EM(m_Z)=1/128.89
wmass = 80.398            # W mass
zmass = 91.1876           # Z mass

xw  = 1-(wmass/zmass)**2
aemmz  = math.sqrt(2)*Gf*wmass**2*xw/math.pi

# From src/Need/coupling.f

gwsq=4*math.pi*aemmz/xw # this is the electroweak "g" coupling parameter squared
esq=gwsq*xw # This is the charge squared
gw=math.sqrt(gwsq) 

facz=esq/4*zmass/(6*math.pi)
facw=gwsq/8*wmass/(6*math.pi)

# From src/Need/mcfm_init.f
wwidth=2.1054
zwidth=2.4952

# From src/Need/couplz.f
sin2w=2.*math.sqrt(xw*(1-xw))
le=(-1.-2.*(-1.)*xw)/sin2w
re=(-2.*(-1.)*xw)/sin2w
# From src/Need/branch.f
pwidth_e=facz*(le**2+re**2)
#c calculated zwidth=3*pwidth_d+2*pwidth_u+3*pwidth_e+3*pwidth_n
brzee=pwidth_e/zwidth
brwen=facw/wwidth

print "Branching ratio of z to ee is %s" % brzee
print "Branching ratio of w to ev is %s" % brwen
