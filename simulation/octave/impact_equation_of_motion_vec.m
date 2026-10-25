function [dx] = impact_equation_of_motion_vec(t,x,nonlinear_spring_info,material_info,F)
% IMPACT_EQUATION_OF_MOTION_VEC  Vectorized copy of impact_equation_of_motion_hetero.
%
%   Same inputs, same outputs, same physics as simulation/core/
%   impact_equation_of_motion_hetero.m. The only difference is that the loop
%   over the masses is replaced by whole-array operations, which Octave runs
%   much faster (Octave has no JIT compiler, so loops are slow).
%
%   State vector x is interleaved: x(2i-1) = position, x(2i) = velocity of
%   body i, where body 1 is the impactor and bodies 2..N+1 are the masses.
%   Spring j connects mass j to mass j+1; spring N connects the last mass to
%   the wall. Springs are linear in tension and cubic in compression.

c1 = nonlinear_spring_info(:,1);
c2 = nonlinear_spring_info(:,2);
c3 = nonlinear_spring_info(:,3);

m        = material_info(1);
m_impact = material_info(2);
C_impact = material_info(3);
zeta     = material_info(4);

pos = x(1:2:end);
vel = x(2:2:end);
P = pos(2:end);            % mass positions
V = vel(2:end);            % mass velocities

% Spring stretch (negative = compression); the last spring is tied to the wall at 0
d = [P(2:end) - P(1:end-1); 0 - P(end)];

% Spring force: linear in tension, cubic in compression
g = c1.*d;
c = d < 0;
g(c) = c1(c).*d(c) - c2(c).*d(c).^2 + c3(c).*d(c).^3;

% Hertzian contact between impactor and first mass (compression only)
if pos(1) > P(1)
    f_imp = C_impact*(pos(1) - P(1))^(3/2);
else
    f_imp = 0;
end

acc = zeros(size(vel));
acc(1) = (F - f_imp)/m_impact;                                         % impactor
acc(2) = (g(1) + f_imp - 2*zeta*(-V(2) + V(1)))/m;                     % first mass
acc(3:end-1) = (g(2:end-1) - g(1:end-2) ...
    - 2*zeta*(-V(3:end) + 2*V(2:end-1) - V(1:end-2)))/m;               % interior masses
acc(end) = (g(end) - g(end-1) - 2*zeta*(V(end) - V(end-1)) - 2*zeta*V(end))/m;  % last mass

dx = zeros(length(x),1);
dx(1:2:end) = vel;
dx(2:2:end) = acc;
end
