![cover-v5-optimized](./dify_on_aws.svg)

<p align="center">
  <a href="https://github.com/aws-samples/dify-aws-tool/blob/main/workflow/README.md">Demos</a> ·
  <a href="https://github.com/aws-samples/dify-aws-tool/blob/main/dify.yaml">Deploy Dify With CloudFormation</a> ·
  <a href="https://github.com/aws-samples/solution-for-deploying-dify-on-aws">Deploy Dify on EKS</a> ·
</p>

<p align="center">
  <a href="https://github.com/langgenius/dify">
    <img src="https://img.shields.io/badge/Powered%20by-Bedrock-277E68" alt="Powered by Bedrock">
  </a>
  <a href="https://aws.amazon.com/">
    <img src="https://img.shields.io/badge/Powered%20by-SageMaker-8750F5" alt="Powered by SageMaker">
  </a>
  <a href="https://aws.amazon.com/">
    <img src="https://img.shields.io/badge/Powered%20by-AWS%20Tools-F37D0B" alt="Powered by S3">
  </a>
</p>

<p align="center">
  <a href="./README_ZH.md"><img alt="简体中文版自述文件" src="https://img.shields.io/badge/简体中文-d9d9d9"></a>
  <a href="./README.md"><img alt="README in English" src="https://img.shields.io/badge/English-d9d9d9"></a>
  <a href="./README_JA.md"><img alt="日本語のREADME" src="https://img.shields.io/badge/日本語-d9d9d9"></a>
</p>

## 📋 はじめに

このリポジトリでは、Difyの3つのプラグイン：Bedrock Model Provider、SageMaker Model Provider、およびAWS Toolsのソースコード、並びにDifyユーザーとAWSユーザー向けの参考となる関連ワークフローとデモを提供しています。

## ⚙️ 前提条件

- Dify環境（AWS CloudFormationを使用してワンクリックでデプロイ可能 - [dify.yaml](./dify.yaml)）
  本番環境へのデプロイについては、ソリューション例 [Dify-on-EKS](https://github.com/aws-samples/solution-for-deploying-dify-on-aws) を参照してください
- AWSアカウントとAWSの使用経験
- 基本的なLinux環境の使用経験

## 🧰 技術リソース

### ワークフロー ([デモページ](./workflow/README.md))

| 名前 | 説明 | リンク | 依存関係 | 担当者 |
|------|------|------|------|------|
| Term_based_translate | 用語マッピングを含む翻訳ワークフロー | [DSL](./workflow/term_based_translation_workflow.yml) | Tool(用語マッピング) | [ybalbert](ybalbert@amazon.com) |
| Code_translate | 異なるコードタイプ間の翻訳ワークフロー | [DSL](./workflow/claude3_code_translation.yml) | | [binc](binc@amazon.com) |
| Basic_RAG_Sample | カスタムリランクノードを含む基本的なRAGワークフロー例 | [DSL](./workflow/basic_rag_sample.yml) | Tool(Rerank) | [ybalbert](ybalbert@amazon.com) |
| Andrewyng/translation-agent | Andrew Ngの翻訳エージェントの再現 | [DSL](./workflow/andrew_translation_agent.yml) | | [ybalbert](ybalbert@amazon.com) |
| rag_based_bot_with_tts | 音声応答機能を持つRAGベースのボット | [DSL](./workflow/rag_based_bot_with_tts.yml) | Tool(TTS) | [ybalbert](ybalbert@amazon.com) |
| s3_rag | シンプルなS3ベースのRAG、ベクターデータベース不要 | [DSL](./workflow/s3_rag.yml) | S3 Operator | [ybalbert](ybalbert@amazon.com) |
| Marketing-copywriter | エンドツーエンドのマーケティングコピーライティング | [DSL](./workflow/marketing-copywriting.yml) | | [Lyson Ober](https://www.youtube.com/@lysonober) |
| Simple_Kimi | シンプルなDIY Kimi | [DSL](./workflow/simple_kimi.yml) | | [ybalbert](ybalbert@amazon.com) |
| SVG_Designer | SVGアイコンデザイナー | [DSL](./workflow/svg_designer.yml) | | [Li Jigang](https://waytoagi.feishu.cn/wiki/TRlTwxCFJis292kNAzEc9D4BnvY) |
| Education_Question_Gen | 教育シナリオ - 問題生成器 | [DSL](./workflow/edu_question_gen.yml) | | [chuanxie](chuanxie@amazon.com) |
| Apply_guardrails | 安全ガードレールを備えたチャットワークフロー | [DSL](./workflow/apply_guardrails.yml) | | [amyli](amyli@amazon.com) |
| LLM-Finetuning-Dataflow | LLMファインチューニングデータ合成ワークフロー | [DSL](./workflow/LLM-Finetuning-Dataflow-dify) | [finetuning-on-aws](https://github.com/tsaol/finetuning-on-aws/tree/main) | [caoliuh](caoliuh@amazon.com) |
| Image/Video Generation Workflow | Amazon Nova CanvasとReelに基づく画像と動画の生成 | [DSL](./workflow/generate_image_video.yml) | | [alexwuu](alexwuu@amazon.com) |
| EKS Upgrade Planning | EKSクラスター情報を収集しアップグレード計画を生成 | [DSL](./workflow/eks_upgrade_planning/eks_upgrade_planning.yml) | | [wxyan](wxyan@amazon.com) |
| Amazon S3 powered DMS with chatbot Capabilities| Nextcloud 統合のための RAG ベースのボット | [DSL](./workflow/rag_based_chatbot_for_nextcloud.yml) | | [tanzhuaz](tanzhuaz@amazon.com) |
| チャットボット機能を備えた Amazon S3 で動作する DMS | Nextcloud 統合のための RAG ベースのボット | DSL（ドメイン固有言語） | | [tanzhuaz（tanzhuaz@amazon.com）] |
| ASR_Transcribe | 音声をテキストに変換 | [DSL](./workflow/ASR_Transcribe.yml) | | [ybalbert](ybalbert@amazon.com) |
| Image(Text)-2-Image Search | 画像検索（テキストから画像、画像から画像） | [DSL](./workflow/opensearch_img_search.yml) | OpenSearch Knn Retriever | [ybalbert](ybalbert@amazon.com) |
| MCP サーバー統合 | MCP サーバー統合デモ | [DSL](./workflow/mcp_server_integration.yml) |  | [ybalbert](ybalbert@amazon.com) |

> 💡 より多くのワークフローについては、コミュニティサイトをご覧ください: [dify101.com](https://dify101.com/)、[difyshare.com](https://difyshare.com/)、[Awesome-Dify-Workflow](https://github.com/svcvit/Awesome-Dify-Workflow)

### 拡張ツール

| ツール名 | ツールタイプ | 説明 | デプロイドキュメント | 担当者 |
|---------|---------|------|---------|-------|
| Rerank | PAAS | テキスト類似性ランキング | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-reranker-v2-m3-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |
| TTS | PAAS | テキスト音声合成 | [Code](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook/cosyvoice) | [ybalbert](ybalbert@amazon.com) |
| Bedrock Guardrails | SAAS | Amazon Bedrock GuardrailのスタンドアロンApplyGuardrail APIを通じて実装されたテキストモデレーションツール | | [amyli](amyli@amazon.com) |
| Term_multilingual_mapping | PAAS | 単語分割/用語マッピング | [Repo](https://github.com/ybalbert001/dynamodb-rag/tree/translate) | [ybalbert](ybalbert@amazon.com) |
| Image Translation Tool | PAAS | 画像内のテキストを翻訳 | Coming | [tangqy](tangqy@amazon.com) |
| Chinese Toxicity Detector | PAAS | 中国語の有害コンテンツ検出 | Coming | [ychchen](ychchen@amazon.com) |
| Transcribe Tool | SAAS | AWS transcribeサービスツール (ASR) | | [river xie](chuanxie@amazon.com) |
| Bedrock Retriever | PAAS | Amazon Bedrockナレッジベース検索ツール | | [ychchen](ychchen@amazon.com) |
| S3 Operator | SAAS | S3バケットのコンテンツの読み書き、署名付きURLの返却が可能 | | [ybalbert](ybalbert@amazon.com) |
| AWS Bedrock Nova Canvas | SAAS | Amazon Nova Canvasに基づく画像生成 | | [alexwuu](alexwuu@amazon.com) |
| AWS Bedrock Nova Reel | SAAS | Amazon Nova Reelに基づく動画生成 | | [alexwuu](alexwuu@amazon.com) |
| OpenSearch Knn Retriever | PAAS | KNN手法を使用してOpenSearchからデータを検索 | [Notebook](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook/search_img_by_img) | [ybalbert](ybalbert@amazon.com) |

### モデルプロバイダー

| モデル名 | モデルタイプ | デプロイドキュメント | 担当者 |
|---------|---------|---------|-------|
| オープンソースLLM全般 | SageMaker\LLM | [Model_hub](https://github.com/aws-samples/llm_model_hub) | [ybalbert](ybalbert@amazon.com) |
| Bge-m3-rerank-v2 | SageMaker\Rerank | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-reranker-v2-m3-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |
| Bge-embedding-m3 | SageMaker\Embedding | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/bge-embedding-m3-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |
| CosyVoice | SageMaker\TTS | [Code](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook/cosyvoice) | [ybalbert](ybalbert@amazon.com) |
| SenseVoice | SageMaker\ASR | [Notebook](https://github.com/aws-samples/dify-aws-tool/blob/main/notebook/funasr-deploy.ipynb) | [ybalbert](ybalbert@amazon.com) |

> **📌 重要な注意事項**
>
> DifyのSageMaker LLM Providerはほとんどのオープンソースモデルをサポートしています。これらのモデルをデプロイするには[Model_hub](https://github.com/aws-samples/llm_model_hub)の使用をお勧めします。非常に使いやすく、コードなしでモデルのファインチューニングとデプロイをサポートしています。[Model_hub](https://github.com/aws-samples/llm_model_hub)をインストールしたくない場合は、[ガイド](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook/llm_sagemaker_deploy)を参照して、vllmを使用してLLMをSageMakerにデプロイすることもできます。
>
> Embedding/Rerank/ASR/TTSモデルをDify Sagemaker Model Providerに追加したい場合は、まずAmazon SageMakerにデプロイする必要があります。デプロイについては、対応する[ノートブック](https://github.com/aws-samples/dify-aws-tool/tree/main/notebook)を参照してください。

## 🔧 使用上の注意

### ヘルプの取得

- リポジトリのIssuesページで問題を提起する
- 内部Larkグループに相談する

![qr](./QR_Lark.png)

### 貢献方法

- このリポジトリをフォークし、マージリクエストを提出する
- README.mdを更新し、あなたの成果（ワークフローやツールなど）を適切な表に追加する

## 📚 追加資料

### デモ動画

- [Dify 1.0.0リリース & AWSプラグイン適応](https://aws.highspot.com/items/67c2e250ac191e72528d176d?lfrm=rhp.0)
- [DifyでAWSのDeepSeekモデルを使用する方法（わずか5分）](https://mp.weixin.qq.com/s/psY6m9xUNce4QIyksKvapg)
- [DifyとModel Hubの統合による主流オープンソースモデルの実現](https://mp.weixin.qq.com/s/t023tUS7QGb9CzFK40YVYw)
- [Difyネイティブコンテンツレビュー拡張APIがBedrock Guardrailを呼び出して責任あるAIアプリケーションを構築](https://amazon.awsapps.com/workdocs-preview/index.html#/document/1c6e65aa34790cbcbdd74871369ca1b079f2eb5a3d044d614c6cf4f622f56468)
- [最新のBedrock C3.5-V2に基づくKimiを構築する3つのステップ](https://mp.weixin.qq.com/s/_2obKrn849a6jOxML_8Btw)
- [AWSサービスをDifyに統合するツール](https://mp.weixin.qq.com/s/ZZK4Qh0kcnlZHIdO82nVZA)
- [DifyとSageMaker ASR/TTSの統合](https://mp.weixin.qq.com/s/g2aey251YPk-tekL1uc_nw)

### 関連ブログ/ドキュメント

- [API拡張を通じてDifyでAmazon Bedrock Guardrailを使用し、チャットアプリケーションにコンテンツレビュー安全ガードレールを追加する](https://amzn-chn.feishu.cn/docx/PhNbdiDRDoj8vlxIDjAcKBlVncb)
- [DifyとAWSサービスを統合してより柔軟な翻訳ワークフローを実現](https://br5879sdns.feishu.cn/docx/Osehd7t5ZocVocxhtQycBHDCnfb)
- [DifyでAWSのDeepSeekモデルを使用する](https://amzn-chn.feishu.cn/docx/BtLHdxaG5o9xL6xXZcyciZUCn0f)

### ハンズオンラボ

- [Difyで迅速にGenAIアプリを構築する](https://catalog.us-east-1.prod.workshops.aws/workshops/2c19fcb1-1f1c-4f52-b759-0ca4d2ae2522/zh-CN)
- [Siliconflow+DeepSeek+Dify workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/87e070e2-5621-4c94-9285-529514ec4454/en-US)