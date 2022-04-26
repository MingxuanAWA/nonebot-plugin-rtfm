<div align="center">

<!-- prettier-ignore-start -->
<!-- markdownlint-disable-next-line MD036 -->

# nonebot-plugin-rtfm

_✨ NoneBot2 文档搜索插件 ✨_
<!-- prettier-ignore-end -->

</div>

## 🚀安装

_目前暂未发布正式版，安装可通过 git 方式安装_

此插件需要 *Python 3.8 及以上*

_待补充_

## 📝命令

### /rtfm [关键词]

#### 概述

若提供了关键词，则根据关键词进行搜索 NoneBot2 文档，否则进入对话模式获取关键词后搜索

#### 例子

<details>
<summary>图片</summary>

![-ff3a75dd1b3b136.png](https://s2.loli.net/2022/04/26/jBCWS9Z6NvdTJeA.png)

</details>

### /obrtfm [关键词]

#### 概述

若提供了关键词，则根据关键词进行搜索 OneBot 适配器 文档，否则进入对话模式获取关键词后搜索

#### 例子

<details>
<summary>图片</summary>

![-736fa5bfcf4805f2.png](https://s2.loli.net/2022/04/26/Tsn8QrWvODygqwI.png)

</details>

### /page <页码>

#### 概述

查看指定页的文档，来源根据上一次的查询结果的缓存

#### 例子

<details>
<summary>图片</summary>

![1650986335404.png](https://s2.loli.net/2022/04/26/vrdhkiVnTs1w37K.png)

</details>

#### 使用戳一戳

戳机器人会发送下一页文档

<details>
<summary>图片</summary>

![1650986464565.png](https://s2.loli.net/2022/04/26/QWH1ul72O9MGqZm.png)

</details>

## 🔧配置

- rtfm_page
    - 设置一条消息的结果数（默认：5）

## 🚧预期加入功能

- [ ] Python 文档查询
- [ ] 插件文档查询（基于 [`nonebot-plugin-help`](https://github.com/XZhouQD/nonebot-plugin-help) 的文档接入方式）
- [ ] 图片生成（预期使用 [`nonebot-plugin-htmlrender`](https://github.com/kexue-z/nonebot-plugin-htmlrender)）
- [ ] _More..._

## 🐛Bug 反馈或提交建议

请通过 [Issue](https://github.com/MingxuanGame/nonebot-plugin-rtfm/issues) 向我反馈 Bug 或提交建议

## 👥参与开发

_待补充_

## 🔒️许可

本插件使用 [MIT 协议](https://github.com/MingxuanGame/nonebot-plugin-rtfm/blob/master/LICENSE) 开源

```
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
