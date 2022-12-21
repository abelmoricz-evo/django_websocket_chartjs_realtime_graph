# Django Channels, WebSockets Chart.js

Simple Django Application using WebSockets to create a continuously updated chart.

## Reference

Followed along to this YouTube video.

https://www.youtube.com/watch?v=tZY260UyAiE

NOTE:

* I have to use channels version 3.0.5.  Version 4 did not seem to work
* I have to use channels-redis 3.4.1.  I just assume v4 would not work.

## Redis

channels-layers requires redis.  The easiest way to run this is with docker

```shell
docker run -p 6379:6379 --name django-redis -d redis
```