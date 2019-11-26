# Ripple-Simulation

A simulation of the Ripple Consensus Algorithm.

## How to run

Install Python3, pip3 and Django on the system.

Install python dependencies by:

``` bash
pip3 install -r ripple_server/requirements.txt
```

This simulation will use 3 nodes (clients) and a server with 5 blocks and 5 transactions in each block. Transactions can be found at `transaction_generator/data/client-s-*.csv`. **Do not modify those files**.

Open 4 terminals. Run the following commands in the terminals, respectively:

Terminal 1:
``` bash
cd ripple_server
python3 manage.py runserver
```

Rest of the terminals, run after the server has successfully started and shows **`Phase = IDLE`**.
Terminal 2:
``` bash
cd ripple_client
python3 client.py 0
```

Terminal 3:
``` bash
cd ripple_client
python3 client.py 1
```

Terminal 4:
``` bash
cd ripple_client
python3 client.py 2
```

The simulation will start running.

Results will be stored in `ripple_server/data/results.txt` after every block is mined.
