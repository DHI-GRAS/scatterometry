# Scatterometry clients

## CLI
The CLI client:
* Accepts the request query parameters
* Breaks the user parameters to multiple requests in accordance with from the API limits
* Makes the requests, downloads the files with the data and finally returns a single file with all the data

### Usage
```bash
# Install the dependencies
pip install -r requirements.txt

# Use the parallel version
python scatterometry-cli-parallel.py --api-key <your_api_key>

# Use the sequential version
python scatterometry-cli.py --api-key <your_api_key>
```
