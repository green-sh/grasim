# Simulation of Dijkstra or A*
This is a implementation of Dijkstra and A* in pygame.

## Installation
- Install Python 3.11
- (Optional) Create a venv using `python -m venv .venv`
- Install Poetry using `pip install poetry`
- Install game using `poetry install` in the root of this repository
- You can now use `grasim -d saves` to start using preconfigured saves

## Functionalities
- load graph files in local directory

## Graph language
Safefiles are loaded when they are in the local folder and end with `.graph`
## Syntax
```
NodeA -<length>- NodeB
NodeA(<heuristic>)
```

## Example
```
A(10)
B(7)
C(4)
E(3)
F(8)
G(5)
D(1)
Z(0)

A -4- B
A -10- F
A -5- G

B -7- C
B -2- G

F -6- G
F -5- E

G -1- C
G -9- E

C -13- Z

E -4- Z
E -5- D

D -1- Z

START G
END Z
```
