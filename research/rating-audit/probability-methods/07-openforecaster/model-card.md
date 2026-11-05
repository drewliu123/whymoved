---
base_model: Qwen/Qwen3-8B
datasets:
- nikhilchandak/OpenForesight
language:
- en
license: mit
pipeline_tag: text-generation
library_name: transformers
tags:
- forecasting
- reasoning
- question-answering
- reinforcement-learning
- calibration
---

# OpenForecaster-8B

[![Paper](https://img.shields.io/badge/arXiv-2512.25070-b31b1b.svg)](https://arxiv.org/abs/2512.25070)
[![Blog](https://img.shields.io/badge/Blog-Read%20More-orange)](https://openforecaster.github.io/)
[![Dataset](https://img.shields.io/badge/🤗%20Dataset-OpenForesight-yellow)](https://huggingface.co/datasets/nikhilchandak/OpenForesight)

**OpenForecaster-8B** is a specialized language model for *open-ended* forecasting and predicting future events. This model is post-trained from **Qwen3-8B** using reinforcement learning on the [OpenForesight dataset](https://huggingface.co/datasets/nikhilchandak/OpenForesight). It was introduced in the paper [Scaling Open-Ended Reasoning to Predict the Future](https://huggingface.co/papers/2512.25070).


### Performance of OpenForecaster-8B on FutureX

![FutureX Performance](assets/scatter_brier_accuracy_futurex-past86-retrieval.png)

Performance on [FutureX](https://huggingface.co/datasets/futurex-ai/Futurex-Past) benchmark in July-August 2025 on non-numeric questions (86 Qs): **OpenForecaster-8B** has a much higher accuracy than 100B+ models. We limit to models released before April 2025 for a fair, equal knowledge cutoff comparison.

<!-- **🌐 [Blog](https://openforecaster.github.io) | 📄 [Paper](https://huggingface.co/papers/2512.25070) | 💻 [Code](https://github.com/OpenForecaster/scaling-forecasting-training)** -->

## Model Description

OpenForecaster-8B is trained to make calibrated predictions on open-ended questions about future events. The model has been trained to:
- Provide calibrated confidence estimates when asked (please prompt explicitly)
- Reason about uncertainty and future scenarios
- Leverage retrieved information (when provided in context) to improve predictions

**Note:** OpenForecaster-8B's knowledge cutoff is, at best, till **April 2025** (base model's cutoff being ~June 2024) so it has no knowledge about the events that have happened since then till now. Thus, if you ask it questions about 2026 or later without providing recent developments/relevant context, it will only be able to answer from its parametric knowledge which might not be helpful/up-to date. Thus, please be aware of this and use it with RAG over recent developments if possible.


## Training

This model was trained on the **OpenForesight** dataset, which contains over 52,000 forecasting questions generated from global news events. The training was done using GRPO optimizing a joint reward function combining accuracy and brier score. Please check the paper for more details.

**Base Model**: Qwen3-8B  
**Training Dataset**: [OpenForesight](https://huggingface.co/datasets/nikhilchandak/OpenForesight)

## Usage

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "nikhilchandak/OpenForecaster-8B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# template 
prompt = "What is the likelihood that [future event] will occur by [date]?"
# example
prompt = "Who will become the next Prime Minister of India based on the general election to be held in 2029? Provide specific predictions with probabilities."
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_length=8192)
prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(prediction)
```

## Performance

OpenForecaster-8B achieves competitive performance with much larger models like DeepSeek-v3 and Qwen3-235B-A22B on forecasting benchmarks. Key improvements include:
- **Improved Accuracy**: Better prediction of future events
- **Better Calibration**: More reliable confidence estimates 
- **Enhanced Consistency**: Reduced logical violations in predictions


## Citation

 If you use this model in any way, please cite the corresponding paper:

 ```bibtex
@article{chandak2025scaling,
  title={Scaling Open-Ended Reasoning to Predict the Future},
  author={Chandak, Nikhil and Goel, Shashwat and Prabhu, Ameya and Hardt, Moritz and Geiping, Jonas},
  journal={arXiv preprint arXiv:2512.25070},
  year={2025}
}
```

## License

This model is released under the MIT License.

## Contact

For questions or issues, please visit our [website](https://openforecaster.github.io) or open an issue on the model repository.