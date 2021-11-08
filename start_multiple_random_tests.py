import subprocess
import json
import time
from colorama import Fore, Back, Style
import multiprocessing as mp

maxprocesses = 6  # mp.cpu_count() - 1
the_queue = mp.Queue()

def read_markets():
    with open('markets.json', 'r+') as infile:
        j = json.load(infile)
        return j['markets']


def start_process(task_queue):
    # linestoshow = 500

    # Consume the queue until a 'None' is reached.
    while True:
        market = task_queue.get(block=True)
        if market is None:
            break

        run_command = f'python3 random_test.py --market {market}'
        list_command = run_command.split(sep=' ')

        print(f'Started {market}')
        process = subprocess.run(list_command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True,
                                 )

        # Print the Return Code and the output. The join allows
        # the stdout which is returned as a list to be properly printed.
        # LinesToShow determines how many lines, starting with last
        # line, counting backwards to be displayed.  Consider increasing this
        # based on how many random tests are performed per market.
        print('-' * 50)
        print(f'{market} random simulation test exit code ' + str(process.returncode))

        # Uncomment if you want to show the last nn lines
        print("." * 80)
        # print("\n".join(process.stdout.splitlines()[-linestoshow:]))
        # print("." * 80)

        # comment out if you want to only show the last nn lines above.
        output = process.stdout
        output = iter(output.splitlines())
        for i in output:
            if "new config" in i:
                print(Fore.RED + i + Style.RESET_ALL)
            if "Total Run time" in i:
                print(Fore.RED + i + Style.RESET_ALL)
            # Comment out this line if you do not want to see the margins appear in the output
            if "Margin" in i:
                print(Fore.RED + i + Style.RESET_ALL)

        print('-' * 50)


def add_task(task_queue, task_list):
    for item in task_list:
        task_queue.put(item)

    # End the queue with 1 'None' per parallel process to permit a gracefull
    # termination of the parallel processes.
    for _ in range(maxprocesses):
        task_queue.put(None)

    return task_queue


def main():
    start_time = time.time()

    # Put everything into a Queue to process by several parallel processes.
    add_task(the_queue, read_markets())
    queuelength = the_queue.qsize() - maxprocesses
    print(f'Running random_test.py for {queuelength} markets with parallel {maxprocesses} processes')
    print('=' * 80)

    # Create and execute the pool of workers. The , after the_queue is required.
    pool = mp.Pool(maxprocesses, start_process, (the_queue,))

    # Cleanup and shutdown the queue and pool of workers
    the_queue.close()
    the_queue.join_thread()
    pool.close()
    pool.join()

    # Note the total run time
    end_time = time.time()
    total_run_time = end_time - start_time
    print('=' * 80)
    print(f'Completed {queuelength} random simulation with {maxprocesses} processes in {total_run_time}')


if __name__ == '__main__':
    main()
