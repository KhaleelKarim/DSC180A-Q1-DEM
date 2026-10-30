# CLAUDE.md — Metamaterials Capstone (UCSD Data Science)

## Who you're working with

- The user is a **UCSD Data Science major** doing their **senior capstone**: apply data science techniques to a domain under a subject-matter expert (their professor).
- The domain is **mechanical metamaterials**, which the user knows very little about.
- The user has **never used MATLAB before**. They are comfortable with Python/pandas.
- **How to communicate:**
  - Define field-specific terms (physics, MATLAB, numerical methods) when you first use them, and use analogies.
  - The user has said that large blocks of code or math leave them lost. Pair any non-trivial code with a plain-English framing before it and a short walk-through after it.
  - The user has chosen to treat the simulation code as a **black box**. Explain what things do and why at a high level; don't walk through MATLAB syntax unless asked.

## Project goal

1. **Replicate** a result from the paper *Disorder DEM* (referred to as "Tamur's paper"; PDFs `Disorder_DEM_Paper_Main.pdf` and `Disorder_DEM_Paper_SI.pdf`, the SI being the supplementary information). **Markdown versions are in `references/Disorder_DEM_Paper_Main.md` and `references/Disorder_DEM_Paper_SI.md`** — prefer these when reading the paper programmatically, as they are easier to parse than the PDFs.
2. Use the simulation to **generate a dataset**.
3. **Go a step further** with a novel data-science proposal. This is not yet defined; likely directions include surrogate modeling or ML-based design.

Other reference papers in the project: `Kochmann_2023.pdf` and `NickFirstPaper.pdf` (the latter is about designing physical springs with target polynomial force laws).

## The physics, in brief

- **Setup:** a 1-D chain of **N = 20 masses** connected by springs. The last mass is tied to a fixed wall.
- **The impact:** a light, fast **impactor** hits the first mass through a **Hertzian contact**: force = C·overlap^(3/2), compression only, so the impactor can bounce off.
- **Spring force law in compression:** f(u) = c₁·u + c₂·u² + c₃·u³, where u is the amount of compression. In tension the springs are linear only (c₁·u).
  - c₁ = 1 is fixed. Everything is nondimensional.
  - c₂ is typically negative, which makes the spring soften.
  - c₃ is positive, which makes it stiffen again at larger compression.
  - A sufficiently negative c₂ makes the spring **bistable**, meaning it snaps through between two resting shapes.
- **Spring families:** the 20 springs form **4 families (A, B, C, D) of 5 consecutive springs**. Each family has its own (c₂, c₃) pair, so there are **8 design variables**.
- **Output metric:** KE ratio = max KE of the last mass with the nonlinear springs ÷ max KE of the last mass in an otherwise identical linear chain (c₂ = c₃ = 0). Lower is better: it means the impact is mitigated more.
- **Fixed parameters:**

  | Parameter | Value |
  |---|---|
  | Damping ζ | 0.02 |
  | Layer mass | 1 |
  | M₀ (half the chain mass) | N/2 = 10 |
  | Impactor mass | 0.01·M₀ = 0.1 |
  | Impactor velocity | 0.25 |
  | Contact stiffness C_impact | 1.2e4 |

- **Paper's design space:** c₂ ∈ [−120, 0], c₃ ∈ [0, 4000].
  - The positive-strain-energy constraint allows bistability: (2/9)·c₂² < c₃.
  - The stricter constraint excludes bistability: c₂² ≤ 4·c₃.
  - The paper optimized with `fmincon` using finite-difference gradients from several starting points. SI-5 also describes Monte Carlo robustness tests: 500 realizations with ±2% perturbations of the coefficients.

## Code files

All provided by the professor. **Do not modify the four original files without asking the user.** Wrap or copy them instead.

| File | Role |
|---|---|
| `impact_force.m` | Hertzian contact force between the impactor and mass 1. |
| `impact_equation_of_motion_hetero.m` | The ODE right-hand side passed to `ode45`. It returns velocities and accelerations for the impactor and all 20 masses. The state vector is interleaved: `x(2i-1)` = position and `x(2i)` = velocity of body i, where i = 1 is the impactor. It matches Eq. (5) of the paper. |
| `main_disorder.m` | Standalone script. Hard-coded example design: c₂ = [-70; -100; -5; -35], c₃ = [1200; 2000; 1500; 3000]. Runs the linear and nonlinear simulations and prints the KE ratio. |
| `main_disorder_v2.m` | Function form of the same thing: `ratio = main_disorder_v2(c2, c3)`. `c2` and `c3` must be **4×1 column vectors**. This is what the authors fed to `fmincon`, and it is the workhorse for data generation. |
| `generate_data.m` | **Written by Claude, not yet tested** (the user hadn't run it at handoff). Details below. |

### `generate_data.m`

**Usage:** `generate_data(n_samples, out_file, seed)`. The defaults are `5`, `'ke_ratio_data.csv'`, and `0`.

**What it does:**
- Samples c₂ and c₃ independently and uniformly over the paper's design space, then redraws any family's (c₂, c₃) pair that violates the positive-strain-energy constraint (2/9)·c₂² < c₃. Result: uniform over the valid region; bistable springs allowed. (Replaced an earlier LHS version; LHS's guarantee doesn't survive rejection.)
- Writes full precision (`%.17g`).
- Calls `main_disorder_v2` for each design.
- Appends one row per design to the CSV and writes the header if the file is new.
- Records `NaN` if a run errors.
- Prints per-run timing.
- Using the same seed with the same file **duplicates rows**, so change the seed for each new batch.

**Output CSV columns:** `c2_A, c2_B, c2_C, c2_D, c3_A, c3_B, c3_C, c3_D, KE_ratio`.

**How to run, from the folder containing all five `.m` files:**
- MATLAB Command Window: `generate_data(5)`
- Terminal: `matlab -batch "generate_data(5)"`

## User's environment

- The user has MATLAB through a UCSD license and works in **VS Code with the MATLAB extension**.
- They mentioned "MATLAB Online", so confirm a **local desktop install** exists if `matlab -batch` fails. If `matlab` isn't on PATH, use the full path to the executable.

## Known issues and open questions

Raise these with the user or their professor rather than silently "fixing" them.

1. **Output time grid differs from the paper.**
   - The paper states Δt_out = 1/(100·f₀).
   - The code uses dt = 1/(100·f), where f uses the stiffest tangent stiffness k_f = max(1 + 2c₂ + 3c₃).
   - The code's grid is about 90× finer for the example design. It catches the peak more accurately but uses more memory and time: roughly 236k rows × 42 columns per solve.
   - Ask the professor which setting produced the published numbers.
2. **Solver tolerances:** the paper says 1e-10 or tighter; the code uses 1e-12.
3. **Runtime is unknown.** It could be seconds to minutes per design, with two solves per call. Time a few runs before planning dataset size.
4. **Redundant linear solve.** The linear baseline is re-solved on every call even though it doesn't depend on c₂ or c₃; only its output grid changes through k_f. Caching it could nearly halve the cost. Only do this after reproducing the original numbers, and confirm that the peak is unaffected by the grid.
5. **Parallelism.** If Parallel Computing Toolbox is available, `parfor` over designs is an easy speedup. Rows would then need writing in a parallel-safe way.
6. **Bistability.** `generate_data.m` now enforces the positive-strain-energy constraint (2/9)·c₂² < c₃, so invalid "mousetrap" designs are gone. Still open: should sampling also exclude bistable designs (c₂² ≤ 4c₃)? Ask the professor. Note `data/raw/LHS_1000_samples_complete.csv` predates this: 707/1000 rows violate the constraint.
7. **Stale comments.** The comment in the main files mentions 5 families ("EEEEE") but there are 4. The header comment of `impact_force.m` lists inputs that don't exist. Both are harmless.
8. **Unused variables.** `displacement_x_*` is computed but unused. Its indexing skips the impactor, giving 20 columns versus 21 for velocity. It's fine for the KE ratio and useful for plotting.

## Status at handoff (2026-10-29)

**Done:**
- The user understands the files at a high level.
- `generate_data.m` is written.
- Markdown versions of Tamur's paper and its SI added to `references/` (`Disorder_DEM_Paper_Main.md`, `Disorder_DEM_Paper_SI.md`). Use these as the primary source when referencing the paper's equations, figures, or methods — they are easier to read programmatically than the PDFs.

**Next steps:**
1. **Sanity check.** Run `main_disorder_v2([-70; -100; -5; -35], [1200; 2000; 1500; 3000])` to confirm the setup works and to get a timing for one design. If possible, compare the result against a value in the paper.
2. **Test batch.** Run `generate_data(5)`, then check the CSV and the per-design runtime.
3. **Organize the repo.** Suggested layout:
   - `simulation/` for the `.m` files. They must stay in one folder or be added with `addpath`, because MATLAB resolves functions by filename.
   - `data/`
   - `analysis/` for Python notebooks.
   - A `README`.
   - Set up git if the user wants it.
4. **Scale up.** Plan dataset size from the measured runtime. Sampling is uniform + rejection (decided 2026-10-29; LHS was dropped because rejection breaks it and batches don't combine).
5. **Analysis.** Load the CSV in Python and begin the data-science extension.
