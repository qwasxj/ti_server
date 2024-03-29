# Tidb_auto_test

## Profile：
    * Tidb_auto_test is a auto test framework for Tidb
    
## Illustration

### 命令：
ti-serverControl 脚本执行 (在项目 bin 路径下运行即可)

    * python3 ti_server_control.py control -a start -c 
    /root/ti_server/config/ti_server.ini
    
    后续： 
    * tidb  -a start -c /root/ti_server/config/ti_server.ini
    
    最终 ti-server 由脚本控制安装，用户不感知
    
    * -a --action 用于控制 ti_server 测试框架起停的, 值有: start, stop, restart
    * -c --config 指定配置文件路径的


使用 ti-server 测试 TiDB 数据库测试用例示例

    python3 ti.py run --workspace /root/tiDB --regex ti_test_plugin
    .bank_transfer

    最终：
    * ti run --workspace workspace_path --regex test_match_string
    
    * run, 运行 TiDB 测试用例的; 现阶段仅有 run 命令
    * --workspace 测试用例工作区间（后续可以对接各个 TiDB 测试插件）
    * --regex 指定 TiDB 测试路径匹配字符串

### 日志路径说明
ti-server 测试框架日志路径: /var/log/ti_server, 其下面有：
    ti-serverControl 控制脚本日志
    ti-server TiDB 测试框架日志

   
用户测试用例日志由用户 workspace 路径指定， 在 workspace 的 test.log 里 


### 其他框架说明
* ti-server 是 TiDB 测试框架, TiDB 自动化测试用例独立于测试框架成为单独的项目
* ti-server 框架会自动加载 TiDB 自动化测试用例插件，通过指定命令运行测试用例即可
* 后续可以配置 Jenkins， 做成流水线测试
* 现阶段仅仅测试单个银行转账用例，未做其他功能，不涉及用户工作空间配置问题
