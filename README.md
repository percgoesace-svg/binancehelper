# Binance RSI Bot

To deploy: click Railway button or use CLI

## API

The application exposes REST endpoints documented at `/docs`:

- `GET /api/data/{symbol}` – retrieve market data for the specified trading pair.
- `GET /api/strategy` – fetch the current trading strategy.
- `POST /api/strategy` – update the trading strategy.
