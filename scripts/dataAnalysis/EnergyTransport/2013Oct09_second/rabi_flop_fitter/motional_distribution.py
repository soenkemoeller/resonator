import numpy as np
from scipy.special.orthogonal import eval_genlaguerre as laguerre
from scipy.misc import factorial
import mpmath as mp

#see Michael Ramm writeup on 'Displaced Coherent States' and references therein.

class motional_distribution(object):
    
    @classmethod
    def thermal(cls, nbar, dimension):
        '''
        returns a thermal distribution of occupational numbers of the required dimensions
        @param nbar: temperature
        @param dimension: number of required entries 
        '''
        return np.fromfunction(lambda n: cls._thermal(nbar, n), (dimension,))
    
    @classmethod
    def _thermal(cls, nbar, n):
        #level population probability for a given nbar, see Leibfried 2003 (57)
        return 1./ (nbar + 1.0) * (nbar / (nbar + 1.0))**n
    
    @classmethod
    def displaced_thermal(cls, alpha, nbar, dimension):
        '''
        outputs occupational numbers for a displaced thermal distribution
        @param alpha: coherent displacement
        @param nbar: temperature of the thermal distribution
        @param dimension: required number of modes   
        '''
        return np.fromfunction(lambda n: cls._displaced_thermal(alpha, nbar, n), (dimension,))
    
    @classmethod
    def _displaced_thermal(cls, alpha, nbar, n):
        '''
        returns the motional state distribution with the displacement alpha, motional temperature nbar for the state n
        '''
        #this is needed because for some inputs (larrge n or small nbar, this term is 0 while the laguerre term is infinite. their product is zero but beyond the floating point precision
        try:
            old_settings = np.seterr(invalid='raise')
            populations = 1./ (nbar + 1.0) * (nbar / (nbar + 1.0))**n * laguerre(n, 0 , -alpha**2 / ( nbar * (nbar + 1.0))) * np.exp( -alpha**2 / (nbar + 1.0))
        except FloatingPointError:
            np.seterr(**old_settings)
            def fib():
                a, b = 0, 1
                while 1:
                    yield a
                    a, b = b, a + b
            import time
            t1 = time.time()
            print 'precise calculation required', alpha, nbar
            expon_term = mp.exp(-alpha**2 / (nbar + 1.0))
            populations = [float(mp.fprod((mp.power(nbar / (nbar + 1.0), k), mp.laguerre(k, 0, -alpha**2 / ( nbar * (nbar + 1.0))), expon))) for k in n]
            populations = np.array(populations) / (nbar + 1)
            print time.time() - t1 
            print 'done'
        return populations
    
    @classmethod
    def test_displaced_thermal(cls):
        '''
        compares the result of the computed distribution with the same result obtained through qutip
        '''
        alpha = np.sqrt(5) * np.random.ranf()
        nbar = 5 * np.random.ranf()
        test_entries = 100
        computed = cls.displaced_thermal(alpha, nbar, test_entries)
        from qutip import thermal_dm, displace
        thermal_dm = thermal_dm(test_entries, nbar, method = 'analytic')
        displace_operator = displace(test_entries, alpha)
        displaced_dm = displace_operator * thermal_dm * displace_operator.dag()
        qutip_result = displaced_dm.diag()
        return np.allclose(qutip_result, computed)
    
    @classmethod
    def test_thermal_distribution(cls):
        '''
        compares the result of the computed distribution with the same result obtained through qutip
        '''
        nbar = 3 * np.random.ranf()
        test_entries = 10
        computed = cls.thermal(nbar, test_entries)
        from qutip import thermal_dm
        thermal_qutip = thermal_dm(test_entries, nbar, method = 'analytic').diag()
        return np.allclose(thermal_qutip, computed)
    
if __name__ == '__main__':
    
    md = motional_distribution
    
    def plot_displaced():
        from matplotlib import pyplot
        hilbert_space_dimension = 5000
        displacement_alpha = 40
        for nbar,color in [(3, 'k'), (0.1, 'b'), (10, 'g'), (20, 'r')]:
            distribution = md.displaced_thermal(displacement_alpha, nbar, hilbert_space_dimension)
            print distribution.sum()
            pyplot.plot(distribution, 'x', color = color, label = 'thermal nbar = {}'.format(nbar))
        
#         pyplot.title('Init temperature 3nbar', fontsize = 16)
        pyplot.suptitle('Displaced Thermal States', fontsize = 20)
        pyplot.legend()
        pyplot.show()
    
#     print md.test_thermal_distribution()
#     print md.test_displaced_thermal()
    plot_displaced()