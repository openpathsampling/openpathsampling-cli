from paths_cli.parameters import (
    MULTI_INIT_SNAP, MULTI_NETWORK, OUTPUT_FILE, INPUT_FILE
)

@MULTI_INIT_SNAP.clicked()
@MULTI_NETWORK.clicked()
@OUTPUT_FILE.clicked()
@INPUT_FILE.clicked()
def bootstrap_init(init_frame, network, output_file, input_file):
    ...

def _update_init_frames(transitions, init_frames):
    transition_to_init_frame = {}
    for transition in transitions:
        # raise error if not TIS transition
        transition_to_init_frame[transition] = None
        for snap in init_frames:
            if init_frame.initial_state(snap):
                transition_to_init_frame[transition] = snap
                break
    return transition_to_init_frame


def bootstrap_init_main(init_frames, networks, output_file):
    all_transitions = {trans for trans in network.sampling_transitions
                       for network in networks}
    trans_to_init_frame = _update_init_frames(all_transitions, init_frames)
    missing = {trans for trans, frame in trans_to_init_frame.items()
               if frame is None}
    # TODO warn about missing initial frames
    found = set(trans_to_init_frame) - missing
    completed = set()
    for transition in found:
        ...

