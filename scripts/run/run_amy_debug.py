"""Debug script to run a single cycle of A.M.Y and capture all output."""
import asyncio
import traceback
import sys

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from amy import AMY, load_config

async def main():
    config = load_config()
    config["mission"]["goal"] = "Use computational experiments to test whether the distribution of prime gaps deviates from normality"
    config["heartbeat"]["base_interval_seconds"] = 5
    config["heartbeat"]["focused_interval_seconds"] = 2
    config["heartbeat"]["idle_interval_seconds"] = 10

    amy = AMY(config)

    # Override the heartbeat to run only 3 cycles then stop
    original_beat = amy.heartbeat._beat

    async def limited_beat():
        if amy.heartbeat.ctx.cycle_number >= 3:
            print(f"\n=== STOPPING AFTER CYCLE {amy.heartbeat.ctx.cycle_number} ===")
            await amy.stop()
            return
        print(f"\n=== STARTING CYCLE {amy.heartbeat.ctx.cycle_number + 1} ===")
        try:
            await asyncio.wait_for(original_beat(), timeout=150)
            print(f"=== CYCLE {amy.heartbeat.ctx.cycle_number} COMPLETED ===")
        except asyncio.TimeoutError:
            print(f"=== CYCLE {amy.heartbeat.ctx.cycle_number} TIMED OUT ===")
            await amy.stop()
        except Exception as e:
            print(f"=== CYCLE {amy.heartbeat.ctx.cycle_number} ERROR: {e} ===")
            traceback.print_exc()
            await amy.stop()

    amy.heartbeat._beat = limited_beat

    try:
        await amy.start()
    except Exception as e:
        print(f"=== STARTUP ERROR: {e} ===")
        traceback.print_exc()
    finally:
        print("\n=== SHUTDOWN COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(main())
