# Binance RSI Bot

To deploy: click Railway button or use CLI.

## API

The application exposes REST endpoints documented at `/docs`:

- `GET /api/data/{symbol}` – retrieve market indicators (RSI, EMA9, EMA20) and signal for the given pair.
- `GET /api/trading_pairs` – list trading pairs used by the bot; falls back to Binance CMS (New Listings) if state is empty.
- `GET /api/strategy` – fetch the current trading strategy.
- `POST /api/strategy` – update the trading strategy.
- `GET /api/debug/pairs` – debug helper showing the trading-pairs state.

