import subprocess, json
from time import sleep
from colorama import Fore, Back, Style

def read_markets():
    with open('markets.json', 'r+') as infile:
        
        j = json.load(infile)
        return j['markets']

def start_process(market):
    global processes
    run_command = f'python3 random_test.py --market {market}'
    list_command = run_command.split(sep=' ')

    process = subprocess.Popen(list_command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                        )

    print(f'Started PID: {process.pid} for {market}')
    processes.append(process)
    
def main():
    global processes
    processes = []
    market_list = read_markets()
    # print(market_list)
    for i in market_list:
        # print(i)
        start_process(i)

    while True:
        print("Scanning")
        alive_check = False
        for i in processes:
            print(f'Exit code for {i.args[3]}: {i.poll()}')
            if i.poll() == None:
                alive_check = True
        if alive_check == False:
            print(Fore.RED + f'Failed to continue' + Style.RESET_ALL)

            break
        sleep(60)
main()