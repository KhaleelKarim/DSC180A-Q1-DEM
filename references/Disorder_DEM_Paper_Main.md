

<!-- Start of picture text -->
Journal Name<br><!-- End of picture text -->





# **Heterogeneity in constitutive nonlinearity enhances impact mitigation robustness** Caglar Tamur,<sup>_a_</sup> Maya Brandy,<sup>_b_</sup> Hyunsun Alicia Kim,<sup>_a,c_</sup> and Nicholas Boechler<sup>_b,c_</sup> 



## Abstract 

Heterogeneity has been shown to enhance material robustness within the context of quasi-static performance metrics such as fracture toughness. Separately, within dynamic settings, nonlinear elastic constitutive response has emerged as a useful mechanism for mitigating the effects of impact. A drawback of using nonlinearity is a potential lack of robustness, where small variations in impact condition or material properties can lead to worse performance. <mark>Here we ask, for impact regimes where wave propagation is important, whether heterogeneity of</mark> _<mark>only</mark>_ <mark>the nonlinear part of the elastic constitutive response can improve robustness.</mark> To address this, we computationally study a damped chain of uniform masses connected by springs having cubic-polynomial forcedisplacement laws, wherein the linear stiffness remains fixed, but higher order terms can vary. Using gradient-based optimization, we minimize peak kinetic energy transmitted to a protected boundary in response to an impact. We then construct three sets of optimal chains for which the performance exceeds a chosen threshold: homogeneous chains, heterogeneous chains, and heterogeneous chains where bistable constitutive responses are excluded (but snap-through is allowed). <mark>We then perturb the nonlinear constitutive terms for all the chains and study the distribution of peak transmitted kinetic energy,</mark> which yields two key outcomes. First, both sets of heterogeneous chains retain better performance, on average, than the set of homogeneous chains. Second, noting that the best performing constitutive responses within our design domain for the homogeneous chain are bistable: the set of heterogeneous chains excluding bistability retains the best performance. Comparison of the spatiotemporal responses of the optimal chains with and without perturbation suggests that adding heterogeneity may <mark>reduce reliance on bistable springs</mark> (in- 

> _a Department of Structural Engineering, University of California, San Diego, La Jolla, CA, US_ 

> _b Department of Mechanical and Aerospace Engineering, University of California, San Diego, La Jolla, CA, US_ 

> _c Program in Materials Science and Engineering, University of California, San Diego, La Jolla, CA, US_ 

stead leveraging snap-through) by introducing other attenuating mechanisms that may have better robustness properties. Comparison of the spatiotemporal responses of the heterogeneous chains with and without bistable springs allowed, however, did not yield clear evidence of an underlying mechanism that would cause the differing robustness. <mark>Our results suggest heterogeneity in nonlinear constitutive responses can enable robust impact mitigation and raise questions about the role of disorder manifesting in constitutive nonlinearity only, as well as the connection of bistability and heterogeneity to system sensitivity.</mark> 

## 1 Introduction 

Material heterogeneity has been shown to enable improved damage tolerance as measured by quasi-static metrics (e.g., fracture toughness). For example, the hierarchical structure of bone<sup>1</sup> and other biological materials<sup>2</sup> help them resist global failure. The advantages of heterogeneity have also been borne out via enhanced fracture toughness in systems such as metallic glasses<sup>3</sup> , bioinspired composites<sup>2</sup> , and metamaterials<sup>4–6</sup> . Heterogeneity has also been shown to enhance energy absorption<sup>7–13</sup> , including in response to impact<sup>7,9,13</sup> , wherein the absorption enhancement was attributed to irreversible mechanisms such as delamination, plasticity, viscosity, or resonant absorption. Separate from these quasi-static mechanisms, heterogeneous structures such as phononic crystals have shown the ability to attenuate mechanical waves induced by impact due to effects such as band gaps<sup>14</sup> , from which an enhancement to damage tolerance in dynamic settings could be inferred. One recent example of this in hierarchical biological materials is the demonstration of megahertz frequency stress wave attenuation in the mantis shrimp club<sup>15</sup> . 

In a related vein to wave attenuation via band gaps, nonlinearity has emerged as a useful means for passive wave manipulation<sup>16–18</sup> . For example, when applied to impact mitigation, the interplay between strong nonlinearity and dispersion introduced by discreteness can decompose an initial impulse into a series of smaller amplitude pulses forming a solitary wave train<sup>19</sup> . It is also well known that nonlinear systems can be highly sensitive 

Journal Name, [year], **[vol.]** , 1–12 | 1 

to perturbations<sup>20</sup> . For example, small variations in the impactor conditions applied to bistable nonlinear chains can lead to the formation of solitary waves that self-localize and <mark>transmit more kinetic energy than its linear counterpart</mark><sup>21</sup> . This sensitivity in performance poses a challenge for materials design <mark>manufacturing when leveraging nonlinear mechanisms for wave tailoring.</mark> 

Energy transport in a broad spectrum of heterogeneous systems (referring to the effects of defects, random disorder, or very highorder periodicity) has been studied in both linear<sup>22</sup> and nonlinear<sup>23</sup> dynamic contexts. A seminal work by Anderson<sup>22</sup> demonstrated in a linear framework that, with sufficient disorder, energy (taking the form, in their case, of electron spins) does not diffuse and remains localized. Related concepts have been applied in the context of designer materials using linear wave phenomena, such as phononic crystals<sup>24</sup> or locally-resonant acoustic metamaterials<sup>25</sup> , wherein disorder or hierarchy (respectively) induced broadening of stop-band regions (albeit at the expense of attenuation strength), which again could be inferred to be beneficial for a system’s robustness. <mark>The effect of nonlinearity on such heterogeneity-induced localization remains less clear</mark><sup>23</sup> , in different cases either preserving or destroying the localization. This includes studies where the disorder was contributed solely through the nonlinear terms<sup>26</sup> and different (power law) localization was observed<sup>27–29</sup> compared to linear systems. 

Given all of this, we ask whether the introduction of designed heterogeneity into constitutive nonlinearity can lead to <mark>enhanced impact mitigation robustness for regimes where wave propagation is important</mark> . We address this question using a one-dimensional (1D) <mark>mass-spring-damper</mark> chain with unit cell level prescribed nonlinearity and spatially heterogeneous spring laws (as shown in Fig. 1a,b). Applying gradient-based optimization to this discrete element model (DEM), <mark>we f</mark> i <mark>rst identify nonlinear constitutive parameters that minimize the peak kinetic energy transmitted to the protected boundary.</mark> We then construct three sets of optimal chains for which the performance exceeds a chosen peak kinetic energy transmission threshold: homogeneous chains, heterogeneous chains, and heterogeneous chains where bistable constitutive responses are excluded (which we refer to as “heterogeneous-excluding-bistability”). We then perturb the nonlinear terms in the constitutive responses for all the chains, and study their distribution of peak kinetic energy transmission. Our study of the three sets of perturbed chains yields two key outcomes. First, both sets of heterogeneous chains retain better (lower) peak kinetic energy transmission, on average, than the set of homogeneous chains. Second, noting that (in agreement with Ref.<sup>30</sup> ) th <mark>e best performing constitutive responses within our design domain for the homogeneous chain are bistable</mark> : the set of heterogeneous chains excluding bistability retains the best performance. Comparison of the spatiotemporal responses of the optimal chains with and without a perturbation suggests that adding heterogeneity may reduce reliance on bistable springs (instead leveraging snap-through springs) <mark>by introducing other attenuating mechanisms such as interfaces, which may have better robustness properties.</mark> Comparison of the spatiotemporal responses of the heterogeneous chains with and without bistable springs allowed, however, did not yield clear evidence of an underly- 

ing <mark>mechanism that would cause heterogeneous chains excluding bistability to show the best robustness</mark> . Our results suggest heterogeneity in nonlinear constitutive responses can enable robust impact mitigation and raise questions about the role of disorder manifesting in constitutive nonlinearity only, as well as the connection of bistability and heterogeneity to system sensitivity. 

## 2 Results 

### **2.1 Inverse-design of heterogeneously nonlinear chains** 

We model the metamaterial as a 1D chain of _N_ = 20 masses connected by linear viscous dampers _ζ_ in parallel with nonlinear springs (Fig. 1a). Each spring takes the form of a cubic polynomial in compression <mark>(keeping the linear term only in tension),</mark> where the linear stiffness is uniform throughout the chain. To introduce heterogeneity, <mark>we allow four spring families {A,B,C,D}, arranged consecutively a</mark> long the chain with five springs assigned to each family (Fig. 1a). The compressive part of the spring behavior as 



where ∆ _x >_ 0 denotes the (dimensionless) spring strain in compression and _I_ denotes the four sections of the chain ( _i.e._ , the blue, green, yellow, and red sections in Fig. 1a). <mark>The equation of motion for the</mark> _<mark>i</mark>_ <mark>th mass</mark> in the interior of the chain is thus written as: 



where _xi_ is the displacement of the _i_ th mass, over-dots denoting the time derivatives. The right boundary is fixed. The impactor is a point mass with <mark>prescribed initial velocity,</mark> where the interaction with the first mass of the metamaterial <mark>is mediated by a tensionless contact spring that allows the free rebound and detachment of the impactor.</mark> Unless stated otherwise, the impact conditions are chosen as <mark>non-dimensiona</mark> l quantities _M/M_ 0 = 0 _._ 01 and _V /V_ 0 = 0 _._ 25, where _M_ and _V_ are the impactor mass and velocity, _M_ 0 is half the mass of the chain and _V_ 0 is the chain’s linear sound speed <mark>. See Supplementary</mark> Information section 1 (SI-1) for full discrete element model details. 

Our design objective is to minimize the peak kinetic energy ( _KEnon_ ) experienced at the <mark>last particle</mark> (furthest from the impactor). The design variables are the nonlinear polynomial coefficients for each of the four families ( _c_ 2 _, c_ 3). With this parametrization, we perform impact simulations and use a gradient-based optimizer to identify the constitutive laws that minimize _KE_ := _KEnon/KElin_ at the chosen impact condition ( _M,V_ ), where _KElin_ is the peak kinetic energy experienced at the last particle in an otherwise identical linear chain (retaining only the linear stiffness term). This results in a constrained optimization problem of the form 



where _W_ <mark>is a physical constraint to ensure positive strain energy over the relevant deformation range</mark> (SI-2). In addition to the heterogeneous chain optimized as per Eq. 3, for the same impact 

2 | Journal Name, [year], **[vol.]** , 1–12 



<!-- Start of picture text -->
a. fa(Ax) fa(Ae) fp (Ae) fp (Ax) A fo(A fp(Aa) fp(Ax)<br>Vv uy ¢ ¢ ¢ ¢ iS iS ¢ un ¢<br>b.0.08 Heterogeneous =~Distance to Impactor0,08, ExcludingHeterogencousBistabitity Co19 Homogeneous Bistable “ Design ;<br>“0 “0 + Heterogeneous neertainty<br>Heterogeneous Excluding Bistability<br>0.06 ‘ y 0.06 ‘ y ot |<br>Zoos ° Foo |. =<br>ad as <i ¢ on oa 5<br>a 0.02 = 0.02 2£0.05) e(1-5)“1-5) c* ct cLot +6)<br>c*: Optimal Design<br>° 0 P(\di| < 6) © 95%<br>0 002 0.04 0.06 0 0.02 004 0) 0 1 2 3 4 5<br>Ax Ax €: Noise Level (%)<br>d<br>15 ——4<br>MBBAIICatcgories}<br>S50 ategi | . axe < 3% Hl Homogeneous Bistable<br>S Uncertainty5% Design Sg —H MlIM HeterogeneousHeterogeneous Excluding Bistability<br>& -2 10- ' 4<br>6 5 \ median(j1x£) = 0.105<br>Py + 38 median(jx2) = 0.067<br>&Z 2 median(u«2) = 0.050<br>Z BS<br>fal$ 0.95c*c* 1.05 aZ<br>0 0<br>0.01 0.02 0.03 0.02 0.04 0.06 008 0.1 0.12 014 0.16 018 0.2<br>KE KE<br>e Heterogeneous f. Me < 3%<br>4 Homogeneous Bistable Heterogeneous Excluding Bistability After Noise<br>00 T ERR ee et] RESIN Es FAR TRC 4<br>3000 eC iceeeae aes ES Ee . ota t—te<br>& 2000 exe BF Fe ged - iets<br>5 :<br>-100 -50 0 -100 -50 0 -100 -50 0 -100 -50 0<br>c2 C2 C2 C2<br>— c3 = (2/9)c} (positive energy) — c3 = (1/4)c3 (snap-through/ bistable) — c3 = (1/3)c3 (monotonic/ snap-through)<br><!-- End of picture text -->

Fig. 1 Heterogeneity in constitutive nonlinearity increases impact mitigation robustness. (a) Metamaterial as a 1D chain with four distinct elastic nonlinearities. (b) Force-displacement relations that minimize the _KE_ ratio. Color indicates the spring families of the heterogeneous chains, shown along with the homogeneous bistable chain (black). (c) Performance of the optimized chains under nonlinear stiffness coefficient perturbations with varied Gaussian noise. _KE_ ratio reported in terms of sample mean and shading indicates one standard deviation, ( _µKE ± σKE_ ). (d) <mark>Categorical</mark> comparisons of chains under 5% random noise. Unperturbed, optimized set of samples with a uniform _KE ∈_ [0 _._ 01 _,_ 0 _._ 03] distribution (left). Mean _KE_ ( _µKE_ ) distribution after perturbations (right). Dashed line indicates the threshold performance (worst of the undisturbed set). (e) Distribution of polynomial coefficients of the unperturbed set of (d), larger markers indicating the means of each spring category. Solid lines indicate the categorical bounds; turquoise is the constraint used in the optimization to ensure positive strain energy across the deformation range, the other two lines indicate the transitions between bistable, snap-through, and monotonic stiffening behavior. (f) Designs that preserve mean( _KE_ ) _<_ 3% after perturbation. 

Journal Name, [year], **[vol.]** , 1–12 | 3 

conditions, we also optimize: a homogeneous chain (single unit cell type, <mark>with the performance denoted as</mark> _KE_ homo); and a heterogeneous chain where bistable springs are excluded through an additional constraint (see SI-3), with the performance denoted as _KE_ hetero _−_ exclude (and which we refer to as the “heterogeneousexcluding-bistability” chain). All three chains types are found to outperform the linear baseline substantially: The best performing designs reach _KE_ hetero = 0 _._ 56%, _KE_ homo = 1 _._ 17%, and _KE_ hetero _−_ exclude = 0 _._ 86%, with the first two chains choosing at least one bistable-type spring law (i.e., Fig. 1b) and both heterogeneous chains outperforming the homogeneous one. Resulting optimized nonlinear coefficients can be found in SI-6. 

### **2.2 Robustness to constitutive nonlinearity uncertainty** 

We model uncertainty in the nonlinear spring law parameters by perturbing the second and third order optimized polynomial coefficients of the three, previously identified, best performing designs. We sweep a prescribed noise level _ε ∈_ [0 _,_ 5%], where _ε_ = 0 recovers the optimal/undisturbed design. For each _ε_ , we sample _Ns_ = 500 independent perturbed designs from a zero-mean Gaussian, 



where _c_<sup>_∗_</sup> is the unperturbed nonlinear stiffness coefficients and _σε_ is chosen such that _∼_ 95% of samples would satisfy _|δi| ≤ ε_ , (i.e, _σε_ = _ε/_ 2 for normal distribution). We discard and resample any realization that violates the positive strain-energy condition (SI-2). The springs of each section ( _i.e._ , _{A, B,C, D}_ from Eq. 3) have the same perturbation applied, such that the homogeneous system remains homogeneous and heterogeneous systems retain four distinct spring types after perturbation. For each perturbed sample, we run a DEM impact simulation and compute the resulting _KE_ ratio. Figure 1c reports the mean and one standard deviation ( _µ ± σ_ ) at each noise level _ε_ . The performance of the homogeneous bistable design degrades rapidly with increasing uncertainty worsening by a factor of 6 _×_ by _ε_ = 0 _._ 25% noise level and ultimately reaching 8 _×_ by _ε_ = 5% noise level. In contrast, the heterogeneous chain worsens by a factor of 3 _×_ by _ε_ = 0 _._ 25% and 12 _×_ by _ε_ = 5% noise level, and the heterogeneous-excludingbistability chain remains approximately 1 _×_ its unperturbed value at _ε_ = 0 _._ 25% and worsens by 3 _×_ by _ε_ = 5% noise level. We note that while the heterogeneous chain worsens proportionally more than the homogeneous chain at _ε_ = 5%, this is due to the lower starting _KE_ of the heterogeneous chain (without noise), with the mean _KE_ of the heterogeneous chain is still remaining lower at _ε_ = 5% (as can be seen in Fig. 1c). 

To assess whether the robustness trend extends beyond the representative (optimum) designs in Fig. 1b,c, we perform an ensemble-level comparison across the three chain categories. For each category (homogeneous, heterogeneous, and heterogeneous-excluding-bistability), we generate sets of optimized designs by solving the corresponding inverse-design problem from randomized initializations and retaining solutions whose _nominal_ (undisturbed) _KE_ ratio falls within _KE ∈_ [0 _._ 01 _,_ 0 _._ 03]. From these solutions, we construct a set of 200 baseline samples per category such that their nominal _KE_ values are 

approximately uniformly distributed over [0 _._ 01 _,_ 0 _._ 03], Fig. 1d. For each baseline sample, we then introduce design uncertainty by applying 5% random perturbations to the polynomial parameters _c_ 2 and _c_ 3 and propagating this uncertainty with 100 Monte Carlo trials (using the same perturbation model and admissibility checks as before). Fig. 1d summarizes the resulting distributions of _KE_ ratios, where the median performance is _KE_ = 0 _._ 105 for the homogeneous bistable, _KE_ = 0 _._ 067 for the heterogeneous and _KE_ = 0 _._ 050 for the heterogeneous excluding bistability chains. Using _KE_ = 0 _._ 03 as a performance target (upper bound of the undisturbed samples, Fig. 1d) we found that 9% of the heterogeneous-excluding-bistability samples retain below the target, i.e., _P_ ( _KE_ ) _<_ 0 _._ 03 = 9%, whereas none of the samples in the other categories do (dashed line in Fig. 1d). Together, these ensemble statistics reproduce the trend in Fig. 1c and indicate that heterogeneity improving mitigation robustness, with heterogeneity-excluding-bistability retaining the best performance, is a category-level trend rather than an isolated property of a single optimized solution. 

To further confirm that the trend in Fig. 1d is categorical, we also study the distribution of the nonlinear coefficients. In Fig. 1e, we show the distribution of the the initial nominal samples together with the bounds that separate the different qualitative types of nonlinear responses ( _i.e._ monotonic increase, snapthrough, or bistability). Coloring of each point denote their spring category, consistent with Fig. 1a, and the larger markers indicate the mean of each category. The cyan curve is the positive energy bound required for the bistable springs (SI-2), the red and the blue bounds indicate the transition from the bistable to the snap-through and from snap-through to the monotonic stiffening, respectively (SI-3). The study presented in this section is repeated for a broader range of nominal performance and the results are provided in the SI-4. 

### **2.3 Robustness to impact condition uncertainty** 

The inverse design in Section 2.2 targets a single excitation; however, real impacts vary in both impactor mass and velocity, which can also greatly affect performance. To assess robustness to excitation uncertainty, we consider the three optimal chains identified in Fig. 1b,c and compute a two-parameter performance map by sweeping the non-dimensional impactor mass and velocity around the design point ( _M/M_ 0 = 0 _._ 01 _,V /V_ 0 = 0 _._ 25) and recording the resulting _KE_ ratios (Fig. 2). 

Across all optimized nonlinear chains, Fig. 2a reveals clear regions where the transmitted _KE_ ratio remains below one, indicating effective attenuation relative to the linear baseline. However a significant difference in sensitivity to impactor conditions can be seen between the three cases (homogeneous, heterogeneous, and heterogeneous-excluding-bistability). To aid visualization of this sensitivity, we plot slices of the _KE_ ratio of Fig. 2a at the design point impactor mass and velocity in Fig. 2b, and the derivative of those curves with respect to _V_ and _M_ , respectively, in Fig. 2c. As can be seen collectively from Fig. 2, the homogeneous chain exhibits the highest sensitivity to impact conditions, the heterogeneous-excluding-bistability exhibits the least, 

4 | Journal Name, [year], **[vol.]** , 1–12 



<!-- Start of picture text -->
a. Homogeneous Heterogeneous Heterogeneous .<br>0.5 Bistable Excluding Bistability<br>pe 0.5 py 0.5 10°<br>=so 03a \\) 034sa} 03. | oo 8<br>>= 02 o so 0.2 q4 0.2 g<br>AES<br>o1 i ey ee 1 a — 04<br>0.01 — 0.01 es 001 10?<br>0.001 0.01 0.02 0.03 0.04 0.05  0.0010.01 0.02 0.03 0.04 0.05 0.0010.01 0.02 0.03 0.04 0.05<br>MIM MIM, MIM,<br>b. c.<br>02 0.25<br>S 2000 Ss<br>Soo0.15 3 ots_ == ‘0000 =So> 100<br>0.05 ot & -1000 g<br>0.05 2° S -100<br>S -2000 4<br>0 0<br>0.009 0.01 0.011 0.2 0.25 03 0.009 0.01 0.011 0.2 0.25 0.3<br>M/IMo V/Vo MIM, V/Vo<br>— Homogeneous Bistable — Heterogeneous — Heterogeneous Excluding Bistability<br><!-- End of picture text -->

Fig. 2 Sensitivity of the KE ratio to impact conditions. (a) KE ratio over the impactor mass–velocity space for the optimized chains. The star markers indicate the design-point impact condition ( _M/M_ 0 = 0 _._ 01 _,V /V_ 0 = 0 _._ 25) used for inverse design; insets magnify the neighborhood of the design point. (b) Slices in the mass and velocity space of (a), centered at the design point. (c) Gradients of KE ratio, corresponding to (b). 

with the heterogeneous chain in between. 

## 3 Discussion 

These observed differences in performance as quantified by _KE_ ratio raise the question: what is the underlying mechanism causing the observed differences in robustness? In Fig. 3, we compare the dynamical response for the linear, and optimized homogeneous, heterogeneous, and heterogeneous-excluding-bistability designs of Fig.1b,c (respectively, the left to right columns in Fig. 3). Figure 3a shows the spatiotemporal kinetic energy response of the chains. In all panels of Fig. 3a-c, a teal star is used to denote the time of maximum kinetic energy experienced at the last particle in the chain. Figure 3b shows the spatiotemporal potential energy and Fig. 3c shows the spatiotemporal evolution of the local stiffness ( _∂ fI/∂_ ∆ _x_ , as per the spring form denoted in Eq. 1), restricted to only show negative values. In Fig. 3d, we show the 2D Fourier transform of the spatiotemporal kinetic energy response (frequency versus wavenumber, computed over the full simulation interval up to the normalized time of _t_ = 20). 

In the spatiotemporal response of the linear chain (left panel of Fig. 3a,b), the impact pulse can be seen to propagate and reflect with some limited decay and dispersion. This is corroborated by the expected monoatomic chain dispersion in the corresponding panel in Fig. 3d. In contrast to the linear chain spatiotem- 

poral response, in all three nonlinear chains, we see the formation of a sharper initial pulse (see SI-7 for comparison of pulse lengths at _t_ = 0 _._ 5), which then exhibits gradual slowing and eventual disintegration before the end of the chain (see, _e.g._ , right three columns of Fig. 3a,b). This is accompanied by significant spectral broadening, as seen in Fig. 3d. Taken together, these behaviors are consistent with that observed for bistable chains in Refs.<sup>21,30,31</sup> , where the pulse was considered as a type of solitary wave (or train thereof), with the slowing attributed to dissipationinduced amplitude reduction. In Refs.<sup>21,30,31</sup> , the spectral broadening was tied to enhanced dissipation due to the interplay between the nonlinear dynamical response and intersite viscosity. We should note trapping of energy from the propagating pulses into strain energy is also a mechanism that can contribute to kinetic energy reduction for bistable systems<sup>32</sup> . This can be seen for the two systems with bistable springs (the middle two columns), in Fig. 3b,c, where the entry into a negative stiffness regime (identifiable in Fig. 3c) is followed by a set of unit cells that retain a finite potential energy (and thus strain) for an extended period of time (identifiable in Fig. 3b). More specifically, this can be seen for the homogeneous chain at unit cells 13 to 15 from _t ≈_ 1.1 onward, and for the heterogeneous chain at unit cell 5 from _t ≈_ 0.5 onward. As expected, while the heterogeneous-excludingbistability chain has negative stiffness regions (which are acti- 

Journal Name, [year], **[vol.]** , 1–12 | 5 



<!-- Start of picture text -->
Homogeneous Heterogeneous<br>a. Linear Bistable Heterogeneous Excluding Bistability<br>4 4 4 4 10°<br>Bc<br>3 3 3 3 10"<br>2<br>& al 2 2 2 10? ~y<br>7<br>1ha =; 1 1 10%<br>0 —_—— = a<br>5 10 15 20 0 5 10 15 20 0 5 10 15 20 0 5 10 15 20 10*<br>b Unit Cell Unit Cell Unit Cell Unit Cell<br>— ‘ ‘ ‘ to<br>a<br>3 3 3 ~ 3<br>2 Bc )<br>£2 2 2 2 = 108<br>= = - om<br>1 1 os= 1 ==soe —ax ==<br>a 0 0 0 40°<br>5 10 15 20 5 10 15 20 5 10 15 20 5 10 15 20<br>c Unit Cell Unit Cell Unit Cell Unit Cell<br>4 4 4 4 tO)<br>aE<br>3 3 Br 3 3 0.02<br>2 . 0.04<br>2 2 2 2 =<br>& 2 -0.06 S<br>ic! eei") ' -= ' --= 0.08<br>0 — — 0 0.4<br>5 10 15 20 5 10 15 20 5 10 15 20 5 10 15 20<br>d Unit Cell Unit Cell Unit Cell Unit Cell<br>1 1 1 1 40°<br>08 0.8 08 08<br>107 &<br>ss 06 0.6 06 06 <7<br>0.4 04) 04 04 qR<br>0.2 == =:= = 028 a 0.26 0.2 ames =<br>0 0 — 0 0 402<br>32-2012 3 32240123 «3227012 3 «32401 2 3<br>ky ky ky ky<br><!-- End of picture text -->

Fig. 3 Dynamic response of the linear, homogeneous bistable, heterogeneous, and heterogeneous-excluding-bistability chains. (a) Spatiotemporal kinetic energy ( _KE_ ) response, normalized by the impactor energy ( _IE_ ). Time is reported as _t_ = _tsim/_ 25, where _tsim_ is the non-dimensional simulation time. Star markers denote the time when the maximum _KE_ occurs at the last cell. (b) Potential energy ( _PE_ ). (c) Local stiffness ( _∂ fI /∂_ ∆ _x_ ) with coloring saturated to display only negative values. (d) Wave number _kx_ versus frequency _fn_ = _f_<sup>_∗_</sup> _/_ ~~�~~ Vv _c_<sup>_<u>∗</u>_</sup> 1<sup>_/m∗_,where</sup><sup>_f ∗_denotes the dimensional frequency;</sup> color indicates normalized FFT magnitude. 

6 | Journal Name, [year], **[vol.]** , 1–12 

vated as can be seen in Fig. 3c), because it does not have any secondary stable states at zero load, the prior phenomenon of unit cells retaining a nearly constant, non-zero potential energy for an extended duration is not present therein. 

From the responses of the three optimized nonlinear systems shown in Fig. 3, no clear underlying mechanism for the increase in robustness for the heterogeneous chains is apparent to the authors. To attempt to address this, we study the dynamical response of all four chains in Fig. 3 for a perturbed impactor mass of 1 _._ 01 _M_ (in the following we will refer to this as the “perturbed” case). The resulting spatiotemporal kinetic energy, potential energy, and negative stiffness activation for the perturbed case are shown in Fig. 4(a,b,c), respectively. The time shown is _t ∈_ [0 _,_ 6] in Fig. 4 compared to _t ∈_ [0 _,_ 4] in Fig. 3, as the time of maximum kinetic energy experienced by the perturbed heterogeneous chain was outside the original window shown. The transmitted kinetic energy in the linear case increases 1 _._ 02 _×_ in the perturbed case compared to the unperturbed case. Comparing the perturbed nonlinear peak kinetic energy transmission to that of the perturbed linear system, the resulting maximum _KE_ at the last particle for each of these perturbed cases are 11%, 2 _._ 6%, and 0 _._ 8% for the homogeneous, heterogeneous, and heterogeneousexcluding-bistability chains, respectively. This corresponds to 9 _._ 4 _×_ and 4 _._ 6 _×_ worse in performance compared to the unperturbed cases for the homogeneous and heterogeneous chains, respectively, whereas the heterogeneous-excluding-bistability chain performance improves by 1 _._ 07 _×_ . 

We consider the differences between the unperturbed and perturbed case of the homogeneous nonlinear chain (second column from the left in Figs. 3 and 4, respectively). The perturbed case has one additional unit cell snapped to the second stable state, extending the snapped region from unit cells 13-15 in the unperturbed case to unit cells 13-16 in the perturbed case (as per the potential energy responses of in the second columns of panel b in Figs. 4 and 3). Similarly, the perturbed case also appears to have disintegration of the primary pulse resulting from impact occur one unit cell further to the right than in the unperturbed case (visible in the second columns of panel a in Figs. 4 and 3). This is consistent with observations for a different bistable chain in Ref.<sup>30</sup> with changes in impactor velocity, where variation in impactor velocity induced a periodic variation in performance that corresponded to movement of the furthest unit cell to snap and protractedly stay near the second stable equilibrium position. We also note that the peak kinetic energy experienced in the perturbed system (second column of Fig. 4a) occurs in the spatiotemporal vicinity of this group of bistable unit cells snapping to a nonzero strain and remaining there for an extended duration (second column of Fig. 4b,c), and may relate to waves radiating from the snapping events. In the unperturbed case, the kinetic energy maximum occurs at a much later time. By comparing the kinetic and potential energy spatiotemporal responses of the unperturbed homogeneous optimal chain (second column of Fig. 3a,b), one may also trace the peak kinetic energy point, at least partially, back to a wave emitted leftwards in the chain from the last unit cell to snap and enter a negative stiffness regime (second column of Fig. 3c). This leftward emitted wave subsequently reflects back 

rightwards from the impacted end to interact with the last particle in the chain. 

Comparing the perturbed and unperturbed cases for the heterogeneous chain (third column of Figs. 4 and 3), we see similar spatiotemporal responses with a retained snap to the secondary bistable state at unit cell 5 (as per the potential energy responses of panel b in Figs. 4 and 3, as well as the negative stiffness responses of panel c in Figs. 4 and 3). As suggested for the homogeneous nonlinear chain, a key difference between the perturbed and unperturbed heterogeneous chain is that the kinetic energy maximum in the perturbed case occurs at a much later time (third column of Fig. 4a at _t ≃_ 5 _._ 9) than in the unperturbed case (third column of Fig. 3a at _t ≃_ 2 _._ 3). While the second section of the heterogeneous chain is not bistable (as can be seen in Fig. 1b), it appears that the peak kinetic energy point in the perturbed heterogeneous case may again (like both the perturbed and unperturbed case for the homogeneous chain) stem from a wave radiated from a negative stiffness event at _t ≈_ 5 _._ 4 and unit cell 10, which can be seen from the solid vertical yellow region in the potential energy response (third column of Fig. 4b) and the white negative stiffness (third column of Fig. 4c) at that time and position. The kinetic energy maximum in the unperturbed heterogeneous chain could also be plausibly connected back to a negative stiffness event (the snapping to a finite strain of unit cell 10 at time _t ≃_ 0 _._ 8) whereafter a wave travels leftward through the chain, reflects from the impacted end and arrives at the end of the chain (see third column of Fig. 3a for the kinetic energy response where the traveling wave can be discerned and Fig. 3c for the negative stiffness even identification). The extended time window of the perturbed heterogeneous case also allows us to observe that there appears to be interface-like behavior that is occurring between the second and third sections of the heterogeneous chain, as can be seen by the small discontinuity in kinetic energy flow (third column of Fig. 4a). The observation of a discontinuity in energy transmission similar to an interface is consistent with the force-displacement curves of Fig. 1b which are plotted up to the maximum strain experienced in that spring section, and shows that the third and fourth section of springs for the heterogeneous chain (yellow and red lines) experience significantly less strain than the first two sections (blue and green lines). However, as the linear stiffnesses of both sections are the same, such an interface behavior would have to stem from the nonlinear terms ( _e.g._ , as in Refs.<sup>26–29</sup> ). 

We next summarize several key observations from the comparison between the heterogeneous and homogeneous nonlinear chains: i) The heterogeneous chain exhibits more robustness than the homogeneous chain; ii) The kinetic energy maxima in both the perturbed and unperturbed heterogeneous cases can be connected to a negative stiffness event in a non-bistable (snapthrough) spring; iii) The kinetic energy maxima in the homogeneous chain can be tied to the snapping of a bistable spring; and iv) The homogeneous chain uses bistable springs to obtain its optimal peak kinetic energy mitigation reduction. We suggest that, taken together, these four observations support the hypothesis that bistability could have a role in poorer robustness in a homogeneous chain (particularly given observation iii), 

Journal Name, [year], **[vol.]** , 1–12 | 7 



<!-- Start of picture text -->
Homogeneous Heterogeneous<br>a. Linear Bistable Heterogeneous Excluding Bistability<br>6 6 6 i 6 10°<br>5 5 5 5<br>10°<br>4 4 4 4 &<br>2 8<br>£3 3 3 3 10? =<br>es Q<br>222<br>1 =——e 1 = * 1 1 *4 ie<br>—— — — 10<br>5 10 15 20 5 10 15 20 5 10 15 20 5 10 15 20<br>b. Unit Cell Unit Cell Unit Cell Unit Cell<br>6 6 6 ye 6 10*<br>5553<br>44 4 4 .<br>2<br>22 = * 2 —— = 2 “ x<br>1 1 = 1 =, ——————-—<br>0 0 -— -= 108<br>5 10 15 20 5 10 15 20 5 10 15 20 5 10 15 20<br>c. Unit Cell Unit Cell Unit Cell Unit Cell<br>6 6 6 ye 6 0)<br>5 5 5 1 5 -0.02<br>4 4 4 4<br>2 -0.04<br>3 3 3 3 =<br>B 0.06 S<br>222<br>1 Jaa os>1 —.= 1 A 0.08<br>0 — — 0 o4<br>5 10 15 20 5 10 15 20 5 10 15 20 5 10 15 20<br>Unit Cell Unit Cell Unit Cell Unit Cell<br><!-- End of picture text -->

Fig. 4 Dynamic response of the linear, homogeneous bistable, heterogeneous, and heterogeneous-excluding-bistability chains for a perturbed impactor mass (1 _._ 01 _M_ ). (a) Spatiotemporal kinetic energy ( _KE_ ) response, normalized by the impactor energy ( _IE_ ). Star markers denote the time when the maximum _KE_ occurs at the last cell. (b) Potential energy ( _PE_ ). (c) Local stiffness ( _∂ fI /∂_ ∆ _x_ ) with coloring saturated to display only negative values. 

while providing greater peak kinetic energy reduction compared to snap-through springs. As such, we further hypothesize that it is possible that the heterogeneous chain obtains as good peak kinetic energy mitigation as the homogeneous chain by combining the mechanisms of snap-through springs (rather than bistable springs) with the interface behavior observed between the second and third sections of the chain, the latter of which may have different robustness properties than bistable and snap-through mechanisms. 

We next compare the spatiotemporal responses for the perturbed and unperturbed cases of the heterogeneous-excludingbistability chains (rightmost column of Figs. 4 and 3, respectively). We observe that the peak kinetic energy experienced at the last particle occurs earlier in the perturbed case (rightmost column Fig. 4, _t ≃_ 1 _._ 4) than the unperturbed case (rightmost column Fig. 3, _t ≃_ 3 _._ 3). In the perturbed case, the peak kinetic energy point stems from the initial pulse propagation through 

the chain (see the rightmost column of Fig. 4). While the peak kinetic energy point in the perturbed heterogeneous-excludingbistability case is most directly connectable to the initial pulse traversing the chain, we note that there are also negative stiffness regions activated in the second section of the chain (see the rightmost column of Fig. 4c). Further, the third section of the heterogeneous-excluding-bistable chain, as can be seen by the yellow curve in Fig. 1b, is monotonically increasing but exhibits a near-snap-through-like plateau. In contrast to the perturbed case, in the unperturbed case, the peak kinetic energy point (rightmost column of panels a and b in Fig. 3) appears to coincide with the main pulse completing a transit cycle forward, back, and forth again through the entire chain. It is also plausible that this peak kinetic energy point in the unperturbed heterogeneous-excludingbistability chain can be tied to an event occurring at unit cell 15 and time _t ≃_ 1 _._ 8. As noted, unit cell 15 of the heterogeneousexcluding-bistability chain is of the near-snap-through plateau 

8 | Journal Name, [year], **[vol.]** , 1–12 

type, which would allow the spring to stay in a more compressed state (the higher displacement side of the plateau) with minimal forcing. The presence of this plateau spring is consistent with the vertical yellow region in the potential energy response (see the rightmost column of Fig. 4b) for unit cell 15 of the heterogeneous-excluding-bistability chain from time _t ≃_ 0 _._ 9 to 1 _._ 8. At time _t ≃_ 1 _._ 8 the spring relaxes and emits a leftward propagating wave which reflects off the impacted end of the chain and travels rightward again to arrive near the point of peak kinetic energy. Comparing the perturbed and unperturbed cases of the heterogeneous-excluding-bistability and the heterogeneous chains, we were unable to clearly identify an underlying mechanism enabling the superior robustness of the heterogeneousexcluding-bistability compared to the heterogeneous chains. In all four cases (perturbed and unperturbed of the heterogeneous and heterogeneous-excluding-bistability chains), the spatiotemporal point of peak kinetic energy can be at least plausibly connected to a snap-through spring passing through a negative stiffness state or sustained straining of plateau springs. In other words, whether the bistable springs were present or not, the peak kinetic energy point could be tied to the action of a snap through spring rather than a bistable one. In the both the perturbed and unperturbed heterogeneous chains, where bistable springs were present in the first section of the chain (see the blue curves in Fig. 1b), there was no clear propagating-wave-tie between any action of these bistable springs and the point of peak kinetic energy. 

In the SI-5 we consider a further case, where instead of perturbing the impactor condition, we perturbed the nonlinear coefficients for the three chains for cases with performance close to the means of the 2% noise level for each chain, shown in Fig. 1c. The perturbed coefficients and corresponding _KE_ ratios can be found in SI-6. In the case with the perturbed nonlinear coefficients, we also see that the peak kinetic energy point is spatiotemporally proximal to snapping of a bistable spring for the homogeneous chain (though the chain location does not stay snapped to a finite strain; see second column of panel b in Fig. S3 near unit cell 15 and _t ≃_ 1 _._ 2). One particularly interesting point, is that in the perturbed case for the heterogeneous chain, the peak kinetic energy point can be tied back to the unsnapping of one of the bistable springs (spring 5 at _t ≃_ 2 _._ 8) in the first section of the chain which was previously snapped to a finite strain for a prolonged duration (see Fig. S3 third column of panel b from _t ≈_ 0 _._ 5 to _t ≈_ 2 _._ 8), wherein the wave radiates leftwards from the unsnapping event reflects off the impacted boundary and propagates back to the right edge. 

kinetic energy transmission, on average, than the set of homogeneous chains. Second, noting that (in agreement with Ref.<sup>30</sup> ) the best performing constitutive responses within our design domain for the homogeneous chain are bistable: the set of heterogeneous chains excluding bistability retains the best performance. 

The results raise questions about the role of disorder manifesting in constitutive nonlinearity and its connection to system robustness. There are several natural next steps addressing such questions. The first would be to increase sample sizes for the perturbed chains, _e.g._ Fig. 1d, and study chains with more types of springs, whether through longer chains with more unit cells or through chains with the same number of unit cells but with more sections of different spring types. An particular advantage of having more sections of different spring types, is that it may allow identification of optimal chain configurations which leverage disorder-based mechanisms via metrics such as power-law localization ( _e.g._ , Refs.<sup>27–29</sup> ). Indeed using metrics from the study of disordered systems, such as participation ratio<sup>33</sup> , may yield further insights into the analysis of such heterogeneous systems. 

Finally, our results also raise questions concerning the link between bistability (versus snap-through or plateau-like constitutive nonlinearities) and system robustness. While the heterogeneousexcluding-bistability chain exhibited better robustness than both the heterogeneous and homogeneous chains, the underlying mechanism driving such robustness remain unclear. One potential future avenue to address this gap would be to conduct a statistical study of when snapping or unsnapping of bistable springs is spatiotemporally related to peak transmitted kinetic energy points. 

## 4 Conclusion 

In this work, we computationally studied a chain of uniform masses connected by uniform linear dampers in parallel with springs having cubic-polynomial force-displacement laws, wherein the linear stiffness remains fixed, but higher order terms can vary throughout the chain. Our study of the three sets of perturbed chains (homogeneous, heterogeneous, and heterogeneous-excluding-bistability) yields two key outcomes. First, both sets of heterogeneous chains retain better (lower) peak 

Journal Name, [year], **[vol.]** , 1–12 | 9 

## 5 Methods 

### **5.1 Discrete Element Modeling** 

The rigid impactor with a prescribed point mass _M_ and an initial velocity _V_ strikes the material chain, where the interaction is mediated by a Hertzian-like contact spring positioned between the impactor and the first unit cell (shown in Fig. 1a). The contact spring features a nonlinear force-displacement relationship in compression with zero stiffness in tension, allowing the impactor to freely bounce. We describe the dimensionless force via _fH_ = _Cimp_ � _ximp − x_ 1�3+ _/_ 2<sup>,where[]+indicatesthepositive(com-</sup> pressive) part of the deformation. We select the dimensionless coefficient _Cimp_ = 1 _._ 2 _×_ 10<sup>4</sup> . Using Eq. (1), we write the full set of equations of motion as follows: 



## 6 New Concepts 

Nonlinearity is known to be a useful material design tool for impact mitigation, but sensitivity to small changes in material properties or impact conditions can limit the usefulness of a design in application. We demonstrate that, when optimizing the nonlinear terms of a material’s elastic constitutive response to achieve minimum peak transmitted kinetic energy, allowing heterogeneity confers greater robustness to perturbations without optimizing for it. We also find that allowing heterogeneity and excluding bistable nonlinearities increases the robustness even further. Our findings raise questions concerning the relationship between heterogeneity, bistable nonlinear constitutive responses, and system robustness. 

## 7 Conflicts of interest 

The authors declare the following competing financial interest(s): N.B. is a founder and holds equity positions in Euler Materials. 

## 8 Data availability 

## 9 Acknowledgments 

This work was supported by the Department of Energy, National Nuclear Security Administration (DOE/NNSA) PSAAP IV under Award Number DE-NA0004262. M.B. acknowledges support from the National Science Foundation Graduate Research Fellowship Program under Grant No. DGE-2038238. 

These equations are numerically integrated using an explicit Runge-Kutta solver (ode45 in MATLAB). The integration timestep was selected adaptively by ode45 with the relative and absolute tolerances set to 10<sup>_−_10</sup> or tighter. The solution was evaluated on a uniform output grid with spacing ∆ _tout_ = 1 _/_ (100 _f_ 0), where _f_ 0 = 21 _π_ ~~�~~ _M_ <u>10</u><sup>.</sup> Each simulation was conducted over the nondimensional time interval 0 _≤ tsim ≤ T_ with _T_ = 25 _/ f_ 0. 

### **5.2 Inverse design of the nonlinear constitutive law** 

Design problem is to identify the nonlinear spring coefficients ( _c_ 2 _, c_ 3) to minimize a chosen dynamic performance metric, under a specified impact condition. The objective function is chosen as the normalized peak kinetic energy at the end of the chain, _J_ = max( _KEnon_ ) _/_ max( _KElin_ ), 



where the positive strain energy constraint for the bistable springs is _W ≥_ 0 = _⇒_ (2 _/_ 9) _c_<sup>2</sup> 2<sup>_< c_3.Toexcludethebistabilityfromthe</sup> design space, the constraint can be replaced by _c_<sup>2</sup> 2<sup>_≤_4</sup><sup>_c_3.SeeSI-</sup> 2 and SI-3 for derivations and further discussion on polynomial categories. 

The design space is set to _c_ 2 _∈_ [ _−_ 120 _,_ 0] and _c_ 3 _∈_ [0 _,_ 4000]. The upper bounds are chosen in accordance with the impactor conditions and resulting strains, thus allowing bistability in the relevant deformation ranges. The problem is solved using a gradientbased optimizer, fmincon in MATLAB, where the gradients are estimated using finite differences and varied initial conditions are studied to investigate a range of solutions. 

10 | Journal Name, [year], **[vol.]** , 1–12 

## Notes and references 

- 1 Tony M Keaveny and Wilson C Hayes. A 20-year perspective on the mechanical properties of trabecular bone. 1993. 

- 2 Ulrike GK Wegst, Hao Bai, Eduardo Saiz, Antoni P Tomsia, and Robert O Ritchie. Bioinspired structural materials. _Nature materials_ , 14(1):23–36, 2015. 

- 3 CC Hays, CP Kim, and William L Johnson. Microstructure controlled shear band pattern formation and enhanced plasticity of bulk metallic glasses containing in situ formed ductile phase dendrite dispersions. _Physical Review Letters_ , 84(13):2901, 2000. 

- 4 Sahar Choukir, Nirosh Manohara, and Chandra Veer Singh. Disorder unlocks the strength-toughness trade-off in metamaterials. _Applied Materials Today_ , 42:102579, 2025. 

- 5 Zhenyang Gao, Xiaolin Zhang, Yi Wu, Minh-Son Pham, Yang Lu, Cunjuan Xia, Haowei Wang, and Hongze Wang. Damage-programmable design of metamaterials achieving crack-resisting mechanisms seen in nature. _Nature Communications_ , 15(1):7373, 2024. 

- 6 Sage Fulco, Michal K Budzik, Hongyi Xiao, Douglas J Durian, and Kevin T Turner. Disorder enhances the fracture toughness of 2d mechanical metamaterials. _PNAS nexus_ , 4(2):pgaf023, 2025. 

- 7 Joanna McKittrick, P-Y Chen, Luca Tombolato, Ekaterina E Novitskaya, Michael W Trim, Gustavo A Hirata, EA Olevsky, Mark Fredrick Horstemeyer, and Marc André Meyers. Energy absorbent natural materials and bioinspired design strategies: a review. _Materials Science and Engineering: C_ , 30(3):331– 342, 2010. 

- 8 Wei Huang, Nicholas A Yaraghi, Wen Yang, Alexis VelazquezOlivera, Zezhou Li, Robert O Ritchie, David Kisailus, Susan M Stover, and Joanna McKittrick. A natural energy absorbent polymer composite: The equine hoof wall. _Acta biomaterialia_ , 90:267–277, 2019. 

- 9 Aaron Drake, Tammy L Haut Donahue, Mitchel Stansloski, Karen Fox, Benjamin B Wheatley, and Seth W Donahue. Horn and horn core trabecular bone of bighorn sheep rams absorbs impact energy and reduces brain cavity accelerations during high impact ramming of the skull. _Acta biomaterialia_ , 44:41– 50, 2016. 

- 10 Shashank Gupta and Reza Moini. Tough cortical boneinspired tubular architected cement-based material with disorder. _Advanced Materials_ , 36(52):2313904, 2024. 

- 11 Antonio Coluccia, Guillaume Meyer, Stefania Liseni, Christian Mittelstedt, and Giorgio De Pasquale. Functionally graded lattice structures for energy absorption: Numerical analysis and experimental validation. _Composite Structures_ , 360:119013, 2025. 

- 12 Nobphadon Suksangpanya, Nicholas A Yaraghi, R Byron Pipes, David Kisailus, and Pablo Zavattieri. Crack twisting and toughening strategies in bouligand architectures. _International Journal of Solids and Structures_ , 150:83–106, 2018. 

- 13 Yuchen Zhang, Wei Huang, Cheryl Hayashi, John Gatesy, and Joanna McKittrick. Microstructure and mechanical properties 

of different keratinous horns. _Journal of the Royal Society Interface_ , 15(143), 2018. 

- 14 Mahmoud I. Hussein, Michael J. Leamy, and Massimo Ruzzene. Dynamics of phononic materials and structures: Historical origins, recent progress, and future outlook. _Applied Mechanics Reviews_ , 66(4):040802, 2014. 

- 15 NA Alderete, S Sandeep, S Raetz, M Asgari, M Abi Ghanem, and HD Espinosa. Does the mantis shrimp pack a phononic shield? _Science_ , 387(6734):659–666, 2025. 

- 16 Ganesh U. Patil and Kathryn H. Matlack. Review of exploiting nonlinearity in phononic materials to enable nonlinear wave responses. _Acta Mechanica_ , 233(1):1–46, January 2022. 

- 17 Mikhail Lapine, Ilya V. Shadrivov, and Yuri S. Kivshar. Colloquium: Nonlinear metamaterials. _Reviews of Modern Physics_ , 86:1093–1123, 2014. 

- 18 R.W. Boyd. _Nonlinear Optics_ . Academic Press, 1992. 

- 19 Vitali F. Nesterenko. _Dynamics of Heterogeneous Materials_ . Springer, New York, 2001. 

- 20 Steven H Strogatz. _Nonlinear dynamics and chaos: with applications to physics, biology, chemistry, and engineering_ . CRC press, 2024. 

- 21 Ryan Fancher, Ian Frankel, K. C. H. Chin, Michael Abi Ghanem, Brianna MacNider, Laura S. Shannahan, James F. Berry, Müge Fermen-Coker, Andrew J. Boydston, and Nicholas Boechler. Dependence of the kinetic energy absorption capacity of bistable mechanical metamaterials on impactor mass and velocity. _Extreme Mechanics Letters_ , 63:102044, 2023. 

- 22 P. W. Anderson. Absence of diffusion in certain random lattices. _Physical Review_ , 109(5):1492–1505, 1958. 

- 23 T V Laptyeva, M V Ivanchenko, and S Flach. Nonlinear lattice waves in heterogeneous media. _Journal of Physics A: Mathematical and Theoretical_ , 47(49):493001, November 2014. Publisher: IOP Publishing. 

- 24 R Sainidou, N Stefanou, and A Modinos. Widening of phononic transmission gaps via anderson localization. _Physical review letters_ , 94(20):205503, 2005. 

- 25 Xiyue An, Fangfang Sun, Peishi Yu, Hualin Fan, Shiping He, and Daining Fang. Negative effective mass density of onedimensional hierarchical metacomposite. _Journal of Applied Mechanics_ , 82(3):031002, 2015. 

- 26 Viola Folli, Katia Gallo, and Claudio Conti. Purely nonlinear disorder-induced localizations and their parametric amplification. _Optics Letters_ , 38(24):5276–5279, 2013. 

- 27 Yonatan Sharabi, Hanan Herzig Sheinfux, Yoav Sagi, Gadi Eisenstein, and Mordechai Segev. Self-induced diffusion in disordered nonlinear photonic media. _Physical Review Letters_ , 121(23):233901, 2018. 

- 28 Alexander Iomin. From power law to anderson localization in nonlinear schrödinger equation with nonlinear randomness. _Physical Review E_ , 100(5):052123, 2019. 

- 29 Ba Phi Nguyen and Kihong Kim. Power-law localization in one-dimensional systems with nonlinear disorder under fixed input conditions. _Physica D: Nonlinear Phenomena_ , 

Journal Name, [year], **[vol.]** , 1–12 | 11 

469:134342, 2024. 

- 30 Brianna MacNider, Haning Xiu, Caglar Tamur, Kai Qian, Ian Frankel, Maya Brandy, Hyunsun Alicia Kim, and Nicholas Boechler. Customizable wave tailoring nonlinear materials enabled by bilevel inverse design. _Nature Communications_ , 16(1):3425, 2025. 

- 31 Haning Xiu, Ryan Fancher, Ian Frankel, Patrick Ziemke, Müge Fermen-Coker, Matthew Begley, and Nicholas Boechler. Minimizing finite viscosity enhances relative kinetic energy absorption in bistable mechanical metamaterials but only with sufficiently fine discretization: a nonlinear dynamical size effect. _Journal of the Mechanics and Physics of Solids_ , 200:106105, 2025. 

- 32 Sicong Shan, Sung H. Kang, Jordan R. Raney, Pai Wang, Lichen Fang, Francisco Candido, Jennifer A. Lewis, and Katia Bertoldi. Multistable architected materials for trapping elastic strain energy. _Advanced Materials_ , 27(29):4296–4301, 2015. 

- 33 RJ Bell and Paul Dean. Atomic vibrations in vitreous silica. _Discussions of the Faraday society_ , 50:55–61, 1970. 

12 | Journal Name, [year], **[vol.]** , 1–12 

