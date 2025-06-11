import os
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import func, and_
from src.utils.db import SessionLocal
from src.analytics import monthly_energy_cost, cost_for_model, scenario_costs, most_and_least_profitable
from src.models.dim_time import DimTime
from src.models.fact_energy import FactEnergy



def generate_report( output_dir='reports', model_rate=0.15, labor_start=8, labor_end=20, scenario_month=2, scenarios=None):
    os.makedirs(output_dir, exist_ok=True)
    df_current = pd.DataFrame(
        monthly_energy_cost(labor_start, labor_end),
        columns=['month', 'cost_actual']
    )
    df_model = pd.DataFrame(
        cost_for_model(model_rate, labor_start, labor_end),
        columns=['month', 'cost_model']
    )
    df = pd.merge(df_current, df_model, on='month')
    cheapest, priciest = most_and_least_profitable(labor_start, labor_end)
    df_s = pd.DataFrame(
        list(scenario_costs(scenario_month, model_rate, scenarios).items()),
        columns=['scenario', 'cost']
    )
    session = SessionLocal()
    try:
        base_q = session.query(func.sum(FactEnergy.cost).label('total_cost'))
        base_q = base_q.join(DimTime, FactEnergy.time_id == DimTime.time_id)
        base_q = base_q.filter(
            and_(FactEnergy.consumption_hour >= labor_start,
                 FactEnergy.consumption_hour < labor_end)
        )
        weekday_cost = base_q.filter(DimTime.is_weekend == False).scalar() or 0
        weekend_cost = base_q.filter(DimTime.is_weekend == True).scalar() or 0
        season_q = (
            session.query(
                DimTime.season,
                func.sum(FactEnergy.cost).label('season_cost')
            )
            .join(FactEnergy, FactEnergy.time_id == DimTime.time_id)
            .filter(
                and_(FactEnergy.consumption_hour >= labor_start,
                     FactEnergy.consumption_hour < labor_end)
            )
            .group_by(DimTime.season)
        )
        df_season = pd.DataFrame(season_q.all(), columns=['season', 'cost'])
        trend_ws_q = (
            session.query(
                DimTime.month.label('month'),
                func.sum(FactEnergy.cost).label('cost')
            )
            .join(FactEnergy, FactEnergy.time_id == DimTime.time_id)
            .filter(
                and_(
                    FactEnergy.consumption_hour >= labor_start,
                    FactEnergy.consumption_hour < labor_end,
                    DimTime.is_weekend == False
                )
            )
            .group_by(DimTime.month)
            .order_by(DimTime.month)
        )
        df_workday = pd.DataFrame(trend_ws_q.all(), columns=['month', 'cost'])
        trend_nfh_q = (
            session.query(
                DimTime.month.label('month'),
                func.sum(FactEnergy.cost).label('cost')
            )
            .join(FactEnergy, FactEnergy.time_id == DimTime.time_id)
            .filter(
                and_(
                    FactEnergy.consumption_hour >= labor_start,
                    FactEnergy.consumption_hour < labor_end,
                    DimTime.is_holiday == False
                )
            )
            .group_by(DimTime.month)
            .order_by(DimTime.month)
        )
        df_noholiday = pd.DataFrame(trend_nfh_q.all(), columns=['month', 'cost'])
    finally:
        session.close()

    df_daytype = pd.DataFrame(
        [['Laboral', float(weekday_cost)], ['Fin de semana', float(weekend_cost)]],
        columns=['day_type', 'cost']
    )
    if scenarios is None:
        scenarios = {'a': [(0,4),(12,16)], 'b': [(0,8),(12,16),(20,24)], 'c': [(0,8),(12,20)]}
    records = []
    for month in sorted(df['month']):
        costs = scenario_costs(month, consumption_rate_mwh=model_rate, scenarios=scenarios)
        rec = {'month': month}
        rec.update(costs)
        records.append(rec)
    df_month_scenarios = pd.DataFrame(records)
    trend_path = os.path.join(output_dir, 'monthly_trend.png')
    plt.figure()
    plt.plot(df['month'], df['cost_actual'], marker='o', label='Actual')
    plt.plot(df['month'], df['cost_model'], marker='o', label=f'Modelo {model_rate}')
    plt.xticks(df['month'])
    plt.xlabel('Mes')
    plt.ylabel('Costo')
    plt.title('Tendencia mensual (08-20h)')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(trend_path)
    plt.close()
    workday_path = os.path.join(output_dir, 'monthly_trend_workdays.png')
    plt.figure()
    plt.plot(df_workday['month'], df_workday['cost'], marker='o', color='tab:green')
    plt.xticks(df_workday['month'])
    plt.xlabel('Mes')
    plt.ylabel('Costo')
    plt.title('Tendencia mensual sin fines de semana (08-20h)')
    plt.grid()
    plt.tight_layout()
    plt.savefig(workday_path)
    plt.close()
    noholiday_path = os.path.join(output_dir, 'monthly_trend_noholiday.png')
    plt.figure()
    plt.plot(df_noholiday['month'], df_noholiday['cost'], marker='o', color='tab:red')
    plt.xticks(df_noholiday['month'])
    plt.xlabel('Mes')
    plt.ylabel('Costo')
    plt.title('Tendencia mensual sin feriados (08-20h)')
    plt.grid()
    plt.tight_layout()
    plt.savefig(noholiday_path)
    plt.close()
    scenario_path = os.path.join(output_dir, f'scenarios_month_{scenario_month}.png')
    plt.figure()
    plt.bar(df_s['scenario'], df_s['cost'])
    plt.xlabel('Escenario')
    plt.ylabel('Costo')
    plt.title(f'Escenarios mes {scenario_month}')
    plt.tight_layout()
    plt.savefig(scenario_path)
    plt.close()
    daytype_path = os.path.join(output_dir, 'cost_by_daytype.png')
    plt.figure()
    plt.bar(df_daytype['day_type'], df_daytype['cost'])
    plt.xlabel('Tipo de Día')
    plt.ylabel('Costo')
    plt.title('Costo por tipo de día')
    plt.tight_layout()
    plt.savefig(daytype_path)
    plt.close()
    season_path = os.path.join(output_dir, 'cost_by_season.png')
    plt.figure()
    plt.bar(df_season['season'], df_season['cost'])
    plt.xlabel('Estación')
    plt.ylabel('Costo')
    plt.title('Costo por estación')
    plt.tight_layout()
    plt.savefig(season_path)
    plt.close()
    month_s_path = os.path.join(output_dir, 'monthly_scenarios.png')
    plt.figure()
    for scenario in scenarios:
        plt.plot(df_month_scenarios['month'], df_month_scenarios[scenario], marker='o', label=scenario)
    plt.xticks(df_month_scenarios['month'])
    plt.xlabel('Mes')
    plt.ylabel('Costo')
    plt.title('Comparación escenarios mensual')
    plt.legend()
    plt.tight_layout()
    plt.savefig(month_s_path)
    plt.close()
    md_path = os.path.join(output_dir, 'report.md')
    with open(md_path, 'w') as md:
        md.write('# Reporte de Rentabilidad Energética\n')
        md.write('\n')
        md.write('## Resumen de Costos\n')
        md.write('\n')
        md.write(df.to_markdown(index=False) + '\n')
        md.write('\n')
        md.write(f'- Mes más rentable: **{cheapest[0]}** ({cheapest[1]:.2f} US$)\n')
        md.write(f'- Mes menos rentable: **{priciest[0]}** ({priciest[1]:.2f} US$)\n')
        md.write('\n')
        md.write('## Tendencia Mensual\n')
        md.write('\n')
        md.write(f'![Tendencia]({os.path.basename(trend_path)})\n')
        md.write('\n')
        md.write('## Tendencia sin fines de semana\n')
        md.write('\n')
        md.write(f'![Sin fines de semana]({os.path.basename(workday_path)})\n')
        md.write('\n')
        md.write('## Tendencia sin feriados\n')
        md.write('\n')
        md.write(f'![Sin feriados]({os.path.basename(noholiday_path)})\n')
        md.write('\n')
        md.write(f'## Escenarios Mes {scenario_month}\n')
        md.write('\n')
        md.write(df_s.to_markdown(index=False) + '\n')
        md.write('\n')
        md.write(f'![Escenarios]({os.path.basename(scenario_path)})\n')
        md.write('\n')
        md.write('## Costos por Tipo de Día (08-20h)\n')
        md.write('\n')
        md.write(df_daytype.to_markdown(index=False) + '\n')
        md.write('\n')
        md.write(f'![Tipo de Día]({os.path.basename(daytype_path)})\n')
        md.write('\n')
        md.write('## Costos por Estación\n')
        md.write('\n')
        md.write(df_season.to_markdown(index=False) + '\n')
        md.write('\n')
        md.write(f'![Estación]({os.path.basename(season_path)})\n')
        md.write('\n')
        md.write('## Comparación Escenarios Mensual\n')
        md.write('\n')
        md.write(df_month_scenarios.to_markdown(index=False) + '\n')
        md.write('\n')
        md.write(f'![Escenarios Mensual]({os.path.basename(month_s_path)})\n')
    print(f'Reporte generado en carpeta: {output_dir}')
if __name__ == '__main__':
    generate_report()
