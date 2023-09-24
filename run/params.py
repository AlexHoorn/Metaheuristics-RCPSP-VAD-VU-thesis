from pathlib import Path


CX_INDPB = 0.2
CXPB = 0.2
REPAIR_PCT = 0.0
INSTANCE = (
    Path(__file__).parent.parent
    / "instances"
    / "generated_param_search"
    / "n_50"
    / "schedule_50_auto_0_1_0.pkl"
)
LAMBDA_ = 250
MU = 200
MUT_INDPB = 0.1
MUT_MU = 0
MUT_SIGMA = 1
MUTPB = 0.1
NEVAL = 100000
PATIENCE = None
PMAX = 50
PMIN = -50
SEED = True
WEIGHTS = (-1, -1)

# Debugging
CREATE_FIGURES = False
CREATE_VIDEO = False
DISABLE_MULTIPROCESSING = True
QUIET = False
SAVE_POPULATION = False

# PSO
PHI1 = 7
PHI2 = 7
SMAX = 1.2
SMIN = -1.2
WEIGHT = 1

# SA
ALPHA = 0.85
TEMP = 70
