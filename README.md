# 芦砚声学材料权衡册

把不同量纲的机构材料试样，放进可复算的多准则权衡；保留每次偏好权重变化，再由负责人审阅试样验证计划。

## 研究室里的工作

芦砚声学材料研究室有13位产品研究员，为展厅、会议室与薄型走廊研发声学板样。上游检测组提供 `LYM_20261112_试样汇总.csv`，记录36份匿名机构试样的吸声、耐冲击、碳强度、单位面积单价和厚度。研究员过去手工把量纲不同的列相加，成本方向偶尔写反；改了一组权重后排名变动很大，纪要却只留下第一名。

本册替代“核对数据/方向→写明偏好→权衡与敏感性→提出验证问题→审阅分发”这一段。下游实验员收到已批准的试样计划CSV，开展独立湿热、吸声与冲击复测。候选排名不等于合格率，系统不采集真实供应商报价，不作采购建议。

| 角色 | 页面 | 权限 | 典型动作 |
|---|---|---|---|
| admin 试样负责人 | 全部六页 | 读写、排队、提出/批准/退回计划、导出 | 同意独立湿热复测，留下条件批注 |
| analyst 产品研究员 | 全部六页 | 研究/试样/指标写入、排队、提交计划、导出已批准计划 | 核对benefit/cost，比较权重情景 |
| viewer 研发观察员 | 全部六页 | 只读及下载已批准计划；写入与审阅403 | 阅读研究边界，分发试样安排 |

本地账号：`admin@luyan.local`、`analyst@luyan.local`、`viewer@luyan.local`；共同密码 `Luyan2026!`。

## 一天如何使用

1. 09:00 林砚用analyst登录，打开 `LY-BAL 芦芯展厅 · 均衡权衡`，查看36份试样的真实单价/吸声散点。
2. 09:05 到“试样与口径”核对候选集合与原始记录。吸声系数αw、耐冲击kJ/m²越大越优；碳强度kgCO₂e/m²、单价元/m²、厚度mm越小越优。
3. 09:15 核对中心权重：吸声0.30、冲击0.20、碳0.20、单价0.20、厚度0.10。另两套研究为 `LY-CARBON 低碳会议室 · 碳优先` 和 `LY-THIN 薄型走廊 · 厚度约束`，共享36份试样，各有5条独立指标口径。
4. 09:20 配置集中度κ=40、seed=20261112、1000情景，命名后点击“冻结并排队计算”。研究冻结候选、原始值、方向、中心权重，worker真实计算。
5. 09:22 阅读LY23麻纤复合毡·11：中心贴近度0.69612994、名次1；LY10芦芯纤维板·10为0.67426986、名次2。选中材料可查看原始、L2标准化、加权、正负理想点及两段距离。
6. 09:25 切换“权重情景名次”。LY23在1000情景中的实际最好/最差为1/27，2.5%–97.5%经验分位1–15，首位分摊频率44.7%；LY10对应首位分摊40.8%。这描述偏好变化，不是最优材料的后验概率。
7. 09:30 查看全部40页情景留档，每页25次；每次保留5个权重、36份贴近度/平均名次及并列首位分摊。
8. 09:40 提出“LY23湿热条件吸声复测”，把权衡中的取舍、复测条件与原始报告要求写进计划。余芦用admin审阅，说明采购另行审议。
9. 10:00 季乔用viewer下载 `trial-note-<id>.csv`，含审批、方案、快照指纹、5项中心权重及36份摘要。新检测结果回资料库后需另建任务，旧结果不改写。
10. 10:20 检测组修订LY23的吸声复测值。系统按源数据指纹把引用该试样的已完成权衡标为“源数据已过期”，列出受影响试样、字段与新旧值；林砚在权衡配置页点“按原偏好批量重算”，每项过期权衡按原中心权重、κ、seed与情景数生成一条重算版本（`recalc_of`指向原始任务）。重复点同一批修订不会新增任务；某条重算失败时可在原任务上重试，失败前后旧的已批准计划CSV都能正常下载。结果页新增“新旧权衡对照”页签，可比较两版名次、贴近度与首位份额变化。

以上数值来自固定seed真实计算；seed只插入输入，不预置模型结果。

## 运行

```bash
cp .env.example .env
docker compose config --quiet
docker compose up -d --build
docker compose ps
docker compose exec -T backend python -m scripts.seed_demo
```

前端 `http://localhost:18227`，后端API文档 `http://localhost:19227/docs`；MySQL `localhost:17727`，库/用户 `material`，密码见 `.env.example`。健康接口 `/health` 同时检查数据库与Redis。

`SEED_DEMO=true` 后端启动时尝试插入演示输入，失败记日志不阻塞。自然键为研究code、全局试样code、指标study_id+code、账号email；重复seed不覆盖研究候选集合/背景、测量值/名称、方向/中心权重，不创建额外计算。默认3研究、36试样、15指标、3角色账号。

来源文件名是溯源元数据。材料可逐份录入/编辑，也可通过API批量调用；未实现任意CSV自动解析或真实检测设备采集。共享资料库修改会影响未来任务，已经提交的冻结快照保持原样。

## 五服务与技术栈

| 服务 | 技术/职责 | 健康条件 |
|---|---|---|
| frontend | Vue3.5.45、Pinia2、Vue Router4、TypeScript、Vite6.4.6 / Nginx1.27 | 127.0.0.1 HTTP |
| backend | Python3.11、FastAPI0.115.6、SQLAlchemy2、PyJWT | SQL SELECT1和Redis ping |
| worker | 同后端镜像，数据库队列扫描/Redis唤醒，单进程数值计算 | 30秒内心跳 |
| db | MySQL8，命名数据卷 | TCP mysqladmin ping |
| redis | Redis7 AOF，队列唤醒/登录限流 | redis-cli ping |

恰好5服务，frontend/backend/worker依赖上游healthy；DB、Redis与共享 `/artifacts` 使用命名卷。MySQL测量值、Criterion.center_weight、DecisionRun.concentration 均显式 `DOUBLE(asdecimal=False)`，不使用默认FLOAT或Decimal截断。完整快照、1000情景及结果采用JSON。Nginx `/api/` 剥离一次前缀，Python路由不再带 `/api`。

| 环境变量 | 用途 / 默认 |
|---|---|
| COMPOSE_PROJECT_NAME | `material-topsis`，容器名前缀 |
| FRONTEND_PORT / BACKEND_PORT / DB_PORT | 18227 / 19227 / 17727 |
| DB_PASSWORD | `material-demo-local`，仅本地示例 |
| JWT_SECRET | 本地示例，部署前改为独立随机键 |
| SEED_DEMO | true，启动插入缺失演示资料 |
| DATABASE_URL / REDIS_URL | Compose内部地址；本地可覆盖 |
| OMP_NUM_THREADS / OPENBLAS_NUM_THREADS | 1，限制数值线程 |

JWT有效8小时，PBKDF2-SHA256密码哈希。角色授权、写入/审批/导出审计、统一错误处理、登录每IP每分钟30次限流。单任务2–120候选、1–5指标、1000–2000情景，UI固定1000；最多3项排队/运行任务。数据库是任务状态的权威来源，即使Redis唤醒失败也会扫描执行；单worker中断后按原快照复算。

## 算法与边界

先把每列用L2范数标准化。中心原始权重全正，除以权重和。对加权矩阵V，benefit列正理想点取最大、负理想点取最小；cost列反向：

```text
r_ij = x_ij / sqrt(sum_i x_ij²)
v_ij = w_j * r_ij
D_i+ = EuclideanDistance(v_i, positive ideal)
D_i− = EuclideanDistance(v_i, negative ideal)
C_i = D_i− / (D_i+ + D_i−)
```

实现先按列最大绝对值缩放再平方，避免极小单位平方下溢；距离也用缩放范数。零范数列明确置零，非零常量列保留标准化值但不贡献区分，权重都保留并逐列记录。只有实际距离同时为0才令C=.5；不以绝对epsilon抹平可表示的小距离。贴近度计算值完全相等时取平均并列名次，并列首位均分一份，不按试样编号假装偏好。

默认独立生成1000个 `Dirichlet(alpha = normalized_center * kappa)` 权重情景，用相同原始矩阵/方向重新计算TOPSIS；有限精度抽样可能含0分量，它是合法的非负情景权重，不能按中心权重的全正要求误拒。全零情景权重、非有限权重无法计算，正中心与κ乘积下溢不可表示时给明确失败原因。随机数参考 [NumPy Generator.dirichlet](https://numpy.org/doc/2.1/reference/random/generated/numpy.random.Generator.dirichlet.html)，范数定义参考 [NumPy norm](https://numpy.org/doc/2.1/reference/generated/numpy.linalg.norm.html)。

每次保留权重、所有材料贴近度/平均名次/首位份额，汇总真实最好/最差、频率与2.5%/97.5%经验名次分位（线性插值可为小数）。κ控制偏好分散程度，不是样本量。范围是人为偏好情景的敏感性描述，不是统计置信区间、贝叶斯后验或采购建议。没有用真实人群抽样估计偏好。

所有指标为有限非负物理值，使用本册规定单位与范围；未实现自动单位换算、碳抵消记账或缺测插补。正比例换单位在数值精度范围内不改变结果，指标平移通常不保持；候选增删会改变范数和理想点，可能逆转原候选排名。贴近度和排名仅相对于当前候选与口径，不能直接跨研究比较为绝对品质。

SHA256覆盖算法版本、完整冻结快照、原始中心权重、κ、情景数和seed。固定软件与输入可完整复算，结果同时存数据库和 `/artifacts/run-<id>.json`。指纹包含数据库ID，重建库或改变来源标识不保证相同指纹。运行列表只返回轻量摘要；详情按需读取完整情景，避免轮询反复搬运大JSON。

## 源数据修订与过期权衡

每份任务在冻结时另存**源数据指纹与签名**（候选试样五项测量值、研究指标口径、候选集合的规范化哈希，测量值统一按双精度数值比较，不受JSON文本存储的 `1`/`1.0` 差异影响）。共享资料库或指标口径被修订后，读取任务时实时比对当前源数据：

- `GET /runs/stale`（可按 `study_id` 过滤）返回每项已完成/失败任务的过期状态、受影响试样与指标清单（含字段级新旧值、`affected_sample_ids`）、当前指纹与冻结指纹。无指纹的历史任务不判过期。
- 重算沿用原始任务的中心权重、κ、seed、情景数与研究，只替换为当前快照，生成版本链上的新任务（`recalc_of_id` 指向原始任务、`recalc_seq` 递增）。原始任务的结果、快照与已批准试样计划**永不改写**，新旧版本可在结果页“新旧权衡对照”页签逐项比较名次与贴近度变化。
- 幂等：同一修订对同一原始任务只存在一条活动/最新重算；对已是最新的链再次调用直接返回该版本，不新增任务。`POST /runs/{id}/recalculate` 为单项，`POST /runs/recalculate` 为批量（返回 `queued/skipped/up_to_date` 三类，活动任务达上限的条目进入 `skipped` 而非整体失败）。
- 失败的重算保留失败原因，`POST /runs/{id}/retry` 在**同一任务行**上重置重试，不产生新任务；重算失败不影响旧任务与已批准计划，失败前后 `trial-note` 导出均正常。
- 仅 admin/analyst 可发起重算与重试，viewer 只读（403）。审计中间件自动记录这些写操作。
- 升级既有数据库：启动时的幂等 schema guard 会补齐 `source_fingerprint/source_signature/recalc_of_id/recalc_seq/recalc_status` 五列，也可手动执行 `migrations/002_run_recalculation.sql`。

## 工程结构与开发

```text
backend/src/{models,schemas,services,controllers,routes}  五个独立业务链
backend/src/services/{normalization,topsis,weight_sensitivity,staleness_service}.py
backend/src/{config,constants,middlewares,utils}/
backend/{scripts/seed_demo.py,migrations/001_initial.sql,migrations/002_run_recalculation.sql}
frontend/src/{api,stores,types,constants,components/common,hooks,pages,router,utils}/
```

CandidateStudy、MaterialSample、Criterion、DecisionRun、TrialNote分别有独立model/schema/service/controller/route/API。studyStore管理研究及指标、sampleStore管理资料、researchStore管理任务/计划；六页为总览、输入口径、配置、结果、审阅、审计，登录另计。StudySelect复用于总览/输入/配置，PageHeading、ErrorNotice、StatusBadge等共享；RunSelect、WeightStrip、RankIntervals负责业务展示。

共享枚举Role、RunStatus、NoteStatus、Direction、MetricCode位于 `backend/src/constants/enums.py` 与 `frontend/src/constants/enums.ts`（类型联集在 `frontend/src/types/domain.ts`）；被auth依赖、criterion/note schema、services/worker状态、前端状态组件、口径与运行/结果/审阅页使用。

```bash
# 项目根目录
docker compose up -d db redis
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='mysql+pymysql://material:material-demo-local@localhost:17727/material?charset=utf8mb4'
export REDIS_URL='redis://localhost:6379/0'
export SEED_DEMO=true
uvicorn src.main:app --host 0.0.0.0 --port 19227
# 另一终端在backend同一虚拟环境和配置下
python -m src.worker
# frontend另一终端
npm ci
npm run dev -- --port 18227
```

Vite开发代理19227并剥离一次 `/api`。本地worker需可写 `/artifacts`，默认推荐Compose共享卷。metadata.create_all创建缺表；迁移目录给出初始DDL供审阅，不提供生产版本升级器。字体Google Fonts Noto Sans SC与ZCOOL XiaoWei，离线回退Georgia/serif。

真实测试、截图、手算oracle、权限、seed与已知差异存于批次独立 `test-artifacts/gb-0023`。收尾 `docker compose down -v --remove-orphans` 会删除本题数据库、Redis和结果卷。MIT License。
