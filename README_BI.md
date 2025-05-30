# Puzzle Swap ETL - Business Intelligence Setup

This document describes the Business Intelligence (BI) setup for the Puzzle Swap ETL pipeline, including Apache Superset integration and the three-schema data warehouse architecture.

## Architecture Overview

The system now implements a modern data warehouse architecture with three distinct schemas:

### 📊 Schema Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   STG Schema    │───▶│   ODS Schema    │───▶│   DM Schema     │
│  (Staging)      │    │ (Operational    │    │ (Data Mart)     │
│                 │    │  Data Store)    │    │                 │
│ • Raw data      │    │ • Cleaned data  │    │ • Aggregated    │
│ • External APIs │    │ • Validated     │    │ • Business KPIs │
│ • Blockchain    │    │ • Enriched      │    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🏗️ Schema Details

#### **STG (Staging) Schema**
- **Purpose**: Raw data from external sources
- **Tables**:
  - `stg.transactions` - Raw blockchain transactions
  - `stg.price_data` - Raw price data from APIs
  - `stg.asset_info` - Raw asset information
  - `stg.pool_info` - Raw pool data from Puzzle API
- **Characteristics**: 
  - Minimal processing
  - Includes ETL metadata (batch_id, loaded_at)
  - Preserves original data structure

#### **ODS (Operational Data Store) Schema**
- **Purpose**: Cleaned, validated, and enriched data
- **Tables**:
  - `ods.transactions` - Cleaned transaction data
  - `ods.swaps` - Processed swap transactions
  - `ods.staking_events` - Processed staking events
  - `ods.assets` - Validated asset information
  - `ods.pools` - Enriched pool data
- **Characteristics**:
  - Data quality validation
  - Business rules applied
  - Normalized amounts and decimals
  - USD value calculations

#### **DM (Data Mart) Schema**
- **Purpose**: Business-ready aggregated data for analytics
- **Tables**:
  - `dm.trading_metrics_daily` - Daily trading aggregations
  - `dm.staking_metrics_daily` - Daily staking aggregations
  - `dm.pool_metrics` - Pool performance metrics
  - `dm.trader_metrics` - Trader performance metrics
  - `dm.asset_metrics` - Asset trading metrics
  - `dm.kpi_summary` - Key Performance Indicators
- **Characteristics**:
  - Pre-calculated metrics
  - Time-series aggregations
  - Business KPIs
  - Optimized for reporting

## 📈 Apache Superset Integration

### Setup and Access

1. **Start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Access Superset**:
   - URL: http://localhost:8088
   - Username: `admin`
   - Password: `admin`

3. **Database Connection**:
   - Superset is pre-configured to connect to the PostgreSQL database
   - All schemas (stg, ods, dm) are accessible

### 🎯 Pre-built Dashboards

The system includes several business-focused data marts perfect for Superset dashboards:

#### **Trading Analytics Dashboard**
- Daily trading volumes
- Unique trader counts
- Pool performance metrics
- Asset trading patterns

#### **Staking Analytics Dashboard**
- Staking/unstaking trends
- Reward distributions
- Staker behavior analysis
- APY calculations

#### **KPI Dashboard**
- Platform overview metrics
- Growth indicators
- Performance benchmarks
- Real-time statistics

## 🚀 Getting Started

### 1. Initialize the Database

```bash
# Initialize all schemas and tables
docker-compose exec puzzle-etl poetry run puzzle-etl init-db
```

This creates:
- All three schemas (stg, ods, dm)
- Complete table structure
- Proper indexes and constraints
- Initial data migration (if applicable)

### 2. Run ETL Pipeline

```bash
# Run full ETL pipeline
docker-compose exec puzzle-etl poetry run puzzle-etl run --full
```

The pipeline now:
- Saves raw data to STG schema
- Processes and validates data in ODS schema
- Creates aggregations in DM schema
- Processes data in batches for real-time updates

### 3. Access Superset

1. Navigate to http://localhost:8088
2. Login with admin/admin
3. Create datasets from DM schema tables
4. Build dashboards using the business-ready data

## 📊 Sample Queries

### Trading Volume Analysis
```sql
SELECT 
    date,
    total_volume_usd,
    total_swaps,
    unique_traders,
    avg_swap_size_usd
FROM dm.trading_metrics_daily
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date;
```

### Top Performing Pools
```sql
SELECT 
    pool_name,
    asset_a_symbol || '/' || asset_b_symbol as pair,
    total_volume_usd,
    total_swaps,
    unique_traders
FROM dm.pool_metrics
WHERE period_type = 'daily'
    AND period_start = CURRENT_DATE - 1
ORDER BY total_volume_usd DESC
LIMIT 10;
```

### Staking Trends
```sql
SELECT 
    date,
    total_staked,
    total_staked_usd,
    unique_stakers,
    net_staking_flow
FROM dm.staking_metrics_daily
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date;
```

### KPI Overview
```sql
SELECT 
    total_volume_usd_24h,
    total_swaps_24h,
    unique_traders_24h,
    total_staked_usd,
    unique_stakers,
    volume_growth_24h,
    trader_growth_24h
FROM dm.kpi_summary
WHERE date = CURRENT_DATE;
```

## 🔧 Configuration

### Environment Variables

Key BI-related environment variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://puzzle_user:puzzle_password@postgres:5432/puzzle_swap

# Superset
SUPERSET_SECRET_KEY=your-secret-key-change-this-in-production

# ETL Batch Processing
BATCH_SIZE=100
MAX_TRANSACTIONS_IN_MEMORY=1000
```

### Superset Configuration

The `superset_config.py` file includes:
- Database connection settings
- Security configuration
- Feature flags for advanced functionality
- Custom styling options

## 📁 File Structure

```
puzzle-swap-etl/
├── src/puzzle_swap_etl/database/
│   ├── models.py          # Legacy models (public schema)
│   ├── models_stg.py      # Staging schema models
│   ├── models_ods.py      # ODS schema models
│   ├── models_dm.py       # Data mart schema models
│   └── init.py            # Database initialization
├── init-scripts/
│   └── 01-create-schemas.sql  # Schema creation script
├── superset_config.py     # Superset configuration
├── superset-init.sh       # Superset initialization script
└── docker-compose.yml     # Updated with Superset service
```

## 🎯 Best Practices

### Data Flow
1. **Extract** → STG schema (raw data)
2. **Transform** → ODS schema (cleaned data)
3. **Aggregate** → DM schema (business metrics)
4. **Visualize** → Superset dashboards

### Performance Optimization
- Use DM schema tables for dashboards (pre-aggregated)
- Leverage indexes on time-based columns
- Implement incremental updates for large datasets
- Cache frequently accessed metrics

### Data Quality
- Validate data in ODS layer
- Track ETL batch metadata
- Monitor data freshness
- Implement data quality checks

## 🔍 Monitoring

### ETL Pipeline Health
- Check `etl_metadata` table for process tracking
- Monitor batch processing logs
- Validate data quality flags in ODS tables

### Superset Performance
- Monitor query performance in SQL Lab
- Use appropriate chart types for data volumes
- Implement caching for heavy queries

## 🆘 Troubleshooting

### Common Issues

1. **Superset won't start**:
   ```bash
   docker-compose logs superset
   ```

2. **Database connection issues**:
   ```bash
   docker-compose exec postgres psql -U puzzle_user -d puzzle_swap -c "\l"
   ```

3. **Schema not found**:
   ```bash
   docker-compose exec puzzle-etl poetry run puzzle-etl init-db
   ```

4. **No data in DM tables**:
   ```bash
   # Check if ODS has data
   docker-compose exec postgres psql -U puzzle_user -d puzzle_swap -c "SELECT COUNT(*) FROM ods.swaps;"
   ```

## 🔮 Future Enhancements

- Real-time streaming updates
- Advanced ML-based analytics
- Custom Superset plugins
- Automated report generation
- Data lineage tracking
- Advanced data quality monitoring

---

For more information, see the main [README.md](README.md) file. 
 