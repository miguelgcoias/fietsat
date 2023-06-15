from datetime import datetime
from json import load
from pathlib import Path
from sys import argv

from pysat.card import CardEnc
from pysat.formula import IDPool
from pysat.solvers import Solver


class Driver:
  
  def __init__(self, id, name, exp, routes):
    self.id, self.name, self.exp, self.routes = id, name, exp, routes


class Route:

  def __init__(self, id, start, end, drivers):
    self.id, self.start, self.end, self.drivers = id, start, end, drivers


class FietSAT:

  def __init__(self, drivers_fp: str | Path, routes_fp: str | Path):
    '''FietSAT constructor.

    Arguments:
    - drivers_fp: JSON drivers file path;
    - routes_fp: JSON routes file path.
    
    Observations:
    - self.syms is a data structure that assigns objects to unique integer IDs.
    '''
    self.drivers_info, self.routes_info = FietSAT.parse(drivers_fp, routes_fp)
    self.syms = IDPool()
    self.solver = Solver('g3')
    self.problem = []
    self.model = []

  @staticmethod
  def parse(drivers_fp: str | Path, routes_fp: str | Path) -> tuple[dict[int, Driver], dict[int, Route]]:
    '''Imports and parses drivers and routes data from JSON files.

    Arguments:
    - drivers_fp: JSON drivers file path;
    - routes_fp: JSON routes file path.
    
    Returns:
    - drivers_info: dict[int, Driver]
      map of driver IDs to driver objects containing the ID, name and the
      experience level of a driver, and the list of routes the driver may be
      allocated to;
    - routes_info: dict[int, Route]
      map of route IDs to route objects containing the ID, start location and
      end location of a route. Additionally, a list of drivers the route may
      be allocated to is created.'''
    # Importing drivers data
    with open(drivers_fp, encoding='utf8') as drivers_obj:
      drivers_info = {driver_obj['id']: Driver(driver_obj['id'],
                                               driver_obj['name'],
                                               driver_obj['exp'],
                                               driver_obj['routes'])
                      for driver_obj in load(drivers_obj)}
    
    # Importing routes data
    with open(routes_fp, encoding='utf8') as routes_obj:
      routes_info = {route_obj['id']: Route(route_obj['id'],
                                            route_obj['start'],
                                            route_obj['end'],
                                            [])
                     for route_obj in load(routes_obj)}
    
    # Filling route drivers lists
    for did in drivers_info:
      for rid in drivers_info[did].routes:
        routes_info[rid].drivers.append(did)
      
    return drivers_info, routes_info
  
  def drivers(self) -> list[int]:
    '''Returns all drivers.'''
    return list(self.drivers_info)
  
  def drivers_of(self, rid: int) -> list[int]:
    '''Returns drivers which may be allocated to the route with ID rid.'''
    return self.routes_info[rid].drivers
  
  def driver_info(self, did) -> Driver:
    '''Returns the driver object with ID did.'''
    return self.drivers_info[did]
  
  def routes(self) -> list[int]:
    '''Returns all routes.'''
    return list(self.routes_info)
  
  def routes_of(self, did: int) -> list[int]:
    '''Returns routes which may be allocated to the driver with ID did.'''
    return self.drivers_info[did].routes

  def route_info(self, rid: int) -> Route:
    '''Returns the route object with ID rid.'''
    return self.routes_info[rid]
  
  def exp(self, did: int) -> int:
    '''Returns the experience level of the driver with ID did.'''
    return self.drivers_info[did].exp

  def vid(self, did: int, rid: int, exp: int) -> int:
    '''Returns the variable ID of the propositional symbol d_{did}_{rid}_{exp},
    where did is the driver ID, rid is the route ID, and exp is an experience
    level.'''
    return self.syms.id(f'd_{did}_{rid}_{exp}')
  
  # Type check for str return type presenting type checking warnings. TODO
  def obj(self, vid: int):
    '''Returns the propositional symbol identified by the variable ID vid.'''
    return self.syms.obj(vid)

  # Same type checking warning here. TODO
  # There seems to be an issue here. Sometimes, models can be wrong! TODO
  def formulate(self):
    '''Returns the four sets of clauses which encode the FietSAT problem rules
    for the given driver and route sets.'''
    # At most one experience level per driver (less than or equal to its
    # experience level)
    c_1 = [CardEnc.atmost([self.vid(did, rid, exp)
                          for exp in range(4, 0, -1)],
                          vpool=self.syms).clauses
           for did in self.drivers()
           for rid in self.routes_of(did)]
    
    # At most one route per driver
    c_2 = [CardEnc.atmost([self.vid(did, rid, exp)
                          for rid in self.routes_of(did)
                          for exp in range(4, 0, -1)],
                          vpool=self.syms).clauses
           for did in self.drivers()]
    
    # Exactly one driver per experience level per route
    c_3 = [CardEnc.equals([self.vid(did, rid, exp)
                          for did in self.drivers_of(rid)],
                          vpool=self.syms).clauses
           for rid in self.routes()
           for exp in range(4, 0, -1)]
    
    # No driver is assigned to an experience level above his
    c_4 = [[[-self.vid(did, rid, exp)]]
           for did in self.drivers()
           for rid in self.routes_of(did)
           for exp in range(self.exp(did)+1, 5)]
    
    self.problem = [c_1, c_2, c_3, c_4]
    return c_1, c_2, c_3, c_4
  
  def solve(self) -> bool:
    # Insert into solver
    for c_group in self.problem:
      for formula in c_group:
        self.solver.append_formula(formula)

    # Check if solution exists
    if self.solver.solve():
      self.model = self.solver.get_model()
      return True
    
    self.model = []
    return False
  
  def report(self):
    solution = {rid: [] for rid in range(1, len(self.routes()) + 1)}

    # Extracting solution from the model
    # Literals which evaluate to None after the obj call are symbols
    # automatically generated by the cardinality encoding
    # The rest are strings d_{did}_{rid}_{exp}, from which the solution is
    # extracted
    if self.model != []:
      for lit in self.model:
        if lit > 0:
          sym = self.obj(lit)
          if sym is not None:
            did, rid, exp = map(int, sym.split('_')[1:])
            solution[rid].append((did, exp))

      print(f'~~ FietSAT report @ {datetime.now():%H:%M, %b %d %Y} ~~\n')
      print(f'Number of drivers: {len(self.drivers())}')
      print(f'Number of routes: {len(self.routes())}\n')

      if self.model != []:
        print('SAT? Yes\n')
        for rid in solution:
          route_info = self.route_info(rid)
          print(f'Route {rid} ({route_info.start} – {route_info.end}):')
          for did, exp in sorted(solution[rid], key=lambda sol_pair: sol_pair[1], reverse=True):
            print(f'\tDriver {did} ({self.driver_info(did).name}) @ exp. level {exp}')
      else:
        print('SAT? No')
    
    return solution


if __name__ == '__main__':
  try:
    _, drivers_fp, routes_fp = argv
  except ValueError:
    print('Invalid number of arguments. Run with \'python fietsat.py <drivers_file_path> <routes_file_path>\'.')
    raise

  fsat = FietSAT(drivers_fp, routes_fp)
  fsat.formulate()
  fsat.solve()     
  fsat.report()
