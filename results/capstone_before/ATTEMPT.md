# Incomplete evaluator attempt

This directory is preserved in full. Each of its three scheduled trials
completed five normal answer requests and four invalid-input requests before
the evaluator stopped between server phases. The two server-fault requests
and the six accounting requests were not executed.

The generated summary conservatively assigned MISSED when observations were
absent. Those provisional counts are not evidence that the unexecuted system
behaviors failed. The complete baseline is in ../capstone_before_verified/.
No application source or criterion target changed during these attempts.
Only the evaluator's startup and cleanup logic was corrected afterward.

This first attempt failed at the evaluator's pre-start socket bind with OSError.
