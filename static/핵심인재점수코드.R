rm(list=ls())
library(openxlsx)
library(dplyr)
library(caret)
library(DMwR)
library(corrplot)
library(car)
library(FSelector)
library(nnet)
library(psych)
library(data.table)
library(e1071)
library(glmnet)
library(scales)
library(AUC)
library(pROC)
library(ROCR)
library(MLmetrics)
library(here)
setwd('C:\\Program Files\\poscoictdashboard\\xxxICTv2\\poscoictsystem\\static\\excels')

#### core ####
## 1. data load
alldat = as.data.frame(fread('input_new.csv',encoding = 'unknown'))
All2 = as.data.frame(fread('input_new_.csv',encoding = 'unknown',sep = ","))
All2 <- All2[,-1]
alldat <- alldat[,intersect(names(All2),names(alldat))]

str(alldat)
for(n in names(alldat)){
    if("integer" != typeof(alldat[,n]) && "double" != typeof(alldat[,n]) ){
        alldat[,n] <- as.factor(alldat[,n])
    }
}


colstoexclude <- c(3,9,11:15,23,30,43,46,53) 
names(alldat[,colstoexclude]) 
Alldata <- alldat[ ,-colstoexclude]   
nacount <- rep(NA, ncol(Alldata)) 
nacount 
names(nacount) <- colnames(Alldata) 

for(i in 1:ncol(Alldata)){               
    nacount[i] <- sum(is.na(Alldata[,i]))}


table(nacount > nrow(Alldata)*0.9)      
nacount[nacount > nrow(Alldata)*0.9]   
Allna <- Alldata[, nacount < nrow(Alldata)*0.9]

Allim <- centralImputation(Allna)        
Allim


factorColNum = c()
for(n in 1:ncol(Allim)){
    if(is.factor(Allim[,n])){
        factorColNum <- c(factorColNum,n)
    }
}


factorColNum <- c(factorColNum,41)
names(Allim)[factorColNum]
Allim_numeric <- Allim[, -factorColNum]
Allim_factor <- Allim[, factorColNum]

Allscale <- cbind(Allim_factor, scale(Allim_numeric))  


nacount <- rep(NA, ncol(Allscale)) 
nacount  
names(nacount) <- colnames(Allscale) 

for(i in 1:ncol(Allscale)){               
    nacount[i] <- sum(is.na(Allscale[,i]))}

Allscale <- Allscale[, nacount < nrow(Allscale)*0.9]





AllNormal = Allscale[Allscale$coreyn == FALSE,]
Allcore = Allscale[Allscale$coreyn == TRUE,]

set.seed(sample(1:10000, 1, replace=T))  

smp_size <- floor(0.7 * nrow(AllNormal))
train_ind <- sample(seq_len(nrow(AllNormal)), size = smp_size)
trainNormal <- AllNormal[train_ind, ]
testNormal <- AllNormal[-train_ind, ]
smp_size <- floor(0.7 * nrow(Allcore))
train_ind <- sample(seq_len(nrow(Allcore)), size = smp_size)
traincore <- Allcore[train_ind, ]
testcore <- Allcore[-train_ind, ]
nrow(traincore)
nrow(testcore)
train <- rbind(trainNormal,traincore)
test <- rbind(testNormal,testcore)
nrow(train)
nrow(test)
table(train$coreyn)
table(test$coreyn)

# resampling

train <- SMOTE(coreyn ~ ., train, perc.over = 200, perc.under=100)
nrow(train)
table(train$coreyn)


summary(train$coreyn)
summary(test$coreyn)

# svm
# 1. train, test split

# put all data
svmfit = svm(coreyn ~ .,data=train,type="C-classification",
             kernel='linear', probability=T) 

sf_pred = predict(svmfit, test[,-1], probability=T)  # prediction
sf_prob = attr(sf_pred, 'probabilities')[,2]    # get probabilities
table(as.numeric(sf_prob>0.6), test$coreyn)  # get confusion matrix
tb_sf = table(as.numeric(sf_prob>0.5), test$coreyn)
sum(diag(tb_sf))/sum(tb_sf)  ## accuracy: 81.56 -> 80.67

pred <- prediction(sf_prob, as.numeric(test$coreyn))
par(mfrow=c(1,1))
plot(performance(pred, "tpr","fpr"),main="ROC Curve for SVM",col=2,lwd=2)
confusionMatrix(sf_pred,test$coreyn)





## train + test dataset prediction 
train_and_test <- rbind(AllNormal,Allcore)

sf_pred = predict(svmfit, train_and_test[,-1], probability=T)  # prediction
allprob = attr(sf_pred, 'probabilities')[,2]    # get probabilities

table(as.numeric(allprob>0.5), train_and_test$coreyn)  # get confusion matrix
tb_sf = table(as.numeric(allprob>0.5), train_and_test$coreyn)
sum(diag(tb_sf))/sum(tb_sf)  ## accuracy: 81.56 -> 80.67

pred <- prediction(allprob, as.numeric(train_and_test$coreyn))
par(mfrow=c(1,1))
plot(performance(pred, "tpr","fpr"),main="ROC Curve for SVM",col=2,lwd=2)
confusionMatrix(sf_pred,train_and_test$coreyn)


core_score = (allprob-min(allprob)+2)/(max(allprob)+0.2-min(allprob)+2)*100

#core = data.frame('ID'=dat0$id, 'hagscore'=core_score)
core <- data.frame(cbind(c(alldat[alldat$coreyn == FALSE,'id'],alldat[alldat$coreyn == TRUE,'id']),core_score))
colnames(core) <- c("ID","hagscore")


write.csv(core,paste(here(),"/hacksim.csv",sep=""),row.names=F)
