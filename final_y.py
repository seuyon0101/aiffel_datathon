def growth_surv(*arg) :
    
    data_all = {'q202':arg[0][0],'q203':arg[0][1],'q204':arg[0][2],'q211':arg[0][3],'q212':arg[0][4],'q213':arg[0][5],'q214':arg[0][6],'q221':arg[0][7],'q222':arg[0][8],'q223':arg[0][9]}

    # merge data
    for k,v in data_all.items() :
        v['분기'] = k
        
    # 대분류 기준 : '음식'
    df_all = pd.DataFrame()
    
    for k,v in data_all.items() :
        df = v[v['상권업종대분류명'] == '음식']
        df_all = pd.concat([df_all, df], axis=0)
        
    #copy df for task
    df_all_copy = df_all.copy()
    
    new_val ={'q202':'a','q203':'b','q204':'c','q211':'d','q212':'e','q213':'f','q214':'g','q221':'h','q222':'i','q223':'j'}
    
    surv = df_all_copy.groupby([df_all_copy['분기'],df_all_copy['상가업소번호']])['상가업소번호'].count().unstack().T
    surv.iloc[:,0:10].interpolate(mothod='linear', limit_area ='inside' , axis=1, inplace=True)
    surv['생존분기수'] = surv.sum(axis=1)
    surv['페업여부'] = (surv['q223'].isnull() == True )
    
    
    for k,v in new_val.items() :
        surv.loc[surv[k].isnull() ==False,k+'_'+v] = ord(v)
    
    col_ls = ['q202','q203','q204','q211','q212','q213','q214','q221','q222','q223']
    for i in range(1,len(col_ls)) :
        surv.loc[(surv[col_ls[i-1]].isnull() == True) & (surv[col_ls[i]].isnull() == False), col_ls[i]+'_status'] = 'open'
        surv.loc[(surv[col_ls[i-1]].isnull() == False) & (surv[col_ls[i]].isnull() == True), col_ls[i]+'_status'] = 'close'

    # label 1 생존
    surv.loc[(surv['생존분기수'] > 8), 'surv'] = 1 
    
    ### merge dataset
    merging_data = surv[['페업여부','생존분기수','surv', 'q203_status', 'q204_status', 'q211_status', 'q212_status','q213_status', 'q214_status', 'q221_status', 'q222_status','q223_status']]
    df_all_copy1 = pd.merge(df_all_copy, merging_data, on='상가업소번호', how = 'inner')
    test = df_all_copy1.loc[:,['페업여부','surv','생존분기수','분기','시군구명','상가업소번호']].sort_values(by=['상가업소번호','분기']).drop_duplicates(subset='상가업소번호', keep='last')
    test['surv'].fillna(0,inplace=True)

    # #생존 count
    survcount = test.groupby(by=['시군구명'])['surv'].mean().multiply(100)
    
    
    df_all_copy1['q203_status'].fillna('ok',inplace=True)
    growth = df_all_copy1.groupby(by='시군구명')['q203_status'].value_counts().unstack()
    growth['g'] = (growth['open'] - growth['close']) / growth.sum(axis=1) *100
    
    statusq = ['q203_status', 'q204_status', 'q211_status', 'q212_status','q213_status', 'q214_status', 'q221_status', 'q222_status', 'q223_status']
    g_all = pd.DataFrame()
    for i in statusq: 
        df_all_copy1[i].fillna('ok',inplace=True)
        growth = df_all_copy1.groupby(by='시군구명')['q203_status'].value_counts().unstack()
        growth['g'+i] = (growth['open'] - growth['close']) / growth.sum(axis=1) *100
        g_all = pd.concat([g_all,growth],axis=1)

    gstatusq = ['gq203_status', 'gq204_status', 'gq211_status', 'gq212_status','gq213_status', 'gq214_status', 'gq221_status', 'gq222_status', 'gq223_status']
    g_all['gmean'] = g_all[gstatusq].mean(axis=1)
    g_mean = g_all = g_all['gmean']
    survcount = pd.DataFrame(survcount)
    final_y = pd.concat([survcount,g_mean], axis=1)
    
    return final_y