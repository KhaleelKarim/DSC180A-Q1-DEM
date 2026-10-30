function generate_oat_data(n_points)
% GENERATE_OAT_DATA  Controlled one-at-a-time DEM sensitivity sweeps.
%
% From the repository root in MATLAB:
%   addpath('simulation')
%   generate_oat_data(5)    % small test: 8 x 5 = 40 DEM runs
%   generate_oat_data(20)   % full sweep: 8 x 20 = 160 DEM runs
%
% Each sweep fixes seven spring coefficients at a common baseline and
% varies only the eighth. Results go to data/oat/oat_<coefficient>.csv,
% readable by src/visualize_data.py. Existing OAT CSV files are overwritten.
%
% Baseline: all four c2 = -60, all four c3 = 3500.
% Constraints checked per family:
%   -120 <= c2 <= 0,  0 <= c3 <= 4000,  c3 > (2/9)*c2^2.
% The c3 sweeps begin above the energy boundary (by 1 coefficient unit).
% These are local OAT responses around this baseline, not global effects.

    if nargin < 1
        n_points = 20;
    end
    if ~isscalar(n_points) || ~isnumeric(n_points) || ~isfinite(n_points) || ...
            n_points ~= floor(n_points) || n_points < 2
        error('n_points must be an integer >= 2.');
    end

    simulation_dir = fileparts(mfilename('fullpath'));
    root_dir = fileparts(simulation_dir);
    addpath(simulation_dir);
    output_dir = fullfile(root_dir, 'data', 'oat');
    if ~exist(output_dir, 'dir')
        mkdir(output_dir);
    end

    names = {'c2_A','c2_B','c2_C','c2_D', ...
             'c3_A','c3_B','c3_C','c3_D'};
    baseline = [-60, -60, -60, -60, 3500, 3500, 3500, 3500];
    c2_min = -120;
    c2_max = 0;
    c3_max = 4000;
    boundary_margin = 1; % avoid sampling exactly on the strict boundary

    assert(all(baseline(5:8) > (2/9) * baseline(1:4).^2), ...
        'Baseline must satisfy positive-strain-energy constraints.');

    total_runs = 8 * n_points;
    failures = 0;
    total_tic = tic;
    fprintf('OAT baseline (c2_A..D, c3_A..D):\n');
    fprintf('  %.17g', baseline);
    fprintf('\n%d points per coefficient; %d total DEM simulations.\n', ...
        n_points, total_runs);

    for col = 1:8
        if col <= 4
            % With c3=3500 fixed, the entire c2 range is admissible.
            sweep = linspace(c2_min, c2_max, n_points);
        else
            % With c2=-60 fixed, c3 must be strictly greater than 800.
            family = col - 4;
            min_c3 = (2/9) * baseline(family)^2 + boundary_margin;
            if min_c3 >= c3_max
                error('No admissible c3 range for %s.', names{col});
            end
            sweep = linspace(min_c3, c3_max, n_points);
        end

        output_file = fullfile(output_dir, ['oat_' names{col} '.csv']);
        fid = fopen(output_file, 'w');
        if fid == -1
            error('Cannot write file: %s', output_file);
        end
        % Retain all inputs to make the seven-fixed-parameter design auditable.
        fprintf(fid, ['parameter_value,KE_ratio,' ...
            'c2_A,c2_B,c2_C,c2_D,c3_A,c3_B,c3_C,c3_D\n']);

        for k = 1:n_points
            design = baseline;
            design(col) = sweep(k);
            c2 = design(1:4)';
            c3 = design(5:8)';

            is_in_box = all(c2 >= c2_min & c2 <= c2_max) && ...
                        all(c3 >= 0 & c3 <= c3_max);
            is_energy_valid = all(c3 > (2/9) * c2.^2);
            if ~is_in_box || ~is_energy_valid
                fclose(fid);
                error('Constraint violation for %s, sweep point %d.', names{col}, k);
            end

            try
                ratio = main_disorder_v2(c2, c3);
                if ~isfinite(ratio) || ratio <= 0
                    warning('Nonpositive/nonfinite KE ratio for %s at point %d.', ...
                        names{col}, k);
                    ratio = NaN;
                    failures = failures + 1;
                end
            catch ME
                warning('DEM failed for %s at point %d: %s', ...
                    names{col}, k, ME.message);
                ratio = NaN;
                failures = failures + 1;
            end

            % 17 significant digits preserve round-trip double precision.
            fprintf(fid, [repmat('%.17g,', 1, 9), '%.17g\n'], ...
                [sweep(k), ratio, design]);
            fprintf('[%d/%d] %s = %.6g, KE ratio = %.17g\n', ...
                (col-1)*n_points+k, total_runs, names{col}, sweep(k), ratio);
        end
        fclose(fid);
        fprintf('Saved %s\n', output_file);
    end

    fprintf('\nOAT finished: %d runs, %d failed/invalid, %.1f seconds.\n', ...
        total_runs, failures, toc(total_tic));
    fprintf('Files: %s\n', output_dir);
    if failures > 0
        warning('Some OAT rows have NaN KE ratios. Inspect the CSV files.');
    end
end
