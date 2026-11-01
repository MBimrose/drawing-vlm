"""TCP relay (2026-10-28, user-approved): cluster compute nodes refuse ssh port forwarding, so chain runners on other
nodes reach an H200 node's repairer servers (127.0.0.1:885x) through this relay on the node's cluster-internal address.
Exits when the repair job <jobid> ends or <pipeline>/RELAY_STOP exists.
    python3 tcp_relay.py <jobid> <listen_host> <listen_port>:<target_host>:<target_port> [...]"""
import asyncio, os, subprocess, sys

STOP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RELAY_STOP")


async def pipe(r, w):
    try:
        while data := await r.read(65536):
            w.write(data); await w.drain()
    except Exception:
        pass
    finally:
        w.close()


def handler(th, tp):
    async def h(cr, cw):
        try:
            tr, tw = await asyncio.open_connection(th, tp)
        except Exception:
            cw.close(); return
        await asyncio.gather(pipe(cr, tw), pipe(tr, cw))
    return h


async def main():
    job, host = sys.argv[1], sys.argv[2]
    for spec in sys.argv[3:]:
        lp, th, tp = spec.split(":")
        await asyncio.start_server(handler(th, int(tp)), host, int(lp), backlog=1024)
    print("relay up", host, sys.argv[3:], flush=True)
    while not os.path.exists(STOP):
        if not subprocess.run(["squeue", "-h", "-j", job], capture_output=True, text=True).stdout.strip():
            break
        await asyncio.sleep(60)

asyncio.run(main())
