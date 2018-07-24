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

setwd('C:\\Program Files\\poscoictdashboard\\xxxICTv2\\poscoictsystem\\static\\excels')

#### core ####
## 1. data load
alldat = as.data.frame(fread('input_new.csv',encoding = 'unknown'))
All2 = as.data.frame(fread('input_new_.csv',encoding = 'unknown',sep = ","))
All2 <- All2[,-1]
alldat <- alldat[,intersect(names(All2),names(alldat))]
#alldat <- alldat[,names(All2)]

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



alldata = as.data.frame(fread('input_new.csv',encoding = 'unknown',stringsAsFactors =T))
alldata$place <- as.factor(alldata$place)
alldata$sex <- as.factor(alldata$sex)
alldata$flow <- as.factor(alldata$flow)


su <- alldata %>% filter(place %in% c("pangyo", "center"))
table(su$flow)
su_mol=su[c("flow", "edu_nbr", "thank_letter_tot_receive","pccontrol_mean_timeh", 
            "vdi_indi_mean_timem", "email_day_mean_receive","dongryo_closeness")]
str(su_mol)
su_mol <- as.data.frame(cbind(clust=su_mol[,1], scale(centralImputation(su_mol[,-1])))) 
su_mol$clust3 <- factor(ifelse(su_mol$clust==3, 1, 0))             
su_mol_o <- su_mol %>% filter(clust %in% c(1,2,3)); dim(su_mol_o)  
su_mol_x <- su_mol %>% filter(clust %in% NA); dim(su_mol_x)
str(su_mol_o)

sumol <- glm(formula = clust3 ~ edu_nbr + thank_letter_tot_receive + pccontrol_mean_timeh + 
                 vdi_indi_mean_timem + email_day_mean_receive + dongryo_closeness, 
             family = "binomial", data = su_mol_o[,-1])
summary(sumol)

pred_o <- predict(sumol, newdata=su_mol_o)
pred_x <- predict(sumol, newdata=su_mol_x)
id_o <- su %>% filter(flow %in% c(1,2,3)) %>% select(id); NROW(id_o)
id_x <- su %>% filter(flow %in% NA) %>% select(id); NROW(id_x)

su_pred <- as.data.frame(rbind(cbind(id_o, pred=pred_o), cbind(id_x, pred=pred_x)))
colnames(su_pred) <- c("ID", "Predict"); head(su_pred)
su_pred$su_mol <- ((su_pred$Predict-min(su_pred$Predict)+1) /
                       
                       (max(su_pred$Predict)+0.5-min(su_pred$Predict)+1)) *100
su_pred$su_mol <- ((log(su_pred$su_mol)-min(log(su_pred$su_mol))+0.2) /
                       (max(log(su_pred$su_mol))+0.1-min(log(su_pred$su_mol))+0.2)) *100
hist(su_pred$su_mol)
summary(su_pred$su_mol)


su_sung=su[c("grade_1", "grade_2", "sex", "grade_co_y", "grade_sv_y_1", "work_duration",
             "off_use_pct_permon", "pcout_tot_request", "vdi_share_mean_time","food_tot_spend",
             "email_day_mean_receive", "email_between_1904_daycnt_send")]
su_sung$r1 <- apply(cbind(su_sung$grade_1,su_sung$grade_2),1,mean)
su_sung <- su_sung[,-c(1:2)] 
su_sung <- as.data.frame(cbind(sex=su_sung[,1], scale(centralImputation(su_sung[,-1]))))
su_sung$sex <- as.factor(su_sung$sex)
str(su_sung)
sulm <- lm(r1 ~ sex + grade_sv_y_1 + grade_co_y + work_duration + off_use_pct_permon +
               pcout_tot_request + vdi_share_mean_time + food_tot_spend + email_day_mean_receive +
               email_between_1904_daycnt_send, data = su_sung)
summary(sulm)

score_sugrade <- as.data.frame(cbind(su$id, predict(sulm, su_sung)))
colnames(score_sugrade) <- c("ID", "Predict")
score_sugrade$su_grade <- ((score_sugrade$Predict-min(score_sugrade$Predict)+0.1) /
                               (max(score_sugrade$Predict)+0.1-min(score_sugrade$Predict)+0.1))*100
hist(score_sugrade$su_grade)
summary(score_sugrade$su_grade)

suscore <- merge(su_pred[,c(1,3)], score_sugrade[,c(1,3)], by="ID", all.x=T)
head(suscore)
cor(suscore$su_mol, suscore$su_grade)
summary(suscore)


ph <- alldata %>% filter(place %in% c("pohang"))
table(ph$flow)
ph_mol <- ph[c("flow", "grade_sv_y_1","work_duration","approve_tot_request","pccontrol_mean_timeh",
               "porta_tot_request","sna_outdegree", "buha_closeness")]
str(ph_mol)
ph_mol <- as.data.frame(cbind(clust=ph_mol[,1], scale(centralImputation(ph_mol[,-1])))) 
ph_mol$clust3 <- factor(ifelse(ph_mol$clust==3, 1, 0))             
ph_mol_o <- ph_mol %>% filter(clust %in% c(1,2,3)); dim(ph_mol_o)  
ph_mol_x <- ph_mol %>% filter(clust %in% NA); dim(ph_mol_x)
str(ph_mol_o)

phmol <- glm(formula = clust3 ~ grade_sv_y_1 + work_duration + approve_tot_request + 
                 pccontrol_mean_timeh + porta_tot_request + sna_outdegree + 
                 buha_closeness, family = "binomial", data = ph_mol_o[, -1])
summary(phmol)

pred_o <- predict(phmol, newdata=ph_mol_o)
pred_x <- predict(phmol, newdata=ph_mol_x)
id_o <- ph %>% filter(flow %in% c(1,2,3)) %>% select(id); NROW(id_o)
id_x <- ph %>% filter(flow %in% NA) %>% select(id); NROW(id_x)

ph_pred <- as.data.frame(rbind(cbind(id_o, pred=pred_o), cbind(id_x, pred=pred_x)))
colnames(ph_pred) <- c("ID", "Predict"); head(ph_pred)
ph_pred$ph_mol <- ((ph_pred$Predict-min(ph_pred$Predict)+1) /
                       (max(ph_pred$Predict)+0.5-min(ph_pred$Predict)+1)) *100
hist(ph_pred$ph_mol)

ph_sung=ph[c("grade_1", "grade_2", "grade_co_y", "grade_sv_y_1", "pmlevel", "ims_tot_enroll",
             "blog_tot_visit", "vdi_indi_tot_access", "food_tot_spend", "email_between_0709_daycnt_send")]
ph_sung$r1 <- apply(cbind(ph_sung$grade_1,ph_sung$grade_2),1,mean)
ph_sung <- ph_sung[,-c(1:2)]
ph_sung <- as.data.frame(scale(centralImputation(ph_sung)))
str(ph_sung)
phlm <- lm(r1 ~ grade_co_y + grade_sv_y_1 + pmlevel + ims_tot_enroll + blog_tot_visit +
               vdi_indi_tot_access + food_tot_spend +email_between_0709_daycnt_send, data = ph_sung)
summary(phlm)

score_phgrade <- as.data.frame(cbind(ph$id, predict(phlm, ph_sung)))
colnames(score_phgrade) <- c("ID", "Predict")
hist(score_phgrade$Predict)
score_phgrade$ph_grade <- ((score_phgrade$Predict-min(score_phgrade$Predict)+0.1) /
                               (max(score_phgrade$Predict)+0.1-min(score_phgrade$Predict)+0.1))*100
hist(score_phgrade$ph_grade)

phscore <- merge(ph_pred[,c(1,3)], score_phgrade[,c(1,3)], by="ID", all.x=T)
head(phscore)
cor(phscore$ph_mol, phscore$ph_grade)
summary(phscore)


gy <- alldata %>% filter(place %in% c("gwangyang"))
table(gy$flow)
gy_mol <- gy[c("flow", "grade_2","work_duration","btrip_nbr","approve_tot_sign","sna_closeness")]
str(gy_mol)

gy_mol <- as.data.frame(cbind(clust=gy_mol[,1], scale(centralImputation(gy_mol[,-1])))) 
gy_mol$clust3 <- factor(ifelse(gy_mol$clust==3, 1, 0))              
gy_mol_o <- gy_mol %>% filter(clust %in% c(1,2,3)); dim(gy_mol_o)  
gy_mol_x <- gy_mol %>% filter(clust %in% NA); dim(gy_mol_x)
str(gy_mol_o)

gymol <- glm(formula = clust3 ~ grade_2 + work_duration + btrip_nbr + 
                 approve_tot_sign + sna_closeness, family = "binomial", data = gy_mol_o[, -1])
summary(gymol)

pred_o <- predict(gymol, newdata=gy_mol_o)
pred_x <- predict(gymol, newdata=gy_mol_x)
id_o <- gy %>% filter(flow %in% c(1,2,3)) %>% select(id); NROW(id_o)
id_x <- gy %>% filter(flow %in% NA) %>% select(id); NROW(id_x)

gy_pred <- as.data.frame(rbind(cbind(id_o, pred=pred_o), cbind(id_x, pred=pred_x)))
colnames(gy_pred) <- c("ID", "Predict"); head(gy_pred)
gy_pred$gy_mol <- ((gy_pred$Predict-min(gy_pred$Predict)+0.01) /
                       (max(gy_pred$Predict)+0.3-min(gy_pred$Predict)+0.01)) *100

gy_sung=gy[c("grade_1", "grade_2", "grade_sv_y_1", "ims_tot_opinion_enroll",
             "thank_letter_tot_receive", "ecm_before_in79", "email_day_mean_send",
             "email_between_0709_daycnt_send", "email_between_1904_mean_send", "sangsa_eigenvector")]
gy_sung$r1 <- apply(cbind(gy_sung$grade_1, gy_sung$grade_2),1,mean)
gy_sung <- gy_sung[,-c(1:2)]
gy_sung <- as.data.frame(scale(centralImputation(gy_sung)))
str(gy_sung)

gylm <- lm(formula = 
               r1 ~ grade_sv_y_1  + 
               ims_tot_opinion_enroll + thank_letter_tot_receive + 
               ecm_before_in79 + email_day_mean_send + email_between_0709_daycnt_send + 
               email_between_1904_mean_send + sangsa_eigenvector, data = gy_sung)
summary(gylm)

score_gygrade <- as.data.frame(cbind(gy$id, predict(gylm, gy_sung)))
colnames(score_gygrade) <- c("ID", "Predict")
hist(score_gygrade$Predict)
score_gygrade$gy_grade <- ((score_gygrade$Predict-min(score_gygrade$Predict)+0.1) /
                               (max(score_gygrade$Predict)+0.1-min(score_gygrade$Predict)+0.1))*100
par(mar = c(5.1, 6.1, 4.1, 2.1))

score_gygrade %>% filter(gy_grade > 90)
score_gygrade %>% filter(gy_grade < 20)


gyscore <- merge(gy_pred[,c(1,3)], score_gygrade[,c(1,3)], by="ID", all.x=T)
head(gyscore)
cor(gyscore$gy_mol, gyscore$gy_grade)
summary(gyscore)

head(core);dim(core)
head(suscore);dim(suscore)
head(phscore);dim(phscore)
head(gyscore);dim(gyscore)

demo <- alldata %>% filter(place %in% c("pangyo", "center","pohang", "gwangyang")) %>% 
    select(id, place);dim(demo); head(demo)
colnames(demo) <- c("ID", "place")

Final_score <- Reduce( function(x, y) merge(x, y, all.x = TRUE),
                       list(demo, core, suscore, phscore, gyscore) ); head(Final_score)

Final_su <- Final_score %>% filter(place %in% c("pangyo","center")) %>% 
    select(ID, place, hagscore, su_mol, su_grade)
colnames(Final_su) <-c("ID", "place", "hagscore", "su_mol", "su_grade")
Final_ph <- Final_score %>% filter(place %in% c("pohang")) %>% 
    select(ID, place, hagscore, ph_mol, ph_grade)
colnames(Final_ph) <-c("ID", "place", "hagscore", "ph_mol", "ph_grade")
Final_gy <- Final_score %>% filter(place %in% c("gwangyang")) %>% 
    select(ID, place, hagscore, gy_mol, gy_grade)
colnames(Final_gy) <-c("ID", "place", "hagscore", "gy_mol", "gy_grade")

Final_su$su_score <- Final_su$hagscore*0.4 + Final_su$su_mol*0.3 + Final_su$su_grade*0.3
head(Final_su); dim(Final_su) 
colnames(Final_su) <- 1:6
Final_ph$phre <- Final_ph$hagscore*0.4 + Final_ph$ph_mol*0.3 + Final_ph$ph_grade*0.3
head(Final_ph); dim(Final_ph)
colnames(Final_ph) <- 1:6
Final_gy$gy_score <- Final_gy$hagscore*0.4 + Final_gy$gy_mol*0.3 + Final_gy$gy_grade*0.3 
head(Final_gy); dim(Final_gy)
colnames(Final_gy) <- 1:6

out <- rbind(Final_su, Final_ph, Final_gy)

out <- out[,c(1,4,5,3,6)]

head(out)



colnames(out) <- c("id", "score1", "score2", "score3", "score4")
head(out)
write.csv(out, "output.csv",row.names=F)
