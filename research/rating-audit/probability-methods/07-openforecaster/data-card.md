---
language:
- en
license: mit
size_categories:
- 10K<n<100K
task_categories:
- text-generation
- question-answering
tags:
- forecasting
- question-answering
- retrieval-augmented-generation
- news
- bayesian-reasoning
dataset_info:
  features:
  - name: qid
    dtype: string
  - name: question_title
    dtype: string
  - name: background
    dtype: string
  - name: resolution_criteria
    dtype: string
  - name: answer_type
    dtype: string
  - name: answer
    dtype: string
  - name: url
    dtype: string
  - name: article_maintext
    dtype: string
  - name: article_publish_date
    dtype: string
  - name: article_modify_date
    dtype: string
  - name: article_download_date
    dtype: string
  - name: article_description
    dtype: string
  - name: article_title
    dtype: string
  - name: data_source
    dtype: string
  - name: news_source
    dtype: string
  - name: resolution_date
    dtype: string
  - name: question_start_date
    dtype: string
  - name: prompt
    dtype: string
  - name: prompt_without_retrieval
    dtype: string
  splits:
  - name: train
    num_bytes: null
    num_examples: 52183
  - name: validation
    num_bytes: null
    num_examples: 207
  - name: test
    num_bytes: null
    num_examples: 302
  - name: skysports2025
    num_bytes: null
    num_examples: 1788
  - name: aljazeeraLate2025
    num_bytes: null
    num_examples: 491
  - name: aljazeera2026Q1
    num_bytes: null
    num_examples: 330
  - name: aljazeera2026Q2
    num_bytes: null
    num_examples: 635
  - name: futureSim2026Q2
    num_bytes: null
    num_examples: 378
arxiv: 2512.25070
---

# OpenForesight Dataset


[![Paper](https://img.shields.io/badge/arXiv-2512.25070-b31b1b.svg)](https://arxiv.org/abs/2512.25070)
[![Blog](https://img.shields.io/badge/Blog-Read%20More-orange)](https://openforecaster.github.io/)
[![Model](https://img.shields.io/badge/🤗%20Model-OpenForecaster--8B-green)](https://huggingface.co/nikhilchandak/OpenForecaster-8B)

<!-- [**Project Page**](https://openforecaster.github.io) | [**Paper**](https://huggingface.co/papers/2512.25070) | [**GitHub**](https://github.com/OpenForecaster/scaling-forecasting-training) -->

Dataset of forecasting questions generated from news articles with retrieval-augmented prompts, designed to evaluate language models' ability to make predictions about future events using relevant context.

**UPDATE Jul 23, 2026:** Added `aljazeera2026Q2` split with 635 new forecasting questions generated from Al Jazeera articles (Apr–Jun 2026). See [AlJazeera 2026 Q2 Split](#aljazeera-2026-q2-split) for details.

**UPDATE Apr 30, 2026:** Added `aljazeera2026Q1` split with 330 new forecasting questions generated from Al Jazeera articles (Jan–Mar 2026). See [AlJazeera 2026 Q1 Split](#aljazeera-2026-q1-split) for details. *Note that this is a relatively hard subset generated using adversarial filtering.* 

**UPDATE Mar 24, 2026:** Added `aljazeeraLate2025` split with 491 new forecasting questions generated from Al Jazeera articles (late 2025). See [AlJazeera Late 2025 Split](#aljazeera-late-2025-split) for details.

**UPDATE Feb 25, 2026:** Added `skysports2025` split with 1,788 new sports forecasting questions generated from Sky Sports (from articles in May 2025 - Dec 2025).

## Benefits of OpenForesight

|   |   |
|:----------------------------:|:-------------------------------:|
| ![Accuracy](assets/accuracy_trainsamples_llama-3.1-8b.png) | ![Brier Score](assets/brier_scores_trainsamples_llama-3.1-8b.png) |

Training Llama-3.1-8B-Instruct on increasing number of samples from **OpenForesight** leads to continued improvements, making it surpass Qwen3-235B, DeepSeek v3, and almost match R1! 




## Dataset Overview

This dataset contains **56,314** forecasting questions across eight splits:
- **Train**: 52,183 questions (Jan 2024 - April 2025)
- **Validation**: 207 questions (July 2025)
- **Test**: 302 questions (May 2025 to August 2025)
- **Skysports2025**: 1,788 questions (May 2025 - December 2025)
- **AlJazeeraLate2025**: 491 questions (September 2025 - December 2025)
- **AlJazeera2026Q1**: 330 questions (January 2026 - March 2026)
- **AlJazeera2026Q2**: 635 questions (April 2026 - June 2026)
- **FutureSim2026Q2**: 378 questions (April 2026 - June 2026)

The questions are generated synthetically from news articles using an automated pipeline. The questions cover events from diverse news sources from 2024 to mid 2025. As the questions are created using LLMs, we expect there to be some amount of noise and ambiguity in train/validation set of questions. 

However, the test set is of high-quality (we expect < 20% noise) as it has gone through human review and more quality checks. 

## Dataset Structure

### Fields Description

| Field | Type | Description |
|-------|------|-------------|
| `qid` | string | Unique question identifier |
| `question_title` | string | The main forecasting question |
| `background` | string | Context and background information for the question |
| `resolution_criteria` | string | HTML-formatted criteria for how the question will be resolved |
| `answer` | string | The ground truth answer to the question |
| `answer_type` | string | Type of answer expected (e.g., "string (location)", "string (name)", "string (date)") |
| `url` | string | URL of the source news article |
| `article_maintext` | string | Full text content of the news article |
| `article_publish_date` | string | Publication date of the article (YYYY-MM-DD format) |
| `article_modify_date` | string | Last modification date of the article (YYYY-MM-DD format) |
| `article_download_date` | string | Date when the article was downloaded (YYYY-MM-DD format) |
| `article_title` | string | Title of the news article |
| `article_description` | string | Description/summary of the news article |
| `data_source` | string | Source identifier for the data generation process |
| `news_source` | string | News outlet that published the article |
| `question_start_date` | string | Start date for the forecasting question (YYYY-MM-DD format) |
| `resolution_date` | string | Date when the question will be resolved (YYYY-MM-DD format) |
| `prompt` | string | Full prompt with retrieved news articles for forecasting |
| `prompt_without_retrieval` | string | Prompt without retrieved articles for baseline comparison |

## Data Generation Process


### News Sources
The dataset is generated from articles from multiple news sources:

Train Set:
- **Hindustan Times** (hindustantimes-2024-25)
- **Irish Times** (irishtimes-2024)
- **Forbes** (forbes-2024)
- **CNN** (cnn-2024)
- **DW** (dw-2024)

Validation Set:
- **The Guardian** (theguardian, UK-based)

Test Set:
- **Al Jazeera** (aljazeera, global news based in Middle East)
- **The Guardian** (theguardian, UK-based)
- **Time** (time.com, global news, US-based)
- **NDTV** (ndtv, India-focused)
- **Fox News** (foxnews, US-centric)

Skysports2025 Set:
- **Sky Sports** (skysports, sports news, UK-based)

AlJazeeraLate2025 Set:
- **Al Jazeera** (aljazeera, global news based in Middle East)

For evaluation with retrieval, please use the `prompt` field and for evaluation without retrieval for the same question, use the `prompt_without_retrieval` field. 

### Model Generation
Questions were generated using language models with the following process:

1. **Article Processing**: News articles were collected and processed to extract relevant information.
2. **Question Generation**: Language models generated forecasting questions based on article content.
3. **Retrieval Augmentation**: Relevant news articles were retrieved and incorporated into prompts.
4. **Question Validation**: Generated questions were validated on whether the source article actually resolves the question and whether the question is specific and correct.
5. **Quality Control**: Questions were filtered for relevance and quality, including leakage detection to prevent future information from appearing in training data.

## Answer Types

The dataset includes various answer types:
- **String (location)**: Geographic locations, places, venues
- **String (name)**: Person names, company names, product names
- **String (date)**: Specific dates or time periods
- **String**: General text answers

The questions are non-numeric in nature.

## AlJazeera Late 2025 Split

The `aljazeeraLate2025` split contains **491 forecasting questions** generated from Al Jazeera news articles published in late 2025.

- **Question generation**: Questions were generated using **GPT-5.2**.
- **Correctness verification**: Each question's answer was verified using **Grok-4.1-fast with web-search**.
- **Additional filtering**: "Knowledge-based" questions — i.e., questions that models could answer using only search results up to 2024 — were filtered out to ensure the split tests genuine forecasting ability on recent events.
- **Earliest resolution date**: 2025-09-01
- **Latest resolution date**: 2025-12-13
- **Questions per month**:

| Month | Questions |
|-------|-----------|
| 2025-09 | 164 |
| 2025-10 | 159 |
| 2025-11 | 123 |
| 2025-12 | 45 |

## AlJazeera 2026 Q1 Split

The `aljazeera2026Q1` split contains **330 forecasting questions** generated from Al Jazeera news articles published in the first quarter of 2026.

- **Question generation**: Questions were generated using **GPT-5.4**.
- **Correctness verification**: Each question's answer was verified using **GPT-5.5** with web-search**.
- **Additional filtering**: "Knowledge-based" questions — i.e., questions that models could answer using only search results up to 2025 — were filtered out to ensure the split tests genuine forecasting ability on recent events.
- **Extra care for Resolution-Date**: For each question, GPT-5.5 and Opus-4.7 were prompted to find the **earliest date** when the answer to the question could be *infered* confidently and resolution date was updated accordingly. This was done multiple times due to false negatives. Questions which could be answered confidently before 2026 were filtered.
- **Earliest resolution date**: 2026-01-01
- **Latest resolution date**: 2026-03-28
- **Questions per month**:

| Month | Questions |
|-------|-----------|
| 2026-01 | 122 |
| 2026-02 | 92 |
| 2026-03 | 116 |

## AlJazeera 2026 Q2 Split

The `aljazeera2026Q2` split contains **635 forecasting questions** generated from Al Jazeera news articles published in the second quarter of 2026 (April–June).

- **Question generation**: Questions were generated using **GPT-5.6**.
- **Correctness verification**: Each question's answer was verified against the source article; questions whose answer was directly recoverable from the article text were filtered out.
- **Adversarial difficulty filtering**: Easy / "knowledge-based" questions were removed via closed-book (no web-search) elicitation from multiple strong models — **GPT-5.4-mini, DeepSeek-v4-pro, GPT-5.5, and Claude-Sonnet-5** (with high/max reasoning effort).
- **Extra care for Resolution-Date**: For each question, the earliest date at which the answer could be confidently inferred was estimated (using GPT-5.4-mini and GPT-5.6-terra-pro over multiple samples) and the resolution date was set to that earliest date.
- **Note**: This split is not suitable for evaluations like FutureSim as it might contain cross-question leakage. Additionally, the start date of the question is also not reliable.
- **Earliest resolution date**: 2026-04-01
- **Latest resolution date**: 2026-06-28
- **Questions per month**:

| Month | Questions |
|-------|-----------|
| 2026-04 | 200 |
| 2026-05 | 250 |
| 2026-06 | 185 |

## FutureSim 2026 Q2 Split

The `futureSim2026Q2` split contains **378 forecasting questions** and is a subset of `aljazeera2026Q2` with cross-question leakage removed (i.e. cases where knowing the content/premise of one question leaks the answer to another question). Suitable for evaluation in benchmarks like FutureSim.

## Usage

### Loading the Dataset

```python
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("nikhilchandak/OpenForesight")

# Access specific splits
train_data = dataset["train"]
validation_data = dataset["validation"]
test_data = dataset["test"]
```

### Example Usage

```python
# Get a sample question
sample = dataset["train"][0]
print(f"Question: {sample['question_title']}")
print(f"Background: {sample['background']}")
print(f"Answer: {sample['answer']}")
print(f"Answer Type: {sample['answer_type']}")
print(f"Resolution Date: {sample['resolution_date']}")

# Use prompt with retrieval
prompt_with_retrieval = sample['prompt']

# Use prompt without retrieval for baseline
prompt_without_retrieval = sample['prompt_without_retrieval']
```

## Evaluation

This dataset is designed for evaluating forecasting capabilities of AI models, particularly with retrieval-augmented generation. Key evaluation metrics include:

- **Accuracy**: Correctness of predicted answers
- **Confidence Calibration**: How well model confidence aligns with actual accuracy
- **Temporal Reasoning**: Ability to reason about future events
- **Retrieval Impact**: Comparison of performance with and without retrieved context
- **Domain Knowledge**: Understanding of various subject areas

## Citation

If you use this dataset in your research, please cite:

```bibtex
@article{chandak2025scaling,
  title={Scaling Open-Ended Reasoning to Predict the Future},
  author={Chandak, Nikhil and Goel, Shashwat and Prabhu, Ameya and Hardt, Moritz and Geiping, Jonas},
  journal={arXiv preprint arXiv:2512.25070},
  year={2025}
}
```

## License

This dataset is released under the MIT License.