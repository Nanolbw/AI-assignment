import cv2
#
from Cnn import CNN, save_model, load_model
import torch
import torch.nn.functional as F
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import torch.utils.data as Data
import numpy as np
import matplotlib as plt
from feature_extraction import get_spectrogram


def train_model(net, data, label, lr, batch_size, epoch):
    print(net)
    # 能用显卡跑的就用显卡跑
    # net = net.cuda()
    data = torch.Tensor(data)
    data = data.unsqueeze(1)
    label = torch.Tensor(label).long()
    # data =data.cuda()
    # label=label.cuda()
    # 训练集和测试集7：3
    train_data, test_data, train_label, test_label = train_test_split(data, label, test_size=0.3, random_state=0)

    # 学习率
    LR = lr
    # 每次投入训练数据大小
    BATCH_SIZE = batch_size
    # 训练模型次数
    EPOCH = epoch

    optimizer = torch.optim.Adam(net.parameters(), lr=LR)

    train_dataset = Data.TensorDataset(train_data, train_label)
    train_loader = Data.DataLoader(
        dataset=train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
    )

    test_dataset = Data.TensorDataset(test_data, test_label)
    test_loader = Data.DataLoader(
        dataset=test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
    )
    scheduler = torch.optim.lr_scheduler.OneCycleLR(optimizer, LR, epochs=EPOCH, steps_per_epoch=len(train_loader))

    for epoch in range(EPOCH):
        for step, (batch_data, batch_label) in enumerate(train_loader):
            print('Epoch:', epoch + 1, '/', EPOCH, 'Step:', step)
            prediction = net(batch_data)
            loss = F.cross_entropy(prediction, batch_label)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            scheduler.step()

            if step % 50 == 0:
                accuracy = []
                for stp, (test_x, test_y) in enumerate(test_loader):
                    test_output = net(test_x)
                    _, pred_y = torch.max(test_output, 1)
                    accuracy.append(torch.sum(pred_y == test_y).item() / len(test_y))

                print('Epoch', epoch + 1, '| train loss:%.4f' % loss, '| test accuracy:%.4f' % np.mean(accuracy))

    return net


def test_model(net, data, label):
    data = torch.Tensor(data)
    data = data.unsqueeze(1)
    label = torch.Tensor(label).long()
    # 训练集和测试集7：3
    train_data, test_data, train_label, test_label = train_test_split(data, label, test_size=0.3, random_state=0)

    test_dataset = Data.TensorDataset(test_data, test_label)
    test_loader = Data.DataLoader(
        dataset=test_dataset,
        batch_size=32,
        shuffle=True,
    )

    y_true = []
    y_pred = []
    for stp, (test_x, test_y) in enumerate(test_loader):
        test_output = net(test_x)
        _, pred_y = torch.max(test_output, 1)
        y_true.extend(test_y)
        y_pred.extend(pred_y)

    print("Accuracy:", accuracy_score(y_true, y_pred))
    print("Precision_score:", precision_score(y_true, y_pred, average='macro'))
    print("Recall_score:", recall_score(y_true, y_pred, average='macro'))
    print("F1_score", f1_score(y_true, y_pred, average='macro'))


def predict(model, file):
    spect = get_spectrogram(file)
    spect = np.abs(spect)
    spect = cv2.resize(spect, (28, 28))
    #plt.matplotlib_fname()
    data = torch.Tensor(spect)
    data = data.unsqueeze(0)
    data = data.unsqueeze(0)
    output = model(data)
    confidence, pred_y = torch.max(output, 1)
    print("识别结果为：", pred_y.numpy()+1)
    return pred_y.numpy()+1


if __name__ == '__main__':
    # data = np.load("data.npy")
    # label = np.load("label.npy")

    # cnn = CNN()
    # cnn = train_model(cnn, data, label, lr=0.03, batch_size=500, epoch=20)
    # save_model(cnn, "cnn.pkl")
    #
    # test_model(cnn, data, label)

    file = "E:/yolov5/yuyin/test.wav"
    cnn = load_model("cnn_final.pkl")
    predict(cnn, file)

