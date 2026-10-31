function generate_data(n_samples, out_file, seed)
% GENERATE_DATA  Build a table of (8 spring coefficients -> KE ratio).
%
%   generate_data(n_samples, out_file, seed)
%
%   n_samples : how many random designs to simulate        (default 5)
%   out_file  : name of the CSV file to write/append to    (default 'ke_ratio_data.csv')
%   seed      : random seed, so a batch can be reproduced  (default 0)
%
%   Each design = 4 c2 values + 4 c3 values (one pair per spring family A-D),
%   sampled independently and uniformly over the design space used in the paper:
%       c2 in [-120, 0],   c3 in [0, 4000]
%   keeping only physically valid springs: every family must satisfy the
%   positive-strain-energy constraint (2/9)*c2^2 < c3 (paper Methods 5.2, SI-2).
%   Any (c2, c3) pair that violates it is redrawn as a pair, so the designs are
%   uniform over the valid region. Bistable springs (4*c3 < c2^2) are allowed.
%
%   Note: this replaced an earlier Latin Hypercube version, so the same seed
%   now gives different designs than older CSVs. Those CSVs are still usable,
%   but may contain invalid designs.
%
%   Output CSV columns:
%       c2_A, c2_B, c2_C, c2_D, c3_A, c3_B, c3_C, c3_D, KE_ratio
%
%   Rows are appended one at a time, so if MATLAB is stopped partway
%   through, every finished row is already saved.
%
%   Requires main_disorder_v2.m, impact_equation_of_motion_hetero.m and
%   impact_force.m to be in the same folder.

% ---- Defaults for any arguments that weren't given ----
if nargin < 1, n_samples = 5; end
if nargin < 2, out_file  = 'data/raw/ke_ratio_data.csv'; end
if nargin < 3, seed      = 0; end

% ---- Design space (from the paper's Methods section) ----
c2_range = [-120, 0];
c3_range = [0, 4000];

rng(seed);   % fix the random number generator so results are reproducible

% ---- Generate all N designs at once: uniform draws + per-family rejection ----
% Draw every (c2, c3) pair uniformly over the box, then redraw just the pairs
% that break the positive-strain-energy constraint until none are left.
% About 73% of pairs pass on each round, so this takes only a few rounds.
designs_c2 = c2_range(1) + (c2_range(2) - c2_range(1)) * rand(n_samples, 4);
designs_c3 = c3_range(1) + (c3_range(2) - c3_range(1)) * rand(n_samples, 4);
bad = (2/9) * designs_c2.^2 >= designs_c3;   % invalid (design, family) pairs
while any(bad(:))
    n_bad = nnz(bad);
    designs_c2(bad) = c2_range(1) + (c2_range(2) - c2_range(1)) * rand(n_bad, 1);
    designs_c3(bad) = c3_range(1) + (c3_range(2) - c3_range(1)) * rand(n_bad, 1);
    bad = (2/9) * designs_c2.^2 >= designs_c3;
end
assert(all((2/9) * designs_c2(:).^2 < designs_c3(:)), 'An invalid design slipped through.');

% ---- Create the CSV with a header row if it doesn't exist yet ----
if ~isfile(out_file)
    fid = fopen(out_file, 'w');
    fprintf(fid, 'c2_A,c2_B,c2_C,c2_D,c3_A,c3_B,c3_C,c3_D,KE_ratio\n');
    fclose(fid);
end

row_format = [repmat('%.17g,', 1, 8), '%.17g\n'];   % 8 inputs, then the ratio
total_tic = tic;

% ---- Main loop: one simulated design per iteration ----
for k = 1:n_samples
    % Extract the k-th design as column vectors (shape main_disorder_v2 expects)
    c2 = designs_c2(k, :)';
    c3 = designs_c3(k, :)';

    % Run the simulation (two ODE solves inside); if it errors, record NaN
    run_tic = tic;
    try
        ratio = main_disorder_v2(c2, c3);
    catch err
        warning('Design %d failed: %s', k, err.message);
        ratio = NaN;
    end
    run_time = toc(run_tic);

    % Append this row to the CSV immediately
    fid = fopen(out_file, 'a');
    fprintf(fid, row_format, [c2; c3; ratio]);
    fclose(fid);

    fprintf('[%d/%d]  KE ratio = %.17g   (%.1f s)\n', k, n_samples, ratio, run_time);
end

fprintf('Done: %d designs in %.1f s. Saved to %s\n', ...
        n_samples, toc(total_tic), fullfile(pwd, out_file));
end
