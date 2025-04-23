
import streamlit as st
import pandas as pd

st.set_page_config(page_title="USDT Price Summary", layout="wide")
st.title("💱 USDT Price Summary (Divide Rules)")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [col.strip().lower() for col in df.columns]

    # Rename for easier access if needed
    df = df.rename(columns={
        "date": "date",
        "type": "type",
        "coin name": "coin",
        "amount": "amount",
        "price": "price",
        "net amount": "net_amount",
        "tds": "tds",
        "usdt received": "usdt_received"
    })

    df["date"] = pd.to_datetime(df["date"]).dt.date
    summary = []

    for coin, grp in df.groupby("coin"):
        earliest_date = grp["date"].min()
        types = grp["type"].str.upper().unique()
        buy_sell = "Both" if len(types) == 2 else types[0]

        pair = "USDT" if "USDT" in coin.upper() else "INR"
        total_amount = grp["amount"].sum()
        avg_price = (grp["price"] * grp["amount"]).sum() / total_amount if total_amount else 0
        total_net = grp["net_amount"].sum()
        tds_inr = 0 if buy_sell == "Buy" else grp["tds"].sum()

        usdt_price = ""
        if buy_sell in ["Sell", "Both"] and pair == "USDT":
            sells = grp[grp["type"].str.lower() == "sell"]
            total_sell_amount = sells["amount"].sum()
            total_usdt_received = sells["usdt_received"].sum()
            avg_buy_price = (grp[grp["type"].str.lower() == "buy"]["price"] * grp[grp["type"].str.lower() == "buy"]["amount"]).sum()
            avg_buy_price /= grp[grp["type"].str.lower() == "buy"]["amount"].sum() if not grp[grp["type"].str.lower() == "buy"]["amount"].sum() == 0 else 1
            usdt_price = (total_sell_amount * avg_buy_price) / total_usdt_received if total_usdt_received else ""

        summary.append({
            "Date": earliest_date,
            "Buy/Sell": buy_sell,
            "Coin": coin,
            "Pair": pair,
            "Amount": total_amount,
            "Price": round(avg_price, 4),
            "Net Amount in Base Currency": round(total_net, 2),
            "TDS in INR": round(tds_inr, 2),
            "USDT Price": round(usdt_price, 4) if usdt_price != "" else ""
        })

    result = pd.DataFrame(summary)
    st.dataframe(result)

    st.download_button("📥 Download Summary as Excel",
                       data=result.to_excel(index=False),
                       file_name="usdt_price_summary.xlsx")
