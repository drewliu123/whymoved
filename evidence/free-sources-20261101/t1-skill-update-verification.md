# T1 Skill更新验证

## 变更

新增 `skills/research/references/expectations.md`，主Skill、来源参考、计划模板及fact-collector增加条件读取与执行入口。源码插件及市场manifest从0.3.1升至0.3.2，README同步。未修改产品脚本、schema或历史研究结论；未新增数据连接器。差异快照见 `t1-skill-update.diff`。

## 已执行检查

- `python3 -m unittest discover -s /Users/frankzhang/Desktop/投研助手/tests`：exit 0，105项测试，4.131秒，OK。现有回归测试通过不证明模型在新会话实际执行质量，也不证明新增来源可用。
- manifest JSON解析、0.3.2版本一致、主Skill和相关参考文档的本地Markdown链接检查：exit 0。
- `claude plugin marketplace update touyan-local --json`：exit 0，outcome=ok。
- `claude plugin update touyan@touyan-local --json`：exit 0，scope=user，0.3.1更新至0.3.2；工具要求Restart to apply changes。
- 首次安装全文一致检查：exit 1，仅主Skill不一致。检查差异发现源码在安装后收到并行的写作约束编辑，未回滚或覆盖；T1段落未被改动。
- 针对本次T1更新复查：exit 0，已安装主Skill的T1触发段与源码匹配，新增参考、sources、templates、fact-collector及两个manifest共6个文件逐字节匹配。并行写作约束的缓存同步不属于本次T1安装核验结论。

## 生效范围

安装位置：`/Users/frankzhang/.claude/plugins/cache/touyan-local/touyan/0.3.2/`。

重启/新建加载更新插件的会话，再调用 `/touyan:research`，会读取本次持久化规则。当前会话已经加载的旧Skill/Agent定义不宣称热更新成功。未启动另一个新会话做端到端研究验证。

普通聊天不会自动继承本次会话全部讨论；显式调用研究Skill可确定加载入口，但不能保证每次模型执行绝无遗漏。没有新增自动后台采集、付费授权或数据访问权限。
