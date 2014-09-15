HttpGraphic
===========

使用http方式动态生成缩略图的简单实现
当前只是测试版本 未完善和优化

当前支持请求方式
---------------------------------------
- http://abc.com/image.jpg-100,200 
  指定宽高

- http://abc.com/image.jpg-w100  (还未实现)
  按指定宽度 正比例缩放

- http://abc.com/image.jpg-h100  (还未实现)
  按指定高度 正比例缩放



框架拓扑
---------------------------------------
```
                                                      +-------------+
                                                      |             |
                                                +---> |   Graphic   |
                                                |     |             |
                                                |     +-------------+
                                                |                    
+------------+           +----------------+     +     +-------------+
|            |   cache   |                | upstream  |             |
|   Client   +---------> |  Apache/Nginx  +-----+---> |   Graphic   |
|            |           |                |     |     |             |
+------------+           +----------------+     |     +-------------+
                                                |                    
                                                |     +-------------+
                                                |     |             |
                                                +---> |   Graphic   |
                                                      |             |
                                                      +-------------+

```
(绘图工具 http://asciiflow.com/)


Apache 配置方式
---------------------------------------
```
<VirtualHost *:80>
    DocumentRoot "/YOUR_IMAGE_PATH"
    ServerName image.your_domain.com
    DirectoryIndex index.htm index.html

    #ErrorLog "logs/error.log"
    #CustomLog "logs/access.log" common

    RewriteEngine on

    #指定宽高生成缩略图规则
    RewriteRule ^/([^\.]+\.[jpg|png]+)-([0-9]+),([0-9]+)$ balancer://backend_serv/image/resize?filename=$1&w=$2&h=$3 [P]

    #后端负载服务器
    <Proxy balancer://backend_serv>
       Order deny,allow
       Allow from all
       
       #后端图片处理程序  默认8080端口
       BalancerMember http://127.0.0.1:8080 loadfactor=1
       #BalancerMember http://localhost2:8081 loadfactor=2
       
       #按流量权重
       ProxySet lbmethod=bytraffic
       ProxySet nofailover=On
       ProxySet timeout=15
    </Proxy>
    
    <Location /balancer-manager>
         SetHandler balancer-manager
         Order Allow,Deny
         Allow from all
    </Location>

    <Location /server-status>
         SetHandler server-status
         Order Allow,Deny
         Allow from all
    </Location>
</VirtualHost>
```


Nginx 配置方式
---------------------------------------
```
upstream backend_serv {
   server 127.0.0.1:8080  weight=1;
   #server 127.0.0.1:8080  weight=5;
}

server{
    listen       80;
    server_name  image.your_domain.com;
    index index.html index.htm;
    root  /YOUR_IMAGE_PATH;
    
    #参数未经过优化 请自行调整
    proxy_redirect off;
    proxy_headers_hash_max_size 51200;
    proxy_headers_hash_bucket_size 6400;

    proxy_connect_timeout 30;
    proxy_read_timeout    30;
    proxy_send_timeout    30;
    proxy_buffer_size     32k;
    proxy_buffers         4 32k;
    proxy_busy_buffers_size  64k;
    proxy_temp_file_write_size  1024m;
    proxy_ignore_client_abort on;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP  $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    location / {
    	#指定宽高生成缩略图规则
        if ($request_uri ~* "^/([^\.]+\.[jpg|png]+)-([0-9]+),([0-9]+)$"){
                rewrite "^/([^\.]+\.[jpg|png]+)-([0-9]+),([0-9]+)$" /image/resize?filename=$1&w=$2&h=$3 break;
                proxy_pass http://backend_serv;
        }
    }
}
```