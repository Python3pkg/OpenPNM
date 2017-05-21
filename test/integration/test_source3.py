import OpenPNM
import scipy as sp
print(('-----> Using OpenPNM version: '+OpenPNM.__version__))
pn = OpenPNM.Network.Cubic(shape=[10,10,40],spacing=0.0001)
pn.add_boundaries()

Ps = pn.pores('boundary',mode='not')
Ts = pn.find_neighbor_throats(pores=Ps,mode='intersection',flatten=True)
geom = OpenPNM.Geometry.Toray090(network=pn,pores=Ps,throats=Ts)

Ps = pn.pores('boundary')
Ts = pn.find_neighbor_throats(pores=Ps,mode='not_intersection')
boun = OpenPNM.Geometry.Boundary(network=pn,pores=Ps,throats=Ts)

air = OpenPNM.Phases.Air(network=pn)

#---------------------------------------------------------------------------------------------
Ps = pn.pores()
Ts = pn.throats()
phys_air = OpenPNM.Physics.Standard(network=pn,phase=air,pores=Ps,throats=Ts)
#Add some additional models to phys_air
phys_air['pore.item1'] = 0.5e-13
phys_air['pore.item2'] = 1.5
phys_air['pore.item3'] = 2.5e-14
phys_air['pore.item4'] = 0.9e-13
phys_air['pore.item5'] = -4e-14

phys_air.add_model(model=OpenPNM.Physics.models.generic_source_term.power_law,
                   propname='pore.blah1',
                   A1='pore.item1',
                   A2='pore.item2',
                   A3='pore.item3')
phys_air.add_model(model=OpenPNM.Physics.models.generic_source_term.linear,
                   propname='pore.blah2',
                   A1='pore.item4',
                   A2='pore.item5')
#------------------------------------------------------------------------------
'''Perform Fickian Diffusion'''
#------------------------------------------------------------------------------
alg = OpenPNM.Algorithms.FickianDiffusion(network=pn,phase=air)
# Assign Dirichlet boundary conditions to top and bottom surface pores
BC1_pores = pn.pores('right_boundary')
alg.set_boundary_conditions(bctype='Dirichlet', bcvalue=0.6, pores=BC1_pores)
BC2_pores = pn.pores('left_boundary')
alg.set_boundary_conditions(bctype='Neumann', bcvalue=0.2e-13, pores=BC2_pores)

alg.set_source_term(source_name='pore.blah1',pores=sp.r_[500:700],tol=1e-9)
alg.set_source_term(source_name='pore.blah2',pores=sp.r_[800:900],maxiter=0)

alg.setup()
alg.solve(iterative_solver='cg',tol=1e-20)
alg.return_results()
print('--------------------------------------------------------------')
try:
    print(('steps: ',alg._steps))
    print(('tol_reached: ',alg._tol_reached))
except: pass
print('--------------------------------------------------------------')
print(('reaction from the physics for pores [500:700]:',\
        sp.sum(0.5e-13*air['pore.mole_fraction'][sp.r_[500:700]]**1.5+2.5e-14)))
print(('rate from the physics for pores [500:700]:',\
        alg.rate(sp.r_[500:700])[0]))
print('--------------------------------------------------------------')
print(('reaction from the physics for pores [800:900]:',\
        sp.sum(0.9e-13*air['pore.mole_fraction'][sp.r_[800:900]]-4e-14)))
print(('rate from the physics for pores [800:900]:',\
        alg.rate(sp.r_[800:900])[0]))

