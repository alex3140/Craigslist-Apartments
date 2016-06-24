import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.neighbors import KNeighborsRegressor
from sklearn import cross_validation
from sklearn import linear_model
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import GradientBoostingRegressor

data=pd.read_csv('C:\\Users\\alex314\\Desktop\\CraigslistProject\\craigslist_data.csv')
data=data.dropna()

fig = plt.figure()
ax1 = fig.add_subplot(2, 2, 1)
ax1.scatter(data.footage, data.price)
ax1.set_xlabel("Footage, squared feet")
ax1.set_ylabel("Price, $")
ax1.set_xlim([0, 9000])
ax1.set_ylim([0, 13000])
ax2 = fig.add_subplot(2, 2, 2)
ax2.scatter(data.num_br, data.price)
ax2.set_xlabel("Number of Bedrooms")
ax2.set_ylabel("Price, $")

ax3 = fig.add_subplot(2, 2, 3)
ax3.scatter(data.num_ba, data.footage)
ax3.set_xlabel("Number of Bathrooms")
ax3.set_ylabel("Footage, square feet")

ax4 = fig.add_subplot(2, 2, 4)
ax4.scatter(data.num_ba, data.num_br)
ax4.set_xlabel("Number of Bathrooms")
ax4.set_ylabel("Number of Bedrooms")


#Remove unusual observations 
#In most cases such listings contain mistakes
#or are not real apartments
data = data[data.footage<3000]
data = data[data.footage>250]
data = data[data.price>800]
data = data[data.price<9000]

#Remove listings with more than 3 bedrooms
#Such listings are usually houses or shared apts
data=data[data.num_br<=3]
data=data[data.num_ba<3]


features = ['latitude', 'longitude', 'footage','num_br', 'num_ba']
#features = ['latitude', 'longitude', 'footage','num_br']
X = data[features]
Y = data['price']

Xtrain, Xtest, Ytrain, Ytest = cross_validation.train_test_split(
        X, Y, test_size=0.05, random_state=777)

#Gradient boosting model           
boost=GradientBoostingRegressor()
boost.fit(Xtrain, Ytrain)
boost.predict(Xtest)
RMSEs_boost = [mean_squared_error(
            Ytest, boost.predict(Xtest))**.5, 
            mean_squared_error(Ytrain, boost.predict(Xtrain))**.5]
MedAPE_test = (abs(Ytest - boost.predict(Xtest)) / Ytest).median()
MeanAPE_test = (abs(Ytest - boost.predict(Xtest)) / Ytest).mean() 

percent = sum(abs(Ytest - boost.predict(Xtest)) / Ytest < .1) / float(Ytest.shape[0])
       
print "***(Stochastic) Gradient Boosting Tree Model***"
print "Median Absolute Percentage Error: %s" %(round(MedAPE_test,4) * 100), "%"
print "Mean Absolute Percentage Error:", round(MeanAPE_test,5) * 100, "%"
print "Percentage of predictions with error below 10%:", round(percent, 4) * 100, "%"
print "Root MSE on train set: %s, Root MSE on test set: %s" \
        %(round(RMSEs_boost[0], 1),round(RMSEs_boost[1], 1))
print "R-square is %s" %(round(r2_score(Ytest,boost.predict(Xtest)), 4) * 100),"%"

featImportances = boost.feature_importances_
pos = np.arange(len(features))
pairs = zip(features, featImportances)
sorted_pairs = sorted(pairs, key = lambda pair: pair[1])
features_sorted, featImportances_sorted = zip(*sorted_pairs)
fig, ax = plt.subplots()
plt.barh(pos, featImportances_sorted, 1, color = "blue")
plt.yticks(pos,features_sorted)
ax.set_title('Gradient Boosting: Relative Feature Importance')

prediction = pd.Series(boost.predict(Xtest).round(1), index=Xtest.index)
prediction.columns=["prediction"]
table=data.ix[Ytest.index]
comparison_tbl=pd.concat([prediction, table[["price", "type", "footage","num_br","num_ba","url"]]],axis=1)
print comparison_tbl

#Is it not OK to use knn with discrete features?
knn = KNeighborsRegressor(weights="distance") #weights=uniform by default
knn.fit(Xtrain, Ytrain)
knn.predict(Xtest)
RMSEs_knn = [mean_squared_error(
            Ytest, knn.predict(Xtest))**.5, 
            mean_squared_error(Ytrain, knn.predict(Xtrain))**.5]

prediction = pd.Series(knn.predict(Xtest), index=Xtest.index)
prediction.columns=["prediction"]
table=data.ix[Ytest.index]
comparison_tbl=pd.concat([prediction, table[["price", "type", "url"]]],axis=1)


#Add furniture to model?
#Take care of missing footage
#Plot data on a map
