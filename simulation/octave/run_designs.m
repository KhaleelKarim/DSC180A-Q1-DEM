function run_designs(in_file, out_file)
% RUN_DESIGNS  Octave worker: simulate every design listed in a CSV.
%
%   run_designs(in_file, out_file)
%
%   in_file  : CSV with a header row and columns
%                  design_id, c2_A, c2_B, c2_C, c2_D, c3_A, c3_B, c3_C, c3_D
%   out_file : CSV to append results to (header written if the file is new)
%
%   Output CSV columns:
%       design_id, c2_A..c2_D, c3_A..c3_D, KE_ratio, runtime_s, status
%
%   Unlike generate_data.m, this does NOT sample designs itself -- src/dataset.py
%   samples them, splits them into chunks, and starts one copy of this worker per
%   chunk so several run in parallel. Each worker writes to its own out_file.
%
%   Rows are appended one at a time, so if Octave is stopped partway through,
%   every finished row is already saved. 'status' is the last column so that a
%   row cut off mid-write (no status) can be detected and re-run.
%
%   Requires simulation/core and simulation/octave on the path. Uses
%   main_disorder_v2_vec, which is main_disorder_v2 with a vectorized ODE
%   function (same physics, faster in Octave).

designs = dlmread(in_file, ',', 1, 0);   % skip the header row
n = size(designs, 1);

if ~exist(out_file, 'file')
    fid = fopen(out_file, 'w');
    fprintf(fid, 'design_id,c2_A,c2_B,c2_C,c2_D,c3_A,c3_B,c3_C,c3_D,KE_ratio,runtime_s,status\n');
    fclose(fid);
end

% %.17g keeps full double precision, so the exact inputs can be re-run elsewhere
row_format = ['%d,', repmat('%.17g,', 1, 9), '%.3f,%s\n'];
total_tic = tic;

for k = 1:n
    design_id = designs(k, 1);
    c2 = designs(k, 2:5)';     % 4x1 columns, the shape main_disorder_v2 expects
    c3 = designs(k, 6:9)';

    run_tic = tic;
    try
        ratio = main_disorder_v2_vec(c2, c3);   % vectorized copy, ~1.5x faster in Octave
        status = 'ok';
    catch err
        warning('Design %d failed: %s', design_id, err.message);
        ratio = NaN;
        status = 'error';
    end
    run_time = toc(run_tic);

    fid = fopen(out_file, 'a');
    fprintf(fid, row_format, design_id, [c2; c3; ratio], run_time, status);
    fclose(fid);

    fprintf('[%d/%d]  design %d  KE ratio = %.4f   (%.1f s)\n', k, n, design_id, ratio, run_time);
    fflush(stdout);
end

fprintf('Done: %d designs in %.1f s. Saved to %s\n', n, toc(total_tic), out_file);
end
