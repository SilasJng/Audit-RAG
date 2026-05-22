# Wiki 页面约定

## 页面类型

### generated

用途：把 JSON 记录导出成 Markdown 导航。

规则：

- 只读。
- 必须标明来源 JSON 路径和 record id。
- 不加入新的事实判断。
- 可链接到 `concepts/` 和 `queries/`。

### concepts

用途：解释一个漏洞家族、判断框架或跨案例联系。

推荐结构：

- 一句话定义
- 为什么重要
- 成立条件
- 常见变体
- 常见误报
- 证据来源
- 验证路线
- 相关页面

### queries

用途：沉淀可复用审计查询和 triage 路线。

推荐结构：

- 适用场景
- 输入材料
- audit-rag 查询
- 当前代码阅读动作
- PoC/单测路线
- 降级/放弃条件

### active

用途：活跃审计临时笔记。

规则：

- 必须写 `status: provisional` 或在正文显著标注。
- 不直接进入 `data/normalized/`。
- 只有 final report、judge/sponsor 反馈或用户确认后，才可重新审校并 promotion。

## 链接规范

- Obsidian 双链格式：`双左括号 + 页面路径 + 竖线 + 显示名 + 双右括号`。本 POC 可参考 `index.md` 里的真实链接。
- normalized id 用反引号：`soroban-require-auth-entrypoint-bypass-pattern`
- 文件路径用反引号：`data/normalized/...json`

## 禁止

- 把 generated 页当成事实源手改。
- 把未确认 active lead 写成正式概念。
- 用 wiki 搜索替代 `hybrid_search.py` / eval regression。
- 批量生成几百页但没有 index、log、broken-link 检查。
