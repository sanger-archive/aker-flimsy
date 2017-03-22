
##Reference implementation for a LIMS connecting to Aker

### Dependencies

These scripts run in Python 2. `postproducts.py` requires the `requests` module, which you can install using `pip install requests`; or simply download the requests module so that the script can use it.

### `postproducts.py`
This script reads a text file (see examples in repository), constructs a JSON request, and posts it to a specified url as a catalogue.

The current version of the script uses `trust_env=False` to avoid using an `http_proxy` environment variable in your shell.

Example:

    ./postproducts.py -u http://workordersurl:4000/catalogue -f sequencing.txt

Run `./postproducts.py -h` to see the usage information.

#### Catalogue file format
The catalogue file mostly consists of key:value pairs.
At the top are properties of the catalogue:

    pipeline: Sequencing
    url: http://localhost:3400
    lims_id: Sequencing

The url indicates what url the work orders service should post work orders to for this catalogue.

Then there should be zero or more product specifications. Each one begins with the word "product" on a line on its own, and then key-value pairs indicating the properties of that product.

    PRODUCT
      name: Toast
      description: Hot delicious toast
      product_version: 4
      ... more properties
      
    PRODUCT
      name: Cake
      description: Blurple cake
      product_version: 2

(The indentation and blank lines are for readability only; the script will ignore them.)
The properties are read and sent off agnostically: you can put whatever properties in here you want, and the script will happily send them, but the work orders service might not happily receive them.

### `receiveworkorders.py`
This script listens for posts on a specified port (default 3400). It will carry on listening until it errors (or quit via `ctrl c`). While it runs, it keeps a list of all posts it has received, and outputs the complete list to `stdout` each time a new one comes in.

Examples:

    ./receiveworkorders.py           # default port
    ./receiveworkorders.py -p 8000   # port 8000

Run `./receiveworkorders.py -h` to see the usage information.

### In Windows

In Windows, you need to have a Python 2 executable in your `PATH` and use it explicitly to run the scripts.

Examples:

    python receiveworkorders.py
    python postproducts.py -u http://workordersurl:4000/catalogue -f sequencing.txt
