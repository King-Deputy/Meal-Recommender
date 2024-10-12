from .models import Profile
from django.shortcuts import render,redirect
from django.contrib import messages
import os
import pandas as pd
import numpy as np
import sklearn
from sklearn.neighbors import NearestNeighbors

dataset_path = "website/dataset.csv"
# dataset_path = "website\dataset.csv"
df = pd.read_csv(os.path.abspath(dataset_path))

def Recommend(request):
    
    if request.user.is_authenticated:
        class Recommender:
            
            def __init__(self):
                dataset_path = "website/dataset.csv"
                self.df = pd.read_csv(os.path.abspath(dataset_path))
            
            def get_features(self):
                #getting dummies of dataset
                nutrient_dummies = self.df.Nutrient.str.get_dummies()
                disease_dummies = self.df.Disease.str.get_dummies(sep=' ')
                diet_dummies = self.df.Diet.str.get_dummies(sep=' ')
                feature_df = pd.concat([nutrient_dummies,disease_dummies,diet_dummies],axis=1)
             
                return feature_df
            
            

            def k_neighbor(self, inputs):
                # Assuming get_features() returns the features DataFrame
                feature_df = self.get_features()
                
                # Initializing model with k=40 neighbors
                model = NearestNeighbors(n_neighbors=40, algorithm='ball_tree')
                
                # Fitting model with dataset features
                model.fit(feature_df)
                
                # Initializing an empty DataFrame with the same columns as self.df
                df_results = pd.DataFrame(columns=list(self.df.columns))
                
                # Getting distance and indices for k nearest neighbors
                distances, indices = model.kneighbors(inputs)
                
                # List to hold DataFrames
                df_list = []
                
                # Loop through the indices and collect the rows
                for idx in indices[0]:  # assuming indices is a 2D array
                    df_list.append(self.df.loc[[idx]])
                
                # Concatenate all DataFrames in the list
                df_results = pd.concat(df_list, ignore_index=True)
                
                # Filtering the required columns
                df_results = df_results.filter(['Meal_Id', 'Name', 'catagory', 'Nutrient', 'Veg_Non', 'Price', 'Review', 'Diet', 'Disease', 'description'])
                df_results = df_results.drop_duplicates(subset=['Name'])
                df_results = df_results.reset_index(drop=True)
                
                return df_results
        
        ob = Recommender()
        data = ob.get_features()
        
        total_features = data.columns
        d = dict()
        for i in total_features:
            d[i]= 0
       
        
        p=Profile.objects.get(number=request.user.username) #extract values from database where Table name is Profie
        diet=list(p.diet.split('++'))
        disease=list(p.disease.split('++'))
        nutrient=list(p.nutrient.split('++'))
        
        Recommend_input=diet+disease+nutrient
        
        image=p.image.url
       
        
        for i in Recommend_input: 
            d[i] = 1
        final_input = list(d.values())
        final_input.pop()
        #print(len(final_input))
        results = ob.k_neighbor([final_input]) # pass 2d array []
        
        
        
        # for i in Recommend_input:
        #     if i in d:         
        #        d[i] = 1
        # final_input = list(d.values())
        # final_input.pop()
        # #print(len(final_input))
        # results = ob.k_neighbor([final_input]) # pass 2d array []
       
        data=dict(results)
        
        ids=list(data['Meal_Id'])
        n=list(data['Name'])
        c=list(data['catagory'])
        vn=list(data['Veg_Non'])
        r=list(data['Review'])
        nt=list(data['Nutrient'])  
        p=list(data['Price'])
        i=range(len(n))   
        sc=c
        
        data=zip(n,ids,n,c,sc,vn,r,nt,p,p)
        
        return render(request,"website/recommend.html",{'data':data,'image':image})
    
    else:
        messages.error(request,'You must be logged in for meal recommendations..')
        return redirect('Home')
        