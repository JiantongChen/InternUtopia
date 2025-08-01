def main():
    import json
    import time

    from internutopia.core.config import Config, SimConfig
    from internutopia.core.gym_env import Env
    from internutopia.core.util import has_display
    from internutopia.macros import gm
    from internutopia_extension import import_extensions
    from internutopia_extension.configs.robots.h1 import (
        H1RobotCfg,
        move_along_path_cfg,
        move_by_speed_cfg,
        rotate_cfg,
    )
    from internutopia_extension.configs.tasks import SingleInferenceTaskCfg

    t0 = time.perf_counter()

    headless = False
    if not has_display():
        headless = True

    h1_1 = H1RobotCfg(
        position=(0.0, 0.0, 1.05),
        controllers=[
            move_by_speed_cfg,
            move_along_path_cfg,
            rotate_cfg,
        ],
        sensors=[],
    )

    config = Config(
        simulator=SimConfig(
            physics_dt=1 / 240, rendering_dt=1 / 240, use_fabric=True, headless=headless, native=headless
        ),
        task_configs=[
            SingleInferenceTaskCfg(
                scene_asset_path=gm.ASSET_PATH + '/scenes/empty.usd',
                scene_scale=(0.01, 0.01, 0.01),
                robots=[h1_1],
            )
        ],
    )

    print(config.model_dump_json(indent=4))

    import_extensions()

    t1 = time.perf_counter()
    env = Env(config)
    t2 = time.perf_counter()
    obs, _ = env.reset()
    t3 = time.perf_counter()
    print(f'========INIT OBS{obs}=============')

    path = [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (3.0, 4.0, 0.0)]
    i = 0

    move_action = {move_along_path_cfg.name: [path]}

    while env.simulation_app.is_running():
        i += 1
        action = move_action
        obs, _, terminated, _, _ = env.step(action=action)
        if i % 100 == 0:
            print(i)
            print(obs)
            pos = obs['position']
            assert pos[0] < 5.0 and pos[1] < 5.0 and pos[2] < 2.0, 'out of range'
        if i == 2000:
            t4 = time.perf_counter()
            run_result = {
                'import_ext': t1 - t0,
                'create_env': t2 - t1,
                'reset_env': t3 - t2,
                '2k_step': t4 - t3,
            }
            with open('./test_result.json', 'w', encoding='utf-8') as f:
                json.dump(run_result, f, ensure_ascii=False, indent=4)
            print(f'times: {run_result}')
            break

    env.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'exception is {e}')
        import sys
        import traceback

        traceback.print_exc()
        sys.exit(1)
