"""
Yahoo Finance Client — free historical price data via yfinance.

Provides annual and monthly high, low, and close prices for stock tickers.
No API key required.
"""

import logging
from typing import Any, Dict, List, Optional

import yfinance as yf

logger = logging.getLogger(__name__)


class YFinanceClient:
    """Client for historical stock price data via yfinance."""

    def get_annual_price_history(
        self,
        ticker: str,
        years: int = 11,
    ) -> Optional[Dict[str, Any]]:
        """
        Get annual high, low, and average close prices.

        Args:
            ticker: Stock ticker symbol.
            years: Number of years of history (default 11 for 2016-2026 range).

        Returns:
            Dict with ticker, rows (year, high, low, avg_close), or None on failure.
        """
        ticker = ticker.upper().strip()
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period=f"{years}y")

            if hist.empty:
                return None

            # Group by calendar year
            hist_year = hist.index.year

            rows: List[Dict[str, Any]] = []
            for year in sorted(hist_year.unique(), reverse=True):
                year_data = hist[hist_year == year]
                rows.append({
                    "year": int(year),
                    "high": round(float(year_data["High"].max()), 2),
                    "low": round(float(year_data["Low"].min()), 2),
                    "avg_close": round(float(year_data["Close"].mean()), 2),
                })

            return {
                "ticker": ticker,
                "periods": len(rows),
                "rows": rows,
            }

        except Exception as e:
            logger.error(f"Failed to get price history for {ticker}: {e}")
            return None

    def get_monthly_price_history(
        self,
        ticker: str,
        years: int = 10,
    ) -> Optional[Dict[str, Any]]:
        """
        Get monthly high, low, and last close prices.

        Built from daily prices grouped by calendar month (not Yahoo's
        1mo interval, whose current-month bar can be stale). Prices are
        split-adjusted but not dividend-adjusted, so recent closes match
        the quoted price.

        Args:
            ticker: Stock ticker symbol.
            years: Number of years of history (default 10).

        Returns:
            Dict with ticker, rows (month "YYYY-MM", high, low, close),
            newest first, or None on failure.
        """
        ticker = ticker.upper().strip()
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period=f"{years}y", auto_adjust=False)

            if hist.empty:
                return None

            month_key = hist.index.strftime("%Y-%m")

            rows: List[Dict[str, Any]] = []
            for month in sorted(month_key.unique(), reverse=True):
                month_data = hist[month_key == month]
                rows.append({
                    "month": str(month),
                    "high": round(float(month_data["High"].max()), 2),
                    "low": round(float(month_data["Low"].min()), 2),
                    "close": round(float(month_data["Close"].iloc[-1]), 2),
                })

            return {
                "ticker": ticker,
                "periods": len(rows),
                "rows": rows,
            }

        except Exception as e:
            logger.error(f"Failed to get monthly price history for {ticker}: {e}")
            return None
