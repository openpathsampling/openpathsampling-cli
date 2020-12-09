import click

import paths_cli.utils
from paths_cli.parameters import (INPUT_FILE, OUTPUT_FILE, ENGINE,
                                  MULTI_ENSEMBLE, INIT_SNAP)

import logging
logger = logging.getLogger(__name__)

@click.command(
    "md",
    short_help=("Run MD for fixed time or until a given ensemble is "
                "satisfied"),
)
@INPUT_FILE.clicked(required=True)
@OUTPUT_FILE.clicked(required=True)
@ENGINE.clicked(required=False)
@MULTI_ENSEMBLE.clicked(required=False)
@click.option('-n', '--nsteps', type=int,
              help="number of MD steps to run")
@INIT_SNAP.clicked(required=False)
def md(input_file, output_file, engine, ensemble, nsteps, init_frame):
    """Run MD for for time of steps or until ensembles are satisfied.

    This can either take a --nsteps or --ensemble, but not both. If the
    --ensemble option is specfied more than once, then this will attempt to
    run until all ensembles are satisfied by a subtrajectory.

    This still respects the maximum number of frames as set in the engine,
    and will terminate if the trajectory gets longer than that.
    """
    storage = INPUT_FILE.get(input_file)
    md_main(
        output_storage=OUTPUT_FILE.get(output_file),
        engine=ENGINE.get(storage, engine),
        ensembles=MULTI_ENSEMBLE.get(storage, ensemble),
        nsteps=nsteps,
        initial_frame=INIT_SNAP.get(storage, init_frame)
    )

class ProgressReporter(object):
    def __init__(self, timestep, update_freq):
        self.timestep = timestep
        self.update_freq = update_freq

    def steps_progress_string(self, n_steps):
        report_str = "Ran {n_steps} frames"
        if self.timestep is not None:
            report_str += " [{}]".format(str(n_steps * timestep))
        report_str += '.'
        return report_str

    def progress_string(self, n_steps):
        report_str = self.steps_progress_string(n_steps) + "\n"
        return report_str.format(n_steps=n_steps)


    def report_progress(self, n_steps):
        import openpathsampling as paths
        if n_steps % self.update_freq == 0:
            string = self.progress_string(n_steps)
            paths.tools.refresh_output(string)

    def __call__(self, trajectory, trusted=False):
        raise NotImplementedError()


class EnsembleSatisfiedContinueConditions(ProgressReporter):
    """Continuation condition for including subtrajs for each ensemble.

    This object creates a continuation condition (a callable) analogous with
    the ensemble ``can_append`` method. This will tell the trajectory to
    keep running until, for each of the given ensembles, a subtrajectory has
    been found that will satisfy the ensemble.

    Parameters
    ----------
    ensembles: List[:class:`openpathsampling.Ensemble`]
        the ensembles to satisfy
    """
    def __init__(self, ensembles, timestep=None, update_freq=10):
        super().__init__(timestep, update_freq)
        self.satisfied = {ens: False for ens in ensembles}

    def progress_string(self, n_steps):
        report_str = self.steps_progress_string(n_steps)
        report_str += (" Found ensembles [{found}]. "
                       "Looking for [{missing}].\n")
        found = [ens.name for ens, done in self.satisfied.items() if done]
        missing = [ens.name for ens, done in self.satisfied.items()
                   if not done]
        found_str = ",".join(found)
        missing_str = ",".join(missing)
        return report_str.format(n_steps=n_steps,
                                 found=found_str,
                                 missing=missing_str)


    def _check_previous_frame(self, trajectory, start, unsatisfied):
        if -start > len(trajectory):
            # we've done the whole traj; don't keep going
            return False
        subtraj = trajectory[start:]
        logger.debug(str(subtraj) + "/" + str(trajectory))
        for ens in unsatisfied:
            if not ens.strict_can_prepend(subtraj, trusted=True):
                # test if we can't prepend because we satsify
                self.satisfied[ens] = ens(subtraj) or ens(subtraj[1:])
                unsatisfied.remove(ens)
        return bool(unsatisfied)

    def _call_untrusted(self, trajectory):
        self.satisfied = {ens: False for ens in self.satisfied}
        for i in range(1, len(trajectory)):
            keep_going = self(trajectory[:i], trusted=True)
            if not keep_going:
                return False
        return self(trajectory, trusted=True)

    def __call__(self, trajectory, trusted=False):
        if not trusted:
            return self._call_untrusted(trajectory)

        # below here, trusted is True
        self.report_progress(len(trajectory) - 1)

        unsatisfied = [ens for ens, done in self.satisfied.items()
                       if not done]
        # TODO: update on how many ensembles left, what frame number we are

        start = -1
        while self._check_previous_frame(trajectory, start, unsatisfied):
            start -= 1

        return not all(self.satisfied.values())


class FixedLengthContinueCondition(ProgressReporter):
    """
    """
    def __init__(self, length, timestep=None, update_freq=10):
        super().__init__(timestep, update_freq)
        self.length = length

    def __call__(self, trajectory, trusted=False):
        len_traj = len(trajectory)
        self.report_progress(len_traj - 1)
        return len_traj < self.length



def md_main(output_storage, engine, ensembles, nsteps, initial_frame):
    import openpathsampling as paths
    if nsteps is not None and ensembles:
        raise RuntimeError("Options --ensemble and --nsteps cannot both be"
                           " used at once.")

    if ensembles:
        continue_cond = EnsembleSatisfiedContinueConditions(ensembles)
    else:
        continue_cond = FixedLengthContinueCondition(nsteps)

    trajectory = engine.generate(initial_frame, running=continue_cond)
    paths_cli.utils.tag_final_result(trajectory, output_storage,
                                     'final_conditions')
    return trajectory, None

CLI = md
SECTION = "Simulation"
REQUIRES_OPS = (1, 0)

