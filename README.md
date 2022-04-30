<p align="center">
  <img src="https://s2.loli.net/2022/05/01/fbZuQPidkqt6vjp.png">
</p>

<div align="center">

<!-- prettier-ignore-start -->
<!-- markdownlint-disable-next-line MD036 -->

# nonebot-plugin-rtfm

_✨ NoneBot2 文档搜索插件 ✨_
<!-- prettier-ignore-end -->

</div>

## 🚀安装

此插件需要 **Python 3.8 及以上**

```bash
# 通过 nb-cli
nb plugin install nonebot-plugin-rtfm
# 通过 poetry
poetry add nonebot_plugin_rtfm
# 通过 pip
pip install nonebot_plugin_rtfm
```

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

### /插件列表

#### 概述

获取商店里的全部插件的简要信息，支持 `/page` 和 `戳一戳`

#### 例子

<details>
<summary>图片</summary>

![_J_T~YS6NJDRF61__6_8M~4.png](https://s2.loli.net/2022/04/27/lmLwqRY86yesfAM.png)

</details>

### /搜索插件 <关键字> [-t] [-n] [-a] [-d] [-p=[0-1]]

**WIP：此功能尚未完成**

#### 概述

搜索插件列表的插件，支持 `/page` 和 `戳一戳`

#### 参数

- `-t`，`--without_tag` 查询时不使用标签查询
- `-n`，`--without_name` 查询时不使用插件名称查询
- `-a`，`--without_author` 查询时不使用作者名查询
- `-d`，`--without_desc` 查询时不使用描述查询
- `-p=[0-1]`，`--percent=[0-1]` 相似度，越接近1相似度越高

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
- use_proxy
  - 使用 `jsdelivr` 源获取插件信息（默认：True）

## 🚧预期加入功能

- [ ] Python 文档查询
- [ ] 插件文档查询（基于 [`nonebot-plugin-help`](https://github.com/XZhouQD/nonebot-plugin-help) 的文档接入方式）
- [ ] 图片生成（预期使用 [`nonebot-plugin-htmlrender`](https://github.com/kexue-z/nonebot-plugin-htmlrender)或 `PIL`）
- [ ] _More..._

## 🐛Bug 反馈或提交建议

请通过 [Issue](https://github.com/MingxuanGame/nonebot-plugin-rtfm/issues) 向我反馈 Bug 或提交建议

## 👥参与开发

_待补充_

## 🔒️许可

本插件使用 [MIT 许可证](https://github.com/MingxuanGame/nonebot-plugin-rtfm/blob/master/LICENSE) 开源

```
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
