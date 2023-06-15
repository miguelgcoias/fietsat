# FietSAT
FietSAT is a program to allocate drivers to routes subject to experience and availability constraints. Each route is assumed to require 4 drivers, each of experience levels at least 1, 2, 3 and 4. Each driver is associated to a subset of routes which he/she knows.

The problem's constraints are encoded in propositional logic and then passed to a SAT solver, using the SAT solving library [PySAT](https://pysathq.github.io/).

## Input
The driver and route data files accepted are in JSON format. Driver files consist of a list of objects of the form

    {
      "id": 1,
      "name": "Isaac Newton",
      "exp": 4,
      "routes": [10, 1, 3, 2, 9, 7, 5, 6]
    }

  where ``id`` is a unique provided ID for each driver, ``exp`` is his/hers experience level from 1 to 4, and ``routes`` is a list of route IDs the driver is available to do.

  Route files are also a list of objects of the form
  
    {
      "id": 1,
      "start": "Braga",
      "end": "Coimbra"
    }

## Usage
Open a terminal in the fietsat folder and install the package requirements using the command

``python -m pip install -r requirements.txt``

This command will install wheel and python-sat in the Python distribution of your Path environment variable. Then, run FietSAT using the command

``python fietsat.py path/to/drivers.json path/to/routes.json``

To run with the provided example, use

``python fietsat.py examples/scientists.json examples/portugal.json``

## Example output

For the provided example, a possible output is

    ~~ FietSAT report @ 20:39, Jun 15 2023 ~~

    Number of drivers: 56
    Number of routes: 10

    SAT? Yes

    Route 1 (Braga – Coimbra):
            Driver 27 (Robert Boyle) @ exp. level 4
            Driver 36 (Amedeo Avogadro) @ exp. level 3
            Driver 23 (Jules Henri Poincaré) @ exp. level 2
            Driver 42 (Gerolamo Cardano) @ exp. level 1
    Route 2 (Aveiro – Coimbra):
            Driver 20 (Nicolaus Copernicus) @ exp. level 4
            Driver 15 (James Clerk Maxwell) @ exp. level 3
            Driver 10 (Srinivasa Ramanujan) @ exp. level 2
            Driver 6 (Galileo Galilei) @ exp. level 1
    Route 3 (Bragança – Aveiro):
            Driver 28 (Pierre-Simon Laplace) @ exp. level 4
            Driver 7 (Nikola Tesla) @ exp. level 3
            Driver 8 (Marie Curie) @ exp. level 2
            Driver 51 (Hendrik Antoon Lorentz) @ exp. level 1

    (...)
    
    Route 10 (Castelo Branco – Braga):
            Driver 40 (Niels Bohr) @ exp. level 4
            Driver 26 (John Von Neumann) @ exp. level 3
            Driver 48 (Enrico Fermi) @ exp. level 2
            Driver 54 (William Thomson Kelvin) @ exp. level 1
