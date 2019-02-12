#encoding=utf8
"""
logistic regression
"""

import sys
from sklearn.datasets import load_iris
import seaborn as sns
import numpy as np


class LRModel(object):
	"""
	LR simple model
	"""
	def __init__(self):
		self.w = 0
		self.loss_list = []
		self.inter_num = 2000
		self.learn_rate = 0.01

	def train(self, X, y):
		"""
		train model
		"""
		inter_num = self.inter_num
		learn_rate = self.learn_rate
		num, k = X.shape

		## init weight parameters
		self.w = learn_rate * np.random.randn(k).reshape((-1, 1))
		loss_list = []
		for i in range(inter_num):
			error, dw = self.cal_loss(X, y)
			self.w += -learn_rate * dw
			self.loss_list.append(error)
			if i % 100 == 0:
				print 'inter_num = ' + str(i) + '; loss = ' + str(error)
	

	def cal_loss(self, X, y):
		"""
		 计算损失函数
		"""
		n = X.shape[0]
		tmp = np.dot(X, self.w).reshape((-1,1))
		z = 1 / (1 + np.exp(-tmp))
		loss = -np.sum(y*np.log(z) + (1-y)*np.log(1-z))
		loss = loss / n
		dw = np.dot(X.T, z - y)/n

		return loss, dw


	def predict(self, X_test):
		"""
		model prediction
		"""
		tmp = np.dot(X_test, self.w).reshape((-1,1))
		z = 1 / (1 + np.exp(-tmp))
		z[z > 0.5] = 1
		z[z < 0.5] = 0
		
		return z

	def evaluation(self):
		"""
		评估模型效果
		"""
		x = range(self.inter_num)
		y = self.loss_list

		sns.regplot(np.array(x), np.array(y), fit_reg = False)


if __name__ == "__main__":

	## 1. load datasets
	iris = load_iris()
	X = iris.data[:100]        # 筛选前100个样本，只有0，1的label
	y = iris.target[:100]
	y = y.reshape((-1, 1))
	one = np.ones((X.shape[0], 1))
	X_train = np.hstack((one, X))

	## 2. train model
	lr = LRModel()
	lr.train(X_train, y)

	## 3. model 效果
	lr.evaluation()