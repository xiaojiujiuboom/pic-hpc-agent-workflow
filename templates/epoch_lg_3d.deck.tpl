# EPOCH 3D input deck skeleton for LG-beam BO campaign.
# This is a control-plane template, not yet a production-validated EPOCH deck.

begin:constant
  lambda0 = 1.0 * micron
  omega0 = 2.0 * pi * c / lambda0
  a0 = {{a0}}
  w0 = {{w0_um}} * micron
  tau = {{tau_fs}} * femto
  lg_l = {{l}}
  lg_p = {{p}}
  final_time = {{final_time_fs}} * femto
end:constant

begin:control
  nx = {{nx}}
  ny = {{ny}}
  nz = {{nz}}
  t_end = final_time
  stdout_frequency = 100
end:control

begin:boundaries
  bc_x_min = simple_laser
  bc_x_max = open
  bc_y_min = periodic
  bc_y_max = periodic
  bc_z_min = periodic
  bc_z_max = periodic
end:boundaries

begin:laser
  boundary = x_min
  intensity_w_cm2 = 1.37e18 * a0^2
  lambda = lambda0
  profile = gauss(y, 0, w0) * gauss(z, 0, w0)
  t_profile = gauss(time, 2.0*tau, tau)
  phase = lg_l * atan2(z, y)
  pol_angle = {{pol_angle_rad}}
end:laser

begin:species
  name = carbon
  charge = 6.0
  mass = 12.0 * 1836.2
  npart_per_cell = {{particles_per_cell}}
  density = if(abs(x) lt {{carbon_thickness_um}} * micron / 2.0, 100.0 * critical(omega0), 0.0)
end:species

begin:species
  name = proton
  charge = 1.0
  mass = 1836.2
  npart_per_cell = {{particles_per_cell}}
  density = if((x gt {{carbon_thickness_um}} * micron / 2.0) and (x lt ({{carbon_thickness_um}} + {{hydrogen_thickness_um}}) * micron) and (sqrt(y^2 + z^2) lt {{hydrogen_radius_um}} * micron), {{hydrogen_density_nc}} * critical(omega0), 0.0)
end:species

begin:output
  name = reduced
  dt_snapshot = 25 * femto
  particles = always
  px = always
  py = always
  pz = always
  ex = always
end:output

