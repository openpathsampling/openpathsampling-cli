# should be able to remove this try block when we drop OpenMM < 7.6
try:
    import openmm as mm
    from openmm import unit
except ImportError:
    try:
        from simtk import openmm as mm
        from simtk import unit  # -no-cov-
    except ImportError:
        HAS_OPENMM = False
        mm = None
        unit = None
    else: # -no-cov-
        HAS_OPENMM = True
else:
    HAS_OPENMM = True


