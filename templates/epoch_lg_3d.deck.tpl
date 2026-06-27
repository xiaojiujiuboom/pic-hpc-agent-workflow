# LG 3D laser-target EPOCH input deck.
# Production starting point, not final physics-validated deck.
# Current LG implementation:
#   - topological charge l enters the azimuthal phase and p=0 radial amplitude.
#   - p is recorded in the deck constants, but arbitrary p needs Python-side
#     Laguerre polynomial expansion in a later iteration.

begin:constant
  lambda0 = 1.0 * micron
  omega0 = 2.0 * pi * c / lambda0
  a0 = {{a0}}
  w0 = {{w0_um}} * micron
  tau = {{tau_fs}} * femto
  lg_l = {{l}}
  lg_p = {{p}}
  final_time = {{final_time_fs}} * femto

  carbon_thickness = {{carbon_thickness_um}} * micron
  hydrogen_thickness = {{hydrogen_thickness_um}} * micron
  hydrogen_radius = {{hydrogen_radius_um}} * micron
  carbon_density = {{carbon_density_nc}} * critical(omega0)
  hydrogen_density = {{hydrogen_density_nc}} * critical(omega0)
  carbon_front = -0.5 * carbon_thickness
  carbon_rear = 0.5 * carbon_thickness
  hydrogen_rear = carbon_rear + hydrogen_thickness
end:constant

begin:control
  nx = {{nx}}
  ny = {{ny}}
  nz = {{nz}}
  t_end = final_time

  x_min = {{x_min_um}} * micron
  x_max = {{x_max_um}} * micron
  y_min = {{y_min_um}} * micron
  y_max = {{y_max_um}} * micron
  z_min = {{z_min_um}} * micron
  z_max = {{z_max_um}} * micron

  stdout_frequency = 100
end:control

begin:boundaries
  bc_x_min = simple_laser
  bc_x_max = open
  bc_y_min = open
  bc_y_max = open
  bc_z_min = open
  bc_z_max = open
end:boundaries

begin:laser
  boundary = x_min
  intensity_w_cm2 = 1.37e18 * a0^2
  lambda = lambda0
  profile = (sqrt(2.0) * r_yz / w0)^abs(lg_l) * gauss(r_yz, 0, w0)
  t_profile = gauss(time, 2.0 * tau, tau)
  phase = lg_l * atan2(z, y)
  pol_angle = {{pol_angle_rad}}
end:laser

begin:species
  name = electron
  charge = -1.0
  mass = 1.0
  npart_per_cell = {{particles_per_cell}}
  number_density = if((x gt carbon_front) and (x lt carbon_rear), 6.0 * carbon_density, 0.0) + if((x gt carbon_rear) and (x lt hydrogen_rear) and (sqrt(y^2 + z^2) lt hydrogen_radius), hydrogen_density, 0.0)
end:species

begin:species
  name = carbon
  charge = 6.0
  mass = 12.0 * 1836.2
  npart_per_cell = {{particles_per_cell}}
  number_density = if((x gt carbon_front) and (x lt carbon_rear), carbon_density, 0.0)
end:species

begin:species
  name = proton
  charge = 1.0
  mass = 1836.2
  npart_per_cell = {{particles_per_cell}}
  number_density = if((x gt carbon_rear) and (x lt hydrogen_rear) and (sqrt(y^2 + z^2) lt hydrogen_radius), hydrogen_density, 0.0)
end:species

begin:output
  name = reduced
  dt_snapshot = {{output_dt_snapshot_fs}} * femto
  dump_first = T
  dump_last = T

  grid = always
  ex = {{field_output}}
  ey = {{field_output}}
  ez = {{field_output}}
  bx = {{field_output}}
  by = {{field_output}}
  bz = {{field_output}}
  number_density = {{density_output}}

  particles = {{particle_output}}
  px = {{particle_momentum_output}}
  py = {{particle_momentum_output}}
  pz = {{particle_momentum_output}}
  particle_weight = {{particle_output}}
end:output
