# Revisiting Joint Modeling of Cross-document Entity and Event Coreference Resolution

## Introduction
This code was used in the paper:

<b>"Revisiting Joint Modeling of Cross-document Entity and Event Coreference Resolution"</b><br/>
Shany Barhom, Vered Shwartz, Alon Eirew, Michael Bugert, Nils Reimers and Ido Dagan. ACL 2019.

A neural model implemented in PyTorch for resolving cross-document entity and event coreference.
The model was trained and evaluated on the ECB+ corpus.

## Prerequisites
* Python 3.6
* [PyTorch](https://pytorch.org/) 0.4.0
    * 原文使用CUDA 9.0和LINUX:
    `pip install https://download.pytorch.org/whl/cu90/torch-0.4.0-cp36-cp36m-linux_x86_64.whl`
    * 我使用cpuonly和win64:
    `pip install http://download.pytorch.org/whl/cpu/torch-0.4.0-cp36-cp36m-win_amd64.whl`
* [spaCy](https://spacy.io/) 2.0.18
    * 安装完spaCy后，再Install the spacy en model with `python -m spacy download en`，注意这个安装需要管理员权限来完成软连接。
* [Matplotlib](https://matplotlib.org/) 3.0.2
* [NumPy](https://www.numpy.org/) 1.16.1(应该是1.17.3)
* [NLTK](https://www.nltk.org/) 3.4
* [scikit-learn](https://scikit-learn.org/) 0.20.2
* [SciPy](https://www.scipy.org/) 1.2.1(应该是1.3.1)
* [seaborn](https://seaborn.pydata.org/) 0.9.0
* [AllenNLP](https://allennlp.org/) 0.5.1
* [perl](https://www.perl.org/get.html) 这玩意不是python包，是一个命令行工具。点击进入官网下载安装包并安装。
你需要新建一个python虚拟环境，然后安装上述包。

## installation
把项目路径添加到python导包目录。
Add your project root path as PYTHONPATH.
方法很多。例如：
* One way is editting your env parameter
* another way is createding a .pth file in Python Interpreter Home
    我的项目在E:\ProgramCode\Barhom2019
    那么我在anaconda安装目录D:\ProgramFiles\Anaconda3下新建mypath.pth文件，
    写入：E:\ProgramCode\Barhom2019。保存。
    然后打开python，import Barhom2019，成功导入，不报错即可。

## Testing Instructions
* 下载。Download pretrained event and entity models and pre-processed data for the ECB+ corpus
  at *https://drive.google.com/open?id=197jYq5lioefABWP11cr4hy4Ohh1HMPGK*  .
  这玩意在谷歌网盘上，你要直接下能卡死。使用多网盘同步工具MultClude把谷歌网盘上的文件转到OneDrive上，在从OneDrive上下载。
  参见 https://blog.csdn.net/zhmxubing/article/details/88681573.
* 配置文件。Configure the model and test set paths in the configuration file test_config.json accordingly. 
  你看他的配置，就知道他本来怎么布置上一步下载的数据和模型的，按照他原来的结构布置你下载的数据和模型即可。我没改动，怕踩坑。
* 其他数据。the script's configuration file (test_config.json) also requires: 
   * An output file of a within-document entity coreference system on the ECB+ corpus (provided in this repo at data/external/stanford_neural_wd_entity_coref_out/ecb_wd_coref.json)
   * An output file of the document clustering algorithm that has been used in the paper (provided in this repo at data/external/document_clustering/predicted_topics)
* 运行。Run the script predict_model.py
    * run with the command:
        `python src/all_models/predict_model.py --config_path test_config.json --out_dir <output_directory>`
        * 参数解释:
            * `config_path` - a path to a JSON file holds the test configuration (test_config.json).
                An explanation about this configuration file is provided in config_files_readme.md.
            * `out_dir` - the output directory.
        * 例子:
        `python src/all_models/predict_model.py --config_path test_config.json --out_dir output`
    * run in PyCharm
        * 在File - Settings - Project - Project interpreter中添加你的虚拟环境。
        * 在Run - Edit Configuration中点“+”，选python，则会新建一个运行配置，修改配置：
            * Script path: <项目根目录>\src\all_models\predict_model.py
            * Parameters: --config_path test_config.json --out_dir output
            * Environment variables: PYTHONUNBUFFERED=1
            * Python interpreter: 选你刚添加的虚拟环境
            * Work directory: <项目根目录>
    * Main output:
        * Two response (aka system prediction) files:
           * `CD_test_entity_mention_based.response_conll` - cross-document entity coreference results in CoNLL format.
           * `CD_test_event_mention_based.response_conll` - cross-document event coreference results in CoNLL format.
        * `conll_f1_scores.txt` - A text file contains the CoNLL coreference scorer's output (F1 score).

## Training Instructions
* 下载。The pre-processed data for ECB+ corpus shoud be put into `data\processed\cybulska_setup\full_swirl_ecb`. This data is available in two way：
    * Download the pre-processed data for the ECB+ corpus at *https://drive.google.com/open?id=197jYq5lioefABWP11cr4hy4Ohh1HMPGK*.
    * Alternatively, you can create the data from scratch by following the instructions below.
* 下载。Download GloVe embeddings from *https://nlp.stanford.edu/projects/glove/* (we used glove.6B.300d).
* 配置文件。Configure paths in the configuration file train_config.json (see details at config_files_readme.md).
* the script's configuration file (train_config.json) also requires: 
   * An output file of a within-document entity coreference system on the ECB+ corpus (provided in this repo at             data/external/stanford_neural_wd_entity_coref_out)
* Run the script train_model.py 
    * Run with the command:
       `python src/all_models/train_model.py --config_path train_config.json --out_dir <output_directory>`
        * Param: 
            * config_path - a path to a JSON file holds the training configuration (train_config.json).
                An explanation about this configuration file is provided in config_files_readme.md.
            * out_dir - an output directory.
       * Example:
          `python src/all_models/train_model.py --config_path train_config.json --out_dir output`
    * Run in PyCharm
    * Output:
        * Two trained models that are saved to the files:
            * `cd_event_best_model` - the event model that got the highest B-cubed F1 score on the dev set.
            * `cd_entity_best_model` - the entity model that got the highest B-cubed F1 score on the dev set.
        * `summery.txt` - a summary of the training.

 

## Creating Data from Scratch
This repository provides pre-processed data for the ECB+ corpus (download from *https://drive.google.com/open?id=197jYq5lioefABWP11cr4hy4Ohh1HMPGK*).
In case you want to create the data from scratch, do the following steps:

### Loading the ECB+ corpus
* ECB+ corpors should be put into `\data\raw\ECBplus`
* extract the gold mentions and documents from the ECB+ corpus:
    * run with the command:
       `python src/data/make_dataset.py --ecb_path <ecb_path> --output_dir <output_directory> --data_setup 2 --selected_sentences_file       data/raw/ECBplus_coreference_sentences.csv`
        * Param:
           * `ecb_path` - a directory contains the ECB+ documents (can be downloaded from *http://www.newsreader-project.eu/results/data/the-ecb-corpus/*).
           * `output_dir` - output directory.
           * `data_setup` - enter '2' to load the ECB+ data in the same evaluation setup as used in our experiments (see the setup description in the paper).
           * `selected_sentences_file` - path to a CSV file contains the selected sentences.
       * Example：E:\ProgramCode\Barhom2019Main\event_entity_coref_ecb_plus > `python src/data/make_dataset.py --ecb_path data\raw\ECBplus --output_dir output --data_setup 2 --selected_sentences_file  data/raw/ECBplus_coreference_sentences.csv`
    * run in PyCharm
    * Main Output: 
        The script saves for each data split (train/dev/test):
        * A json file contains its mention objects.
        * A text file contains its sentences.
        they are listed here:
        *  ECB_All_Entity_gold_mentions.json
        *  ECB_All_Event_gold_mentions.json
        *  ECB_Dev_corpus.txt
        *  ECB_Dev_Entity_gold_mentions.json
        *  ECB_Dev_Event_gold_mentions.json
        *  ECB_Test_corpus.txt
        *  ECB_Test_Entity_gold_mentions.json
        *  ECB_Test_Event_gold_mentions.json
        *  ECB_Train_corpus.txt
        *  ECB_Train_Entity_gold_mentions.json
        *  ECB_Train_Event_gold_mentions.json
        *  mention_stats.txt  (statistic info)
* After: All the output files( except statistic info) should be put into `data\interim\cybulska_setup` to works as input data in `Feature extraction` step.

### Feature extraction
* Allennlp: 
    Allennlp do not officially support Windows. So there is a a little bug to be fixed in Windows. In
    allennlp/commands/common/util.py, comment out this command `import resource`.
* Data from last step: 
    The output files (JSON and text files) of `Loading the ECB+ corpus` step( `make_dataset.py`) should be put into
    `data\interim\cybulska_setup`.
* Output files of SwiRL SRL system on the ECB+ corpus (already provided in this repo at `data/external/swirl_output`).
* Download ELMo's files (options file and weights) from *https://allennlp.org/elmo* (we used Original 5.5B model files. It is at `Pre-trained ELMo Models` chapter in that website). Download and put it into `data\external\elmo`.
* Feature extraction. 
    Run the feature extraction script, which extracts predicate-argument
    structures, mention head and ELMo embeddings, for each mention in each split
    (train/dev/test):
    * run with command:
        `python src/features/build_features.py --config_path
        build_features_config.json --output_path <output_path>`
        * Param:
            * `config_path` - a path to a JSON file holds the feature extraction configuration (build_features_config.json).
                An explanation about this configuration file is provided in config_files_readme.md.
            * `output_path` - a path to the output directory.
        * Example: `python src/features/build_features.py --config_path build_features_config.json --output_path output`
    * run in PyCharm
    * Output: 
        This script saves 3 pickle files, each contains a Corpus object representing each split:
        * `train_data` - the training data, used as an input to the script train_model.py.
        * `dev_data` - the dev data, used as an input to the script train_model.py.
        * `test_data` - the test data, used as an input to the script predict_model.py.
        * `build_features_config.json` - config info. It is a copy of the file which is given by `config_path` parameter in the instruction.
        * `train_statistics.txt` - statistic info
        * `dev_statistics.txt` - statistic info
        * `test_statistics.txt` - statistic info
* All the output files( except the config info and statistic info ) should be put into `\data\processed\cybulska_setup\full_swirl_ecb` to works as input data in the `training` step.

## Contact info
Contact [Shany Barhom](https://github.com/shanybar) at *shanyb21@gmail.com* for questions about this repository.