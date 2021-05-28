### 说明
&nbsp;&nbsp;&nbsp;&nbsp;这个脚本可以帮助开发者在本地快速启动一个 Fabric 联盟链网络。可以通过简单的组织名称和节点的配置，就可以实现测试各种不同组织场景下的联盟链网络。

&nbsp;&nbsp;&nbsp;&nbsp;默认情况下，所有的节点均以本地进程的形式启动的，chaincode 是在 docker 容器中启动的，未来还会支持节点和 chaincode 更多的启动方式。
### 环境准备
&nbsp;&nbsp;&nbsp;&nbsp;这里列举了运行这个脚本和 Fabric 联盟链网络所必须依赖的软件环境，请根据自己操作系统的环境自行安装下列软件：
* Golang 环境，chaincode 的 example 默认是使用的是 Go 语言版的，所以需要依赖 Golang 环境编译和打包 chaincode。Golang 版本建议选择 go1.16+
* Docker 环境，chaincode 默认需要运行在 Docker 容器中。
* Python 环境，本脚本基于 Python 3.9 开发，请安装 Python 3.9。
* virtualenv，用于隔离项目的运行环境。

### 下载和初始化

#### 1、将代码 clone 到本地

```shell
git clone https://github.com/ChainDrawn/fabric-easy-dev	
```

#### 2、更新依赖项目

```shell
cd $fabric-easy-dev
git submodule init & git submodule update
```

#### 3、初始化项目

```shell
cd $fabric-easy-dev
。/setup.sh
```

### 使用测试项目

#### 1、启动测试项目

```shell
source venv/bin/activate
python example.py up
```

#### 2、停止并清理测试项目

```shell
python example.py down
```



