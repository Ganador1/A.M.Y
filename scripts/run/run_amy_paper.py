"""Run A.M.Y long enough to generate a paper from the experiment."""
import asyncio
import sys

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from amy import AMY, load_config

async def main():
    config = load_config()
    config["mission"]["goal"] = "Use computational experiments to test whether the distribution of prime gaps deviates from normality"
    config["heartbeat"]["base_interval_seconds"] = 5
    config["heartbeat"]["focused_interval_seconds"] = 3
    config["heartbeat"]["idle_interval_seconds"] = 10
    config["heartbeat"]["max_cycles_before_reflection"] = 6

    amy = AMY(config)
    original_beat = amy.heartbeat._beat

    async def limited_beat():
        # Stop after 8 cycles or if a paper was written
        if amy.heartbeat.ctx.cycle_number >= 8:
            print(f"\n=== STOPPING AFTER CYCLE {amy.heartbeat.ctx.cycle_number} ===")
            await amy.stop()
            return
        print(f"\n=== STARTING CYCLE {amy.heartbeat.ctx.cycle_number + 1} ===")
        try:
            await asyncio.wait_for(original_beat(), timeout=200)
            print(f"=== CYCLE {amy.heartbeat.ctx.cycle_number} COMPLETED (action={amy.heartbeat.ctx.thoughts[-1].get('action_type','?') if amy.heartbeat.ctx.thoughts else 'none'}) ===")
        except asyncio.TimeoutError:
            print(f"=== CYCLE {amy.heartbeat.ctx.cycle_number} TIMED OUT ===")
            await amy.stop()
        except Exception as e:
            print(f"=== CYCLE ERROR: {e} ===")
            import traceback
            traceback.print_exc()
            await amy.stop()

    amy.heartbeat._beat = limited_beat

    try:
        await amy.start()
    except Exception as e:
        print(f"=== STARTUP ERROR: {e} ===")
        import traceback
        traceback.print_exc()
    finally:
        print("\n=== SHUTDOWN COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(main())
