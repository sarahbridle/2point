#Tests to make sure library works for cluster counts
import twopoint
import numpy as np

def test_cluster():

    #Let's imagine we have two lens redshift bins and two source redshift bins
    #Each lens redshift bins has three richness bins.
    #We need to generate the lensing profiles and counts.
    #Are measurements should iterate first source bin, then richness bin, then 
    #cluster redshit bin
    #Each cluster redshift,richness bin has a boost factor two...
    n_zbin_cluster = 2
    n_lambda_bin = 3
    n_cluster_bin = n_zbin_cluster * n_lambda_bin
    n_source_bin = 2

    #use same thetas for all gamma_t
    n_theta, log_theta_min, log_theta_max = 10, np.log(2.5), np.log(25.)
    log_theta_arcmin_lims = np.linspace(log_theta_min, log_theta_max, n_theta+1)
    log_theta_arcmin_mids = 0.5*( log_theta_arcmin_lims[:-1] + log_theta_arcmin_lims[1:] )
    theta_arcmin = np.exp(log_theta_arcmin_mids)

    #Also make some fake n(z) extensions
    z_lims = np.linspace(0.,2.,200)
    z_lo,z_hi = z_lims[:-1], z_lims[1:]
    z_mid = 0.5 * ( z_lo + z_hi )

    #Make some fake lens n(z)s (just Gaussians)
    cluster_z_means = [ 0.1, 0.1, 0.1, 0.3, 0.3, 0.3 ]
    cluster_sigmas = [ 0.03 ] * n_cluster_bin
    cluster_nzs = []
    k=0
    for i in range(n_zbin_cluster):
        for j in range(n_lambda_bin):    
            mu,sigma = cluster_z_means[k], cluster_sigmas[k]
            cluster_nzs.append( np.exp(-( (z_mid-mu)**2 / ( 2.0 * sigma**2 ) ) ) )
    #make number density object
    nz_cluster = twopoint.NumberDensity( 'nz_cluster', z_lo, z_mid, z_hi, cluster_nzs )

    #And sources
    source_z_means = [ 0.5, 0.9 ]
    source_sigmas = [0.2, 0.3]
    source_nzs = []
    for i in range(n_source_bin):
        mu,sigma = source_z_means[k], source_sigmas[k]
        source_nzs.append( np.exp(-( (z_mid-mu)**2 / ( 2.0 * sigma**2 ) ) ) )
    #make number density object
    nz_source = twopoint.NumberDensity( 'nz_source', z_lo, z_mid, z_hi, source_nzs )

    #make some counts
    count_vals = np.random.random(n_lambda_bin * n_zbin_cluster)
    counts = twopoint.CountMeasurement( 'cluster_counts', 'nz_cluster', count_vals)

    #make some lensing profiles and counts
    #total length of gamma_t measurements is n_theta * n_cluster_bin * n_source_bin
    gamma_t_length = n_theta * n_cluster_bin * n_source_bin
    gammat_values = np.zeros(gamma_t_length, dtype=float)
    bin1 = np.zeros(gamma_t_length, dtype=int)
    bin2 = np.zeros_like(bin1)
    angular_bin = np.zeros_like(bin1)
    angle = np.zeros_like(gammat_values)
    gammat_base = 0.03/theta_arcmin 
    dv_start=0
    #loop through cluster z bins
    for zcl_ind in range(n_zbin_cluster):
        for lambda_ind in range(n_lambda_bin):
            #cluster bin index is a combination of zcl_ind and lambda_ind
            cl_ind = zcl_ind * n_lambda_bin + lambda_ind + 1
            for zs_ind in range(1, n_source_bin + 1):
                bin_pair_inds = np.arange(dv_start, dv_start + n_theta)
                gammat_amp = zcl_ind * lambda_ind * zs_ind #Give bin combination its own amplitude
                gammat_values[bin_pair_inds] = gammat_base * gammat_amp
                bin1[bin_pair_inds] = zcl_ind
                bin2[bin_pair_inds] = zs_ind
                angular_bin[bin_pair_inds] = np.arange(n_theta)
                angle[bin_pair_inds] = theta_arcmin

    #Now make SpectrumMeasurement object
    gamma_t = twopoint.SpectrumMeasurement( 'cluster_gamma_t', (bin1, bin2),
              (twopoint.Types.galaxy_position_real, twopoint.Types.galaxy_shear_plus_real),
              [ 'nz_cluster', 'nz_source' ], 'SAMPLE', angular_bin, gammat_values, angle = angle,
              angle_unit = 'arcmin' )

    # make twopoint object
    twopoint_file = twopoint.TwoPointFile( [gamma_t, counts], [ nz_cluster, nz_source ],
    None, None )
    #save to fits
    twopoint_file.to_fits('test_cluster.fits')                   



if __name__=="__main__":
    test_cluster()

