# pycryptobot_random_tester
Runs pycryptobot trading algorithm creating random configurations that yield historically high margin configs.

Clone this folder into the same root folder as pycryptobot so that both folders are next to each other. This script will go up one level using ../pycryptobot/pycryptobot.py. This can be editted in the variables at the top of the scripts. 

Enter your telegram info in the base config or disable the telegram bot to avoid errors. 

Set the markets you want to trade in the markets.json file then run python3 start_multiple_random_tests.py to do sims on those markets. In short periods of testing its been able to find fairly good historical configs. However much more live testing is needed to determine viability. The random values need a great deal of tweaking to see if they are even in a reasonable range.

Once reasonable configs have been created you can begin trading by running python3 start_traders.py. Output must be viewed in the log files. See tail -f "logfile.log"