import React, { useEffect, useState, useRef } from "react";
import io from "socket.io-client";
import { Card } from "@mui/material";

function Ticker() {
  const [value, setValue] = useState("0.00"); // Move useState outside of useEffect
  const [valueColor, setValueColor] = useState("info");
  const [ticker, setTicker] = useState("");

  const previousPrice = useRef(null);

  useEffect(() => {
    const socket = io("http://localhost:5001");

    // Listen for data from level 1 stream
    socket.on("LEVEL_ONE_STREAM", function (data) {
      console.log("Received data from LEVEL_ONE_STREAM:", data);
      const lastPrice = parseFloat(data.last_price);

      if (previousPrice.current !== null) {
        if (lastPrice > previousPrice.current) {
          setValueColor("green");
        } else if (lastPrice < previousPrice.current) {
          setValueColor("red");
        } else {
          setValueColor("black");
        }
      }

      previousPrice.current = lastPrice;
      setValue(lastPrice);
    });

    // Handle connection
    socket.on("connect", function () {
      console.log("Ticker Component Connected to server");
    });

    // Handle disconnection
    socket.on("disconnect", () => {
      console.log("Ticker Component Disconnected from the server");
    });

    // Clean up on component unmount
    return () => {
      socket.disconnect();
    };
  }, []);

  useEffect(() => {
    fetch("http://localhost:5001/ticker")
      .then((res) => res.json())
      .then((data) => {
        setTicker(data.ticker);
        console.log("TICKER:", data.ticker);
      })
      .catch((error) => console.log("ERROR", error));
  }, []);

  return (
    <Card sx={{ minWidth: 275, minHeight: 195, textAlign: "center", padding: 1 }}>
      <div style={{ fontWeight: "bold", paddingBottom: 12 }}>Ticker</div>
      <div style={{ fontSize: "32px", paddingBottom: 12 }}>{ticker}</div>
      <div>
        <span>
          <span style={{ color: valueColor }}>{value}</span>
        </span>
      </div>
    </Card>
  );
}

export default Ticker;
