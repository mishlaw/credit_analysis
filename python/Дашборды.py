import pandas as pd
from sqlalchemy import create_engine

import sys
print(sys.executable)

engine = create_engine("postgresql://postgres:admin@localhost:5432/Credit_analysis")

df = pd.read_sql("SELECT * FROM credit_data", engine)
df.head()

print(df.shape)          
df.info()                
df.isna().sum()          
df['default_status'].value_counts() 
total_loans  = len(df)
total_amount = df['amount'].sum()
avg_amount   = df['amount'].mean()
bad_loans    = (df['default_status'] == 'yes').sum()
npl_percent  = bad_loans / total_loans * 100

print(f"Всего кредитов: {total_loans}")
print(f"Общая сумма: {total_amount:,.2f}")
print(f"Средний кредит: {avg_amount:,.2f}")
print(f"NPL: {npl_percent:.2f}%")

#средний размер по типу занятости
job_stats = (df
    .groupby('job', as_index=False)
    .agg(count=('amount', 'size'),
         avg_amount=('amount', 'mean'))
    .sort_values('count', ascending=False)
)
job_stats

#Доля просрочки по цели кредита
purpose_stats = (df
    .groupby('purpose')
    .agg(
        total=('default_status', 'size'),
        bad=('default_status', lambda x: (x == 'yes').sum())
    )
)
purpose_stats['npl_percent'] = purpose_stats['bad'] / purpose_stats['total'] * 100
purpose_stats = purpose_stats.sort_values('npl_percent', ascending=False).reset_index()
purpose_stats

# NPL по типу занятости
npl_by_job = (df
    .assign(is_bad=df['default_status'] == 'yes')
    .groupby('job', as_index=False)
    .agg(total=('is_bad', 'size'),
         bad=('is_bad', 'sum'))
)
npl_by_job['npl_percent'] = npl_by_job['bad'] / npl_by_job['total'] * 100

# Распределение сумм кредитов
df['amount'].describe()

import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

sns.set_style("whitegrid")
fig = plt.figure(figsize=(16, 10))
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.3)

#KPI
kpi_ax = fig.add_subplot(gs[0, :])
kpi_ax.axis('off')
kpi_text = (
    f"Всего кредитов: {total_loans:,}     |     "
    f"Общая сумма: {total_amount:,.0f}     |     "
    f"Средний кредит: {avg_amount:,.0f}     |     "
    f"Просрочки: {bad_loans:,} ({npl_percent:.1f}%)"
)
kpi_ax.text(0.5, 0.5, kpi_text, ha='center', va='center',
            fontsize=16, fontweight='bold', color='#2c3e50')
kpi_ax.set_title("Кредитная аналитика — ключевые метрики",
                 fontsize=20, fontweight='bold', pad=20)

#Средний размер кредита по профессии 
ax1 = fig.add_subplot(gs[1, :2])
job_stats_sorted = job_stats.sort_values('avg_amount', ascending=True)
ax1.barh(job_stats_sorted['job'], job_stats_sorted['avg_amount'], color='#3498db')
ax1.set_title("Средний размер кредита по типу занятости")
ax1.set_xlabel("Средняя сумма")

# NPL по цели кредита 
ax2 = fig.add_subplot(gs[1, 2])
ax2.pie(purpose_stats['bad'],
        labels=purpose_stats['purpose'],
        autopct='%1.0f%%',
        colors=sns.color_palette("Set2"))
ax2.set_title("Просрочки по целям")

# NPL % по профессии 
ax3 = fig.add_subplot(gs[2, :])
npl_sorted = npl_by_job.sort_values('npl_percent', ascending=False)
sns.barplot(
    data=npl_sorted,
    x='job',
    y='npl_percent',
    ax=ax3,
    hue='job',           
    palette='Reds_r',
    legend=False         
)
ax3.set_title("Доля просрочки (NPL %) по типу занятости")
ax3.set_ylabel("NPL, %")
plt.setp(ax3.get_xticklabels(), rotation=30, ha='right')

plt.savefig("dashboard.png", dpi=150, bbox_inches='tight')
plt.show()