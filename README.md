# mxdown
Check how much load your MX server can handle

To disable debug, please remove `-vvv`

Example:
```shell
./maildown.py --host yourdomain.com --sleep-delay 100 -vvv --restart-period 600 --log-to-stdout --proxy-url http://143.244.166.15/proxy.list --concurrency 1
```

```shell
docker run -it 7d05576ba889  --host yourdomain.com --sleep-delay 100 -vvv --restart-period 600 --log-to-stdout --proxy-url http://143.244.166.15/proxy.list --concurrency 1
```