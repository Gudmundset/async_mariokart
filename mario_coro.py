#!/usr/bin/python3.8
"""
AI MARIO KART BUILT WITH COROUTINES
ADAPTING FLUENT PYTHON TAXI COROUTINE CODE TO PYTHON3.8

STILL A WORK IN PROGRESS
ARRANGED BY: PHILIP LARSON
"""

import asyncio
import random
import collections
import queue
import argparse

async def event(time, ident, action):
    return action

async def kart_process(ident, trips, start_time=0):
    """Yield to simulator issuing event at each state change"""
    time = await event(start_time, ident, 'leave starting line')
    for _ in range(trips):
        time = await event(time, ident, 'pick up item')
        time = await event(time, ident, 'use item')
    await event(time, ident, 'finish line')


class MarioKart:
    # IT'S MARIO KART, WOOHOO
    def __init__(self, procs_map, options):
        self.events = queue.PriorityQueue()
        self.procs = dict(procs_map)
        self.search_duration = options.search_duration
        self.trip_duration = options.trip_duration

    def run(self, end_time):
        """Schedule and display events until time is up"""
        # schedule the first event for each cab
        for _, proc in sorted(self.procs.items()):
            first_event = next(proc)
            self.events.put(first_event)

        # main loop of the simulation
        sim_time = 0
        while sim_time < end_time:
            if self.events.empty():
                print('*** end of events ***')
                break

            current_event = self.events.get()
            sim_time, proc_id, previous_action = current_event
            print('kart:', proc_id, proc_id * '   ', current_event)
            active_proc = self.procs[proc_id]
            next_time = sim_time + self.compute_duration(previous_action)
            try:
                next_event = active_proc.send(next_time)
            except StopIteration:
                del self.procs[proc_id]
            else:
                self.events.put(next_event)
        else:
            msg = '*** end of simulation time: {} events pending ***'
            print(msg.format(self.events.qsize()))


    def compute_duration(self, previous_action):
        """Compute action duration using exponential distribution"""
        if previous_action in ['leave garage', 'drop off passenger']:
            # new state is prowling
            interval = self.search_duration
        elif previous_action == 'pick up passenger':
            # new state is trip
            interval = self.trip_duration
        elif previous_action == 'going home':
            interval = 1
        else:
            raise ValueError('Unknown previous_action: %s' % previous_action)
        return int(random.expovariate(1/interval)) + 1

def get_options():
    default_number_of_karts = 3
    default_end_time = 180
    
    parser = argparse.ArgumentParser(
                        description='kart fleet simulator.')
    parser.add_argument('-e', '--end_time', type=int,
                        default=default_end_time,
                        help='simulation end time; default = %s'
                        % default_end_time)
    parser.add_argument('-k', '--karts', type=int,
                        default=default_number_of_karts,
                        help='number of karts running; default = %s'
                        % default_number_of_karts)
    parser.add_argument('-s', '--seed', type=int, default=None,
                        help='random generator seed (for testing)')
    parser.add_argument('--departure_interval', type=int, default=5,
                        help='departure interval')
    parser.add_argument('--search_duration', type=int, default=5,
                        help='search duration')
    parser.add_argument('--trip_duration', type=int, default=20,
                        help='trip duration')

    return parser.parse_args()


def main():
    options = get_options()
    """Initialize random generator, build procs and run simulation"""
    if options.seed is not None:
        random.seed(options.seed)
    print(asyncio.run(kart_process(1,1,0)))
    karts = {i: asyncio.run(kart_process(i, (i+1)*2, i*options.departure_interval)) for i in range(options.karts)}
    sim = MarioKart(karts, options)
    sim.run(options.end_time)

if __name__ == '__main__':
    main()
