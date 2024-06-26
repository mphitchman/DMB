
df1 = hit_lg[['ops']].rename(columns = {'ops':'ops_hit'})
df2 = pit_lg[['ops']].rename(columns = {'ops':'ops_pit'})
df = df1.join(df2)
x_sel = 'ops_pit'
y_sel = 'ops_hit'
x_avg = df[x_sel].mean()
y_avg = df[y_sel].mean()
x_max = df[x_sel].max()
y_max = df[y_sel].max()
x_space = (x_max-df[x_sel].min())/60
y_space = (y_max-df[y_sel].min())/50 
p1 = sns.scatterplot(data=df,x=x_sel,y=y_sel).set_title("Team Hit and Pitch OPS")
plt.axvline(x=x_avg,linestyle="dashed",linewidth=1)
plt.axhline(y=y_avg,linestyle="dashed",linewidth=1)
#plt.text(x=x_avg+x_space,y=y_max-y_space,s="avg",color='blue')
#plt.text(x=x_max-x_space,y=y_avg+y_space,s="avg",color='blue')
for line in range(0,df.shape[0]):
    plt.text(x=df[x_sel].iloc[line],y=df[y_sel].iloc[line]+y_space,s=df.index[line],horizontalalignment='left',size='small', color='black')
#import seaborn.objects as so
#p1=(so.Plot(mph, x="ops_hit", y="ops_pit",).add(so.Dot(color="g")))

st.pyplot(p1.get_figure())

