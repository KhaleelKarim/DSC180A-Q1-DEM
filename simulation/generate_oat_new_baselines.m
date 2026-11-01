function generate_oat_new_baselines(kind, n_points)
% NEW OAT centered at one REAL baseline row from python_seed35.csv.
% From repository root in MATLAB:
%   addpath('simulation')
%   generate_oat_new_baselines('representative', 21)
%   generate_oat_new_baselines('best_ke', 21)
%
% Each baseline: 8 coefficients x 21 points = 168 DEM runs.
% Out: data/oat/<kind>/oat_<coefficient>.csv.
% The old data/oat/oat_*.csv files are NOT modified.
%
% IMPORTANT: MATLAB DEM and dataset-generating solver may be different.
% A baseline output check stops the sweep when disagreement exceeds 5%.

    if nargin < 1, kind = 'representative'; end
    if nargin < 2, n_points = 21; end
    if ~ismember(kind, {'representative', 'best_ke'})
        error('kind must be representative or best_ke');
    end
    if ~isscalar(n_points) || n_points < 3 || n_points ~= round(n_points) || mod(n_points,2) ~= 1
        error('n_points must be an ODD integer >=3, e.g. 21 (baseline is the center point).');
    end

    sim_dir = fileparts(mfilename('fullpath'));
    root_dir = fileparts(sim_dir);
    addpath(sim_dir);
    baseline_path = fullfile(root_dir, 'data', 'oat', 'baselines', [kind '.csv']);
    if ~isfile(baseline_path)
        error('Missing baseline file: %s. Run select_oat_baselines.py first.',baseline_path);
    end
    tbl = readtable(baseline_path);
    names = {'c2_A','c2_B','c2_C','c2_D','c3_A','c3_B','c3_C','c3_D'};
    base = zeros(1,8);
    for j=1:8
        base(j) = tbl.(names{j})(1);
    end
    csv_ke = tbl.KE_ratio(1);
    if ~is_feasible(base)
        error('The chosen baseline violates the checked constraints.');
    end

    % Check the score of THIS EXACT design with local MATLAB DEM.
    matlab_ke = main_disorder_v2(base(1:4)', base(5:8)');
    discrepancy = abs(matlab_ke - csv_ke) / max(abs(csv_ke), eps);
    fprintf('\nBaseline: %s\n',kind);
    fprintf('CSV KE ratio     = %.17g\n',csv_ke);
    fprintf('MATLAB KE ratio  = %.17g\n',matlab_ke);
    fprintf('Relative gap     = %.2f%%\n',100*discrepancy);
    if ~isfinite(matlab_ke) || matlab_ke <= 0 || discrepancy > 0.05
        error(['MATLAB and CSV disagree by more than 5%%. ' ...
            'STOP: check the Python/MATLAB DEM implementations with teammates before OAT.']);
    end

    outdir = fullfile(root_dir, 'data', 'oat', kind);
    if ~exist(outdir,'dir'), mkdir(outdir); end
    nside = (n_points - 1)/2;
    t0 = tic;
    failures = 0;
    for j=1:8
        b = base(j);
        if j <= 4
            % c2 bound must satisfy c3 > (2/9)*c2^2.
            family = j;
            lower_physical = -sqrt((9/2) * base(4+family));
            lower = max(-120, lower_physical + 1e-6);
            upper = 0;
            radius = 12;  % 10% of full 120-unit c2 range
        else
            family = j-4;
            lower = max(0, (2/9) * base(family)^2 + 1e-6);
            upper = 4000;
            radius = 400; % 10% of full 4000-unit c3 range
        end
        low_end = max(lower, b-radius);
        high_end = min(upper, b+radius);
        if low_end > b || high_end < b
            error('Baseline is outside admissible sweep interval for %s.',names{j});
        end
        % 10 points to left + EXACT baseline + 10 to right.
        sweep = [linspace(low_end,b,nside+1), linspace(b,high_end,nside+1)];
        sweep(nside+2) = [];  % remove repeated baseline
        % Note: unequal spacing close to a constraint is expected.

        outfile = fullfile(outdir, ['oat_' names{j} '.csv']);
        fid = fopen(outfile,'w');
        if fid < 0, error('Cannot create file %s',outfile); end
        fprintf(fid,'parameter_value,KE_ratio,c2_A,c2_B,c2_C,c2_D,c3_A,c3_B,c3_C,c3_D\n');
        for k=1:numel(sweep)
            design = base;
            design(j) = sweep(k);
            if ~is_feasible(design)
                fclose(fid);
                error('Infeasible point: %s at k=%d',names{j},k);
            end
            try
                if k == nside+1
                    ratio = matlab_ke; % Exact baseline: already simulated
                else
                    ratio = main_disorder_v2(design(1:4)',design(5:8)');
                end
                if ~isfinite(ratio) || ratio <= 0
                    ratio = NaN;
                    failures = failures+1;
                end
            catch ME
                warning('Failed: %s at point %d: %s',names{j},k,ME.message);
                ratio = NaN;
                failures = failures+1;
            end
            fprintf(fid,[repmat('%.17g,',1,9),'%.17g\n'],[sweep(k), ratio, design]);
            fprintf('[%s %d/%d] %s=%.6g  KE=%.9g\n',kind,(j-1)*n_points+k,8*n_points,names{j},sweep(k),ratio);
        end
        fclose(fid);
    end
    fprintf('\nFinished: %s, %d requested points, %d invalid, %.1fs\n',kind,8*n_points,failures,toc(t0));
    fprintf('Saved to %s\n',outdir);
end

function ok = is_feasible(x)
    c2=x(1:4); c3=x(5:8);
    ok = all(isfinite(x)) && all(c2>=-120 & c2<=0) && ...
         all(c3>=0 & c3<=4000) && all(c3>(2/9)*c2.^2);
end
