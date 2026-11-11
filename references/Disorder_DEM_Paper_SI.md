# **Supplementary Information: Engineered heterogeneity in constitutive nonlinearity enhances impact mitigation robustness** 

Caglar Tamur<sup>1</sup> , Maya Brandy<sup>2</sup> , H. Alicia Kim<sup>1</sup><sup>_,_3</sup> , Nicholas Boechler<sup>2</sup><sup>_,_3</sup> 

> 1Department of Structural Engineering, University of California, San Diego. 

> 2Department of Mechanical and Aerospace Engineering, University of California, San Diego. 

> 3Program in Materials Science and Engineering, University of California, San Diego. 

## **SI-1. Discrete element model non-dimensionalization** 

The reduced-order discrete element model (DEM) includes N = 20 layers of unit cells in the direction of impact. Each unit cell consists of a lumped mass _m_<sup>_∗_</sup> , a massless nonlinear spring _fI_<sup>_∗_(∆</sup><sup>_x∗_),andalinearinter-siteviscousdamper</sup><sup>_η∗_connectedinparallel.Asterisksindicate</sup> dimensional quantities, and the subscript _I_ denotes spring family _I ∈ A, B, C, D_ . With these dimensional quantities, the equation of motion for the _i_ th unit cell can be written as 



where _x_<sup>_∗_</sup> _i_<sup>isthedimensionaldisplacementofmass</sup><sup>_i_fromrest,andtheoverdotdenotesa</sup> derivative with respect to time. 

To non-dimensionalize, we introduce a dimensionless displacement ∆ _xi_ and time _t_ , which we define as 



where _a_ is the unit cell spacing and _c_<sup>_∗_</sup> 1<sup>isthelinearstiffnessofeachspring,keptuniformacross</sup> all spring families. A dimensionless velocity _x_ ˙ _i_ can follow as 



from which we then define a dimensionless acceleration _x_ ¨ _i_ : 

1 



_SI-1.1. Non-dimensionalizing the nonlinear spring_ 

The springs _fI_<sup>_∗_(∆</sup><sup>_x∗_)aretakentobelinearintensionandfollowinganonlinearthird-order</sup> polynomial in compression. We write this piecewise as 



We can rewrite each term in Eq. S1.5 in terms of the dimensionless quantity definitions introduced. Substituting ∆ _x_<sup>_∗_</sup> = ∆ _xa_ into Eq. S1.5 and normalizing out a _c_<sup>_∗_</sup> 1<sup>_a_termgives</sup> 



where dimensionless quadratic and cubic terms can be grouped as 



## _SI-1.2. Non-dimensionalizing viscous force_ 

Using the definition for dimensionless velocity _x_ ˙ _i_ , we capture the force due to viscosity in a unit cell as 



and we divide by _c_<sup>_∗_</sup> 1<sup>_a_tomaketheexpressiondimensionless:</sup> 



We can relate the coefficient to typical convention for defining a damping ratio _ζ_ as: 

such that 



For simplicity, we set _ζ_ = 0.02 for all unit cells to capture small but non-negligible behavior due to damping. 

2 

_SI-1.3. Non-dimensionalizing force due to Hertzian-like contact spring_ 

The point mass impactor is taken to have a dimensional mass _M_<sup>_∗_</sup> and is traveling at an initial velocity _V_<sup>_∗_</sup> . It interacts with the nonlinear material via a contact spring that features a nonlinear force-displacement relationship in compression and zero stiffness in tension, allowing the impactor to rebound. We express this in a dimensional form via 



which can be made dimensionless by substituting ∆ _x_<sup>_∗_</sup> = ∆ _xa_ and dividing out the terms _c_<sup>_∗_</sup> 1<sup>_a_.</sup> 



For simplicity, we set _Cimp_ = 1 _._ 2 _×_ 10<sup>4</sup> . The impactor can be made dimensionless by defining _M_ = _M_<sup>_∗_</sup> _/M_ 0<sup>_∗_and</sup><sup>_V_=</sup><sup>_V∗/V_</sup> 0<sup>_∗_,wherethenominalimpactormass</sup><sup>_M_</sup> 0<sup>_∗_ishalfofthemassof</sup> chain and the nominal impactor velocity _V_ 0<sup>_∗_=</sup><sup>_a_</sup> ~~�~~ _c_<sup>_∗_</sup> 1<sup>_/m∗_isthelinearlatticesoundspeed.</sup> 

_SI-1.4. Non-dimensionalized equations of motion_ 

The entire non-dimensional discrete element system modeling the nonlinear material impact can thus be written as: 



## **SI-2. Discrete element model constraints** 

Consider the non-dimensional force-displacement relation: 



with _c_ 2 _<_ 0 and _c_ 3 _>_ 0, where positive ∆ _x_ indicates compression. 

Stored strain energy at any strain level ∆ _x_ is 



3 

Consider the case where _f_ (∆ _x_ ) has three real roots at 



which corresponds to a bistable curve that crosses the force axis at ∆ _x_ = 0 _,_ ∆ _x_ 1 _,_ ∆ _x_ 2. 

The positive strain energy constraint: 



Since _f_ (∆ _x_ ) _<_ 0 on [∆ _x_ 1 _,_ ∆ _x_ 2], this indicates 



which is equivalent to 



Note: This guarantees _F_ (∆ _x_ ) _>_ 0 for any ∆ _x >_ 0. 

Since ∆ _x_ 2 is a root of _f_ (∆ _x_ ), it should satisfy Eq.S1 





Plugging this into Eq.S7, we get 



Since the first term is positive and ∆ _x_ 2 _>_ 0, the constraint simplifies to 



Using quadratic formula and since _c_ 3 _>_ 0, the larger root is 



Plugging this into the inequality constraint Eq.S11, we get 



4 

## **SI-3. Spring categorization** 

Here we categorize the force-displacement of springs into monotonic increase, bistable, snapthrough and local maximum. Consider the compressive spring force-displacement and the local stiffness. 





## _SI-3.1. Monotonic Increase_ 

If _f_<sup>_′_</sup> (∆ _x_ ) _>_ 0 _∀_ ∆ _x >_ 0, then _f_ is monotonically increasing. 

For _c_ 3 _>_ 0, _f_<sup>_′_</sup> (∆ _x_ ) is convex, which means that _f_<sup>_′_</sup> (∆ _x_ ) _>_ 0 iff it has no real roots. Discriminant of _f_<sup>_′_</sup> (∆ _x_ ) 



_f_<sup>_′_</sup> (∆ _x_ ) has no real roots iff Disc( _f_<sup>_′_</sup> ) _<_ 0, thus we get the condition 



## _SI-3.2. Bistability_ 

Bistability indicates two positive real roots for 



Nontrivial roots of _f_ (∆ _x_ ) should satisfy 



The real roots of _g_ (∆ _x_ ) are 



which is always positive since _c_ 2 _<_ 0 and _c_ 3 _>_ 0. 

_g_ (∆ _x_ ) has two real roots roots iff Disc( _g_ ) _>_ 0, thus we get the condition 



_SI-3.3. Snap-through_ 

Snap-through indicates: 

1. Two local extrema for ∆ _x >_ 0 

2. No positive roots. 

From (1.), _f_<sup>_′_</sup> (∆ _x_ ) should have two real roots for ∆ _x >_ 0 



From (2.), _g_ (∆ _x_ ) should have no real roots 



_SI-3.4. Local max_ 

This case indicates the energy should be positive only up to the maximum deformation (versus in the bistable case, where it should be positive for _any_ deformation). 



We can factor _F_ ( _s_ ): 



where 



Then for a given max deformation _smax_ 



_G_ ( _s_ ) is convex ( _c_ 3 _>_ 0). The critical points where it can be negative in _s ∈_ (0 _, smax_ ] are: 

- Left end point (0). Since _G_ (0) = 1 _/_ 2 _>_ 0, we can ignore this one. 

- Right end point _smax_ . 

- Local minimum _s∗_ where _G_<sup>_′_</sup> ( _s∗_ ) = 0. 

6 

Let’s derive _s∗_ first: 



Since _c_ 2 _<_ 0 and _c_ 3 _>_ 0, the local min happens at a positive value _s∗ >_ 0. 

This gives us two cases where _s∗ > smax_ and _s∗ < smax_ . 

1. Case (1): _s∗ > smax_ 

This case happens when the local minimum _s∗_ happens to the right of the interval (0 _, smax_ ]. 



The global minimum is at _smax_ and we want this to be positive: 



In summary, 



2. Case (2): _s∗ < smax_ 

This happens when the local minimum is inside the interval (0 _, smax_ ]. 



The global minimum is at _s∗_ , and should be positive: 



Plug in the expression for _s∗_ (Eq.25) into above: 



In summary, 



7 

## **SI-4. Broader categorical comparison under constitutive uncertainty** 

To test whether the ensemble-level robustness trend reported in the main text persists over a broader range of nominal performance, we repeat the categorical comparison using optimized designs with unperturbed KE ratios in the interval _KE ∈_ [0 _._ 01 _,_ 0 _._ 10]. For each chain category, this interval is divided into nine bins of width 0 _._ 01, and 100 designs are selected from each bin. This produces 900 baseline designs per category with approximately uniform nominal KE-ratio distributions over the prescribed interval. 

For each baseline design, we apply 5% random perturbations to the nonlinear polynomial coefficients and propagate the uncertainty using 100 Monte Carlo trials, following the same perturbation model and admissibility checks used in the main text. We then calculate the mean perturbed KE ratio for each baseline design. Figure S1 shows the distributions of these mean values. 



<!-- Start of picture text -->
15 : . .<br>g GALI Categories 5% Design _.S P(KE) Pas<0.1! I Homogeneous Bisable Median Performance<br>= Uncertainty an ‘WA mi Heterogeneous Excluding Bistability | med(KE) = 0.127<br>310 = med(KE) = 0.102<br>Pa Py med(KE) = 0.087<br>A + 7<br>25 | gs ‘Threshold Probability<br>& dose 10s P(KE) < 0.1 = 16%<br>e: Optimal Design P(KE) < 0.1 = 48%<br>50.01 0 P(KE) < 0.1 = 64%<br>ot 005 «401 860.45) 020253<br>KE, IRE<br>or KE in KEKE,<br><!-- End of picture text -->

Figure S1: Performance of optimized chains under constitutive uncertainty 

The distribution of the polynomial coefficients of the Monte Carlo ensembles of Fig. S1, shown together with the categorical bounds. 



<!-- Start of picture text -->
Homogeneous Bistable Heterogeneous Heterogeneous Excluding Bistablity<br>4000<br>3500<br>3000<br>2500<br>2000<br>1500<br>1000<br>500<br>0<br>-120 -100 -80 -60 -40 -20 0 -120 -100 -80 -60 -40 -20 0 -120 -100 -80 -60 -40 -20 0<br>c2 c2 c2<br>c3<br><!-- End of picture text -->

Figure S2: Nonlinear coefficient distributions 

8 

## **SI-5. Robustness under perturbed nonlinear coefficients** 

To complement the impactor-mass perturbation study in Fig. 4, we repeat the same spatiotemporal analysis using perturbations to the nonlinear polynomial coefficients. At a fixed noise level of _ϵ_ = 2%, we generate 500 Monte Carlo realizations for each optimized chain and select one representative realization per category whose _K_ E ratio is within 1% of the corresponding sample mean. For these representative perturbed designs, we then plot the spatiotemporal kinetic energy, potential energy, and local stiffness using the same format as Fig. 4. 



<!-- Start of picture text -->
Homogeneous Heterogeneous<br>a Linear Bistable Heterogeneous —_Excluding Bistability<br>4 4 4 Be 4 10°<br>3 3 3 3 10"<br>g 8<br>coi 2 2 2 10? =<br>.<br>a<br>1eee = 1 1 10°<br>0 oo— 0 all 0 _ 10*<br>5 10 15 20 5 10 15 20 5 10 15 20 5 10 15 20<br>b. Unit Cell Unit Cell Unit Cell Unit Cell<br>4EE 4 4 4 104<br>3 3 3 3<br>E2 2 2 2 = 108 8<br>&<br>= = a<br>1 1 =—_ 1 1 SS<br>—, -F, ° 5 toe<br>5 10 15 20 5 10 15 20 5 10 15 20 5 10 15 20<br>Unit Cell Unit Cell Unit Cell Unit Cell<br>c444<br>33 3 3 -0.02<br>2 0.04<br>£2 2 2 - 2 x<br>aa —4* J Bf}-0.06<br>1 a ae 1 = 1 0.08<br>0 — — 0 01<br>5 10 15 20 5 10 15 20 5 10 15 20 5 10 15 20<br>Unit Cell Unit Cell Unit Cell Unit Cell<br><!-- End of picture text -->

Figure S3: Dynamic response of the linear, homogeneous bistable, heterogeneous, and heterogeneous excluding bistability chains for perturbed nonlinear coefficients. (a) Spatiotemporal kinetic energy ( _KE_ ) response, normalized by the impactor energy ( _IE_ ). Star markers denote the time when the maximum _KE_ occurs at the last cell. (b) Potential energy ( _PE_ ). (c) Local stiffness ( _∂fI /∂_ ∆ _x_ ) with coloring saturated to display only negative values. 

9 

## **SI-6. Parameters of the optimized and representative perturbed designs** 

The nonlinear polynomial coefficients of the optimized designs used throughout the paper and the corresponding representative perturbed realizations used in Fig. S3 are reported together in Table S1 for direct comparison. The resulting KE ratios of the representative perturbed realizations are reported separately in Table S2. 

|||Optim|ized|Pertu|rbed|
|---|---|---|---|---|---|
|Chain category|Spring family|_c_2|_c_3|_c_2|_c_3|
|Homogeneous bistable|–|_−_116_._12|3052_._97|_−_116_._06|2993_._32|
|Heterogeneous||||||
||A|_−_84_._36|1589_._77|_−_83_._57|1570_._73|
||B|_−_94_._08|2426_._41|_−_94_._50|2415_._17|
||C|_−_10_._11|1682_._13|_−_10_._28|1632_._89|
||D|_−_33_._35|3300_._14|_−_33_._83|3324_._89|
|Heterogeneous excludin|g bistability|||||
||A|_−_59_._83|2715_._10|_−_59_._51|2706_._04|
||B|_−_69_._15|1472_._62|_−_67_._46|1465_._52|
||C|_−_100_._21|3374_._10|_−_99_._08|3378_._14|
||D|_−_53_._23|1371_._83|_−_53_._49|1384_._72|



Table S1: Nonlinear polynomial coefficients of the optimized designs and the representative perturbed realizations used in Fig. S3. 

|Chain category|_KE_|
|---|---|
|Homogeneous bistable|0_._062|
|Heterogeneous|0_._036|
|Heterogeneous excluding bistability|0_._015|



Table S2: KE ratios of the representative perturbed realizations used in Fig. S3. 

10 

## **SI-7. Comparison of pulse lengths** 

To quantify the sharper initial pulses observed in the nonlinear chains in Fig. 3a, we compare their spatial kinetic-energy profiles at _t_ = 0 _._ 5. For each chain, the spatial profile of ( _KE/IE_ ) is normalized by its maximum value at this time. We define the pulse length as the spatial full width at half maximum (FWHM) of the dominant kinetic-energy pulse, with the half-maximum crossing locations obtained by linear interpolation between adjacent unit cells. 



<!-- Start of picture text -->
t=0.5<br>1 R R -@- Linear i<br>> 0.8 —€- Heterogeneous<br>g ] -@= Heterogeneous Excluding Bistability<br><06 /<br>3Bo b----------------- ih -- pag ee ee |<br>5 0.43 1 4<br>—<br>80.2 4<br>—————YF—s= DA — — 0<br>2 4 6 8 10 12 14 16 18 20<br>Unit Cell<br><!-- End of picture text -->

Figure S4: Spatial kinetic energy profiles at _t_ = 0 _._ 5 for the linear and three optimized nonlinear chains. 

From the spatial profiles shown in Fig. S4, the linear, homogeneous bistable, heterogeneous, and heterogeneous-excluding-bistability chains have pulse lengths of (2.14), (1.13), (1.08), and (1.86) unit cell spacings, respectively. Thus, all three nonlinear chains exhibit a narrower dominant pulse than the linear chain at _t_ = 0 _._ 5, consistent with the sharper initial pulses observed in the spatiotemporal response. 

11 

