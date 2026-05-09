'''AI utilities for uplogic.

Provides a NavMesh-based agent controller (:class:`~uplogic.ai.Agent`) that
computes paths via the BGE ``KX_NavMeshObject`` API, optionally rounds corners
with a bevel distance, avoids physics obstacles via raycasts, and drives a
``KX_GameObject`` along the resulting waypoints each game tick.

Typical usage::

    from uplogic.ai import Agent

    # wrap a BGE game object and point it at the scene NavMesh
    agent = Agent(scene_obj, speed=0.15, bevel=0.3, dynamic=False)
    agent.set_navmesh(navmesh_obj)

    # in the game loop: recalculate when the target moves, advance every tick
    agent.find_path(target_position)
    agent.move()
    agent.lookat(factor=0.08)
'''

from .agent import Agent