# Minimal 3D laser-target smoke deck.
# Purpose: verify remote submit -> SDF -> density plot, not production physics.

begin:constant
  lambda0 = 1.0 * micron
  omega0 = 2.0 * pi * c / lambda0
  a0 = {{a0}}
  w0 = {{w0_um}} * micron
  tau = {{tau_fs}} * femto
  final_time = {{final_time_fs}} * femto
  slab_half = {{carbon_thickness_um}} * micron / 2.0
  n0 = {{hydrogen_density_nc}} * critical(omega0)
end:constant

begin:control
  nx = {{nx}}
  ny = {{ny}}
  nz = {{nz}}
  t_end = final_time
  x_min = -2.0 * micron
  x_max =  2.0 * micron
  y_min = -2.0 * micron
  y_max =  2.0 * micron
  z_min = -2.0 * micron
  z_max =  2.0 * micron
  stdout_frequency = 1
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
  t_profile = gauss(time, tau, tau)
  pol_angle = {{pol_angle_rad}}
end:laser

begin:species
  name = electron
  charge = -1.0
  mass = 1.0
  npart_per_cell = {{particles_per_cell}}
  number_density = if(abs(x) lt slab_half, n0, 0.0)
end:species

begin:species
  name = proton
  charge = 1.0
  mass = 1836.2
  npart_per_cell = {{particles_per_cell}}
  number_density = if(abs(x) lt slab_half, n0, 0.0)
end:species

begin:output
  name = smoke
  dt_snapshot = final_time
  dump_first = T
  dump_last = T
  grid = always
  ex = always
  number_density = always + species
end:output
