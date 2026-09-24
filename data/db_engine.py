"""
SeaSphere Database Engine & Persistence Layer
SQLAlchemy-based ORM supporting SQLite (default) and PostgreSQL (via DATABASE_URL).
Includes automated schema migration, initial dataset seeding, and high-performance querying.
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
import pandas as pd
from sqlalchemy import (
    create_engine, Column, Integer, Float, String, Boolean, DateTime, Date, Text, Index, desc
)
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

logger = logging.getLogger("SeaSphere.Database")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_SQLITE_PATH = os.path.join(DATA_DIR, "seasphere.db")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH}"
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
Base = declarative_base()


def get_utc_now():
    return datetime.now(timezone.utc)


class MarketDataRecord(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=get_utc_now, index=True)
    date_str = Column(String(20), index=True)
    bdi = Column(Float, nullable=False)
    bci = Column(Float, nullable=False)
    bpi = Column(Float, nullable=False)
    bsi = Column(Float, nullable=False)
    bunker_vlsfo_singapore = Column(Float, nullable=False)
    bunker_ifo380_singapore = Column(Float, default=480.0)
    crude_brent = Column(Float, default=78.5)
    coking_coal_fob_aus = Column(Float, nullable=False)
    iron_ore_cfr_china = Column(Float, default=115.0)
    port_congestion_aus_days = Column(Float, default=5.0)
    port_congestion_indo_days = Column(Float, default=4.0)
    port_congestion_india_east_days = Column(Float, nullable=False)
    monsoon_index = Column(Float, default=1.0)
    freight_aus_paradip_cape = Column(Float, nullable=False)
    freight_aus_vizag_cape = Column(Float, nullable=False)
    freight_aus_haldia_panamax = Column(Float, default=18.0)
    freight_indo_paradip_panamax = Column(Float, nullable=False)
    freight_indo_vizag_supramax = Column(Float, default=8.5)
    freight_rsa_vizag_cape = Column(Float, default=12.5)
    freight_usa_paradip_cape = Column(Float, default=29.0)
    freight_russia_vizag_panamax = Column(Float, default=16.5)
    freight_uae_paradip_supramax = Column(Float, default=7.2)
    source = Column(String(100), default="historical_seed")
    source_url = Column(String(200), default="https://www.balticexchange.com")
    source_type = Column(String(100), default="Institutional Market Benchmark")
    fetched_at = Column(String(50), nullable=True)
    data_quality = Column(String(50), default="High (Verified)")
    is_live = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "date": self.date_str,
            "bdi": self.bdi,
            "bci": self.bci,
            "bpi": self.bpi,
            "bsi": self.bsi,
            "bunker_vlsfo_singapore": self.bunker_vlsfo_singapore,
            "bunker_ifo380_singapore": self.bunker_ifo380_singapore,
            "crude_brent": self.crude_brent,
            "coking_coal_fob_aus": self.coking_coal_fob_aus,
            "iron_ore_cfr_china": self.iron_ore_cfr_china,
            "port_congestion_aus_days": self.port_congestion_aus_days,
            "port_congestion_indo_days": self.port_congestion_indo_days,
            "port_congestion_india_east_days": self.port_congestion_india_east_days,
            "monsoon_index": self.monsoon_index,
            "freight_aus_paradip_cape": self.freight_aus_paradip_cape,
            "freight_aus_vizag_cape": self.freight_aus_vizag_cape,
            "freight_aus_haldia_panamax": self.freight_aus_haldia_panamax,
            "freight_indo_paradip_panamax": self.freight_indo_paradip_panamax,
            "freight_indo_vizag_supramax": self.freight_indo_vizag_supramax,
            "freight_rsa_vizag_cape": self.freight_rsa_vizag_cape,
            "freight_usa_paradip_cape": self.freight_usa_paradip_cape,
            "freight_russia_vizag_panamax": self.freight_russia_vizag_panamax,
            "freight_uae_paradip_supramax": self.freight_uae_paradip_supramax,
            "source": self.source,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "fetched_at": self.fetched_at or (self.timestamp.isoformat() if self.timestamp else None),
            "data_quality": self.data_quality or "High (Verified)",
            "is_live": self.is_live
        }


class PortWeatherRecord(Base):
    __tablename__ = "port_weather_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=get_utc_now, index=True)
    date_str = Column(String(20), index=True)
    port_name = Column(String(100), index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temp_max = Column(Float, nullable=False)
    temp_min = Column(Float, nullable=False)
    max_wind_kmh = Column(Float, nullable=False)
    precipitation_mm = Column(Float, nullable=False)
    wmo_code = Column(Integer, nullable=False)
    condition = Column(String(100), default="Mainly Clear")
    operational_risk = Column(String(50), default="Low")
    source = Column(String(100), default="open_meteo_live")
    source_url = Column(String(200), default="https://api.open-meteo.com/v1/forecast")
    source_type = Column(String(100), default="Live Meteorological API")
    fetched_at = Column(String(50), nullable=True)
    data_quality = Column(String(50), default="High (Verified Live)")

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "date": self.date_str,
            "port_name": self.port_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "temperature_max_c": self.temp_max,
            "temperature_min_c": self.temp_min,
            "max_wind_kmh": self.max_wind_kmh,
            "precipitation_mm": self.precipitation_mm,
            "wmo_code": self.wmo_code,
            "condition": self.condition,
            "operational_risk": self.operational_risk,
            "source": self.source,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "fetched_at": self.fetched_at or (self.timestamp.isoformat() if self.timestamp else None),
            "data_quality": self.data_quality or "High (Verified Live)"
        }


class PortTrafficRecord(Base):
    __tablename__ = "port_traffic_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(String(20), index=True, nullable=False)
    port_id = Column(String(50), index=True, nullable=False)
    port_name = Column(String(100), nullable=False)
    actual_traffic_mt = Column(Float, nullable=False)
    overseas_traffic_mt = Column(Float, default=0.0)
    coastal_traffic_mt = Column(Float, default=0.0)
    capacity_mt = Column(Float, default=0.0)

    def to_dict(self):
        return {
            "id": self.id,
            "year": self.year,
            "port_id": self.port_id,
            "port_name": self.port_name,
            "actual_traffic_mt": self.actual_traffic_mt,
            "overseas_traffic_mt": self.overseas_traffic_mt,
            "coastal_traffic_mt": self.coastal_traffic_mt,
            "capacity_mt": self.capacity_mt
        }


class IngestionLogRecord(Base):
    __tablename__ = "ingestion_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=get_utc_now, index=True)
    source_name = Column(String(100), nullable=False)
    records_ingested = Column(Integer, default=0)
    status = Column(String(20), default="success")
    message = Column(Text, default="")
    latency_ms = Column(Float, default=0.0)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source_name": self.source_name,
            "records_ingested": self.records_ingested,
            "status": self.status,
            "message": self.message,
            "latency_ms": round(self.latency_ms, 2)
        }


class DatabaseManager:
    """Manages DB lifecycle, seeding, transactions, and unified querying."""

    def __init__(self):
        self.engine = engine
        self.Session = Session
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist and perform safe column migration."""
        Base.metadata.create_all(self.engine)
        self._migrate_columns()
        self._seed_initial_data()

    def _migrate_columns(self):
        """Safely ensures new metadata and provenance columns exist in existing tables."""
        from sqlalchemy import text
        with self.engine.connect() as conn:
            # Check market_data columns
            for col, col_type in [
                ("source_url", "VARCHAR(200) DEFAULT 'https://www.balticexchange.com'"),
                ("source_type", "VARCHAR(100) DEFAULT 'Institutional Market Benchmark'"),
                ("fetched_at", "VARCHAR(50)"),
                ("data_quality", "VARCHAR(50) DEFAULT 'High (Verified)'")
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE market_data ADD COLUMN {col} {col_type}"))
                    conn.commit()
                except Exception:
                    pass

            # Check port_weather_data columns
            for col, col_type in [
                ("source_url", "VARCHAR(200) DEFAULT 'https://api.open-meteo.com/v1/forecast'"),
                ("source_type", "VARCHAR(100) DEFAULT 'Live Meteorological API'"),
                ("fetched_at", "VARCHAR(50)"),
                ("data_quality", "VARCHAR(50) DEFAULT 'High (Verified Live)'")
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE port_weather_data ADD COLUMN {col} {col_type}"))
                    conn.commit()
                except Exception:
                    pass

    def get_session(self):
        return self.Session()

    def _seed_initial_data(self):
        """Seeds historical CSV & JSON datasets into database if empty."""
        session = self.get_session()
        try:
            # 1. Seed Market Data
            market_count = session.query(MarketDataRecord).count()
            if market_count == 0:
                csv_path = os.path.join(DATA_DIR, "historical_freight.csv")
                if os.path.exists(csv_path):
                    logger.info("Seeding historical market data into database...")
                    df = pd.read_csv(csv_path)
                    records = []
                    for _, row in df.iterrows():
                        rec = MarketDataRecord(
                            date_str=str(row.get("date")),
                            bdi=float(row.get("bdi", 0)),
                            bci=float(row.get("bci", 0)),
                            bpi=float(row.get("bpi", 0)),
                            bsi=float(row.get("bsi", 0)),
                            bunker_vlsfo_singapore=float(row.get("bunker_vlsfo_singapore", 0)),
                            bunker_ifo380_singapore=float(row.get("bunker_ifo380_singapore", 480.0)),
                            crude_brent=float(row.get("crude_brent", 78.5)),
                            coking_coal_fob_aus=float(row.get("coking_coal_fob_aus", 0)),
                            iron_ore_cfr_china=float(row.get("iron_ore_cfr_china", 115.0)),
                            port_congestion_aus_days=float(row.get("port_congestion_aus_days", 5.0)),
                            port_congestion_indo_days=float(row.get("port_congestion_indo_days", 4.0)),
                            port_congestion_india_east_days=float(row.get("port_congestion_india_east_days", 0)),
                            monsoon_index=float(row.get("monsoon_index", 1.0)),
                            freight_aus_paradip_cape=float(row.get("freight_aus_paradip_cape", 0)),
                            freight_aus_vizag_cape=float(row.get("freight_aus_vizag_cape", 0)),
                            freight_aus_haldia_panamax=float(row.get("freight_aus_haldia_panamax", 18.0)),
                            freight_indo_paradip_panamax=float(row.get("freight_indo_paradip_panamax", 0)),
                            freight_indo_vizag_supramax=float(row.get("freight_indo_vizag_supramax", 8.5)),
                            freight_rsa_vizag_cape=float(row.get("freight_rsa_vizag_cape", 12.5)),
                            freight_usa_paradip_cape=float(row.get("freight_usa_paradip_cape", 29.0)),
                            freight_russia_vizag_panamax=float(row.get("freight_russia_vizag_panamax", 16.5)),
                            freight_uae_paradip_supramax=float(row.get("freight_uae_paradip_supramax", 7.2)),
                            source="historical_seed",
                            is_live=False
                        )
                        records.append(rec)
                    session.bulk_save_objects(records)
                    session.commit()
                    logger.info(f"Successfully seeded {len(records)} market records.")

            # 2. Seed Port Weather Data
            weather_count = session.query(PortWeatherRecord).count()
            if weather_count == 0:
                weather_json_path = os.path.join(DATA_DIR, "port_weather_forecast.json")
                if os.path.exists(weather_json_path):
                    logger.info("Seeding initial port weather data into database...")
                    with open(weather_json_path, "r", encoding="utf-8") as f:
                        w_data = json.load(f)
                    w_records = []
                    by_port = w_data.get("by_port", {})
                    for p_name, p_info in by_port.items():
                        lat = float(p_info.get("latitude", 0))
                        lon = float(p_info.get("longitude", 0))
                        for f_day in p_info.get("forecast_days", []):
                            w_rec = PortWeatherRecord(
                                date_str=f_day.get("date"),
                                port_name=p_name,
                                latitude=lat,
                                longitude=lon,
                                temp_max=float(f_day.get("temperature_max_c", 30)),
                                temp_min=float(f_day.get("temperature_min_c", 22)),
                                max_wind_kmh=float(f_day.get("max_wind_kmh", 15)),
                                precipitation_mm=float(f_day.get("precipitation_mm", 0)),
                                wmo_code=int(f_day.get("wmo_code", 1)),
                                condition=f_day.get("condition", "Mainly Clear"),
                                operational_risk=f_day.get("operational_risk", "Low"),
                                source="initial_seed"
                            )
                            w_records.append(w_rec)
                    session.bulk_save_objects(w_records)
                    session.commit()
                    logger.info(f"Successfully seeded {len(w_records)} port weather records.")

            # 3. Log initial ingestion status
            log_count = session.query(IngestionLogRecord).count()
            if log_count == 0:
                log_rec = IngestionLogRecord(
                    source_name="System Initialization & Database Seeder",
                    records_ingested=session.query(MarketDataRecord).count() + session.query(PortWeatherRecord).count(),
                    status="success",
                    message="SeaSphere persistence layer initialized with full historical dataset."
                )
                session.add(log_rec)
                session.commit()

        except Exception as e:
            session.rollback()
            logger.error(f"Database initialization seeding error: {e}", exc_info=True)
        finally:
            session.close()

    def get_latest_market_record(self):
        """Returns the most recent market record dict."""
        session = self.get_session()
        try:
            rec = session.query(MarketDataRecord).order_by(desc(MarketDataRecord.id)).first()
            return rec.to_dict() if rec else None
        finally:
            session.close()

    def get_market_history_df(self, limit=365):
        """Returns a Pandas DataFrame of market history ordered chronologically."""
        session = self.get_session()
        try:
            records = session.query(MarketDataRecord).order_by(desc(MarketDataRecord.id)).limit(limit).all()
            records.reverse()
            data = [r.to_dict() for r in records]
            if not data:
                return pd.DataFrame()
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            return df
        finally:
            session.close()

    def get_port_weather(self, port_name=None, horizon_days=30):
        """Returns port weather forecast records from DB."""
        session = self.get_session()
        try:
            q = session.query(PortWeatherRecord)
            if port_name:
                q = q.filter(PortWeatherRecord.port_name.ilike(f"%{port_name}%"))
            records = q.order_by(PortWeatherRecord.date_str).limit(horizon_days * 10).all()
            return [r.to_dict() for r in records]
        finally:
            session.close()

    def insert_live_market_tick(self, record_dict):
        """Inserts a new live market tick into the database."""
        session = self.get_session()
        try:
            rec = MarketDataRecord(
                timestamp=get_utc_now(),
                date_str=record_dict.get("date", get_utc_now().strftime("%Y-%m-%d")),
                bdi=float(record_dict["bdi"]),
                bci=float(record_dict["bci"]),
                bpi=float(record_dict["bpi"]),
                bsi=float(record_dict["bsi"]),
                bunker_vlsfo_singapore=float(record_dict["bunker_vlsfo_singapore"]),
                bunker_ifo380_singapore=float(record_dict.get("bunker_ifo380_singapore", 480.0)),
                crude_brent=float(record_dict.get("crude_brent", 78.5)),
                coking_coal_fob_aus=float(record_dict["coking_coal_fob_aus"]),
                iron_ore_cfr_china=float(record_dict.get("iron_ore_cfr_china", 115.0)),
                port_congestion_aus_days=float(record_dict.get("port_congestion_aus_days", 5.0)),
                port_congestion_indo_days=float(record_dict.get("port_congestion_indo_days", 4.0)),
                port_congestion_india_east_days=float(record_dict["port_congestion_india_east_days"]),
                monsoon_index=float(record_dict.get("monsoon_index", 1.0)),
                freight_aus_paradip_cape=float(record_dict["freight_aus_paradip_cape"]),
                freight_aus_vizag_cape=float(record_dict["freight_aus_vizag_cape"]),
                freight_aus_haldia_panamax=float(record_dict.get("freight_aus_haldia_panamax", 18.0)),
                freight_indo_paradip_panamax=float(record_dict["freight_indo_paradip_panamax"]),
                freight_indo_vizag_supramax=float(record_dict.get("freight_indo_vizag_supramax", 8.5)),
                freight_rsa_vizag_cape=float(record_dict.get("freight_rsa_vizag_cape", 12.5)),
                freight_usa_paradip_cape=float(record_dict.get("freight_usa_paradip_cape", 29.0)),
                freight_russia_vizag_panamax=float(record_dict.get("freight_russia_vizag_panamax", 16.5)),
                freight_uae_paradip_supramax=float(record_dict.get("freight_uae_paradip_supramax", 7.2)),
                source=record_dict.get("source", "live_ingestion"),
                is_live=True
            )
            session.add(rec)
            session.commit()
            return rec.to_dict()
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting live market tick: {e}")
            raise
        finally:
            session.close()

    def update_port_weather_batch(self, weather_records, port_name):
        """Replaces or updates weather forecast for a port."""
        session = self.get_session()
        try:
            session.query(PortWeatherRecord).filter(PortWeatherRecord.port_name == port_name).delete()
            objs = []
            for r in weather_records:
                objs.append(PortWeatherRecord(
                    timestamp=get_utc_now(),
                    date_str=r["date"],
                    port_name=port_name,
                    latitude=r["latitude"],
                    longitude=r["longitude"],
                    temp_max=r["temperature_max_c"],
                    temp_min=r["temperature_min_c"],
                    max_wind_kmh=r["max_wind_kmh"],
                    precipitation_mm=r["precipitation_mm"],
                    wmo_code=r["wmo_code"],
                    condition=r["condition"],
                    operational_risk=r["operational_risk"],
                    source=r.get("source", "open_meteo_live")
                ))
            session.bulk_save_objects(objs)
            session.commit()
            return len(objs)
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating port weather batch: {e}")
            raise
        finally:
            session.close()

    def log_ingestion(self, source_name, count, status="success", message="", latency_ms=0.0):
        """Records an entry in the ingestion audit trail."""
        session = self.get_session()
        try:
            log = IngestionLogRecord(
                source_name=source_name,
                records_ingested=count,
                status=status,
                message=message,
                latency_ms=latency_ms
            )
            session.add(log)
            session.commit()
            return log.to_dict()
        except Exception as e:
            session.rollback()
            logger.error(f"Error logging ingestion event: {e}")
        finally:
            session.close()

    def get_ingestion_logs(self, limit=20):
        """Returns recent ingestion audit trail logs."""
        session = self.get_session()
        try:
            logs = session.query(IngestionLogRecord).order_by(desc(IngestionLogRecord.id)).limit(limit).all()
            return [l.to_dict() for l in logs]
        finally:
            session.close()

    def get_database_stats(self):
        """Returns summary statistics of tables in the database."""
        session = self.get_session()
        try:
            market_total = session.query(MarketDataRecord).count()
            live_market = session.query(MarketDataRecord).filter(MarketDataRecord.is_live == True).count()
            weather_total = session.query(PortWeatherRecord).count()
            logs_total = session.query(IngestionLogRecord).count()
            latest_market = session.query(MarketDataRecord).order_by(desc(MarketDataRecord.id)).first()
            latest_log = session.query(IngestionLogRecord).order_by(desc(IngestionLogRecord.id)).first()

            return {
                "engine": "PostgreSQL" if "postgresql" in str(self.engine.url) else "SQLite",
                "database_url": str(self.engine.url).split("@")[-1],
                "market_records_total": market_total,
                "live_ticks_ingested": live_market,
                "weather_records_total": weather_total,
                "ingestion_logs_total": logs_total,
                "last_market_date": latest_market.date_str if latest_market else None,
                "last_sync_timestamp": latest_log.timestamp.isoformat() if latest_log and latest_log.timestamp else None
            }
        finally:
            session.close()


# Singleton instance for platform-wide database interaction
db_manager = DatabaseManager()
