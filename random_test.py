from os import write
import subprocess
from pprint import pprint
import json
import random
import time, math
from statistics import mean 
import datetime
# from models.PyCryptoBot import truncate
from colorama import Fore, Back, Style
import sys

# print((datetime.datetime.today() + datetime.timedelta(days=-1)).date())

# User selectable
id = random.randrange(1,1000)
start_date = str((datetime.datetime.today() + datetime.timedelta(days=-1)).date()) # By default run previous days data
end_date = str((datetime.datetime.today() + datetime.timedelta(days=-1)).date()) # By default run previous days data
random_test_count = 5000 # Number of iterations to randomly test
required_sell_count = 3 # Number of required sales to consider margin acceptable
sim_speed = 'fast'
directory = '../pycryptobot/'
config_directory = './configs/'
test_config_directory = './tests/configs/'
test_directory = './tests/'

if("--market" in  sys.argv):
    market = sys.argv[sys.argv.index("--market") + 1]   
else:
    market = 'DOGE-USD' # default market can be whatever you choose

testing_telegram = 1 # Disable telegram by default to keep from lots of useless alerts during testing
live_telegram = 0 # Enable/Disable telegram on the produced configurations

def random_float(negative = False):
    number = random.randrange(10, 50)
    if negative:
        number = number * -.1
    else:
        number = number * .1
    return number

def random_bool():
    return random.randrange(0,2)


def build_test_config():
    config = read_test_config(f'base_config.json') # Load the base config to randomize off of. 
    
    # Randomize config here
    config['coinbasepro']['config']['sellatloss'] = random_bool()
    config['coinbasepro']['config']['sellatresistance'] = random_bool()
    config['coinbasepro']['config']['nobuynearhighpcnt'] = random_float()
    config['coinbasepro']['config']['trailingstoploss'] = random_float(True)
    config['coinbasepro']['config']['trailingstoplosstrigger'] = random_float()
    config['coinbasepro']['config']['nosellmaxpcnt'] = random_float()
    config['coinbasepro']['config']['nosellminpcnt'] = random_float(True)
    config['coinbasepro']['config']['disablebullonly'] = random_bool()
    config['coinbasepro']['config']['disablebuynearhigh'] = random_bool()
    config['coinbasepro']['config']['disablebuyema'] = random_bool()
    config['coinbasepro']['config']['disablebuymacd'] = random_bool()
    config['coinbasepro']['config']['disablebuyobv'] = random_bool()
    config['coinbasepro']['config']['disablebuyelderray'] = random_bool()
    config['coinbasepro']['config']['disablefailsafefibonaccilow'] = random_bool()
    config['coinbasepro']['config']['disableprofitbankreversal'] = random_bool()
    # config['coinbasepro']['config']['granularity'] = granularity
    # config['coinbasepro']['config']['sim'] = 'fast'
    # config['coinbasepro']['config']['simstartdate'] = start_date
    # config['coinbasepro']['config']['simenddate'] = end_date
    config['coinbasepro']['config']['live'] = 0
    config['coinbasepro']['config']['disabletelegram'] = testing_telegram
    write_to_config(config, f"{test_config_directory}test_config_{market}_{id}.json")
    return config

def log_updates(update):
    f = open(f"{test_directory}config_generator.log", "a+")
    f.write(update)
    f.close()

def write_to_config(config_json, name):
    with open(name, "w+") as outfile:
        json.dump(config_json, outfile, indent=4)

def read_test_config(name):
    try:
        with open(name, 'r+') as infile:
            j = json.load(infile)
            return j
    except FileNotFoundError:
        config = read_test_config('base_config.json')
        write_to_config(config, f'{config_directory}generated_config_{market}.json')
        return config

def run_config_test():
    # Load the current best configuration
    best_config = read_test_config(f'{config_directory}generated_config_{market}.json') # Try to load existing standard config

    # Get a random assortment of config.json and save to variable and file
    test_config = build_test_config()

    # Run the test configuration file
    run_command = f'python3 {directory}pycryptobot.py --market {market} --config {test_config_directory}test_config_{market}_{id}.json --sim {sim_speed} --simstartdate {start_date} --logfile ./tests/test_{market}.log'
    list_command = run_command.split(sep=' ')

    process = subprocess.run(list_command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                        )
    output = process.stderr

    output = iter(output.splitlines())
    sell_count = 0

    # Search the test output for sell count and margin info
    for i in output:
        if "Sell Count" in i:
            sell_count = int(i.split(':')[1][1:]) # Get the number of sells
            
        if 'All Trades Margin' in i:
            margin = i.split(':')
            margin = float(margin[1][1:-1])
            print(Fore.RED + f'Margin: {margin}, sells: {sell_count}' + Style.RESET_ALL)

            if sell_count < required_sell_count:
                continue

            if margin > best_config['test_info']['margin']:
                log_updates(f'\n{market} upgrade margin: {margin} on {sell_count} trades')
                print(Fore.RED + '*' * 80)
                print(f"Improved margin on {market} {margin}... writing new config")
                test_config['test_info']['margin'] = margin
                test_config['test_info']['date'] = start_date
                test_config['test_info']['sell_count'] = sell_count
                test_config['coinbasepro']['config']['live'] = 1
                test_config['coinbasepro']['config']['disabletelegram'] = live_telegram
                test_config.pop('sim', None)
                test_config.pop('simstartdate', None)
                test_config.pop('simenddate', None)
                write_to_config(test_config, f"{config_directory}generated_config_{market}.json")
                print('*' * 80 + Style.RESET_ALL)

def main():
    
    start_time = time.time()
    run_times = []
    for i in range(1, random_test_count):
        run_start_time = time.time() # Make note of the start time
        run_config_test() # Run the test which builds random configuration

        # Find the average run time and print average every 10 runs
        run_end_time = time.time()
        run_time = run_end_time - run_start_time
        run_times.append(run_time)
        if i % 10 == 0:
            average = round(mean(run_times), 2)
            print(f"------------------- Average run time: {average}")
        
    # Note the total run time
    end_time = time.time()
    total_run_time = end_time - start_time
    print('*' * 50)
    print(f'Total Run time: {total_run_time} over {random_test_count} iterations')
    print('*' * 50)

main()
