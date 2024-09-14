import os
from sklearn.metrics import classification_report
import torch
from tqdm import tqdm
import clip
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import joblib
import numpy as np

# 设置路径
positive_dir = './positive'
negative_dir = './negative'

# 加载CLIP模型
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 提取图像特征
def extract_features(img_path):
    img = Image.open(img_path).convert('RGB')
    img_tensor = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        img_features = clip_model.encode_image(img_tensor)
    return img_features.cpu().numpy()

# 获取正负样本
def load_data_from_directory(directory, label):
    features, labels = [], []
    for img_name in tqdm(os.listdir(directory)):
        img_path = os.path.join(directory, img_name)
        features.append(extract_features(img_path))
        labels.append(label)
    return features, labels

if __name__ == "__main__":
    print("加载CLIP模型中...")
    clip_model, transform = clip.load('ViT-B/16', device=device)
    clip_model=clip_model.eval()
    print("加载数据中...")
    pos_features, pos_labels = load_data_from_directory(positive_dir, 1)  # 正样本label为1
    neg_features, neg_labels = load_data_from_directory(negative_dir, 0)  # 负样本label为0

    # 合并数据
    features = np.vstack(pos_features + neg_features)
    labels = np.array(pos_labels + neg_labels)

    # 划分训练集和测试集 (8:2)
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)
    
    if not os.path.exists('./models'):
        os.makedirs('./models')
        
    kernels=['linear','poly','rbf','sigmoid']
    for kernel in kernels:
        print(f"使用 {kernel} 核训练SVM...")
        # 训练支持向量机（SVM）
        svm = SVC(kernel=kernel)  # 可以选择不同的kernel
        svm.fit(X_train, y_train)
        y_predict = svm.predict(X_test)
        
        print(f"{kernel}训练集准确率:", svm.score(X_train, y_train))
        print(f"{kernel}测试集准确率:", svm.score(X_test, y_test))
        
        # 打印分类报告，包括召回率
        report = classification_report(y_test, y_predict, target_names=['Negative', 'Positive'])
        print(f"{kernel}的分类报告:\n{report}")
        
        # 保存模型参数
        model_path = f'./models/{kernel}.pkl'
        joblib.dump(svm, model_path)
        print(f"模型已保存至 {model_path}")
