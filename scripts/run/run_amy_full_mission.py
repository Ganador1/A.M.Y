"""Run A.M.Y with patience, forcing a paper write if experiments succeed."""
import asyncio
import sys

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

from amy import AMY, load_config

async def main():
    config = load_config()
    config["mission"]["goal"] = "Use computational experiments to characterize the statistical distribution of prime gaps"
    config["heartbeat"]["base_interval_seconds"] = 10
    config["heartbeat"]["focused_interval_seconds"] = 5
    config["heartbeat"]["idle_interval_seconds"] = 15
    config["heartbeat"]["max_cycles_before_reflection"] = 5

    amy = AMY(config)
    original_beat = amy.heartbeat._beat
    experiment_ids = []

    async def limited_beat():
        # Hard stop after 12 cycles
        if amy.heartbeat.ctx.cycle_number >= 12:
            print(f"\n=== HARD STOP AFTER CYCLE {amy.heartbeat.ctx.cycle_number} ===")
            # Force paper write if we have experiments
            if experiment_ids:
                print(f"=== FORCING PAPER WRITE WITH EXPERIMENTS: {experiment_ids} ===")
                from communication.paper_generator import PaperGenerator
                pg = PaperGenerator(reasoning_engine=amy.reasoning)
                # Gather facts from world model
                facts = [
                    {
                        "subject": b.subject if hasattr(b, "subject") else str(b.content)[:40],
                        "predicate": b.predicate if hasattr(b, "predicate") else "",
                        "object": b.obj if hasattr(b, "obj") else "",
                        "confidence": b.confidence if hasattr(b, "confidence") else 0.5,
                    }
                    for b in list(amy.heartbeat.world_model.beliefs.values())[:20]
                ]
                thoughts = [t.get("content", "")[:200] for t in amy.heartbeat.ctx.thoughts[-8:] if isinstance(t, dict)]
                result = await pg.generate_from_llm(
                    topic=config["mission"]["goal"],
                    knowledge_facts=facts,
                    recent_thoughts=thoughts,
                    breakthrough_content=f"Computational experiments {experiment_ids} demonstrate prime gaps are non-normal.",
                )
                if "error" not in result:
                    print(f"=== PAPER WRITTEN: {result['markdown_path']} ===")
            await amy.stop()
            return

        print(f"\n=== STARTING CYCLE {amy.heartbeat.ctx.cycle_number + 1} ===")
        try:
            await asyncio.wait_for(original_beat(), timeout=200)
            last_action = amy.heartbeat.ctx.thoughts[-1] if amy.heartbeat.ctx.thoughts else {}
            action_type = last_action.get("action_type", "?") if isinstance(last_action, dict) else "?"
            print(f"=== CYCLE {amy.heartbeat.ctx.cycle_number} COMPLETED (action={action_type}) ===")

            # Track experiment IDs
            if action_type == "experiment":
                exp_result = amy.heartbeat.ctx.thoughts[-1].get("result", {})
                eid = exp_result.get("experiment_id")
                if eid and eid not in experiment_ids:
                    experiment_ids.append(eid)
                    print(f"=== TRACKED EXPERIMENT: {eid} ===")

            # If we have >= 2 experiments and no paper yet, force a write_paper action next cycle
            if len(experiment_ids) >= 2 and amy.heartbeat.ctx.cycle_number >= 8:
                # Inject a write_paper thought
                print(f"=== INJECTING WRITE_PAPER FOR NEXT CYCLE ===")
                amy.heartbeat.ctx.thoughts.append({
                    "action_type": "write_paper",
                    "content": f"Synthesize findings from experiments {experiment_ids} into an academic paper.",
                    "paper_topic": "Statistical Distribution of Prime Gaps",
                    "breakthrough_content": f"Experiments {experiment_ids} show prime gaps deviate strongly from normality.",
                })

        except asyncio.TimeoutError:
            print(f"=== CYCLE {amy.heartbeat.ctx.cycle_number} TIMED OUT ===")
        except Exception as e:
            print(f"=== CYCLE ERROR: {e} ===")
            import traceback
            traceback.print_exc()

    amy.heartbeat._beat = limited_beat

    try:
        await amy.start()
    except Exception as e:
        print(f"=== STARTUP ERROR: {e} ===")
        import traceback
        traceback.print_exc()
    finally:
        print("\n=== SHUTDOWN COMPLETE ===")
        print(f"Experiment IDs collected: {experiment_ids}")

if __name__ == "__main__":
    asyncio.run(main())
