# -*- coding: utf-8 -*-

import unittest
import numpy

"""
*******************************************************************************


    Tests of the quantarhei.Molecule class


*******************************************************************************
"""

from quantarhei import Molecule
from quantarhei import Mode
from quantarhei import CorrelationFunction
from quantarhei import TimeAxis
from quantarhei import eigenbasis_of

from quantarhei.core.units import kB_intK

class TestMolecule(unittest.TestCase):
    """Tests for the Manager class
    
    
    """
    
    def setUp(self):
        self.en = [0.0, 1.0, 2.0]
        self.m = Molecule(name="Molecule",elenergies=self.en)     
    
    def test_Molecule_instantiation(self):
        """Testing Molecule instantiation
        
        
        """

        
        self.assertEqual(self.m.name,"Molecule")
        for i in range(2):
            self.assertEqual(self.m.elenergies[i],self.en[i])
            
            
    def test_get_Hamiltonian(self):
        """Testing that Molecule returns correct Hamiltonian 
        
        """
        
        H = self.m.get_Hamiltonian()

        h = numpy.zeros((3,3),dtype=numpy.float)
        h[1,1] = 1.0
        h[2,2] = 2.0
        
        self.assertTrue(numpy.allclose(H.data,h))
        
        
class TestMoleculeVibrations(unittest.TestCase):
    
    def setUp(self):
        
        en = [0.0, 1.0]
        self.m = Molecule(name="Molecule",elenergies=en)

        mod1 = Mode(frequency=0.1)
        self.m.add_Mode(mod1)
        mod1.set_nmax(0,3)
        mod1.set_nmax(1,3)
    
        en2 = [0.0,0.1,0.1]
        self.m2 = Molecule(name="AdMolecule",elenergies=en2)    
        self.m2.set_adiabatic_coupling(1,2,0.02)
        mod2 = Mode(frequency=0.01)
        self.m2.add_Mode(mod2)
        mod2.set_nmax(0,3)
        mod2.set_nmax(1,3)
        mod2.set_nmax(2,3)
        

    def test_molecule_with_vibrations_1(self):
        """Testing hamiltonian of a two-level molecule with one mode
        
        """
        
        H1 = self.m.get_Hamiltonian()
        H1expected = numpy.diag([0.0, 0.1, 0.2, 1.0, 1.1, 1.2])        
        self.assertTrue(numpy.allclose(H1expected,H1.data))
        
        mod1 = self.m.get_Mode(0)
        mod1.set_nmax(1,2)
        H2 = self.m.get_Hamiltonian()
        H2expected = numpy.diag([0.0, 0.1, 0.2, 1.0, 1.1])        
        self.assertTrue(numpy.allclose(H2expected,H2.data))    
        
        
    def test_thermal_density_matrix_0_temp(self):
        """Thermal density matrix: molecule with one mode, zero temperature
        
        """
        rho_eq = self.m.get_thermal_ReducedDensityMatrix()

        # Check if the matrix is diagonal        
        dat = rho_eq.data.copy()
        for i in range(dat.shape[0]):
            dat[i,i] = 0.0
        zer = numpy.zeros(dat.shape,dtype=numpy.float)
        self.assertTrue(numpy.allclose(dat,zer))
        
        # Check if diagonal is a thermal population
        pop = numpy.zeros(dat.shape[0])
        # get temperature from the molecule
        T = self.m.get_temperature()
        self.assertEquals(T,0.0)        
        
        # get density matrix
        rho = self.m.get_thermal_ReducedDensityMatrix()
        rpop = rho.get_populations()
        
        if numpy.abs(T) < 1.0e-10:
            pop[0] = 1.0
            
        else:
            # thermal populations
            pass

        self.assertTrue(numpy.allclose(pop,rpop))
        
        
    def test_thermal_density_matrix_finite_temp(self):
        """Thermal density matrix: molecule with one mode, finite temperature
        
        """
        
        timeAxis = TimeAxis(0.0,1000,1.0)
        params = {"ftype":"OverdampedBrownian",
                  "T":300,
                  "reorg":30,
                  "cortime":100}
        cfcion = CorrelationFunction(timeAxis,params)
        self.m.set_egcf((0,1),cfcion)
        
        rho_eq = self.m.get_thermal_ReducedDensityMatrix()

        # Check if the matrix is diagonal        
        dat = rho_eq.data.copy()
        for i in range(dat.shape[0]):
            dat[i,i] = 0.0
        zer = numpy.zeros(dat.shape,dtype=numpy.float)
        self.assertTrue(numpy.allclose(dat,zer))
        
        # Check if diagonal is a thermal population
        pop = numpy.zeros(dat.shape[0])
        # get temperature from the molecule
        T = self.m.get_temperature()
        self.assertTrue(T==300.0)

        
        # get density matrix
        rpop = rho_eq.get_populations()
        
        # get Hamiltonian
        H = self.m.get_Hamiltonian()       

        if numpy.abs(T) < 1.0e-10:
            pop[0] = 1.0
            
        else:
            # thermal populations
            psum = 0.0
            for n in range(pop.shape[0]):
                pop[n] = numpy.exp(-H.data[n,n]/(kB_intK*T))
                psum += pop[n]
            pop *= 1.0/psum
            
        self.assertTrue(numpy.allclose(pop,rpop))
        
        
    def test_thermal_density_matrix_finite_temp_nondiag(self):
        """Thermal density matrix: finite temperature, non-diagonal Hamiltonian
        
        """
        
        timeAxis = TimeAxis(0.0,1000,1.0)
        params = {"ftype":"OverdampedBrownian",
                  "T":300.0,
                  "reorg":30,
                  "cortime":100}
        cfcion = CorrelationFunction(timeAxis,params)
        self.m2.set_egcf((0,1),cfcion)
        self.m2.set_egcf((0,2),cfcion)
        
        rho_eq = self.m2.get_thermal_ReducedDensityMatrix()

        pop = numpy.zeros(rho_eq._data.shape[0])
        # get temperature from the molecule
        T = self.m2.get_temperature()
        self.assertTrue(numpy.abs(T-300.0)<1.0e-10)
 
        # get Hamiltonian
        H = self.m2.get_Hamiltonian() 
        
        with eigenbasis_of(H):
            # get density matrix

            rpop = rho_eq.get_populations()


            if numpy.abs(T) < 1.0e-10:
                pop[0] = 1.0
            
            else:
                # thermal populations
                psum = 0.0
                for n in range(pop.shape[0]):
                    pop[n] = numpy.exp(-H.data[n,n]/(kB_intK*T))
                    psum += pop[n]
                pop *= 1.0/psum

        
        self.assertTrue(numpy.allclose(pop,rpop))
        
        
        
                
        