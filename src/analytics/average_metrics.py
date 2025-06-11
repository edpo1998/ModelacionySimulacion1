from sqlalchemy import func, and_, or_
import statistics
from src.utils.db import SessionLocal
from src.models.dim_time import DimTime
from src.models.fact_energy import FactEnergy
from pprint import pprint

def monthly_energy_cost(labor_start=8, labor_end=20):
    """
    Devuelve lista de (mes, costo_total) considerando solo horas entre labor_start (incluido)
    y labor_end (excluido)."""
    session = SessionLocal()
    try:
        q = (
            session.query(
                DimTime.month.label('month'),
                func.sum(FactEnergy.cost).label('total_cost')
            )
            .join(FactEnergy, FactEnergy.time_id == DimTime.time_id)
            .filter(
                and_(
                    FactEnergy.consumption_hour >= labor_start,
                    FactEnergy.consumption_hour < labor_end
                )
            )
            .group_by(DimTime.month)
            .order_by(DimTime.month)
        )
        return [(int(m), float(c)) for m, c in q.all()]
    finally:
        session.close()


def cost_for_model(consumption_rate_mwh, labor_start=8, labor_end=20, time_factor=1.0):
    """
    Recalcula los costos mensuales variando el consumo_mwh por hora dentro del horario dado
    y ajustando por un factor de tiempo (por ejemplo 0.5 para trabajar la mitad del tiempo).
    """
    base = monthly_energy_cost(labor_start, labor_end)
    factor = consumption_rate_mwh / 0.2
    return [(m, c * factor * time_factor) for m, c in base]


def most_and_least_profitable(labor_start=8, labor_end=20):
    """
    Retorna tuplas (mes_mas_barato, costo), (mes_mas_caro, costo) dentro del horario dado.
    """
    data = monthly_energy_cost(labor_start, labor_end)
    cheapest = min(data, key=lambda x: x[1])
    priciest = max(data, key=lambda x: x[1])
    return cheapest, priciest


def scenario_costs(month, consumption_rate_mwh=0.2, labor_start=8, labor_end=20, time_factor=1.0, scenarios=None):
    """
    Calcula costo total en un mes dado para diferentes esquemas de descanso.
    Permite ajustar consumo y factor de tiempo.
    """
    session = SessionLocal()
    try:
        if scenarios is None:
            scenarios = {
                'a': [(0, 4), (12, 16)],
                'b': [(0, 8), (12, 16), (20, 24)],
                'c': [(0, 8), (12, 20)]
            }
        results = {}
        for key, intervals in scenarios.items():
            query = (
                session.query(func.sum(FactEnergy.cost).label('cost'))
                .join(DimTime, FactEnergy.time_id == DimTime.time_id)
                .filter(DimTime.month == month)
            )
            interval_conditions = [
                and_(
                    FactEnergy.consumption_hour >= start,
                    FactEnergy.consumption_hour < end
                )
                for start, end in intervals
            ]
            total = query.filter(or_(*interval_conditions)).scalar() or 0
            factor = consumption_rate_mwh / 0.2
            results[key] = float(total) * float(factor) * float(time_factor)
        return results
    finally:
        session.close()

if __name__ == '__main__':
    pprint(f"Costo actual (8-20h): {statistics.mean([item for _,item in monthly_energy_cost()])}")
    pprint(f"Costo al 0.15 MWh/h, mitad tiempo: { statistics.mean([item for _,item in cost_for_model(0.15, time_factor=0.5)])}")
    pprint(f"Más/menos rentable (8-20h): {most_and_least_profitable()}")
    pprint(f"Escenarios en feb (mitad tiempo): {scenario_costs(2, consumption_rate_mwh=0.15, time_factor=0.5)}")
