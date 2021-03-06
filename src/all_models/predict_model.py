import os
import sys
import json
import subprocess
import torch

from src.config import config_dict
import src.shared.eval_utils
import src.all_models.model_utils
import src.shared.classes as classes
# 下边是自己写的包
# 这个classes类定义了corpus、topic、document等基本类，而测试集是以corpus类对象的形式存储的
from src.shared.classes import *  # from classes import *
from src.shared.eval_utils import *  # from eval_utils import *
from src.all_models.model_utils import load_entity_wd_clusters, test_models

print(os.getcwd())
print("环境变量：", os.environ["PATH"], "\n")

'''
# 把"工作路径/src"下的文件都加入搜索路径
for pack in os.listdir("src"):  # 遍历"工作路径/src"下的文件
    # 把每个文件加入到包的搜索路径
    sys.path.append(os.path.join("src", pack))
'''
# 把项目根路径添加到模块搜索路径中
projectRootPath = os.path.abspath(os.path.join(__file__, "..", ".."))
sys.path.append(projectRootPath)

'''
因为现有数据在序列化的时候是用的classes.Topic等名字,而现在是src.shared.classes.Topic等
名字，不能对应，你反序列化之后识别不了。所以权宜之计是先按原来的方法import一遍
'''
sys.path.append(os.path.abspath(os.path.join(projectRootPath, "shared")))
from classes import *

# 设置命令行参数
import argparse
parser = argparse.ArgumentParser(description='Testing the regressors')
parser.add_argument('--config_path', type=str, help=' The path configuration json file')
parser.add_argument('--out_dir', type=str, help=' The directory to the output folder')

# 全局配置
if 1:
    # config in command
    args = parser.parse_args()
    config_dict["config_path"] = args.config_path
    config_dict["out_dir"] = args.out_dir
    # config in config file(test_config.json)
    with open(config_dict["config_path"], 'r') as js_file:
        config_file = json.load(js_file)
        print(config_file)
        config_dict.update(config_file)
    # config "use_cuda": want to use and is able to use cuda
    if 1:
        if config_dict["gpu_num"] != -1:  # gpu_num为-1表示不想使用cuda
            # 新增环境变量
            os.environ["CUDA_VISIBLE_DEVICES"]= str(config_dict["gpu_num"])
            # 新增配置参数
            use_cuda = True
        else:  # gpu_num为其他表示想使用cuda
            use_cuda = False
        # 只有当配置文件中要求使用cuda，且cuda确实可用时，才使用cuda
        config_dict["use_cuda"] = use_cuda and torch.cuda.is_available()
        if config_dict["use_cuda"]:
            print('使用cuda，cuda版本：')
            os.system("nvcc --version")
        else:
            print("不使用cuda")

# 根据out_dir参数，创建输出路径（如果不存在）
if not os.path.exists(config_dict["out_dir"]):
    os.makedirs(config_dict["out_dir"])
# 把当前配置文件序列化为json保存在输出路径(test_config.json)
with open(os.path.join(config_dict["out_dir"],'test_config.json'), "w") as js_file:
    json.dump(config_file, js_file, indent=4, sort_keys=True)
# 配置random
import random
random.seed(config_dict["random_seed"])
# 配置numpy
import numpy as np
np.random.seed(config_dict["random_seed"])
# 配置pytorch
torch.manual_seed(config_dict["seed"])
if use_cuda:
    torch.cuda.manual_seed(config_dict["seed"])
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# 配置logger
import logging
logging.basicConfig(
    # 使用fileHandler,日志文件在输出路径中(test_log.txt)
    filename=os.path.join(config_dict["out_dir"], "test_log.txt"),
    filemode="w",
    # 配置日志级别
    level=logging.INFO
)



def read_conll_f1(filename):
    '''
    This function reads the results of the CoNLL scorer , extracts the F1 measures of the MUS,
    B-cubed and the CEAF-e and calculates CoNLL F1 score.
    :param filename: a file stores the scorer's results.
    :return: the CoNLL F1
    '''
    f1_list = []
    with open(filename, "r") as ins:
        for line in ins:
            new_line = line.strip()
            if new_line.find('F1:') != -1:
                f1_list.append(float(new_line.split(': ')[-1][:-1]))

    muc_f1 = f1_list[1]
    bcued_f1 = f1_list[3]
    ceafe_f1 = f1_list[7]

    return (muc_f1 + bcued_f1 + ceafe_f1)/float(3)


def run_conll_scorer():
    if config_dict["test_use_gold_mentions"]:
        event_response_filename = os.path.join(args.out_dir, 'CD_test_event_mention_based.response_conll')
        entity_response_filename = os.path.join(args.out_dir, 'CD_test_entity_mention_based.response_conll')
    else:
        event_response_filename = os.path.join(args.out_dir, 'CD_test_event_span_based.response_conll')
        entity_response_filename = os.path.join(args.out_dir, 'CD_test_entity_span_based.response_conll')

    event_conll_file = os.path.join(args.out_dir,'event_scorer_cd_out.txt')
    entity_conll_file = os.path.join(args.out_dir,'entity_scorer_cd_out.txt')

    event_scorer_command = ('perl scorer/scorer.pl all {} {} none > {} \n'.format
            (config_dict["event_gold_file_path"], event_response_filename, event_conll_file))

    entity_scorer_command = ('perl scorer/scorer.pl all {} {} none > {} \n'.format
            (config_dict["entity_gold_file_path"], entity_response_filename, entity_conll_file))

    processes = []
    print('Run scorer command for cross-document event coreference')
    processes.append(subprocess.Popen(event_scorer_command, shell=True))

    print('Run scorer command for cross-document entity coreference')
    processes.append(subprocess.Popen(entity_scorer_command, shell=True))

    while processes:
        status = processes[0].poll()
        if status is not None:
            processes.pop(0)

    print ('Running scorers has been done.')
    print ('Save results...')

    scores_file = open(os.path.join(args.out_dir, 'conll_f1_scores.txt'), 'w')

    event_f1 = read_conll_f1(event_conll_file)
    entity_f1 = read_conll_f1(entity_conll_file)
    scores_file.write('Event CoNLL F1: {}\n'.format(event_f1))
    scores_file.write('Entity CoNLL F1: {}\n'.format(entity_f1))

    scores_file.close()


def test_model(test_set: src.shared.classes.Corpus):
    r"""
    Loads trained event and entity models and test them on the test set

    :param test_set: 测试数据
    """
    # 加载设备
    if config_dict["use_cuda"]:
        cudan = "cuda:"+config_dict["gpu_num"]
        device = torch.device(cudan)
    else:
        device = torch.device("cpu")
    # 加载模型
    if config_dict["use_cuda"]:  # 训练模型时使用的是0号GPU，现在使用n号GPU，需要转换
        cd_event_model = torch.load(config_dict["cd_event_model_path"], map_location={'cuda:0': cudan})
        cd_entity_model = torch.load(config_dict["cd_entity_model_path"], map_location={'cuda:0': cudan})
    else:  # 训练模型时使用的是0号GPU，现在使用CPU，需要转换
        cd_event_model = torch.load(config_dict["cd_event_model_path"], map_location={'cuda:0': 'cpu'})
        cd_entity_model = torch.load(config_dict["cd_entity_model_path"], map_location={'cuda:0': 'cpu'})
    # 把模型放到设备中
    cd_event_model.to(device)
    cd_entity_model.to(device)

    # 加载外部wd ec结果
    doc_to_entity_mentions = load_entity_wd_clusters(config_dict)

    # 算法主体(数据，模型)
    _,_ = test_models(test_set, cd_event_model, cd_entity_model,
                                  device, config_dict, write_clusters=True,
                                  out_dir=args.out_dir,
                                  doc_to_entity_mentions=doc_to_entity_mentions,
                                  analyze_scores=True)

    run_conll_scorer()


def main():
    """
    This script loads the trained event and entity models and test them on the test set
    """

    # 读入测试数据
    logging.info('Loading test data...')
    # 根据配置文件加载测试集
    import _pickle as cPickle  # python3之后，cPickle包改名成了_pickle
    with open(config_dict["test_path"], 'rb') as f:  # test_path是测试数据路径
        test_data = cPickle.load(f)
        '''
        测试集test_data是一个自定义类Corpus的实例化对象，Corpus类在src/shared/classes.py中定义
          Corpus包含Topic；Topic包含Document(以及E和V指称)；Document包含Sentence
          Sentence包含Token(以及真实的和预测的E和V指称)；...
        '''
    logging.info('Test data have been loaded.')

    # 运行算法进行测试
    test_model(test_data)  # test_model这玩意是上边定义的函数


if __name__ == '__main__':

    main()
